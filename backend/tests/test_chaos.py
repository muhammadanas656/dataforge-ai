import pytest
import concurrent.futures
import numpy as np
import pandas as pd
from src import profiler, executor, chart_mpl, eda_engine
from src.utils import repair_and_load_json

def test_empty_csv():
    """0-row dataset must profile cleanly without ZeroDivisionError."""
    df = pd.DataFrame(columns=["a", "b", "c"])
    prof = profiler.profile_dataframe(df)
    assert prof["total_rows"] == 0
    assert prof["duplicate_pct"] == 0.0
    assert prof["payload_duplicates"] == 0


def test_single_row_csv():
    """1-row dataset must profile without IQR/variance crashes."""
    df = pd.DataFrame({"a": [10.0], "b": ["test"]})
    prof = profiler.profile_dataframe(df)
    assert prof["total_rows"] == 1
    assert prof["columns"][0]["outliers"] == 0


def test_all_null_column_fill():
    """100% null columns must not crash fill_nulls with IndexError."""
    # Text/Object column
    df_text = pd.DataFrame({"notes": pd.Series([np.nan, np.nan, np.nan], dtype="object")})
    step_text = {"action": "fill_nulls", "column": "notes"}
    res_text = executor.apply_step(df_text, step_text)
    assert res_text["notes"].isnull().sum() == 0
    assert (res_text["notes"] == "Unknown").all()

    # Numeric column
    df_num = pd.DataFrame({"scores": pd.Series([np.nan, np.nan], dtype="float64")})
    step_num = {"action": "fill_nulls", "column": "scores"}
    res_num = executor.apply_step(df_num, step_num)
    assert res_num["scores"].isnull().sum() == 0
    assert (res_num["scores"] == 0.0).all()


def test_zero_variance_correlation():
    """Zero variance numeric columns must not crash correlation calculations with NaNs."""
    df = pd.DataFrame({
        "constant_col": [5.0, 5.0, 5.0, 5.0],
        "var_a": [1.0, 2.0, 3.0, 4.0],
        "var_b": [10.0, 20.0, 30.0, 40.0]
    })
    res = eda_engine.correlation_matrix(df)
    assert "Spearman Correlation" in res["title"]
    assert "data" in res


def test_nan_preservation_in_text_standardization():
    """Standardizing text must preserve real NaNs without turning them into 'Nan' strings."""
    df = pd.DataFrame({"city": [" new york ", np.nan, "LOS ANGELES", None]})
    step = {"action": "standardize_text", "column": "city"}
    result = executor.apply_step(df, step)
    assert result["city"].iloc[0] == "New York"
    assert pd.isna(result["city"].iloc[1])
    assert result["city"].iloc[2] == "Los Angeles"
    assert pd.isna(result["city"].iloc[3])
    # Must have exactly 2 nulls
    assert result["city"].isnull().sum() == 2


def test_intelligent_payload_deduplication_7517_rows():
    """
    Simulate the exact user scenario:
    7,517 rows with an 'Unnamed: 0' auto-increment index column (0..7516)
    and only ~1,517 unique business records (~6,000 duplicates).
    Verify that DataForge AI identifies the 6,000 duplicates and prunes them cleanly!
    """
    n_total = 7517
    n_unique = 1517

    # Generate 1517 base unique products
    base_products = [f"Product SKU {i}" for i in range(n_unique)]
    base_prices = [round(float(10.0 + (i % 50)), 2) for i in range(n_unique)]
    base_categories = ["Electronics", "Apparel", "Footwear", "Home", "Sports"]

    # Repeat them to create 7517 total rows
    repeated_indices = [i % n_unique for i in range(n_total)]
    df = pd.DataFrame({
        "Unnamed: 0": list(range(n_total)),  # Artificial index column 0..7516
        "product_name": [base_products[i] for i in repeated_indices],
        "price": [base_prices[i] for i in repeated_indices],
        "category": [base_categories[i % len(base_categories)] for i in repeated_indices]
    })

    # 1. Verify standard df.duplicated() fails to see duplicates due to Unnamed: 0
    assert df.duplicated().sum() == 0

    # 2. Verify profiler detects the 6000 payload duplicates
    prof = profiler.profile_dataframe(df)
    assert prof["payload_duplicates"] == (n_total - n_unique)
    assert "Unnamed: 0" not in prof["payload_columns"]

    # 3. Verify executor.apply_step reduces dataset to exactly 1517 unique rows
    step = {"action": "remove_duplicates", "subset": prof["payload_columns"]}
    cleaned_df = executor.apply_step(df, step)
    assert len(cleaned_df) == n_unique


def test_json_repair_self_healing():
    """Verify repair_and_load_json handles markdown, trailing commas, and Python literals."""
    # 1. Markdown codeblock with trailing comma
    bad_json_1 = """```json
    {
      "domain": "sports-retail",
      "confidence": 0.95,
    }
    ```"""
    res1 = repair_and_load_json(bad_json_1)
    assert res1.get("domain") == "sports-retail"
    assert res1.get("confidence") == 0.95

    # 2. Python dictionary with single quotes and True boolean
    py_dict_str = "{'semantic_type': 'currency', 'pii': False, 'confidence': 0.9}"
    res2 = repair_and_load_json(py_dict_str)
    assert res2.get("semantic_type") == "currency"
    assert res2.get("pii") is False


def test_canonical_order_of_operations():
    """Verify approved steps execute in canonical data engineering precedence."""
    df = pd.DataFrame({
        "item": [" A ", " B ", " A ", None],
        "price": [10.0, 1000.0, 10.0, np.nan]
    })
    # Given out-of-order approval IDs: standardize before dedup
    gov = {
        "steps": [
            {"id": 10, "action": "standardize_text", "column": "item", "impact": {"pct": 25}},
            {"id": 20, "action": "remove_duplicates", "subset": ["item", "price"], "impact": {"pct": 25}},
            {"id": 30, "action": "fill_nulls", "column": "price", "impact": {"pct": 25}}
        ]
    }
    # Mock prof on disk for execution
    dataset_id = "test_order_exec"
    import os, json
    os.makedirs("reports", exist_ok=True)
    os.makedirs("data/canonical", exist_ok=True)
    csv_path = f"data/canonical/{dataset_id}.csv"
    df.to_csv(csv_path, index=False)
    with open(f"reports/profile_{dataset_id}.json", "w") as f:
        json.dump({"dataset_id": dataset_id, "snapshot": {"csv": csv_path}}, f)

    res = executor.run_execution(dataset_id, [10, 20, 30], gov)
    # The first executed step in report must be remove_duplicates (action order 1)
    applied_actions = [r["action"] for r in res["report"] if r["applied"]]
    assert applied_actions[0] == "remove_duplicates"
    assert applied_actions[1] == "fill_nulls"
    assert applied_actions[2] == "standardize_text"


def test_matplotlib_thread_safety_concurrent():
    """Verify 10 concurrent threads rendering charts with chart_mpl succeed without collision."""
    df = pd.DataFrame({
        "sales": np.random.normal(100, 15, 200),
        "dept": np.random.choice(["Apparel", "Footwear", "Gear"], 200)
    })

    def render_worker(i):
        chart_type = "histogram" if i % 2 == 0 else "box"
        return chart_mpl.render_dist(df, "sales", f"Sales Dist {i}", chart_type=chart_type)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor_pool:
        futures = [executor_pool.submit(render_worker, i) for i in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 10
    assert all(r is not None and len(r) > 100 for r in results)
