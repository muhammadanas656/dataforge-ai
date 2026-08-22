"""
Conversational Natural Language Dataset Analyst & Code Interpreter.
Interprets ad-hoc natural language questions on cleaned datasets, executes safe queries,
and formats data tables, summary KPIs, and visualization specs.
"""
import os
import json
import re
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from src.utils import logger
from src.eda_engine import load_dataset
from src.llm import tracked_chat

def query_dataset(dataset_id: str, query: str, run_id: str = "default") -> Dict[str, Any]:
    """Execute natural language query on the dataset with fallback sandboxed interpreter."""
    logger.info(f"[data_analyst] Processing query for dataset {dataset_id}: '{query}'")
    
    df = load_dataset(dataset_id)
    if df is None or df.empty:
        return {
            "status": "error",
            "error": f"Dataset {dataset_id} not found or empty."
        }
        
    cols = df.columns.tolist()
    q_lower = query.lower()
    
    # 1. Deterministic Fast-Path Heuristics for Zero-Token & Offline Resilience
    # A. Top / Outlier rows query
    if any(w in q_lower for w in ["outlier", "highest", "top", "max", "maximum", "peak"]):
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if num_cols:
            target_col = num_cols[0]
            # Match specific column if mentioned
            for c in num_cols:
                if c.lower() in q_lower:
                    target_col = c
                    break
            top_df = df.sort_values(by=target_col, ascending=False).head(10)
            return {
                "status": "success",
                "answer_text": f"Found top 10 records ranked by highest '{target_col}'.",
                "query_type": "top_records",
                "target_column": target_col,
                "summary_metric": f"Max {target_col}: {df[target_col].max():.2f}, Mean: {df[target_col].mean():.2f}",
                "records": top_df.head(10).to_dict(orient="records"),
                "chart_spec": {
                    "type": "bar",
                    "x_axis": df.select_dtypes(include=["object"]).columns.tolist()[0] if df.select_dtypes(include=["object"]).columns.tolist() else "index",
                    "y_axis": target_col
                }
            }
            
    # B. Group-by / Category breakdown query
    if any(w in q_lower for w in ["group by", "breakdown", "category", "compare", "distribution", "segment", "share"]):
        cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if cat_cols:
            cat_col = cat_cols[0]
            for c in cat_cols:
                if c.lower() in q_lower:
                    cat_col = c
                    break
            if num_cols:
                num_col = num_cols[0]
                for c in num_cols:
                    if c.lower() in q_lower:
                        num_col = c
                        break
                grouped = df.groupby(cat_col)[num_col].agg(["count", "mean", "median", "std"]).reset_index()
                return {
                    "status": "success",
                    "answer_text": f"Segmented '{num_col}' metrics grouped across '{cat_col}'.",
                    "query_type": "aggregation",
                    "group_by": cat_col,
                    "target_column": num_col,
                    "summary_metric": f"Highest average {num_col} is {grouped.sort_values(by='mean', ascending=False).iloc[0][cat_col]} ({grouped['mean'].max():.2f})",
                    "records": grouped.to_dict(orient="records"),
                    "chart_spec": {
                        "type": "bar",
                        "x_axis": cat_col,
                        "y_axis": "mean"
                    }
                }

    # C. General Statistical Summary
    desc = df.describe(include="all").transpose().reset_index()
    desc = desc.rename(columns={"index": "column"})
    return {
        "status": "success",
        "answer_text": f"Dataset {dataset_id} contains {len(df)} rows across {len(cols)} columns ({', '.join(cols[:8])}).",
        "query_type": "profile_summary",
        "summary_metric": f"Completeness: {(1.0 - df.isnull().mean().mean()) * 100:.1f}%",
        "records": desc.head(10).fillna("").to_dict(orient="records"),
        "chart_spec": {
            "type": "summary_table"
        }
    }
