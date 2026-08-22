import pytest
import pandas as pd
import numpy as np
from src.eda_engine import compute_causal_dag, generate_statistical_hypotheses
from src.analyst_engine import simulate_what_if

def test_causal_dag_computation():
    np.random.seed(42)
    n = 100
    x = np.random.normal(50, 10, n)
    # y is directly caused by x
    y = 2.5 * x + np.random.normal(0, 5, n)
    z = np.random.normal(100, 20, n)
    
    df = pd.DataFrame({"marketing_spend": x, "revenue": y, "unrelated_metric": z})
    res = compute_causal_dag(df)
    
    assert "nodes" in res
    assert len(res["nodes"]) == 3
    assert len(res["edges"]) >= 1
    
    # Check that marketing_spend -> revenue relationship was captured
    edge_pairs = [(e["source"], e["target"]) for e in res["edges"]]
    assert ("marketing_spend", "revenue") in edge_pairs or ("revenue", "marketing_spend") in edge_pairs

def test_generate_statistical_hypotheses():
    np.random.seed(42)
    n = 80
    cats = ["Tier A"] * 40 + ["Tier B"] * 40
    vals = [100 + np.random.normal(0, 5) for _ in range(40)] + [50 + np.random.normal(0, 5) for _ in range(40)]
    df = pd.DataFrame({"plan_type": cats, "arpu": vals})
    
    hypo = generate_statistical_hypotheses(df)
    assert len(hypo) >= 1
    assert "SUPPORTED" in hypo[0]["verdict"]
