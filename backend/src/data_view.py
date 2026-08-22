import os
import json
import pandas as pd
from src.utils import logger

def _profile(did):
    profile_path = f"reports/profile_{did}.json"
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile for {did} not found")
    return json.load(open(profile_path, encoding="utf-8"))

def get_available_stages(did):
    stages = ["raw"]
    snap = f"data/snapshots/{did}"
    if os.path.isdir(snap):
        for f in sorted(os.listdir(snap)):
            if f.endswith(".parquet"):
                stages.append(f.replace(".parquet", ""))
    if os.path.exists(f"data/canonical/{did}_cleaned.csv"):
        stages.append("cleaned")
    return stages

def get_stage_df(did, stage):
    if stage == "raw":
        return pd.read_csv(_profile(did)["snapshot"]["csv"])
    if stage == "cleaned":
        cleaned_path = f"data/canonical/{did}_cleaned.csv"
        if os.path.exists(cleaned_path):
            return pd.read_csv(cleaned_path)
        return pd.read_csv(_profile(did)["snapshot"]["csv"])
    
    snap_path = f"data/snapshots/{did}/{stage}.parquet"
    if os.path.exists(snap_path):
        return pd.read_parquet(snap_path)
    return pd.read_csv(_profile(did)["snapshot"]["csv"])

def data_view(did, stage="raw", page=1, page_size=50, search=""):
    df = get_stage_df(did, stage)
    if search:
        search_str = str(search).strip()
        mask = df.astype(str).apply(lambda r: r.str.contains(search_str, case=False, na=False).any(), axis=1)
        df = df[mask]
        
    total = len(df)
    page = max(1, int(page))
    page_size = max(1, min(100, int(page_size)))
    start = (page - 1) * page_size
    
    page_df = df.iloc[start:start + page_size].fillna("")
    
    return {
        "columns": list(df.columns),
        "rows": page_df.to_dict("records"),
        "total": total,
        "page": page,
        "page_size": page_size,
        "stage": stage
    }

def _norm_zeros(df):
    df_c = df.copy()
    for c in df_c.select_dtypes(include="number").columns:
        df_c[c] = df_c[c].apply(lambda v: 0.0 if isinstance(v, float) and v == 0.0 else v)
    return df_c

def diff_stages(prev, curr, limit=50):
    prev = _norm_zeros(prev)
    curr = _norm_zeros(curr)
    if len(prev) == len(curr):
        changed = []
        prev_aligned = prev.reset_index(drop=True)
        curr_aligned = curr.reset_index(drop=True)
        
        for col in prev_aligned.columns:
            if col not in curr_aligned.columns:
                continue
            b = prev_aligned[col].astype(str)
            a = curr_aligned[col].astype(str)
            m = (b != a)
            for i in b[m].index[:limit]:
                changed.append({
                    "column": col,
                    "row_index": int(i),
                    "before": b[i],
                    "after": a[i]
                })
                
        total_changed = int((prev_aligned.astype(str) != curr_aligned.astype(str)).sum().sum())
        return {
            "type": "modify",
            "changed_cells": total_changed,
            "changed": changed,
            "sample_changed": curr_aligned[prev_aligned.astype(str) != curr_aligned.astype(str)].dropna(how="all").head(10).fillna("").to_dict("records")
        }
    
    # Row removals or additions
    prev_h = prev.astype(str).agg("|".join, axis=1)
    curr_h = set(curr.astype(str).agg("|".join, axis=1))
    removed = prev[~prev_h.isin(curr_h)]
    return {
        "type": "remove",
        "removed_rows": len(removed),
        "removed": removed.head(limit).fillna("").to_dict("records"),
        "sample_removed": removed.head(limit).fillna("").to_dict("records")
    }

def data_diff(did, stage):
    stages = get_available_stages(did)
    if stage not in stages:
        stage = stages[-1]
    idx = stages.index(stage)
    if idx == 0:
        return {"type": "none", "note": "Raw snapshot has no preceding stage to diff against."}
    prev_df = get_stage_df(did, stages[idx - 1])
    curr_df = get_stage_df(did, stage)
    return diff_stages(prev_df, curr_df)
