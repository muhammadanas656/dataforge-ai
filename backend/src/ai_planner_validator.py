import pandas as pd
from src.ai_planner import SAFE_ACTIONS, SAFE_ANALYSES, SAFE_CHARTS
from src.planner import compute_impact, score_step
from src.utils import logger

def _col_exists(name, profile):
    return any(c["name"] == name for c in profile.get("columns", []))

def _col_kind(name, profile):
    for c in profile.get("columns", []):
        if c["name"] == name:
            return c.get("kind")
    return None

def validate_analysis(a, profile):
    t = a.get("analysis_type")
    cols = a.get("columns", []) or []
    if t not in SAFE_ANALYSES:
        return False, f"analysis_type '{t}' not allowed"
    if a.get("chart_type") and a["chart_type"] not in SAFE_CHARTS:
        return False, "chart_type not allowed"
    for c in cols:
        if not _col_exists(c, profile):
            return False, f"column '{c}' does not exist"

    # Type-compatibility checks
    if t in ("numeric_distribution", "top_n") and any(_col_kind(c, profile) != "numeric" for c in cols):
        return False, "requires numeric column"
    if t == "category_breakdown" and any(_col_kind(c, profile) == "numeric" for c in cols):
        return False, "requires categorical column"
    if t in ("numeric_relationship", "correlation") and len(cols) < 2:
        return False, "needs at least 2 numeric columns"
    return True, "ok"

def validate_cleaning(treatment, profile, df):
    action = treatment.get("action")
    col = treatment.get("column")
    if action not in SAFE_ACTIONS:
        return False, "unsafe action", None
    if col and not _col_exists(col, profile):
        return False, f"column '{col}' missing", None
    step = {"action": action, "column": col}
    if df is not None:
        try:
            impact = compute_impact(df, step)
        except Exception as e:
            return False, f"impact failed: {e}", None
        step["impact"] = impact
    else:
        step["impact"] = {"rows_removed": 0, "pct": 0.0}

    step["description"] = treatment.get("reasoning", f"AI-proposed: {action} on {col or 'all'}")
    step["source"] = "ai"
    score, tier, risk = score_step(step)
    step["score"], step["tier"], step["risk"] = score, tier, risk
    return True, "ok", step

def filter_proposals(plan, profile, df=None):
    analyses, cleaning = [], []
    for a in plan.get("analyses", []) or []:
        ok, why = validate_analysis(a, profile)
        if ok:
            analyses.append({**a, "source": "ai"})
        else:
            logger.info(f"[ai_planner] drop analysis: {why}")
    for t in plan.get("cleaning", []) or []:
        ok, why, step = validate_cleaning(t, profile, df)
        if ok:
            cleaning.append(step)
        else:
            logger.info(f"[ai_planner] drop cleaning: {why}")
    return {"analyses": analyses, "cleaning": cleaning}
