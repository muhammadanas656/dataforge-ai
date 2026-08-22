import pandas as pd
import numpy as np
from src import coercion, llm_context, llm_critic, sources, rag_cache, data_view

def test_locale_and_units():
    s = pd.Series(["$1,200", "1.234,56", "99", "$500.25", "10%"])
    out, kind, err = coercion.coerce_series(s)
    assert kind == "numeric"
    assert abs(out.iloc[0] - 1200.0) < 1e-6
    assert abs(out.iloc[1] - 1234.56) < 1e-6


def test_boolean_coercion():
    out, kind, _ = coercion.coerce_series(pd.Series(["Y", "n", "Yes", "TRUE", "false"]))
    assert kind == "boolean"
    assert out.iloc[0] == 1
    assert out.iloc[1] == 0


def test_unique_columns():
    df = pd.DataFrame({"price": [1], "price_": [2]})
    df.columns = ["price", "price"]
    deduped = coercion.ensure_unique_columns(df)
    assert list(deduped.columns) == ["price", "price_1"]


def test_mask_only_for_llm():
    df = pd.DataFrame({"email": ["user@example.com", "admin@domain.org"], "phone": ["+1 555-123-4567", "555-987-6543"]})
    ctx = llm_context.safe_samples_for_llm(df, ["email", "phone"])
    assert "<email>" in ctx
    assert "<phone>" in ctx
    assert llm_context.BOUNDARY in ctx
    # Ensure real dataset in memory was NOT mutated
    assert df["email"].iloc[0] == "user@example.com"
    assert df["phone"].iloc[0] == "+1 555-123-4567"


def test_critic_rejects_regex_and_timeout():
    assert llm_critic._expr_safe("price.str.contains('.*.*')") is False
    assert llm_critic._expr_safe("column.__class__") is False
    assert llm_critic._expr_safe("price > 0") is True
    res = llm_critic.safe_count_violations(pd.DataFrame({"p": [1, -2, 3]}), "p > 0")
    assert res == (1, 3)


def test_domain_scoped_rag_cache(tmp_path):
    cache_path = str(tmp_path / "cache.json")
    c = rag_cache.ColumnCache(path=cache_path)
    c.store({"name": "price", "kind": "numeric"}, {"type": "currency"}, domain="e-commerce")
    c.store({"name": "price", "kind": "numeric"}, {"type": "medical_procedure_fee"}, domain="healthcare")

    ecom_hit = c.lookup({"name": "price", "kind": "numeric"}, domain="e-commerce")
    assert ecom_hit["type"] == "currency"

    health_hit = c.lookup({"name": "price", "kind": "numeric"}, domain="healthcare")
    assert health_hit["type"] == "medical_procedure_fee"


def test_zero_diff_normalization():
    df1 = pd.DataFrame({"val": [-0.0, 10.0]})
    df2 = pd.DataFrame({"val": [0.0, 10.0]})
    diff = data_view.diff_stages(df1, df2)
    assert diff["changed_cells"] == 0
