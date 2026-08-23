"""
Autonomous Invention Engine Test Suite.
Verifies:
1. Data Science Invention Engine computes regularized precision matrices and significant causal edges.
2. Heavy-tailed Student-t (df=3) VaR 95% and Expected Shortfall CVaR calculations.
3. Generative Vector Design Invention Engine produces React JSX, Vue 3, and WCAG AAA compliant SVGs.
"""
import pytest
import numpy as np
from src.autonomous_invention_engine import autonomous_invention


def test_data_science_invention_causal_structure():
    """Verify data science invention engine discovers grounded precision matrix and partial correlations."""
    np.random.seed(42)
    n_samples = 500
    x1 = np.random.normal(0, 1, n_samples)
    x2 = 0.8 * x1 + np.random.normal(0, 0.5, n_samples)
    x3 = 0.5 * x2 + np.random.normal(0, 0.5, n_samples)
    matrix = np.column_stack([x1, x2, x3])

    res = autonomous_invention.invent_causal_structure(matrix, ["X1", "X2", "X3"])

    assert res.is_grounded is True
    assert res.precision_matrix.shape == (3, 3)
    assert len(res.significant_edges) >= 1
    assert res.ridge_lambda > 0.0


def test_heavy_tail_risk_estimation():
    """Verify Student-t heavy tail risk modeling computes VaR 95% and CVaR."""
    np.random.seed(42)
    returns = np.random.standard_t(df=3, size=1000)

    risk = autonomous_invention.estimate_heavy_tail_risk(returns, degrees_of_freedom=3)

    assert risk["degrees_of_freedom"] == 3
    assert risk["observations_count"] == 1000
    assert risk["var_95"] < 0
    assert risk["cvar_95"] < risk["var_95"]
    assert risk["tail_risk_detected"] is True


def test_generative_vector_design_invention():
    """Verify vector design invention synthesizes React JSX, Vue 3 SFCs, and WCAG AAA SVGs."""
    res = autonomous_invention.invent_generative_vector("TestShield", domain_theme="CyberSecurity", accent_color="#6366f1")

    assert res.asset_name == "TestShield"
    assert "<svg" in res.svg_code
    assert "0 0 64 64" in res.svg_code
    assert "export const TestShield" in res.react_jsx
    assert "<template>" in res.vue_component
    assert res.fitness_score >= 90.0
    assert res.wcag_aaa_compliant is True
    assert len(res.applied_triz_operators) == 3
