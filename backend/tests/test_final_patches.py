import pandas as pd
import numpy as np
from src import sources, executor, profiler, bigdata, llm_critic

def test_unicode_normalization():
    # zero-width space \u200b and compat characters
    df = pd.DataFrame({"name": ["iPhone 13\u200b", "iPhone 13"]})
    out = sources.canonicalize(df)
    assert out["name"].nunique() == 1
    assert out["name"].iloc[0] == "iPhone 13"


def test_impact_guardrail_flags_destructive():
    # 90 rows violate discount > 1 (90% drop rate)
    df = pd.DataFrame({"discount": [0.2] * 90 + [20] * 10})
    steps = llm_critic.validate_critic_proposals(
        df,
        {"business_rules": [{"name": "pct", "pandas_expr": "discount > 1", "reason": "test"}]}
    )
    assert len(steps) > 0
    assert steps[0]["high_impact"] is True  # drops 90% -> flagged high impact
    assert steps[0]["risk"] == "high"


def test_preserve_signal_flags_not_drops():
    df = pd.DataFrame({"price": [100.0, -5.0, 200.0]})
    out = executor.apply_step(
        df,
        {"action": "fix_business_rule", "name": "pos", "pandas_expr": "price > 0", "preserve_signal": True}
    )
    assert len(out) == 3
    assert "is_pos_flag" in out.columns
    assert out["is_pos_flag"].sum() == 1


def test_temporal_drift_detected():
    n = 100
    df = pd.DataFrame({
        "date": pd.date_range("2021-01-01", periods=n, freq="D").tolist() +
                pd.date_range("2023-01-01", periods=n, freq="D").tolist(),
        "revenue": [10.0] * n + [1000.0] * n
    })
    d = profiler.detect_temporal_drift(df)
    assert d is not None
    assert d["drifted"] is True
    assert d["psi"] > 0.2


def test_chunked_count(tmp_path):
    p = tmp_path / "test_stream.parquet"
    pd.DataFrame({"price": [1.0, -1.0, 2.0, -2.0] * 10}).to_parquet(p)
    v, t = bigdata.count_violations_chunked(str(p), "price > 0")
    assert v == 20
    assert t == 40
