import pytest
import os
import pandas as pd
from fastapi.testclient import TestClient
from src.api import app
from src import security, plugin_sandbox, eda_engine

client = TestClient(app)

def test_path_traversal_validation():
    # Valid IDs
    assert security.validate_dataset_id("raw_ecommerce") == "raw_ecommerce"
    assert security.validate_dataset_id("dataset-123_456") == "dataset-123_456"
    assert security.validate_dataset_id("a1b2c3d4") == "a1b2c3d4"

    # Path traversal attempts
    with pytest.raises(ValueError):
        security.validate_dataset_id("../../etc/passwd")
    with pytest.raises(ValueError):
        security.validate_dataset_id("..\\..\\windows\\system32")
    with pytest.raises(ValueError):
        security.validate_dataset_id("foo/bar")
    with pytest.raises(ValueError):
        security.validate_dataset_id("")


def test_api_path_traversal_blocked():
    res = client.get("/api/profile/..%2F..%2Fetc%2Fpasswd")
    assert res.status_code == 400 or res.status_code == 404


def test_plugin_ast_sandbox_blocks_dangerous_code():
    # Disallowed: import os
    bad_code_1 = """
import os
from src.plugins import BaseAnalysis
class MaliciousPlugin(BaseAnalysis):
    name = "malicious"
    def run(self, df):
        os.system("echo hacked")
        return {}
"""
    res1 = plugin_sandbox.smoke_test(bad_code_1)
    assert not res1["ok"]
    assert any("Forbidden import: 'os'" in issue for issue in res1["issues"])

    # Disallowed: subprocess call
    bad_code_2 = """
import subprocess
"""
    res2 = plugin_sandbox.smoke_test(bad_code_2)
    assert not res2["ok"]

    # Disallowed: eval() or exec()
    bad_code_3 = """
from src.plugins import BaseAnalysis
class EvalPlugin(BaseAnalysis):
    name = "eval"
    def run(self, df):
        eval("2+2")
        return {}
"""
    res3 = plugin_sandbox.smoke_test(bad_code_3)
    assert not res3["ok"]
    assert any("eval()" in issue for issue in res3["issues"])


def test_eda_gating_on_uncleaned_dataset(tmp_path):
    fake_did = "uncleaned_test_did"
    # Ensure cleaned file does not exist
    cleaned_path = f"data/canonical/{fake_did}_cleaned.csv"
    if os.path.exists(cleaned_path):
        os.remove(cleaned_path)

    # API call to EDA catalog should be gated with 400
    res = client.get(f"/api/eda/catalog/{fake_did}")
    assert res.status_code == 400
    assert "cleaned" in res.json().get("detail", "").lower()


def test_eda_advanced_statistics():
    df = pd.DataFrame({
        "category": ["Electronics", "Electronics", "Clothing", "Home", "Electronics"],
        "price": [100.0, 150.0, 45.0, 60.0, 200.0]
    })
    cat_res = eda_engine.category_breakdown(df, "category")
    assert "statistical_brief" in cat_res
    assert "hhi_index" in cat_res["stats"]
    assert cat_res["stats"]["hhi_index"] > 0

    dist_res = eda_engine.numeric_distribution(df, "price")
    assert "statistical_brief" in dist_res
    assert "ci_95" in dist_res["stats"]
    assert len(dist_res["stats"]["ci_95"]) == 2

    numcat_res = eda_engine.numeric_by_category(df, "category", "price")
    assert "statistical_brief" in numcat_res
    assert "anova_p_value" in numcat_res["stats"]
