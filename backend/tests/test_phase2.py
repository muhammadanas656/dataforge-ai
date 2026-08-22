import pandas as pd
import numpy as np
from src.verification_sandbox import (
    verify_scatter_fidelity, 
    verify_heatmap_fidelity,
    extract_entity_claims,
    verify_entity_claims
)

def test_scatter_fidelity():
    df = pd.DataFrame({
        "price": [10, 20, 30, 40, 50],
        "discount": [5, 10, 15, 20, 25]
    })
    chart_spec = {
        "chart_type": "scatter",
        "x_column": "price",
        "y_column": "discount",
        "data": [
            {"price": 10, "discount": 5},
            {"price": 20, "discount": 10},
            {"price": 30, "discount": 15},
            {"price": 40, "discount": 20},
            {"price": 50, "discount": 25}
        ]
    }
    result = verify_scatter_fidelity(df, chart_spec)
    assert result["verified"]

def test_scatter_fidelity_mismatch():
    df = pd.DataFrame({
        "price": [10, 20, 30, 40, 50],
        "discount": [5, 10, 15, 20, 25]
    })
    # Corrupted chart data (inverted relationship)
    chart_spec = {
        "chart_type": "scatter",
        "x_column": "price",
        "y_column": "discount",
        "data": [
            {"price": 10, "discount": 50},
            {"price": 20, "discount": 40},
            {"price": 30, "discount": 30},
            {"price": 40, "discount": 20},
            {"price": 50, "discount": 10}
        ]
    }
    result = verify_scatter_fidelity(df, chart_spec)
    assert not result["verified"]

def test_heatmap_fidelity():
    df = pd.DataFrame({
        "price": [10, 20, 30],
        "discount": [5, 10, 15],
        "rating": [4, 5, 3]
    })
    actual_corr = df.corr(method="spearman").round(3)
    chart_spec = {
        "chart_type": "heatmap",
        "data": [
            {"column": "price", "discount": float(actual_corr.loc["price", "discount"])},
            {"column": "discount", "price": float(actual_corr.loc["discount", "price"])}
        ]
    }
    result = verify_heatmap_fidelity(df, chart_spec)
    assert result["verified"]

def test_extract_entity_claims():
    narrative = "The most expensive product is iPhone 13. The top 5 categories are electronics."
    claims = extract_entity_claims(narrative)
    assert len(claims) >= 1
    assert any(c["type"] == "most" for c in claims)
    assert any(c["type"] == "top_n" for c in claims)

def test_verify_entity_claims():
    df = pd.DataFrame({
        "product": ["A", "B", "C"],
        "price": [10, 50, 30]
    })
    narrative = "The most expensive product is B."
    result = verify_entity_claims(narrative, df, {})
    assert result["verified"]
