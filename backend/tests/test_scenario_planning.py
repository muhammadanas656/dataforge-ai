import pytest
from src.scenario_planning import ScenarioPlanner

def test_scenario_planning_and_monte_carlo():
    planner = ScenarioPlanner(n_simulations=500)
    result = planner.generate_scenarios("Cold Plunge Chiller", {
        'units_per_month': 150,
        'price_usd': 89.0,
        'cogs_usd': 28.0,
        'cac_usd': 20.0
    })
    
    assert "scenarios" in result
    assert "conservative" in result["scenarios"]
    assert "base" in result["scenarios"]
    assert "aggressive" in result["scenarios"]
    assert "monte_carlo" in result
    mc = result["monte_carlo"]
    assert "probability_of_profit" in mc
    assert 0.0 <= mc["probability_of_profit"] <= 1.0
    assert "histogram" in mc
