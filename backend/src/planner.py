import pandas as pd
from src.utils import logger

ALTERNATIVES = {
    "remove_duplicates": ["remove exact duplicates", "fuzzy dedup (near-matches)", "keep all (flag dupes)"],
    "fill_nulls": ["fill median/mode", "drop null rows", "add was_null indicator + fill"],
    "drop_null_rows": ["drop null rows", "fill median/mode", "add was_null indicator + fill"],
    "remove_outliers": ["remove IQR outliers", "flag outliers (keep)", "winsorize (cap)"],
    "remove_invalid_prices": ["remove rows <=0", "set to NaN then fill", "keep (flag)"],
    "standardize_text": ["strip+title-case", "lower-case", "keep as-is"],
    "clip_values": ["clip to IQR", "clip to percentiles 1/99", "keep as-is"],
    "cast_dtype": ["cast to numeric", "cast to string", "cast to datetime"],
}

BASE = {  # action: (benefit, risk)
    "remove_duplicates": (0.9, 0.1),
    "fill_nulls": (0.7, 0.2),
    "drop_null_rows": (0.5, 0.6),
    "remove_outliers": (0.5, 0.5),
    "remove_invalid_prices": (0.8, 0.15),
    "standardize_text": (0.6, 0.1),
    "fuzzy_dedup": (0.6, 0.4),
    "clip_values": (0.55, 0.35),
    "cast_dtype": (0.6, 0.3),
}

def score_step(step):
    impact_pct = step["impact"].get("pct", 0)
    benefit, risk = BASE.get(step["action"], (0.5, 0.5))
    caution = min(impact_pct / 50.0, 1.0)
    score = benefit - 0.5 * risk - 0.3 * caution
    tier = (
        "STRONGLY RECOMMEND" if score >= 0.6 else
        "RECOMMEND" if score >= 0.35 else
        "OPTIONAL" if score >= 0.15 else
        "NOT RECOMMENDED"
    )
    risk_level = "low" if risk < 0.3 else "medium" if risk < 0.6 else "high"
    return round(score, 2), tier, risk_level

def compute_impact(df, step):
    action = step["action"]
    col = step.get("column")
    subset = step.get("subset")
    total = len(df) if len(df) > 0 else 1
    def pct(n): return round(n / total * 100, 2)
    
    if action == "remove_duplicates":
        if subset and len(subset) > 0 and all(c in df.columns for c in subset):
            df_sub = df[subset].copy()
            for c in df_sub.select_dtypes(include=["object", "string"]).columns:
                df_sub[c] = df_sub[c].astype(str).str.strip().str.lower()
            n = int(df_sub.duplicated().sum())
        else:
            n = int(df.duplicated().sum())
        return {"rows_removed": n, "pct": pct(n)}
    if action == "drop_null_rows":
        n = int(df[col].isnull().sum())
        return {"rows_removed": n, "pct": pct(n)}
    if action == "fill_nulls":
        n = int(df[col].isnull().sum())
        return {"values_changed": n, "pct": pct(n)}
    if action == "remove_outliers":
        s = df[col].dropna()
        if len(s) < 4:
            return {"rows_removed": 0, "pct": 0.0}
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            return {"rows_removed": 0, "pct": 0.0}
        n = int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
        return {"rows_removed": n, "pct": pct(n)}
    if action == "remove_invalid_prices":
        n = int((df[col] <= 0).sum())
        return {"rows_removed": n, "pct": pct(n)}
    if action == "standardize_text":
        s = df[col].dropna().astype(str)
        cleaned = s.str.strip().str.title()
        n = int((s != cleaned).sum())
        return {"values_changed": n, "pct": pct(n)}
    return {"rows_removed": 0, "pct": 0.0}

def detect_leakage(profile, dictionary):
    flags = []
    sem = {d["name"]: d for d in dictionary}
    for col in profile.get("columns", []):
        name = col["name"]
        if col.get("unique_pct", 0) > 95 and sem.get(name, {}).get("semantic_type") == "identifier":
            flags.append({"column": name, "type": "identifier", "note": "near-unique ID; exclude from modeling"})
        if col.get("unique", 0) == 1:
            flags.append({"column": name, "type": "constant", "note": "zero variance; useless"})
    return flags

def build_plan(profile, dictionary, df):
    steps = []
    sid = 1
    sem = {d["name"]: d for d in dictionary}
    
    # 1. Intelligent Deduplication
    payload_dupes = profile.get("payload_duplicates", 0)
    exact_dupes = profile.get("duplicate_rows", 0)
    payload_cols = profile.get("payload_columns") or df.columns.tolist()

    if payload_dupes > 0 or exact_dupes > 0:
        use_subset = payload_cols if (payload_dupes > exact_dupes and len(payload_cols) < len(df.columns)) else None
        desc = "Remove duplicate business entities (ignoring row index)" if use_subset else "Remove exact duplicate rows"
        s = {
            "id": sid,
            "action": "remove_duplicates",
            "subset": use_subset,
            "description": desc
        }
        s["impact"] = compute_impact(df, s)
        s["alternatives"] = ALTERNATIVES["remove_duplicates"]
        s["score"], s["tier"], s["risk"] = score_step(s)
        steps.append(s)
        sid += 1

    # 2. Column-level cleaning steps
    for col in profile.get("columns", []):
        name = col["name"]
        if col.get("is_index_column"):
            continue

        if col.get("null_pct", 0) > 0:
            act = "drop_null_rows" if col["null_pct"] > 50 else "fill_nulls"
            s = {
                "id": sid,
                "action": act,
                "column": name,
                "description": f"{'Drop' if act == 'drop_null_rows' else 'Fill'} nulls in '{name}'"
            }
            s["impact"] = compute_impact(df, s)
            s["alternatives"] = ALTERNATIVES[act]
            s["score"], s["tier"], s["risk"] = score_step(s)
            steps.append(s)
            sid += 1

        if col.get("kind") == "numeric" and col.get("outliers", 0) > 0:
            s = {
                "id": sid,
                "action": "remove_outliers",
                "column": name,
                "description": f"Remove IQR outliers in '{name}'"
            }
            s["impact"] = compute_impact(df, s)
            s["alternatives"] = ALTERNATIVES["remove_outliers"]
            s["score"], s["tier"], s["risk"] = score_step(s)
            steps.append(s)
            sid += 1

        if col.get("kind") == "numeric" and "price" in name.lower():
            if int((df[name] <= 0).sum()) > 0:
                s = {
                    "id": sid,
                    "action": "remove_invalid_prices",
                    "column": name,
                    "description": f"Remove rows where '{name}' <= 0"
                }
                s["impact"] = compute_impact(df, s)
                s["alternatives"] = ALTERNATIVES["remove_invalid_prices"]
                s["score"], s["tier"], s["risk"] = score_step(s)
                steps.append(s)
                sid += 1

        if sem.get(name, {}).get("semantic_type") in ("categorical", "free_text", "identifier"):
            s = {
                "id": sid,
                "action": "standardize_text",
                "column": name,
                "description": f"Standardize text in '{name}'"
            }
            s["impact"] = compute_impact(df, s)
            s["alternatives"] = ALTERNATIVES["standardize_text"]
            s["score"], s["tier"], s["risk"] = score_step(s)
            steps.append(s)
            sid += 1

    # Blend with learned user preferences from PreferenceModel
    from src.preference import pref_model
    for s in steps:
        pref_prob = pref_model.score_step(s["action"], s["impact"].get("pct", 0), s["risk"])
        if pref_prob < 0.3:
            s["tier"] = "NOT RECOMMENDED"
        elif pref_prob > 0.8:
            s["tier"] = "STRONGLY RECOMMEND"

    logger.info(f"Built {len(steps)} candidate steps")
    return steps
