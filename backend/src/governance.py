import json
import os
from src.utils import logger

REMOVING = {"remove_duplicates", "remove_outliers", "drop_null_rows", "remove_invalid_prices"}
MODIFYING = {"fill_nulls", "standardize_text", "fuzzy_dedup"}
OVERCLEAN_THRESHOLD = 20.0   # warn if total rows removed > 20%

def govern(step, dictionary):
    action = step["action"]
    pct = step["impact"].get("pct", 0)
    sem = {d["name"]: d for d in dictionary}
    col = step.get("column")
    sensitive = bool(col and sem.get(col, {}).get("pii"))
    verdict = step.get("llm_review", {}).get("verdict", "agree")

    if action in REMOVING:
        if pct < 1 and not sensitive:
            perm, decision = "TRANSFORM_LOW", "auto"
        elif pct < 10 and not sensitive:
            perm, decision = "TRANSFORM_MED", "one_click"
        else:
            perm, decision = "DESTRUCTIVE_HIGH", "mandatory_approval"
    elif action in MODIFYING:
        if pct < 5 and not sensitive:
            perm, decision = "TRANSFORM_LOW", "auto"
        elif pct < 50 and not sensitive:
            perm, decision = "TRANSFORM_MED", "one_click"
        else:
            perm, decision = "DESTRUCTIVE_HIGH", "mandatory_approval"
    else:
        perm, decision = "READ", "auto"

    # LLM review escalation (never downgrade caution)
    if verdict == "reject":
        perm, decision = "DESTRUCTIVE_HIGH", "mandatory_approval"
    elif verdict == "modify" and decision == "auto":
        perm, decision = "TRANSFORM_MED", "one_click"

    kind = "rows" if action in REMOVING else "values"
    return {
        "permission": perm,
        "decision": decision,
        "reason": f"{action} affects {pct}% of {kind}"
                  + ("; PII-sensitive" if sensitive else "")
                  + (f"; LLM said {verdict}" if verdict != "agree" else "")
    }

def validate_addition(add, profile):
    """Cross-check LLM-suggested additions against the profile."""
    act = add.get("action", "")
    if act in ("impute_missing", "fill_nulls"):
        has_nulls = any(c.get("null_pct", 0) > 0 for c in profile.get("columns", []))
        if not has_nulls:
            return False, "rejected_by_crosscheck: no nulls in dataset"
    return True, "ok"

def run_governance(plan_path):
    if not os.path.exists(plan_path):
        if os.path.exists(f"reports/cleaning_plan_{plan_path}.json"):
            plan_path = f"reports/cleaning_plan_{plan_path}.json"
        elif os.path.exists(f"reports/plan_{plan_path}.json"):
            plan_path = f"reports/plan_{plan_path}.json"
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    dataset_id = plan["dataset_id"]
    dict_path = f"reports/dictionary_{dataset_id}.json"
    profile_path = f"reports/profile_{dataset_id}.json"
    dictionary = json.load(open(dict_path, encoding="utf-8"))["dictionary"]
    profile = json.load(open(profile_path, encoding="utf-8"))

    governed = []
    total_removed = 0.0
    for st in plan["steps"]:
        g = govern(st, dictionary)
        st.update(g)
        if st["action"] in REMOVING:
            total_removed += st["impact"].get("pct", 0)
        governed.append(st)

    additions = []
    for add in plan.get("additions", []):
        ok, why = validate_addition(add, profile)
        add["crosscheck"] = why
        additions.append(add)
        if not ok:
            logger.warning(f"LLM addition rejected: {add} ({why})")

    overclean = total_removed > OVERCLEAN_THRESHOLD

    out = {
        "dataset_id": dataset_id,
        "steps": governed,
        "additions": additions,
        "cumulative_rows_removed_pct": round(total_removed, 2),
        "overclean_warning": overclean
    }
    
    os.makedirs("reports", exist_ok=True)
    path = f"reports/governance_{dataset_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n=== PHASE 4: GOVERNANCE ===")
    for st in governed:
        print(f"  #{st['id']} [{st['decision']:20s}] {st['permission']:16s} "
              f"{st['action']:24s} {st['reason']}")
    print(f"\n  cumulative rows removed: {round(total_removed, 2)}% "
          f"{'[!] OVERCLEAN WARNING' if overclean else '(within budget)'}")
    for add in additions:
        print(f"  addition: {add.get('action')} -> {add['crosscheck']}")
    return out

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "reports/plan_feab58be.json"
    run_governance(path)
