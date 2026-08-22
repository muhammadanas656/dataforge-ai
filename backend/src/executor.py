import os
import json
import pandas as pd
import numpy as np
from src.utils import logger
from src.telemetry import telemetry
from src.profiler import get_payload_columns

# Canonical execution order to guarantee mathematically deterministic cleaning
ACTION_ORDER = {
    "remove_duplicates": 1,
    "drop_null_rows": 2,
    "remove_invalid_prices": 3,
    "fix_business_rule": 4,
    "remove_outliers": 5,
    "fill_nulls": 6,
    "standardize_text": 7,
    "extract_category": 8,
    "derive_metric": 9,
    "clip_values": 10,
    "cast_dtype": 11,
}

def quality_breakdown(df):
    n = len(df)
    if n == 0 or df.shape[1] == 0:
        return {
            "overall": 0.0,
            "completeness": 0.0,
            "uniqueness": 0.0,
            "validity": 0.0,
            "consistency": 0.0
        }
    
    # 1. Completeness
    completeness = 1.0 - (df.isnull().sum().sum() / (n * df.shape[1]))
    
    # 2. Uniqueness (evaluated on semantic payload columns with whitespace normalization)
    payload_cols = get_payload_columns(df)
    df_payload = df[payload_cols].copy()
    for c in df_payload.select_dtypes(include=["object", "string"]).columns:
        df_payload[c] = df_payload[c].astype(str).str.strip().str.lower()
    uniqueness = 1.0 - float(df_payload.duplicated().mean())
    
    # 3. Validity (outliers, invalid prices, and cross-column business violations)
    invalid = 0
    tot = 0
    for c in df.select_dtypes(include="number").columns:
        s = df[c].dropna()
        tot += len(s)
        if len(s) >= 4:
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                invalid += int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
        if "price" in c.lower():
            invalid += int((s <= 0).sum())
        if "discount" in c.lower():
            invalid += int(((s < 0) | (s > 100)).sum())
            
    # Cross-column check: special_price <= old_price
    if "special_price" in df.columns and "old_price" in df.columns:
        tot += len(df)
        invalid += int((df["special_price"] > df["old_price"]).sum())

    validity = 1.0 - (invalid / tot) if tot > 0 else 1.0
    
    # 4. Consistency (string casing, whitespace standard)
    ct = 0
    cc = 0
    for c in df.select_dtypes(include="object").columns:
        s = df[c].dropna().astype(str)
        cc += len(s)
        ct += int((s == s.str.strip().str.title()).sum())
    consistency = (ct / cc) if cc > 0 else 1.0

    comp_pct = round(completeness * 100, 2)
    uniq_pct = round(uniqueness * 100, 2)
    val_pct = round(validity * 100, 2)
    cons_pct = round(consistency * 100, 2)
    overall = round((comp_pct + uniq_pct + val_pct + cons_pct) / 4, 2)
    
    return {
        "overall": overall,
        "completeness": comp_pct,
        "uniqueness": uniq_pct,
        "validity": val_pct,
        "consistency": cons_pct,
    }

def describe_changes(prev, curr, step):
    action, col = step["action"], step.get("column")
    changes = []
    num = pd.api.types.is_numeric_dtype(prev[col]) if col and col in prev.columns else False

    if action == "remove_duplicates":
        changes.append({
            "column": "(all rows)" if not step.get("subset") else f"({', '.join(step['subset'][:3])}...)",
            "kind": "rows_removed",
            "count": len(prev) - len(curr),
            "reason": "Duplicate business entities removed.",
        })
    elif action == "fix_business_rule":
        changes.append({
            "column": step.get("pandas_expr", "rule"),
            "kind": "rows_removed",
            "count": len(prev) - len(curr),
            "reason": f"Rows violating business rule '{step.get('pandas_expr')}' removed.",
        })
    elif action == "derive_metric":
        new_col = step.get("new_column", "derived_metric")
        changes.append({
            "column": new_col,
            "kind": "feature_created",
            "count": len(curr),
            "reason": f"Created derived feature '{new_col}' = {step.get('pandas_expr')}.",
        })
    elif action in ("remove_outliers", "remove_invalid_prices", "drop_null_rows"):
        reason_map = {
            "remove_outliers": f"Extreme values beyond 1.5×IQR in '{col}' removed.",
            "remove_invalid_prices": f"Rows where '{col}' ≤ 0 removed (invalid).",
            "drop_null_rows": f"Rows missing '{col}' removed.",
        }
        changes.append({
            "column": col,
            "kind": "rows_removed",
            "count": len(prev) - len(curr),
            "reason": reason_map.get(action, "Rows removed."),
        })
    elif action == "fill_nulls":
        modes = prev[col].dropna().mode() if not num else None
        fill = prev[col].median() if num else (modes.iloc[0] if (modes is not None and len(modes) > 0) else "Unknown")
        changes.append({
            "column": col,
            "kind": "values_filled",
            "count": int(prev[col].isnull().sum()),
            "before": "null",
            "after": str(round(fill, 2)) if isinstance(fill, float) else str(fill),
            "reason": f"Missing values filled with {'median' if num else 'most frequent value'}.",
        })
    elif action == "standardize_text":
        b = prev[col]
        a = curr[col]
        mask = (b.notna()) & (b != a)
        sample = [{"before": str(b[i]), "after": str(a[i])} for i in b[mask].index[:3]]
        changes.append({
            "column": col,
            "kind": "values_standardized",
            "count": int(mask.sum()),
            "sample": sample,
            "reason": "Text trimmed + title-cased for consistency (NaNs preserved).",
        })
    elif action == "clip_values":
        b = prev[col]
        a = curr[col]
        mask = b != a
        changes.append({
            "column": col,
            "kind": "values_clipped",
            "count": int(mask.sum()),
            "reason": "Extreme tail values clipped to 1st/99th percentiles.",
        })
    elif action == "cast_dtype":
        changes.append({
            "column": col,
            "kind": "type_cast",
            "count": len(curr),
            "reason": f"Coerced '{col}' to appropriate numeric/datetime type.",
        })
    return changes

def apply_step(df, step):
    action = step["action"]
    col = step.get("column")
    subset = step.get("subset")
    
    if action == "remove_duplicates":
        if subset and len(subset) > 0 and all(c in df.columns for c in subset):
            df_sub = df.copy()
            for c in subset:
                if c in df_sub.columns and df_sub[c].dtype == "object":
                    df_sub[c] = df_sub[c].astype(str).str.strip().str.lower()
            return df[~df_sub.duplicated(subset=subset)].reset_index(drop=True)
        else:
            payload_cols = get_payload_columns(df)
            if len(payload_cols) < len(df.columns):
                df_sub = df.copy()
                for c in payload_cols:
                    if c in df_sub.columns and df_sub[c].dtype == "object":
                        df_sub[c] = df_sub[c].astype(str).str.strip().str.lower()
                return df[~df_sub.duplicated(subset=payload_cols)].reset_index(drop=True)
            return df.drop_duplicates().reset_index(drop=True)

    if action == "fix_business_rule":
        expr = step.get("pandas_expr")
        if expr:
            if step.get("preserve_signal"):
                df = df.copy()
                try:
                    ok = df.eval(expr, engine="python").astype(bool)
                    flag_col = f"is_{step.get('name', 'rule')}_flag"
                    df[flag_col] = (~ok).astype(int)
                    return df
                except Exception as e:
                    logger.warning(f"Failed to preserve signal for '{expr}': {e}")
                    return df
            try:
                return df.query(expr).reset_index(drop=True)
            except Exception as e:
                logger.warning(f"Failed to query business rule '{expr}': {e}")
                return df
        return df

    if action == "derive_metric":
        new_col = step.get("new_column")
        expr = step.get("pandas_expr")
        if new_col and expr:
            df = df.copy()
            try:
                df[new_col] = df.eval(expr, engine="python")
            except Exception as e:
                logger.warning(f"Failed to eval derived metric '{new_col}' = '{expr}': {e}")
            return df
        return df

    if action == "drop_null_rows":
        return df[df[col].notna()].reset_index(drop=True)

    if action == "fill_nulls":
        df = df.copy()
        if pd.api.types.is_numeric_dtype(df[col]):
            s_clean = df[col].dropna()
            val = float(s_clean.median()) if len(s_clean) > 0 else 0.0
        else:
            modes = df[col].dropna().mode()
            val = modes.iloc[0] if len(modes) > 0 else "Unknown"
        df[col] = df[col].fillna(val)
        return df

    if action == "remove_outliers":
        s = df[col]
        s_clean = s.dropna()
        if len(s_clean) < 4:
            return df
        q1, q3 = s_clean.quantile(0.25), s_clean.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            return df
        return df[(s.isna()) | ((s >= q1 - 1.5 * iqr) & (s <= q3 + 1.5 * iqr))].reset_index(drop=True)

    if action == "remove_invalid_prices":
        return df[(df[col].isna()) | (df[col] > 0)].reset_index(drop=True)

    if action == "standardize_text":
        df = df.copy()
        df[col] = df[col].apply(lambda v: v.strip().title() if pd.notna(v) and isinstance(v, str) else v)
        return df

    if action == "clip_values":
        df = df.copy()
        s = df[col].dropna()
        if len(s) > 0:
            df[col] = df[col].clip(lower=s.quantile(0.01), upper=s.quantile(0.99))
        return df

    if action == "cast_dtype":
        df = df.copy()
        df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    return df

def validate_step(df_after, step):
    action = step["action"]
    col = step.get("column")
    subset = step.get("subset")
    if action == "remove_duplicates":
        if subset and len(subset) > 0 and all(c in df_after.columns for c in subset):
            return df_after.duplicated(subset=subset).sum() == 0
        return df_after.duplicated().sum() == 0
    if action in ("drop_null_rows", "fill_nulls"):
        return df_after[col].isnull().sum() == 0
    if action == "remove_invalid_prices":
        return (df_after[col].dropna() <= 0).sum() == 0
    return True

import threading
import shutil

_LOCKS = {}
_G_LOCK = threading.Lock()

def _dataset_lock(did):
    with _G_LOCK:
        _LOCKS.setdefault(did, threading.Lock())
        return _LOCKS[did]

from src.verification_sandbox import verify_step
from src.query_audit import audit_logger

def run_execution(dataset_id, approved_ids, governance, preserve=None):
    with _dataset_lock(dataset_id):
        snap = f"data/snapshots/{dataset_id}"
        if os.path.isdir(snap):
            shutil.rmtree(snap, ignore_errors=True)  # retention: purge old intermediate step snapshots
        os.makedirs(snap, exist_ok=True)
        prof_path = f"reports/profile_{dataset_id}.json"
        prof = json.load(open(prof_path, encoding="utf-8"))
        df = pd.read_csv(prof["snapshot"]["csv"])
    
    before_rows = len(df)
    before_qb = quality_breakdown(df)
    steps_dict = {s["id"]: s for s in governance["steps"]}
    report = []
    preserve = preserve or {}
    
    # Record approval vs rejection in telemetry
    for s in governance["steps"]:
        if s["id"] in approved_ids:
            telemetry.record("approve", action=s["action"], column=s.get("column"), dataset_id=dataset_id)
        else:
            telemetry.record("reject", action=s["action"], column=s.get("column"), dataset_id=dataset_id)
    
    # Sort approved steps by Canonical Order of Operations while preserving step_id
    approved_steps = [steps_dict[sid] for sid in approved_ids if sid in steps_dict]
    sorted_steps = sorted(approved_steps, key=lambda s: ACTION_ORDER.get(s["action"], 99))

    for st in sorted_steps:
        sid = st["id"]
        if preserve.get(str(sid)) or preserve.get(int(sid)):
            st["preserve_signal"] = True
        prev = df.copy()
        prev.to_parquet(f"{snap}/step_{sid}.parquet", index=False)  # snapshot for undo
        try:
            df_new = apply_step(df, st)
            if validate_step(df_new, st):
                # Anti-hallucination verification
                df_verified, verification = verify_step(prev, df_new, st, dataset_id)
                df = df_verified
                
                # Audit log the pandas transformation
                pandas_code = st.get("pandas_expr") or f"df.{st['action']}(column='{st.get('column')}')"
                audit_logger.log_query(
                    query=pandas_code,
                    schema={"columns": list(df.columns)},
                    metrics={"rows_scanned": len(prev), "rows_returned": len(df)},
                    dataset_id=dataset_id,
                    query_type="pandas"
                )

                report.append({
                    "step_id": sid,
                    "action": st["action"],
                    "column": st.get("column") or st.get("new_column") or st.get("pandas_expr"),
                    "applied": True,
                    "rolled_back": not verification.get("verified", True),
                    "rows_before": len(prev),
                    "rows_after": len(df),
                    "reason": st.get("description"),
                    "changes": describe_changes(prev, df, st),
                    "verification": verification
                })
                telemetry.record("applied", action=st["action"], column=st.get("column"), dataset_id=dataset_id)
                logger.info(f"Step {sid} ({st['action']}) applied: {len(prev)} -> {len(df)} rows (verified: {verification.get('verified')})")
            else:
                logger.warning(f"Step {sid} failed validation -> rollback to previous state")
                df = prev
                report.append({
                    "step_id": sid,
                    "action": st["action"],
                    "column": st.get("column"),
                    "applied": False,
                    "rolled_back": True,
                    "reason": "Post-step validation failed",
                })
                telemetry.record("rollback", action=st["action"], column=st.get("column"), dataset_id=dataset_id)
        except Exception as e:
            logger.error(f"Step {sid} error: {e} -> rollback")
            df = prev
            report.append({
                "step_id": sid,
                "action": st["action"],
                "column": st.get("column"),
                "applied": False,
                "rolled_back": True,
                "error": str(e),
            })
            telemetry.record("rollback", action=st["action"], column=st.get("column"), dataset_id=dataset_id)
            
    out_csv = f"data/canonical/{dataset_id}_cleaned.csv"
    out_pq = f"data/canonical/{dataset_id}_cleaned.parquet"
    os.makedirs("data/canonical", exist_ok=True)
    df.to_csv(out_csv, index=False)
    df.to_parquet(out_pq, index=False)
    
    after_qb = quality_breakdown(df)
    quality_delta = round(after_qb["overall"] - before_qb["overall"], 2)
    exec_summary = {
        "dataset_id": dataset_id,
        "before_rows": before_rows,
        "after_rows": len(df),
        "rows_removed": before_rows - len(df),
        "before_quality": before_qb["overall"],
        "after_quality": after_qb["overall"],
        "quality_delta": quality_delta,
        "before_quality_breakdown": before_qb,
        "after_quality_breakdown": after_qb,
        "quality_breakdown_deltas": {
            "completeness": round(after_qb["completeness"] - before_qb["completeness"], 2),
            "uniqueness": round(after_qb["uniqueness"] - before_qb["uniqueness"], 2),
            "validity": round(after_qb["validity"] - before_qb["validity"], 2),
            "consistency": round(after_qb["consistency"] - before_qb["consistency"], 2),
        },
        "report": report,
        "cleaned_path": {"csv": out_csv, "parquet": out_pq}
    }
    
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/execution_{dataset_id}.json", "w", encoding="utf-8") as f:
        json.dump(exec_summary, f, indent=2, ensure_ascii=False, default=str)
        
    logger.info(f"Execution finished for {dataset_id}: Quality {before_qb['overall']}% -> {after_qb['overall']}%, Rows {before_rows} -> {len(df)}")
    return exec_summary


def execute_plan(dataset_id, approved_ids=None, preserve=None):
    """Convenience entrypoint that loads governance report and executes plan."""
    gov_path = f"reports/governance_{dataset_id}.json"
    if not os.path.exists(gov_path):
        from src import governance as gov_mod
        plan_path = f"reports/cleaning_plan_{dataset_id}.json"
        gov = gov_mod.run_governance(plan_path)
    else:
        gov = json.load(open(gov_path, encoding="utf-8"))
    if approved_ids is None:
        approved_ids = [s["id"] for s in gov.get("steps", [])]
    return run_execution(dataset_id, approved_ids, gov, preserve)

