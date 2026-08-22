import pandas as pd
import numpy as np
from src.eda_briefs import calculate_hhi, calculate_trend_significance, calculate_boxplot_stats, generate_executive_brief


def test_hhi_concentration():
    # Monopoly (100% one category)
    s_mono = pd.Series(["A"] * 100)
    assert calculate_hhi(s_mono) == 1.0
    
    # Perfect competition (4 equal categories)
    s_comp = pd.Series(["A", "B", "C", "D"] * 25)
    assert abs(calculate_hhi(s_comp) - 0.25) < 0.01


def test_trend_significance():
    # Strong upward trend
    up = pd.Series(np.arange(50) + np.random.normal(0, 0.1, 50))
    res = calculate_trend_significance(up)
    assert res["trend"] == "upward"
    assert res["p_value"] < 0.05
    
    # Random noise (stable)
    np.random.seed(42)
    noise = pd.Series(np.random.normal(0, 1, 50))
    res_noise = calculate_trend_significance(noise)
    assert res_noise["trend"] == "stable"


def test_boxplot_kruskal():
    # Two distinctly different groups
    g1 = np.random.normal(10, 1, 50)
    g2 = np.random.normal(50, 1, 50)
    res = calculate_boxplot_stats([g1, g2])
    assert res["significant"] is True
    
    # Two identical distribution groups
    np.random.seed(42)
    g3 = np.random.normal(10, 1, 50)
    g4 = np.random.normal(10, 1, 50)
    res_same = calculate_boxplot_stats([g3, g4])
    assert res_same["significant"] is False


def test_generate_executive_brief_all_types():
    types = ["histogram", "scatter", "bar", "box", "line"]
    for t in types:
        b = generate_executive_brief(t, {"mean": 25, "median": 20, "skew": 1.5, "rho": 0.8, "p_value": 0.01, "hhi": 0.35, "significant": True, "trend": "upward", "tau": 0.6}, f"Test {t}")
        assert "headline" in b
        assert len(b["key_insight"]) > 10
        assert len(b["statistical_verdict"]) > 0
