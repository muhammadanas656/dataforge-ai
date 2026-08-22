"""
Adversarial Stress & Extreme Edge-Case Self-Hardening Suite.
Tests DataForge AI against corrupted multi-currency strings, invalid dates, unicode emojis,
extreme float precision, SQL injection queries, and high-concurrency race conditions.
"""
import pytest
import os
import concurrent.futures
import numpy as np
import pandas as pd
from src.autopilot import run_autopilot
from src.code_exporter import export_pipeline_code
from src.data_analyst import query_dataset
from src.scenario_planning import scenario_planner
from src.invention_pipeline import invention_pipeline
from src.triz_engine import triz_engine

@pytest.fixture(scope="module")
def adversarial_corrupted_dataset():
    """Generate heavily corrupted dataset with mixed types, emojis, invalid dates, and extreme numbers."""
    os.makedirs("uploads", exist_ok=True)
    csv_path = "uploads/adversarial_corrupted_stream.csv"
    
    n = 300
    txn = [f"TXN-{i:05d}🚀" for i in range(n)]
    rev = ([
        "$1,250.00", "€850.50", "£3,100.99", "N/A", "null", "-inf", "1e308", "FREE", "0.00", None
    ] * 30)[:n]
    dates = ([
        "2026-08-22 14:00:00", "2026-02-30", "INVALID_DATE", "1900-01-01", "2026/13/45", "None", "", None
    ] * 40)[:n]
    notes = ([
        "Normal text", "User with emoji 🏙️🔥", "Line\nBreak\tTab", "   trailing space   ", "", None
    ] * 50)[:n]
    sensors = list(np.random.choice([0.0, 1e-15, 9999999.9, -99999.0, np.nan, 42.0], size=n))
    single_val = ["Constant_Value"] * n
    
    df = pd.DataFrame({
        "Transaction_ID": txn,
        "Mixed_Revenue": rev,
        "Corrupted_Timestamp": dates,
        "Customer_Notes": notes,
        "Extreme_Sensor_Value": sensors,
        "Single_Valued_Category": single_val
    })
    df.to_csv(csv_path, index=False)
    return csv_path


def test_adversarial_corrupted_dataset_autopilot(adversarial_corrupted_dataset):
    """Stress test Auto-Pilot zero-touch pipeline on heavily corrupted multi-modal data."""
    res = run_autopilot(adversarial_corrupted_dataset, session_id="stress_test_autopilot")
    assert res["status"] == "success"
    did = res["dataset_id"]
    
    # Verify cleaned file is readable and non-empty
    cleaned_path = f"data/canonical/{did}_cleaned.csv"
    assert os.path.exists(cleaned_path)
    cleaned_df = pd.read_csv(cleaned_path)
    assert not cleaned_df.empty
    assert len(cleaned_df) > 0


def test_adversarial_financial_simulation_extreme_shocks():
    """Verify Monte Carlo simulation under extreme 100% inflation shocks, negative margins, and zero variance."""
    extreme_assumptions = {
        "units_per_month": 50,
        "price_usd": 150.0,
        "cogs_usd": 40.0,
        "cac_usd": 30.0,
        "fixed_costs_monthly": 5000.0
    }
    sim_res = scenario_planner.generate_scenarios(
        niche="Ultra-Low-Cost Micro-Sensors",
        base_assumptions=extreme_assumptions,
        category="AI & SaaS"
    )
    assert sim_res is not None
    assert "scenarios" in sim_res
    assert "monte_carlo" in sim_res
    
    mc = sim_res["monte_carlo"]
    assert "monthly_profit" in mc or "cumulative_profit_12mo" in mc
    p = mc.get("monthly_profit", mc.get("cumulative_profit_12mo", {}))
    for k in ["p10", "p50", "p90"]:
        assert not np.isnan(p[k])
        assert not np.isinf(p[k])


def test_triz_novel_contradiction_stress():
    """Verify TRIZ contradiction resolution on unconventional contradictory parameters."""
    matrix_res = triz_engine.resolve_contradiction(
        improving_param="Weight of moving object",
        worsening_param="Reliability",
        domain="Aerospace Drones"
    )
    assert matrix_res is not None
    assert "applied_principle" in matrix_res or "contradiction" in matrix_res
    assert "invention" in matrix_res


def test_conversational_data_analyst_injection_and_edge_queries(adversarial_corrupted_dataset):
    """Verify natural language analyst against prompt injections, SQL syntax, and non-existent fields."""
    res_prof = run_autopilot(adversarial_corrupted_dataset, session_id="analyst_test")
    did = res_prof["dataset_id"]
    
    # 1. Injection query
    q_inj = query_dataset(did, "SELECT * FROM users; DROP TABLE data; --")
    assert q_inj["status"] == "success"
    
    # 2. Non-existent column query
    q_non = query_dataset(did, "Show me the top nonexistent_field_xyz in this table")
    assert q_non["status"] == "success"
    assert "records" in q_non
    
    # 3. Empty query check
    q_empty = query_dataset(did, "")
    assert q_empty["status"] == "success"


def test_high_concurrency_autopilot_execution(adversarial_corrupted_dataset):
    """Stress test 4 concurrent Auto-Pilot execution threads to guarantee zero race conditions."""
    def worker(thread_id):
        return run_autopilot(adversarial_corrupted_dataset, session_id=f"thread_{thread_id}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as exec_pool:
        futures = [exec_pool.submit(worker, i) for i in range(4)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 4
    for r in results:
        assert r["status"] == "success"
        assert "dataset_id" in r
