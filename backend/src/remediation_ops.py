"""
Standard deterministic remediation operations execution.
"""
import pandas as pd
import numpy as np
from src.utils import logger

ALLOWED_OPS = {
    "coerce_numeric",
    "coerce_date",
    "extract_text",
    "drop_constant",
    "fill_mode",
    "clip",
    "flag_outliers",
    "custom_eval"
}

def apply_plan(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    op = plan.get("op")
    params = plan.get("params", {})
    col = params.get("column")
    df = df.copy()

    if op == "coerce_numeric" and col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    if op == "coerce_date" and col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    if op == "fill_mode" and col in df.columns:
        modes = df[col].dropna().mode()
        val = modes.iloc[0] if len(modes) > 0 else (0.0 if pd.api.types.is_numeric_dtype(df[col]) else "Unknown")
        df[col] = df[col].fillna(val)
        return df

    if op == "clip" and col in df.columns:
        lo = params.get("lo")
        hi = params.get("hi")
        if lo is not None or hi is not None:
            df[col] = df[col].clip(lower=lo, upper=hi)
        return df

    if op == "flag_outliers" and col in df.columns:
        s = df[col].dropna()
        if len(s) >= 4:
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                is_out = (df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)
                df[f"is_{col}_outlier"] = is_out.astype(int)
        return df

    if op == "custom_eval":
        expr = params.get("expr")
        new_col = params.get("new", "derived")
        if expr:
            df[new_col] = df.eval(expr, engine="python")
        return df

    if op == "drop_constant" and col in df.columns:
        return df.drop(columns=[col])

    if op == "extract_text" and col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        return df

    return df
