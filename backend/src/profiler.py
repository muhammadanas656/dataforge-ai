import re
import pandas as pd
import numpy as np
from src.utils import logger

# Expanded PII patterns supporting international formats (E.164) and subdomains
PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "phone": r"(?:\+?\d{1,4}[ -]?)?(?:\(?\d{2,5}\)?[ -]?)?\d{3,5}[ -]?\d{3,5}\b",
    "credit_card": r"\b(?:\d[ -]?){13,19}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
}

def _is_index_column(col_name: str, s: pd.Series, n_rows: int) -> bool:
    """Detect if a column is an auto-generated row index, counter, or artificial ID."""
    name_lower = str(col_name).lower().strip()
    if name_lower in ("unnamed: 0", "index", "row_id", "row_number", "id", "_id", "level_0"):
        return True
    if pd.api.types.is_numeric_dtype(s) and n_rows > 10:
        s_clean = s.dropna()
        if len(s_clean) == n_rows and s.nunique() == n_rows:
            # Check if monotonic sequence (e.g. 0..N-1 or 1..N)
            diffs = s_clean.diff().dropna()
            if (diffs == 1).all() or (diffs == -1).all():
                return True
    return False

def get_payload_columns(df: pd.DataFrame) -> list:
    """Get the semantic business columns of the dataframe, excluding artificial row indices and noisy scrape tags."""
    cols = df.columns.tolist()
    n_rows = len(df)
    if n_rows == 0 or len(cols) <= 1:
        return cols

    # 1. Exclude obvious auto-generated indices
    payload = [c for c in cols if not _is_index_column(c, df[c], n_rows)]
    if len(payload) <= 1:
        return payload

    # 2. Identify candidate business entity columns (e.g. Product Name, Title, SKU + Prices)
    name_cols = []
    for c in payload:
        clow = str(c).lower().strip().replace(" ", "_")
        if any(k in clow for k in ("name", "title", "sku", "item", "product_name", "model", "description", "item_name")):
            name_cols.append(c)
        elif df[c].dtype == "object" and df[c].nunique() > 50 and df[c].nunique() < 0.99 * n_rows:
            name_cols.append(c)

    if not name_cols:
        return payload

    attr_cols = []
    for c in payload:
        clow = str(c).lower().strip().replace(" ", "_")
        if any(k in clow for k in ("price", "cost", "amount", "discount", "qty", "quantity", "rate", "val", "value")):
            attr_cols.append(c)

    entity_subset = [c for c in payload if c in name_cols or c in attr_cols]
    if not entity_subset or len(entity_subset) == len(payload):
        # Drop secondary low-cardinality repeat tags (e.g. 'Product' search tag with 69 values)
        low_card_cols = [c for c in payload if df[c].dtype == "object" and df[c].nunique() < 100 and c not in name_cols]
        if low_card_cols:
            candidate = [c for c in payload if c not in low_card_cols]
            if len(candidate) > 0:
                entity_subset = candidate

    if entity_subset and len(entity_subset) < len(payload):
        df_sub = df[entity_subset].copy()
        for c in df_sub.select_dtypes(include=["object", "string"]).columns:
            df_sub[c] = df_sub[c].astype(str).str.strip().str.lower()
        sub_dupes = int(df_sub.duplicated().sum())
        all_dupes = int(df.duplicated().sum())
        if sub_dupes > all_dupes:
            return entity_subset

    return payload

def near_dup_estimate(df, sample=300, threshold=90):
    if len(df) <= 1:
        return 0
    try:
        from rapidfuzz import fuzz
        sample_df = df.sample(min(sample, len(df)), random_state=42)
        sig = sample_df.astype(str).fillna("").apply(lambda r: "|".join([str(x) for x in r.values]), axis=1).tolist()
        count = sum(1 for i in range(len(sig)) for j in range(i + 1, len(sig))
                    if fuzz.ratio(sig[i], sig[j]) >= threshold)
        return int(count * (len(df) / len(sig))) if len(sig) > 0 else 0
    except Exception as e:
        logger.warning(f"near-dup estimate failed: {e}")
        return 0

def pii_scan(df):
    found = {}
    for col in df.select_dtypes(include=["object", "string"]).columns:
        s = df[col].dropna().astype(str).head(200)
        for name, pat in PII_PATTERNS.items():
            try:
                hits = int(s.str.contains(pat, regex=True).sum())
                if hits > 0:
                    found.setdefault(col, {})[name] = hits
            except Exception:
                pass
    return found

def detect_temporal_drift(df: pd.DataFrame):
    """Detect significant distribution drift across time/years for primary metric."""
    from src.drift import psi_numeric
    date_col = None
    for col in df.columns:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        try:
            if pd.to_datetime(s.head(200), errors="coerce").notna().mean() > 0.8:
                date_col = col
                break
        except Exception:
            continue

    if not date_col:
        return None

    try:
        yrs = pd.to_datetime(df[date_col], errors="coerce").dt.year
        df2 = df.assign(__year=yrs)
        years = sorted(df2["__year"].dropna().unique())
        num = df.select_dtypes(include="number").columns
        if len(years) < 2 or len(num) == 0:
            return None
        col = num[0]
        a = df2[df2["__year"] == years[0]][col].dropna()
        b = df2[df2["__year"] == years[-1]][col].dropna()
        if len(a) < 8 or len(b) < 8:
            return None
        psi = float(psi_numeric(a, b))
        return {
            "date_column": date_col,
            "measure": col,
            "years": [int(years[0]), int(years[-1])],
            "psi": round(psi, 3),
            "drifted": bool(psi > 0.2)
        }
    except Exception as e:
        logger.warning(f"Temporal drift detection failed: {e}")
        return None

def profile_dataframe(df: pd.DataFrame):
    n_rows = int(len(df))
    n_cols = int(len(df.columns))

    if n_rows == 0:
        return {
            "shape": [0, n_cols],
            "total_rows": 0,
            "total_columns": n_cols,
            "duplicate_rows": 0,
            "duplicate_pct": 0.0,
            "payload_duplicates": 0,
            "payload_duplicate_pct": 0.0,
            "payload_columns": df.columns.tolist(),
            "near_duplicate_estimate": 0,
            "temporal_drift": None,
            "pii": {},
            "columns": []
        }

    # 1. Exact full-row duplicates
    exact_dupes = int(df.duplicated().sum())

    # 2. Intelligent Payload Duplicates (excluding artificial indices with trimmed strings)
    payload_cols = get_payload_columns(df)
    df_payload = df[payload_cols].copy()
    for c in df_payload.select_dtypes(include=["object", "string"]).columns:
        df_payload[c] = df_payload[c].astype(str).str.strip().str.lower()
    payload_dupes = int(df_payload.duplicated().sum())
    payload_pct = round(payload_dupes / n_rows * 100, 2)

    logger.info(f"Deduplication profile: exact_dupes={exact_dupes}/{n_rows}, payload_dupes={payload_dupes}/{n_rows} ({payload_pct}%) on columns {payload_cols}")

    profile = {
        "shape": list(df.shape),
        "total_rows": n_rows,
        "total_columns": n_cols,
        "duplicate_rows": exact_dupes,
        "duplicate_pct": round(exact_dupes / n_rows * 100, 2),
        "payload_duplicates": payload_dupes,
        "payload_duplicate_pct": payload_pct,
        "payload_columns": payload_cols,
        "near_duplicate_estimate": near_dup_estimate(df),
        "temporal_drift": detect_temporal_drift(df),
        "pii": pii_scan(df),
        "columns": []
    }

    for col in df.columns:
        s = df[col]
        n_null = int(s.isnull().sum())
        n_unique = int(s.nunique(dropna=True))
        is_idx = _is_index_column(col, s, n_rows)
        
        cp = {
            "name": col,
            "dtype": str(s.dtype),
            "is_index_column": is_idx,
            "nulls": n_null,
            "null_pct": round(n_null / n_rows * 100, 2) if n_rows > 0 else 0.0,
            "unique": n_unique,
            "unique_pct": round(n_unique / n_rows * 100, 2) if n_rows > 0 else 0.0
        }
        
        s_clean = s.dropna()
        if pd.api.types.is_numeric_dtype(s) and len(s_clean) > 0:
            cp["kind"] = "numeric"
            cp["stats"] = {
                "min": float(s_clean.min()),
                "max": float(s_clean.max()),
                "mean": round(float(s_clean.mean()), 2),
                "median": round(float(s_clean.median()), 2)
            }
            if len(s_clean) >= 4:
                q1, q3 = s_clean.quantile(0.25), s_clean.quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    out = int(((s_clean < q1 - 1.5 * iqr) | (s_clean > q3 + 1.5 * iqr)).sum())
                else:
                    out = 0
            else:
                out = 0
            cp["outliers"] = out
            cp["outlier_pct"] = round(out / n_rows * 100, 2) if n_rows > 0 else 0.0
        else:
            cp["kind"] = "text"
            cp["sample_values"] = [str(v) for v in s_clean.unique()[:5]]

        profile["columns"].append(cp)

    logger.info(f"Profiled {profile['total_rows']}x{profile['total_columns']}")
    return profile
