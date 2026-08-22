import json
from src.utils import logger, repair_and_load_json
from src.llm import tracked_chat

CP1_SYSTEM_PROMPT = """You are a senior data scientist reviewing a freshly-generated
automated profile of a dataset. You have NOT seen raw rows — only the profile.

Given the profile (shape, column names/types, nulls, duplicates, PII hints, samples),
respond with ONLY a valid JSON object (no markdown, no commentary):

{
  "domain": "<one of: e-commerce, finance, healthcare, telecom, education, sports-retail, generic>",
  "confidence": <0.0 to 1.0>,
  "purpose": "<one sentence describing what this dataset is likely used for>",
  "red_flags": ["<flag 1>", "<flag 2>", ...],
  "pii_risk": "<none|low|medium|high>",
  "next_step_hint": "<one sentence guiding what to focus on next>"
}

Rules:
- Base every claim on the profile data. Never invent.
- If unsure, say "generic" domain and low confidence.
- Red flags must cite specific columns/stats (e.g. "column 'Product' has only 5 unique values across 7878 rows").
- PII risk must reflect the pii_scan results in the profile.
"""

def run_cp1(profile_path):
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    dataset_id = profile.get("dataset_id", "unknown")

    # Build a summarized context (profile, never raw rows)
    summary = {
        "source": profile.get("source"),
        "shape": profile.get("shape"),
        "encoding": profile.get("encoding"),
        "duplicate_pct": profile.get("duplicate_pct"),
        "payload_duplicate_pct": profile.get("payload_duplicate_pct"),
        "near_duplicate_estimate": profile.get("near_duplicate_estimate"),
        "pii_detected": profile.get("pii", {}),
        "columns": [
            {
                "name": c["name"],
                "dtype": c["dtype"],
                "kind": c.get("kind"),
                "null_pct": c["null_pct"],
                "unique": c["unique"],
                "unique_pct": c.get("unique_pct"),
                "samples": c.get("sample_values", []),
                "outliers": c.get("outliers"),
                "stats": c.get("stats")
            }
            for c in profile.get("columns", [])
        ]
    }

    logger.info(f"CP1 invoking tracked_chat for dataset {dataset_id}")
    text = tracked_chat(
        dataset_id, "CP1", "understanding",
        [
            {"role": "system", "content": CP1_SYSTEM_PROMPT},
            {"role": "user", "content": f"Profile:\n{json.dumps(summary, ensure_ascii=False, indent=2)}"}
        ],
        temperature=0.2,
        max_completion_tokens=800
    )

    fallback = {
        "domain": "generic",
        "confidence": 0.5,
        "purpose": "A general tabular dataset recording operations.",
        "red_flags": [],
        "pii_risk": "low",
        "next_step_hint": "Inspect column distributions and verify data quality."
    }
    cp1_result = repair_and_load_json(text, default=fallback)

    # Save alongside profile
    out = profile_path.replace("profile_", "cp1_")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cp1_result, f, indent=2, ensure_ascii=False)
    logger.info(f"CP1 saved to {out}")

    print("\n=== CP1: INGEST UNDERSTANDING ===")
    for k, v in cp1_result.items():
        print(f"  {k}: {v}")
    return cp1_result

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "reports/profile_feab58be.json"
    run_cp1(path)
