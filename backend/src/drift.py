import numpy as np
import pandas as pd
from scipy import stats

def psi_numeric(exp, act, bins=10):
    if isinstance(exp, pd.Series):
        exp = exp.dropna().to_numpy()
    else:
        exp = np.asarray(exp)
        exp = exp[~np.isnan(exp)]

    if isinstance(act, pd.Series):
        act = act.dropna().to_numpy()
    else:
        act = np.asarray(act)
        act = act[~np.isnan(act)]

    if len(exp) == 0 or len(act) == 0:
        return 0.0
    bp = np.unique(np.quantile(exp, np.linspace(0, 1, bins + 1)))
    if len(bp) < 2:
        return 1.0 if abs(np.mean(exp) - np.mean(act)) > 1e-6 else 0.0
    e, _ = np.histogram(exp, bins=bp)
    a, _ = np.histogram(act, bins=bp)
    e = np.clip(e / max(len(exp), 1), 1e-4, None)
    a = np.clip(a / max(len(act), 1), 1e-4, None)
    return float(np.sum((a - e) * np.log(a / e)))

def psi_categorical(exp, act):
    if isinstance(exp, (list, np.ndarray)):
        exp = pd.Series(exp)
    if isinstance(act, (list, np.ndarray)):
        act = pd.Series(act)
    if len(exp) == 0 or len(act) == 0:
        return 0.0
    e = exp.dropna().value_counts(normalize=True)
    a = act.dropna().value_counts(normalize=True)
    total = 0.0
    for c in set(e.index) | set(a.index):
        pe = max(e.get(c, 0), 1e-4)
        pa = max(a.get(c, 0), 1e-4)
        total += (pa - pe) * np.log(pa / pe)
    return float(total)

def drift_report(before, after, psi_thresh=0.2, ks_thresh=0.05):
    out = []
    for col in before.columns:
        if col not in after.columns:
            continue
        if pd.api.types.is_numeric_dtype(before[col]):
            b = before[col].dropna()
            a = after[col].dropna()
            if len(b) < 8 or len(a) < 8:
                continue
            p = float(psi_numeric(b, a))
            ks = float(stats.ks_2samp(b, a).pvalue)
            is_drifted = bool((p > psi_thresh) or (ks < ks_thresh))
            out.append({
                "column": str(col),
                "type": "numeric",
                "psi": round(p, 3),
                "ks_p": round(ks, 4),
                "drifted": is_drifted
            })
        else:
            b = before[col].dropna()
            a = after[col].dropna()
            if len(b) == 0 or len(a) == 0:
                continue
            p = float(psi_categorical(b, a))
            is_drifted = bool(p > psi_thresh)
            out.append({
                "column": str(col),
                "type": "categorical",
                "psi": round(p, 3),
                "drifted": is_drifted
            })
    return out
