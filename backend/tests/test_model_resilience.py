import pytest
from src.model_quality import probe_model, get_tier
from src.model_resilience import get_config, get_prompt_template, TIER_CONFIG, PROMPT_TEMPLATES
from src.deterministic_fallbacks import (
    fallback_semantic_type, fallback_cleaning_plan, fallback_narrative
)


def test_probe_model_structure(monkeypatch):
    def mock_chat(*args, **kwargs):
        return '{"status": "ok", "count": 42}'

    monkeypatch.setattr("src.model_quality.tracked_chat", mock_chat)
    result = probe_model("test")

    assert "tier" in result
    assert result["tier"] in ["high", "mid", "low"]
    assert "score" in result
    assert "results" in result
    assert len(result["results"]) == 5


def test_tier_configs():
    for tier in ["high", "mid", "low"]:
        config = TIER_CONFIG[tier]
        assert "prompt_complexity" in config
        assert "verification_threshold" in config
        assert "delegation_preference" in config
        assert 0 <= config["learning_rate"] <= 1


def test_prompt_templates():
    assert len(PROMPT_TEMPLATES["high"]["cp2_system"]) > 50
    assert len(PROMPT_TEMPLATES["low"]["cp2_system"]) < 100

    for tier in ["high", "mid", "low"]:
        assert "cp2_system" in PROMPT_TEMPLATES[tier]
        assert "cp3_system" in PROMPT_TEMPLATES[tier]
        assert "narrative_system" in PROMPT_TEMPLATES[tier]


def test_fallback_semantic_type():
    col = {"name": "price", "dtype": "float64", "kind": "numeric"}
    result = fallback_semantic_type(col)
    assert result["source"] == "rule_fallback"
    assert result["semantic_type"] in ["currency", "numeric_continuous", "numeric_discrete"]


def test_fallback_cleaning_plan():
    profile = {
        "total_rows": 1000,
        "duplicate_pct": 15,
        "duplicate_rows": 150,
        "columns": [
            {"name": "price", "kind": "numeric", "null_pct": 10, "nulls": 100},
            {"name": "name", "kind": "text", "null_pct": 2, "nulls": 20}
        ]
    }
    steps = fallback_cleaning_plan(profile)
    assert len(steps) >= 2
    assert any(s["action"] == "remove_duplicates" for s in steps)
    assert any(s["action"] == "fill_nulls" and s["column"] == "price" for s in steps)


def test_fallback_narrative():
    profile = {
        "total_rows": 5000,
        "total_columns": 10,
        "duplicate_pct": 5.5,
        "columns": [{"null_pct": 3} for _ in range(10)]
    }
    narrative = fallback_narrative(profile)
    assert "5,000" in narrative
    assert "10 columns" in narrative
    assert isinstance(narrative, str)
    assert len(narrative) > 40
