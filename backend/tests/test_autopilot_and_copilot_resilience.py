"""
Adversarial & Autonomous Resilience Tests for Auto-Pilot, Pipeline Code Exporter,
and Conversational Data Analyst.
"""
import pytest
import os
import pandas as pd
import numpy as np
from src.autopilot import run_autopilot
from src.code_exporter import export_pipeline_code
from src.data_analyst import query_dataset
from src import phase1, cp2, cp3, governance, executor

@pytest.fixture(scope="module")
def sample_retail_dataset():
    """Create a realistic retail churn and revenue dataset with outliers and missingness."""
    os.makedirs("uploads", exist_ok=True)
    csv_path = "uploads/autopilot_test_retail.csv"
    np.random.seed(42)
    n = 250
    df = pd.DataFrame({
        "Customer_ID": [f"CUST-{i:04d}" for i in range(n)],
        "Account_Age_Months": np.random.randint(1, 60, size=n),
        "Monthly_Spend_USD": np.random.exponential(scale=120.0, size=n),
        "Region": np.random.choice([" North America ", "Europe", "Asia-Pacific", None], size=n, p=[0.4, 0.3, 0.2, 0.1]),
        "Support_Tickets": np.random.choice([0, 1, 2, 3, 15, None], size=n, p=[0.5, 0.25, 0.15, 0.05, 0.03, 0.02]),
        "Churn_Flag": np.random.choice([0, 1], size=n, p=[0.8, 0.2])
    })
    # Add dirty text and extreme outliers
    df.loc[0:5, "Monthly_Spend_USD"] = 99999.0
    df.loc[10:15, "Region"] = "   europe   "
    df.to_csv(csv_path, index=False)
    return csv_path


def test_autopilot_end_to_end_orchestration(sample_retail_dataset):
    """Verify 1-click Auto-Pilot pipeline from raw upload to causal EDA."""
    result = run_autopilot(sample_retail_dataset, session_id="test_autopilot")
    assert result["status"] == "success"
    assert "dataset_id" in result
    did = result["dataset_id"]
    
    # Verify all 5 stages ran
    stages = result["stages"]
    assert len(stages) == 5
    assert stages[0]["stage"] == "Phase 1: Profiling"
    assert stages[3]["stage"] == "Phase 4: Governed Execution"
    assert stages[4]["stage"] == "Phase 5: Visual EDA & Causal DAG"
    
    # Verify quality improvement
    qi = result["quality_improvement"]
    assert qi["after"] > qi["before"]
    assert qi["delta"] >= 0
    
    # Verify canonical outputs exist on disk
    assert os.path.exists(f"data/canonical/{did}_cleaned.csv")
    assert os.path.exists(f"reports/eda_{did}.json")


def test_pipeline_code_exporter(sample_retail_dataset):
    """Verify generation of standalone Python, SQL/dbt, and Airflow DAG code."""
    prof = phase1.run_phase1(sample_retail_dataset)
    did = prof["dataset_id"]
    cp2.run_cp2(did)
    cp3.run_cp3(did)
    governance.run_governance(did)
    executor.execute_plan(did)
    
    exported = export_pipeline_code(did)
    assert exported["dataset_id"] == did
    assert "python_script" in exported
    assert "sql_model" in exported
    assert "airflow_dag" in exported
    
    # Verify Python script contains functional pandas logic
    py_code = exported["python_script"]
    assert "import pandas as pd" in py_code
    assert "def clean_dataset" in py_code
    assert "df.to_csv" in py_code
    
    # Verify SQL model contains valid CTE structure
    sql_code = exported["sql_model"]
    assert "WITH raw_source AS" in sql_code
    assert "SELECT * FROM cleaned_stage;" in sql_code
    
    # Verify Airflow DAG structure
    dag_code = exported["airflow_dag"]
    assert "from airflow import DAG" in dag_code
    assert f"dataforge_clean_{did}" in dag_code


def test_conversational_data_analyst_queries(sample_retail_dataset):
    """Verify natural language querying, group-by aggregation, and summary profiling."""
    prof = phase1.run_phase1(sample_retail_dataset)
    did = prof["dataset_id"]
    cp2.run_cp2(did)
    cp3.run_cp3(did)
    governance.run_governance(did)
    executor.execute_plan(did)
    
    # 1. Top / Outlier Query
    res_top = query_dataset(did, "Show me the highest Monthly_Spend_USD customers")
    assert res_top["status"] == "success"
    assert "records" in res_top and len(res_top["records"]) > 0
    assert "chart_spec" in res_top
    
    # 2. Group-By Segment Breakdown Query
    res_group = query_dataset(did, "Breakdown of Monthly_Spend_USD by Region")
    assert res_group["status"] == "success"
    assert "records" in res_group
    assert res_group["query_type"] == "aggregation"
    assert "summary_metric" in res_group
    
    # 3. Profile Summary Query
    res_summary = query_dataset(did, "Give me an overview of all columns")
    assert res_summary["status"] == "success"
    assert "records" in res_summary
    assert "Completeness" in res_summary["summary_metric"]
