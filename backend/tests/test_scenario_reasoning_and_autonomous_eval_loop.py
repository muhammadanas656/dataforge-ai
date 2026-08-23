"""
Scenario-Specific Impact Reasoning, Executable Self-Evolution & Autonomous Eval Loop Test Suite.
Verifies:
1. ScenarioImpactReasoner explains feature utility across e-commerce churn, high-frequency trading, healthcare, and SaaS runway.
2. SelfEvolutionEngine compiles, deploys, and executes real functional code (Fibonacci, Z-Score standardizer).
3. AutonomousEvaluationLoop extracts and evaluates unseen scenario questions, achieving average score >= 0.85.
4. AssistantEngine integrates scenario impact breakdowns with direct workspace redirection cards.
"""
import pytest
from src.scenario_impact_reasoner import scenario_reasoner
from src.self_evolution_engine import self_evolution_engine
from src.autonomous_eval_loop import autonomous_eval_loop
from src.assistant_engine import assistant_engine


# =====================================================================
# 1. SCENARIO-SPECIFIC VALUE & IMPACT REASONING
# =====================================================================

def test_causal_dag_reasoning_for_ecommerce_churn():
    """Verify Causal DAG explanation for e-commerce checkout churn."""
    res = scenario_reasoner.analyze_scenario_impact(
        "How will Causal DAGs be helpful for an e-commerce checkout churn scenario?"
    )
    assert res is not None
    assert "Causal" in res.feature_name
    assert "E-Commerce Checkout Churn" in res.scenario_name or "Churn" in res.scenario_name
    assert "/eda" == res.target_route
    assert "Concrete Example" in res.formatted_response or "Walkthrough" in res.formatted_response


def test_triz_reasoning_for_high_frequency_trading():
    """Verify TRIZ explanation for high-frequency trading bot latency."""
    res = scenario_reasoner.analyze_scenario_impact(
        "How does TRIZ help if I'm scaling a high-frequency trading bot?"
    )
    assert res is not None
    assert "TRIZ" in res.feature_name
    assert "/niche" == res.target_route
    assert "Speed" in res.concrete_example or "throughput" in res.concrete_example.lower()


def test_ssrf_security_reasoning_for_healthcare():
    """Verify SSRF security explanation for healthcare data pipelines."""
    res = scenario_reasoner.analyze_scenario_impact(
        "How will SSRF security protect a healthcare patient portal data pipeline?"
    )
    assert res is not None
    assert "SSRF" in res.feature_name
    assert "/intel" == res.target_route
    assert "metadata" in res.concrete_example.lower() or "169.254" in res.concrete_example


def test_fat_tail_reasoning_for_saas_runway():
    """Verify Fat-Tail risk explanation for SaaS startup runway forecasting."""
    res = scenario_reasoner.analyze_scenario_impact(
        "How does Fat-Tail risk modeling help a SaaS startup forecast runway?"
    )
    assert res is not None
    assert "Fat-Tail" in res.feature_name
    assert "/niche" == res.target_route
    assert "Value at Risk" in res.formatted_response or "VaR" in res.formatted_response


# =====================================================================
# 2. REAL EXECUTABLE CODE IN SELF-EVOLUTION ENGINE
# =====================================================================

def test_self_evolution_engine_executes_compiled_code():
    """Verify SelfEvolutionEngine actually compiles and executes functional Python code."""
    # 1. Test built-in/compiled Fibonacci execution
    fib_res = self_evolution_engine.execute_feature("fibonacci", n=7)
    assert fib_res == [0, 1, 1, 2, 3, 5, 8]
    assert self_evolution_engine.is_deployed("fibonacci") is True

    # 2. Test Z-Score standardization execution
    z_res = self_evolution_engine.execute_feature("z_score_standardizer", values=[10.0, 20.0, 30.0])
    assert len(z_res) == 3
    assert z_res[1] == 0.0 # Mean is at center

    # 3. Compile on-demand custom feature
    plan = self_evolution_engine.generate_self_improvement_plan("Build feature Calculate ROI Multiplier")
    impl = self_evolution_engine.dynamically_implement_feature(plan)
    assert impl["status"] == "implemented"


# =====================================================================
# 3. AUTONOMOUS QUESTION EVALUATION & BENCHMARK LOOP
# =====================================================================

@pytest.mark.asyncio
async def test_autonomous_evaluation_loop_exceeds_threshold():
    """Verify autonomous evaluation loop scores unseen questions above 0.85 threshold."""
    test_batch = [
        "How will Causal DAGs be helpful for an e-commerce checkout churn scenario?",
        "How does TRIZ help if I'm scaling a high-frequency trading bot?",
        "How will SSRF security protect a healthcare patient portal data pipeline?",
        "How does Fat-Tail risk modeling help a SaaS startup forecast runway?"
    ]
    eval_res = await autonomous_eval_loop.run_evaluation_loop(
        questions=test_batch,
        target_threshold=0.85,
        max_self_heal_rounds=2
    )
    assert eval_res["status"] == "passed"
    assert eval_res["overall_average_score"] >= 0.85
    assert eval_res["passed_count"] == len(test_batch)


@pytest.mark.asyncio
async def test_copilot_end_to_end_scenario_query():
    """Verify Copilot answers scenario inquiries with actionable impact breakdown and route button."""
    res = await assistant_engine.process_query(
        session_id="sess_scenario_copilot",
        query="How will Causal DAGs be helpful for an e-commerce checkout churn scenario?"
    )
    assert res.get("status") == "success"
    assert "Direct Business" in res["response"] or "Forensic" in res["response"]
    assert "action_card" in res
    assert res["action_card"]["route_link"] == "/eda"
    assert "Causal" in res["action_card"]["title"]
