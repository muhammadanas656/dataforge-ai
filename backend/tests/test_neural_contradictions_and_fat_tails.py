"""
Modern Neural Contradiction & Fat-Tail Distribution Test Suite.
Verifies:
1. NeuralContradictionEngine resolves modern AI/Cloud engineering tradeoffs (latency vs accuracy, KV cache vs VRAM, ZK proof vs verify).
2. ScenarioPlanner executes Monte Carlo with Student-t (df=3) and Pareto heavy-tailed distributions.
3. ScenarioPlanner computes Value at Risk (VaR 95%) and Conditional VaR (Expected Shortfall).
"""
import pytest
from src.neural_contradiction import neural_triz_engine
from src.scenario_planning import scenario_planner


# =====================================================================
# 1. MODERN NEURAL CONTRADICTION & FRONTIER INVENTIONS
# =====================================================================

def test_neural_triz_resolves_ai_latency_vs_accuracy():
    """Verify NeuralContradictionEngine maps AI latency vs accuracy to MoE and Speculative Decoding."""
    res = neural_triz_engine.resolve_frontier_tradeoff("inference latency", "model accuracy", domain="ai_llms")
    assert res["improving_parameter"] == "inference latency"
    assert len(res["actionable_architectural_solutions"]) >= 2
    assert any("MoE" in s or "Speculative" in s or "Quantization" in s for s in res["actionable_architectural_solutions"])
    assert res["confidence_score"] > 0.90


def test_neural_triz_resolves_context_window_vs_vram():
    """Verify NeuralContradictionEngine maps long context vs VRAM to PageAttention/StreamingLLM."""
    res = neural_triz_engine.resolve_frontier_tradeoff("context window length", "memory vram footprint", domain="llm_inference")
    assert len(res["principles_applied"]) > 0
    assert any("PageAttention" in s or "StreamingLLM" in s or "RingAttention" in s for s in res["actionable_architectural_solutions"])


def test_neural_triz_resolves_zk_cryptography_tradeoff():
    """Verify NeuralContradictionEngine resolves zero-knowledge proof generation vs verification cost."""
    res = neural_triz_engine.resolve_frontier_tradeoff("zk proof generation time", "zk verification cost", domain="cryptography")
    assert any("Recursive SNARK" in s or "MSM" in s for s in res["actionable_architectural_solutions"])


# =====================================================================
# 2. FAT-TAIL & HEAVY-TAILED MONTE CARLO RISK DISTRIBUTIONS
# =====================================================================

def test_scenario_planner_student_t_fat_tails_and_var():
    """Verify Monte Carlo simulator computes heavy-tailed Student-t (df=3) shocks with VaR 95%."""
    base_assumptions = {
        "units_per_month": 200,
        "price_usd": 150.0,
        "cogs_usd": 40.0,
        "cac_usd": 30.0,
        "fixed_costs_monthly": 4000.0
    }
    res = scenario_planner.generate_scenarios("Autonomous AI Cloud", base_assumptions)
    assert "monte_carlo" in res
    mc = res["monte_carlo"]
    
    assert mc["distribution_model"] == "student_t"
    assert "fat_tail_risk_metrics" in mc
    assert "var_95_percent" in mc["fat_tail_risk_metrics"]
    assert "expected_shortfall_cvar_95" in mc["fat_tail_risk_metrics"]
    assert mc["fat_tail_risk_metrics"]["black_swan_resilience"] in ["High", "Moderate", "Vulnerable"]
    assert mc["probability_of_profit"] > 0.0


def test_scenario_planner_pareto_power_law_distribution():
    """Verify Monte Carlo simulator models Pareto power-law returns for viral growth."""
    base_scenario = {
        "units_per_month": 100,
        "price_usd": 100.0,
        "cogs_usd": 20.0,
        "cac_usd": 15.0,
        "growth_rate_monthly": 0.20
    }
    mc_pareto = scenario_planner._run_monte_carlo(base_scenario, fixed_costs=1500.0, distribution="pareto")
    assert mc_pareto["distribution_model"] == "pareto"
    assert mc_pareto["monthly_profit"]["max"] > mc_pareto["monthly_profit"]["p90"]
    assert mc_pareto["probability_of_profit"] > 0.5
