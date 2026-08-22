import pandas as pd
from src import ai_planner_validator as v
from src import chart_mpl

PROFILE = {
    "columns": [
        {"name": "Old Price", "kind": "numeric", "dtype": "float64"},
        {"name": "Product", "kind": "text", "dtype": "object"}
    ]
}

def test_drops_missing_column():
    assert not v.validate_analysis({"analysis_type": "numeric_distribution", "columns": ["NonExistentColumn"]}, PROFILE)[0]

def test_drops_unsafe_analysis():
    assert not v.validate_analysis({"analysis_type": "magic_hallucinated_analysis", "columns": ["Old Price"]}, PROFILE)[0]

def test_passes_valid_analysis():
    assert v.validate_analysis({"analysis_type": "numeric_distribution", "columns": ["Old Price"], "chart_type": "histogram"}, PROFILE)[0]

def test_drops_unsafe_action():
    assert not v.validate_cleaning({"action": "delete_all_database_records", "column": "Old Price"}, PROFILE, pd.DataFrame({"Old Price": [1]}))[0]

def test_cleaning_computes_impact():
    df = pd.DataFrame({"Old Price": [100.0, -5.0, 200.0]})
    ok, why, step = v.validate_cleaning({"action": "remove_invalid_prices", "column": "Old Price"}, PROFILE, df)
    assert ok and step["impact"]["rows_removed"] == 1

def test_chart_returns_png_base64():
    img = chart_mpl.render_dist(pd.DataFrame({"Old Price": [1, 2, 3, 4, 5] * 10}), "Old Price", "Test Price Distribution")
    assert img and img.startswith("iVBOR")

def test_chart_unknown_kind_none():
    assert chart_mpl.render_analysis(pd.DataFrame({"a": [1]}), "invalid_kind", ["invalid_kind"], "table", "Test") is None
