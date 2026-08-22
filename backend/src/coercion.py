import re
import pandas as pd
import numpy as np

BOOL_MAP = {
    "y": 1, "n": 0,
    "yes": 1, "no": 0,
    "true": 1, "false": 0,
    "t": 1, "f": 0,
    "1": 1, "0": 0
}

UNIT_PATTERN = re.compile(r"^\s*[$€£¥₹]?\s*-?\d[\d.,]*\s*(%|kg|g|m|cm|km|lb|lbs|oz|usd|eur|gbp|in|ft)?\s*$", re.IGNORECASE)

def extract_number(s):
    if pd.isna(s):
        return None
    if isinstance(s, (int, float, np.number)):
        return float(s)
    if not isinstance(s, str):
        return None
    s_str = s.strip()
    if not UNIT_PATTERN.match(s_str):
        return None
    cleaned = re.sub(r"[$€£¥₹%]|(?i:kg|lbs?|oz|usd|eur|gbp|cm|km|ft|in)\b", "", s_str).strip()
    match = re.search(r"-?\d[\d.,]*", cleaned)
    if not match:
        return None
    t = match.group(0)
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):  # EU format: 1.234,56
            t = t.replace(".", "").replace(",", ".")
        else:  # US format: 1,234.56
            t = t.replace(",", "")
    elif "," in t:
        t = t.replace(",", ".") if re.search(r",\d{1,3}$", t) and not re.search(r",\d{3}$", t) else t.replace(",", "")
    try:
        return float(t)
    except Exception:
        return None

def coerce_series(s: pd.Series):
    """
    Tries to infer and coerce mixed-type/string series to numeric or boolean.
    Returns: (coerced_series, kind, error_pct)
    """
    if not pd.api.types.is_object_dtype(s) and not pd.api.types.is_string_dtype(s):
        return s, None, 0.0

    valid_s = s.dropna()
    if len(valid_s) == 0:
        return s, None, 0.0

    # 1. Check numeric coercion
    nums = s.map(extract_number)
    num_valid_rate = nums.dropna().count() / len(valid_s)
    if num_valid_rate >= 0.80:
        err_pct = round((1.0 - num_valid_rate) * 100, 2)
        return nums.astype(float), "numeric", err_pct

    # 2. Check boolean coercion
    low = s.astype(str).str.strip().str.lower()
    bool_matches = low.isin(BOOL_MAP)
    bool_valid_rate = bool_matches.sum() / len(valid_s)
    if bool_valid_rate >= 0.80:
        coerced_bool = low.map(BOOL_MAP)
        return coerced_bool, "boolean", 0.0

    return s, None, 0.0

def is_blob(s: pd.Series) -> bool:
    """Detect if column contains large JSON / base64 blobs (>200 chars avg)."""
    if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
        s_clean = s.dropna().astype(str)
        if len(s_clean) > 0 and s_clean.str.len().mean() > 200:
            return True
    return False

def ensure_unique_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate column names with collision suffixes (_1, _2)."""
    cols = list(df.columns)
    seen = {}
    new_cols = []
    for c in cols:
        name = str(c).strip()
        if name in seen:
            seen[name] += 1
            new_cols.append(f"{name}_{seen[name]}")
        else:
            seen[name] = 0
            new_cols.append(name)
    df.columns = new_cols
    return df
