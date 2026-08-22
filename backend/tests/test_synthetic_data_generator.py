import pytest
import pandas as pd
import numpy as np
from src.synthetic_data_generator import generate_realistic_unit_economics, generate_comprehensive_unit_economics

def test_generate_realistic_unit_economics():
    df = generate_realistic_unit_economics("Cold Plunge Chiller", n_months=12, rows_per_month=10, inject_quality_issues=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 100
    assert "retail_price_usd" in df.columns
    assert "customer_acquisition_cost" in df.columns
    assert "segment" in df.columns

def test_comprehensive_datasets():
    datasets = generate_comprehensive_unit_economics("SaaS Tool")
    assert "unit_economics" in datasets
    assert "customers" in datasets
    assert "cohorts" in datasets
    assert len(datasets["customers"]) == 100
