import json
import os
import nbformat
from src.notebook_export import generate_notebook


def test_notebook_generation_and_assertions(tmp_path, monkeypatch):
    dataset_id = "test_nb"

    profile = {
        "total_rows": 1000,
        "total_columns": 5,
        "snapshot": {"csv": "data/canonical/test_nb.csv"}
    }
    execution = {
        "steps": [
            {
                "step_id": 1,
                "action": "remove_outliers",
                "column": "price",
                "description": "Remove IQR outliers",
                "impact": {"rows_removed": 50},
                "rows_after": 950,
                "verification": {"checks": []}
            },
            {
                "step_id": 2,
                "action": "fill_nulls",
                "column": "category",
                "description": "Fill nulls with mode",
                "impact": {"nulls_filled": 10},
                "rows_after": 950,
                "verification": {"checks": []}
            }
        ]
    }

    os.makedirs("reports", exist_ok=True)
    with open(f"reports/profile_{dataset_id}.json", "w") as f:
        json.dump(profile, f)
    with open(f"reports/execution_{dataset_id}.json", "w") as f:
        json.dump(execution, f)

    monkeypatch.setattr("src.notebook_export.ensure_local", lambda x: x)

    nb = generate_notebook(dataset_id)

    # 1. Validate notebook structure
    nbformat.validate(nb)

    # 2. Check Sandbox Assertions
    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    all_code = "\n".join([c.source for c in code_cells])

    assert "assert len(df) == 950" in all_code
    assert "assert df['category'].isna().sum() == 0" in all_code
    assert "Outlier lower bound violated" in all_code

    if os.path.exists(f"reports/profile_{dataset_id}.json"):
        os.remove(f"reports/profile_{dataset_id}.json")
    if os.path.exists(f"reports/execution_{dataset_id}.json"):
        os.remove(f"reports/execution_{dataset_id}.json")
