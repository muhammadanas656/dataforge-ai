"""
L1/L2/L3 Contextual Bandit Remediation Engine with Thompson Sampling.
"""
import os
import pandas as pd
from src.utils import logger
from src.remediation_ops import apply_plan
from src.remediation_memory import memory as default_memory
from src.remediation_agent import propose_and_validate
from src import incidents

# L3 AUTO-FIX THRESHOLDS
AUTO_FIX_MAX_DROP_PCT = 5.0     # Never auto-drop more than 5% of rows
AUTO_FIX_MAX_DROP_ROWS = 500    # Never auto-drop more than 500 rows absolute
SAFE_AUTO_OPS = {
    "coerce_numeric", "coerce_date", "fill_mode", "clip", "flag_outliers", "extract_text"
}

def is_safe_for_auto_fix(plan: dict) -> bool:
    """Determines if a proposed fix is safe enough to apply without human approval."""
    if not plan:
        return False
    op = plan.get("op")
    if op not in SAFE_AUTO_OPS:
        return False
    
    impact = plan.get("impact", {})
    if impact.get("drop_pct", 100.0) > AUTO_FIX_MAX_DROP_PCT:
        return False
    if impact.get("rows_dropped", 9999) > AUTO_FIX_MAX_DROP_ROWS:
        return False
    return True

def remediate(run_id: str, df: pd.DataFrame, incident: dict, mem=None):
    """
    The Contextual Bandit Master Remediation Loop:
    1. L1: Thompson-sample among validated candidate arms in memory (0 tokens).
    2. L2/L3: Propose new candidate arm via Agent.
    3. L3: If safe (drop <= 5% and non-destructive op), auto-apply and reward arm in bandit.
    4. L2: If high-impact, escalate to human approval queue with candidate plan_id.
    """
    mem = mem or default_memory
    sig = mem.signature(incident)

    # 1. L1 Check: Thompson sampling among validated arms
    sel = mem.select(sig)
    if sel:
        plan, pid = sel
        try:
            df_fixed = apply_plan(df, plan)
            mem.update(sig, pid, True)  # positive reward
            logger.info(f"L1 Bandit Hit ({pid}): Applied learned plan via Thompson sampling")
            return df_fixed, {"source": "memory_l1", "selection": "thompson", "plan": plan}
        except Exception as e:
            mem.update(sig, pid, False)  # negative reward for failing arm
            logger.warning(f"L1 Bandit Arm {pid} failed: {e}")
            incidents.report_incident(incident.get("kind", "unknown"), incident.get("context", {}), f"learned fix failed: {e}")

    # 2. Agent Proposal: New arm enters the bandit
    sample = df.head(5000) if len(df) > 5000 else df
    proposal = propose_and_validate(run_id, incident, sample)

    if not proposal:
        inc = incidents.report_incident(incident.get("kind", "unknown"), incident.get("context", {}), "agent_failed_to_propose")
        return df, {"source": "escalate", "incident_id": inc["id"], "reason": "no_valid_proposal"}

    pid = mem.add_candidate(sig, proposal)

    # 3. L3 Auto-Fix Check (Safe low-impact)
    auto_l3_enabled = os.getenv("DATAFORGE_AUTO_L3", "true").lower() == "true"
    if auto_l3_enabled and is_safe_for_auto_fix(proposal):
        try:
            df_fixed = apply_plan(df, proposal)
            mem.update(sig, pid, True)  # validate arm into memory
            inc = incidents.report_incident(incident.get("kind", "unknown"), incident.get("context", {}))
            incidents.mark_resolved(inc["id"], {"resolution": "auto_fixed_l3", "plan": proposal, "sig": sig, "plan_id": pid})
            logger.info(f"L3 Auto-Fix Applied & Arm Validated: {proposal.get('op')} on {proposal.get('params', {}).get('column')}")
            return df_fixed, {"source": "auto_l3", "plan": proposal, "incident_id": inc["id"]}
        except Exception as e:
            mem.update(sig, pid, False)
            inc = incidents.report_incident(incident.get("kind", "unknown"), incident.get("context", {}), f"auto fix failed: {e}")
            return df, {"source": "escalate", "incident_id": inc["id"]}

    # 4. L2 Escalation (High Impact or Destructive)
    inc = incidents.report_incident(incident.get("kind", "unknown"), incident.get("context", {}))
    incidents.update_incident(inc["id"], {"proposal": proposal, "sig": sig, "plan_id": pid})
    logger.info(f"L2 Escalation: Incident {inc['id']} (arm {pid}) queued for human approval")
    return df, {"source": "needs_approval_l2", "incident_id": inc["id"], "proposal": proposal}
