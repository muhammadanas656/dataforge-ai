import pandas as pd
from src.planner import compute_impact
from src.governance import govern
from src.executor import apply_step, validate_step
from src.reporter import check_contract

def make_df():
    return pd.DataFrame({
        "Product Name": ["A", "B", "A", "C", "D"],
        "Old Price": [100.0, 200.0, 100.0, 50.0, -5.0],
        "Special Price": [90.0, 180.0, 90.0, 45.0, 10.0],
        "Discount %": [10.0, 10.0, 10.0, 10.0, 10.0],
        "Product": ["x", "y", "x", "z", "w"],
    })

def test_remove_duplicates_impact():
    imp = compute_impact(make_df(), {"action": "remove_duplicates"})
    assert imp["rows_removed"] == 1
    assert abs(imp["pct"] - 20.0) < 0.1

def test_remove_invalid_prices_impact():
    imp = compute_impact(make_df(), {"action": "remove_invalid_prices", "column": "Old Price"})
    assert imp["rows_removed"] == 1

def test_governance_auto_vs_mandatory():
    assert govern({"action": "remove_duplicates", "impact": {"pct": 0.5}}, [])["decision"] == "auto"
    assert govern({"action": "remove_outliers", "impact": {"pct": 30}}, [])["decision"] == "mandatory_approval"

def test_governance_llm_reject_escalates():
    g = govern({
        "action": "remove_duplicates",
        "impact": {"pct": 0.5},
        "llm_review": {"verdict": "reject"}
    }, [])
    assert g["decision"] == "mandatory_approval"

def test_executor_apply_and_validate():
    out = apply_step(make_df(), {"action": "remove_duplicates"})
    assert len(out) == 4 and validate_step(out, {"action": "remove_duplicates"})

def test_executor_removes_negative_price():
    out = apply_step(make_df(), {"action": "remove_invalid_prices", "column": "Old Price"})
    assert (out["Old Price"] > 0).all()

def test_contract_flags_negative_price():
    c = check_contract(make_df(), {"total_rows": 5, "columns": [{"name": "Old Price"}]})
    assert "fail" in [x["status"] for x in c["checks"]]
