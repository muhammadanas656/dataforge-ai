"""
Relational detection, referential integrity check, orphan rows, and flattening for multi-table datasets.
"""
import pandas as pd
from src.utils import logger

def _guess_pk(df, name_hint):
    """Find the most likely primary key column of a table."""
    candidates = [c for c in df.columns if c == name_hint or c == f"{name_hint}_id" or c == "id"]
    for c in candidates:
        if df[c].is_unique and df[c].notna().mean() > 0.99:
            return c
    # Fallback: any unique column with >99% non-nulls
    for c in df.columns:
        if df[c].is_unique and df[c].notna().mean() > 0.99:
            return c
    return None

def detect_foreign_keys(tables: dict):
    """Auto-detect foreign keys via naming conventions and referential integrity matching."""
    fks = []
    for child, dchild in tables.items():
        for fk_col in dchild.columns:
            if not fk_col.endswith("_id"):
                continue
            parent = fk_col[:-3]  # e.g. customers_id -> customers
            if parent not in tables or parent == child:
                continue
            pk = _guess_pk(tables[parent], parent)
            if not pk:
                continue
            child_vals = dchild[fk_col].dropna()
            parent_vals = set(tables[parent][pk].dropna())
            if len(parent_vals) == 0 or len(child_vals) == 0:
                continue
            integrity = float(child_vals.isin(parent_vals).mean())
            if integrity >= 0.5:
                fks.append({
                    "child": child,
                    "child_col": fk_col,
                    "parent": parent,
                    "parent_col": pk,
                    "integrity": round(integrity, 3)
                })
    logger.info(f"Detected {len(fks)} foreign-key relationships across {len(tables)} tables")
    return fks

def orphan_counts(tables: dict, fks: list):
    out = []
    for fk in fks:
        child_vals = tables[fk["child"]][fk["child_col"]].dropna()
        parent_vals = set(tables[fk["parent"]][fk["parent_col"]].dropna())
        orphans = int((~child_vals.isin(parent_vals)).sum())
        total_child = max(1, len(tables[fk["child"]]))
        out.append({
            **fk,
            "orphans": orphans,
            "orphan_pct": round(orphans / total_child * 100, 2)
        })
    return out

def flatten(tables: dict, fks: list, primary: str):
    """Join all referenced parent tables onto the primary child table."""
    df = tables[primary].copy()
    for fk in fks:
        if fk["child"] != primary:
            continue
        parent_tbl = tables[fk["parent"]]
        df = df.merge(
            parent_tbl,
            left_on=fk["child_col"],
            right_on=fk["parent_col"],
            how="left",
            suffixes=("", f"__{fk['parent']}")
        )
    return df

def summarize(tables: dict, fks: list):
    """Build a JSON-serializable relational summary."""
    return {
        "tables": [
            {"name": n, "rows": int(len(t)), "columns": int(len(t.columns))}
            for n, t in tables.items()
        ],
        "foreign_keys": fks,
        "orphans": orphan_counts(tables, fks)
    }
