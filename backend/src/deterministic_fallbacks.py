"""Rule-based fallbacks for when LLM is weak or unavailable."""
import re
import pandas as pd
from src.frugal import semantic_type_rules


def fallback_semantic_type(col):
    """Rule-based semantic type detection."""
    sem, confidence = semantic_type_rules(col)
    return {
        "semantic_type": sem,
        "meaning": _generate_meaning(col.get("name", "column"), sem),
        "source": "rule_fallback",
        "confidence": confidence
    }


def fallback_cleaning_plan(profile):
    """Rule-based cleaning plan generation."""
    steps = []
    sid = 1

    if profile.get("duplicate_pct", 0) > 1:
        steps.append({
            "id": sid,
            "action": "remove_duplicates",
            "description": f"Remove {profile.get('duplicate_rows', 0)} duplicate rows",
            "impact": {"rows_removed": profile.get("duplicate_rows", 0), "pct": profile.get("duplicate_pct", 0)}
        })
        sid += 1

    for col in profile.get("columns", []):
        if col.get("null_pct", 0) > 5:
            steps.append({
                "id": sid,
                "action": "fill_nulls",
                "column": col["name"],
                "description": f"Fill {col['null_pct']}% nulls in '{col['name']}'",
                "impact": {"nulls_filled": col.get("nulls", 0)}
            })
            sid += 1

    for col in profile.get("columns", []):
        if col.get("kind") == "numeric" and col.get("outlier_pct", 0) > 2:
            steps.append({
                "id": sid,
                "action": "remove_outliers",
                "column": col["name"],
                "description": f"Remove {col['outlier_pct']}% outliers from '{col['name']}'",
                "impact": {"rows_affected": col.get("outliers", 0)}
            })
            sid += 1

    return steps


def fallback_narrative(profile):
    """Template-based narrative generation."""
    rows = profile.get("total_rows", 0)
    cols = profile.get("total_columns", 0)
    dup_pct = profile.get("duplicate_pct", 0)

    null_pcts = [c.get("null_pct", 0) for c in profile.get("columns", [])]
    avg_null = sum(null_pcts) / len(null_pcts) if null_pcts else 0

    narrative = (
        f"Dataset contains {rows:,} rows and {cols} columns. "
        f"Duplicate rate is {dup_pct:.1f}%. "
        f"Average null rate is {avg_null:.1f}%."
    )

    if dup_pct > 10:
        narrative += " High duplication suggests data collection issues."
    if avg_null > 20:
        narrative += " Significant missing values may impact analysis."

    return narrative


def fallback_critic_findings(profile):
    """Rule-based critic findings."""
    findings = []

    if profile.get("duplicate_pct", 0) > 5:
        findings.append({
            "type": "high_duplicates",
            "severity": "medium",
            "message": f"Dataset has {profile['duplicate_pct']}% duplicates"
        })

    high_null_cols = [
        c["name"] for c in profile.get("columns", [])
        if c.get("null_pct", 0) > 30
    ]
    if high_null_cols:
        findings.append({
            "type": "high_nulls",
            "severity": "high",
            "message": f"Columns with >30% nulls: {', '.join(high_null_cols)}"
        })

    return findings


def _generate_meaning(col_name, semantic_type):
    meanings = {
        "currency": f"Monetary value in '{col_name}'",
        "numeric_continuous": f"Continuous measurement in '{col_name}'",
        "numeric_discrete": f"Count in '{col_name}'",
        "identifier": f"Unique ID in '{col_name}'",
        "categorical": f"Category label in '{col_name}'",
        "free_text": f"Text field '{col_name}'",
        "date": f"Date/timestamp in '{col_name}'",
    }
    return meanings.get(semantic_type, f"Data field '{col_name}'")
