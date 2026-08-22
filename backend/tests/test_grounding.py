import pytest
from src.tech_capability_graph import tech_capability_graph
from src.grounding_validator import grounding_validator
from src.future_models import novelty_detector, market_predictor, adoption_forecaster

def test_tech_capability_interpolation():
    cap_2026 = tech_capability_graph.get_capability("edge_ai_silicon", 2026)
    cap_2028 = tech_capability_graph.get_capability("edge_ai_silicon", 2028)
    assert cap_2028["tops_per_watt"] > cap_2026["tops_per_watt"]
    
    # Test 2027 interpolation
    cap_2027 = tech_capability_graph.get_capability("edge_ai_silicon", 2027)
    assert cap_2026["tops_per_watt"] <= cap_2027["tops_per_watt"] <= cap_2028["tops_per_watt"]

def test_grounding_validator():
    # Compliant blueprint
    valid_bp = {
        "concept_name": "Ambient Acoustic Sensor",
        "technical_spec_summary": "Low-power MEMS audio processing with local 2-bit SLM",
        "regulatory_category": "consumer_hardware",
        "target_market_year": 2028,
        "unit_economics": {"gross_margin_pct": 72, "estimated_bom_or_cogs_usd": 35, "suggested_price_usd": 125}
    }
    res = grounding_validator.validate_invention(valid_bp, current_year=2026)
    assert res["valid"] is True
    assert res["feasibility_score"] >= 0.75

    # Violating blueprint (impossible physics & bad margin)
    invalid_bp = {
        "concept_name": "Perpetual Quantum Teleporter",
        "technical_spec_summary": "Asserts perpetual motion energy harvesting without dissipation",
        "regulatory_category": "consumer_hardware",
        "target_market_year": 2028,
        "unit_economics": {"gross_margin_pct": 10}
    }
    res_bad = grounding_validator.validate_invention(invalid_bp, current_year=2026)
    assert res_bad["valid"] is False
    assert len(res_bad["violations"]) >= 2

def test_adoption_forecaster():
    curve = adoption_forecaster.forecast_s_curve("Edge SLM", start_year=2026, horizon_years=5)
    assert len(curve["five_year_trajectory"]) == 6
    assert curve["projected_inflection_year"] >= 2026
