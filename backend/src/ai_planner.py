import json
from src.llm import tracked_chat
from src.utils import logger, repair_and_load_json

PLAN_PROMPT = """You are an expert data scientist advising on a specific dataset.
Given ONLY the profile, data dictionary, and domain playbook, propose:
(A) A tailored set of EDA analyses that would actually reveal something useful about THIS data, AND
(B) A tailored set of cleaning treatments.

Rules:
- Base every proposal on the profile/dictionary. Never invent columns or numbers.
- Use only these analysis_types: numeric_distribution | category_breakdown | numeric_relationship | numeric_by_category | correlation | top_n
- Use only these chart_types: histogram | bar | scatter | box | heatmap | table
- Use only these cleaning actions: remove_duplicates | fill_nulls | drop_null_rows | remove_outliers | remove_invalid_prices | standardize_text | clip_values | cast_dtype
- For each proposal return: kind, columns (real names from the profile), chart_type or cleaning params, title, why, expected_output, beginner_hint, priority (high|medium|low)

Return ONLY valid JSON:
{
  "analyses": [
    {
      "analysis_type": "...",
      "columns": ["col1", "col2"],
      "chart_type": "...",
      "title": "...",
      "why": "...",
      "expected_output": "...",
      "beginner_hint": "...",
      "priority": "high"
    }
  ],
  "cleaning": [
    {
      "action": "...",
      "column": "col1",
      "reasoning": "...",
      "priority": "high"
    }
  ]
}"""

SAFE_ACTIONS = {"remove_duplicates", "fill_nulls", "drop_null_rows", "remove_outliers",
                "remove_invalid_prices", "standardize_text", "clip_values", "cast_dtype"}
SAFE_ANALYSES = {"numeric_distribution", "category_breakdown", "numeric_relationship",
                 "numeric_by_category", "correlation", "top_n"}
SAFE_CHARTS = {"histogram", "bar", "scatter", "box", "heatmap", "table"}

def ai_plan(run_id, profile, dictionary, domain):
    payload = {
        "shape": profile.get("shape"),
        "domain": domain,
        "columns": [
            {
                "name": c["name"],
                "dtype": c.get("dtype"),
                "kind": c.get("kind"),
                "null_pct": c.get("null_pct"),
                "unique": c.get("unique"),
                "unique_pct": c.get("unique_pct"),
                "stats": c.get("stats")
            }
            for c in profile.get("columns", [])
        ],
        "dictionary": [
            {
                "name": d["name"],
                "semantic_type": d.get("semantic_type"),
                "meaning": d.get("meaning")
            }
            for d in dictionary
        ]
    }
    text = tracked_chat(
        run_id, "AI_PLANNER", "planner",
        [
            {"role": "system", "content": PLAN_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ],
        temperature=0.2, max_completion_tokens=900
    )
    plan = repair_and_load_json(text, default={"analyses": [], "cleaning": []})
    logger.info(f"AI planner returned {len(plan.get('analyses', []))} analyses, {len(plan.get('cleaning', []))} cleaning")
    return plan
