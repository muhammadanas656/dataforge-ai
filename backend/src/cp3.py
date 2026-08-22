import json
import os
import pandas as pd
from src.utils import logger, repair_and_load_json
from src.llm import tracked_chat
from src.planner import build_plan, detect_leakage
from src import ai_planner, ai_planner_validator, llm_critic

CP3_SYSTEM_PROMPT = """You are a senior data scientist reviewing an auto-generated cleaning plan.
Each step has an action, column, code-computed impact, and recommendation tier.
Respond with ONLY valid JSON (no commentary, no markdown):
{
  "reviews": [
    {"step_id": 1, "verdict": "agree", "reason": "<one line>"}
  ],
  "additions": [
    {"action": "<action>", "column": "<col or null>", "reason": "<one line>"}
  ]
}
Rules:
- Base verdicts on the impact numbers and data-science best practice.
- Verdict must be one of: "agree", "modify", "reject".
- Prefer reversible/low-risk steps. Reject steps whose impact is disproportionate."""

def run_cp3(profile_path):
    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)
    dataset_id = profile["dataset_id"]
    
    dict_path = profile_path.replace("profile_", "dictionary_")
    dict_obj = json.load(open(dict_path, encoding="utf-8"))
    dictionary = dict_obj["dictionary"]
    domain = dict_obj.get("domain", "generic")
    df = pd.read_csv(profile["snapshot"]["csv"])

    # 1. Base statistical cleaning plan
    steps = build_plan(profile, dictionary, df)
    
    # 2. LLM Critic & Blind-Spot Scanner (relational rules & derived features)
    try:
        critic_proposals = llm_critic.scan_blind_spots(dataset_id, profile, dictionary, domain)
        validated_critic_steps = llm_critic.validate_critic_proposals(df, critic_proposals)
        for st in validated_critic_steps:
            st["id"] = len(steps) + 1
            steps.append(st)
        logger.info(f"Integrated {len(validated_critic_steps)} mathematically validated Critic steps")
    except Exception as e:
        logger.warning(f"LLM Critic scanning skipped: {e}")

    # 3. AI Planner Cleaning Treatments
    try:
        ai_p = ai_planner.ai_plan(dataset_id, profile, dictionary, domain)
        validated = ai_planner_validator.filter_proposals(ai_p, profile, df)
        seen = set((s["action"], s.get("column")) for s in steps)
        for st in validated["cleaning"]:
            key = (st["action"], st.get("column"))
            if key in seen:
                continue
            seen.add(key)
            st["id"] = len(steps) + 1
            steps.append(st)
        logger.info(f"Merged {len(validated['cleaning'])} AI cleaning proposals")
    except Exception as e:
        logger.warning(f"AI cleaning merge skipped: {e}")

    leakage = detect_leakage(profile, dictionary)

    payload = {
        "steps": [
            {k: s[k] for k in ("id", "action", "column", "subset", "pandas_expr", "impact", "tier", "risk") if k in s}
            for s in steps
        ],
        "leakage_flags": leakage
    }
    
    logger.info(f"CP3 calling tracked_chat to review {len(steps)} candidate steps for dataset {dataset_id}")
    fallback = {
        "reviews": [{"step_id": st["id"], "verdict": "agree", "reason": "Default auto-approval based on scoring"} for st in steps],
        "additions": []
    }
    try:
        text = tracked_chat(
            dataset_id, "CP3", "plan_reviewer",
            [
                {"role": "system", "content": CP3_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
            ],
            temperature=0.1,
            max_completion_tokens=800
        )
        review = repair_and_load_json(text, default=fallback)
    except Exception as e:
        logger.warning(f"[cp3] Plan review LLM fallback: {e}")
        review = fallback

    # Attach reviews to steps
    rev = {v["step_id"]: v for v in review.get("reviews", []) if "step_id" in v}
    for st in steps:
        st["llm_review"] = rev.get(st["id"], {"verdict": "agree", "reason": "Auto-reviewed"})

    out = {
        "dataset_id": dataset_id,
        "steps": steps,
        "leakage": leakage,
        "additions": review.get("additions", [])
    }
    
    os.makedirs("reports", exist_ok=True)
    path = f"reports/plan_{dataset_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n=== CP3: CLEANING PLAN ({len(steps)} steps) ===")
    for st in steps:
        col_repr = str(st.get("column") or st.get("pandas_expr") or st.get("new_column"))
        print(f"  #{st['id']} [{st['tier']:18s}] {st['action']:24s} "
              f"target={col_repr[:20]:20s} impact={st['impact']} risk={st['risk']}")
        print(f"       LLM: {st['llm_review']['verdict']} - {st['llm_review']['reason']}")
    print(f"\n  leakage flags: {leakage}")
    print(f"  LLM additions: {review.get('additions', [])}")
    return out

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "reports/profile_feab58be.json"
    run_cp3(path)
