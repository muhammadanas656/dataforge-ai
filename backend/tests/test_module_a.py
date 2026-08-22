import pandas as pd
import numpy as np
from src import drift, grounding, frugal

def test_psi_identical_is_low():
    np.random.seed(42)
    x = pd.Series(np.random.normal(0, 1, 500))
    assert drift.psi_numeric(x, x) < 0.05

def test_psi_shift_is_high():
    np.random.seed(42)
    a = pd.Series(np.random.normal(0, 1, 500))
    b = pd.Series(np.random.normal(3, 1, 500))
    assert drift.psi_numeric(a, b) > 0.2

def test_grounding_verified():
    prof = {
        "duplicate_pct": 8.66,
        "total_rows": 7878,
        "columns": [{"null_pct": 0, "unique_pct": 0.88, "unique": 69}]
    }
    g = grounding.verify("There are 7878 rows and 8.66% duplicates.", prof)
    assert g["grounded"]

def test_grounding_unverified():
    prof = {
        "duplicate_pct": 8.66,
        "total_rows": 7878,
        "columns": []
    }
    g = grounding.verify("There are 99999 rows.", prof)
    assert not g["grounded"]

def test_frugal_price_uses_rules():
    col = {"name": "Old Price", "kind": "numeric", "unique_pct": 50}
    t, c = frugal.semantic_type_rules(col)
    assert t == "currency" and c >= 0.8

def test_frugal_escalates_ambiguous():
    col = {"name": "notes", "kind": "text", "unique_pct": 60, "unique": 4000}
    t, c = frugal.semantic_type_rules(col)
    assert c < 0.8  # would escalate to RAG/LLM
