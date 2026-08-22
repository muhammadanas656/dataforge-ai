import pandas as pd
from src.verification_sandbox import verify_step, distribution_check
from src.query_audit import audit_logger

def test_row_budget_check():
    df = pd.DataFrame({"price": [10, 20, 30]})
    step = {"action": "standardize_text", "column": "price"}
    curr_df, result = verify_step(df, df.copy(), step)
    assert result["verified"]

def test_distribution_check_small_sample():
    before = pd.Series([1, 2, 3, 4, 5])
    after = pd.Series([1, 2, 3, 4, 6])
    result = distribution_check(before, after)
    assert result["test"] in ("wasserstein", "skipped")

def test_query_audit_logs():
    audit_logger.log_query(
        query="SELECT * FROM data LIMIT 10",
        schema={"columns": ["price"]},
        metrics={"runtime_ms": 50, "rows_returned": 10},
        dataset_id="test_ds_phase1",
        query_type="sql"
    )
    queries = audit_logger.get_recent("test_ds_phase1")
    assert len(queries) >= 1
    assert queries[0]["query_type"] == "sql"
