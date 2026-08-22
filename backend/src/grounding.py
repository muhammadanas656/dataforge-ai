import re

def extract_numbers(text):
    if not text:
        return []
    # Match integers and floats (excluding percentage signs and commas)
    clean = text.replace(",", "")
    return [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", clean)]

def profile_numbers(profile):
    nums = set()
    for k in ("duplicate_pct", "total_rows", "total_columns"):
        if profile.get(k) is not None:
            nums.add(float(profile[k]))
    for c in profile.get("columns", []):
        for k in ("null_pct", "unique_pct", "unique", "outliers"):
            if c.get(k) is not None:
                nums.add(float(c[k]))
        for v in (c.get("stats") or {}).values():
            if isinstance(v, (int, float)):
                nums.add(float(v))
    return nums

def verify(llm_text, profile, tol=0.5):
    """Check every number the LLM stated against computed stats."""
    known = profile_numbers(profile)
    extracted = extract_numbers(llm_text)
    verified = []
    unverified = []
    
    for n in extracted:
        # Check against known statistics with tolerance
        if any(abs(n - k) <= max(tol, abs(k) * 0.02) for k in known):
            verified.append(n)
        else:
            unverified.append(n)
            
    return {
        "verified": verified,
        "unverified": unverified,
        "grounded": len(unverified) == 0,
        "grounding_score_pct": round(len(verified) / max(len(extracted), 1) * 100, 1)
    }
