import pytest
import pandas as pd
import numpy as np
from src import profiler, planner, executor, llm_critic, analyst_engine

def test_critic_mathematical_validation_gate():
    """Verify that Critic proposals are verified by Pandas dry-run before reaching the plan."""
    df = pd.DataFrame({
        "old_price": [100.0, 200.0, 50.0, 300.0],
        "special_price": [80.0, 250.0, 40.0, 290.0], # Row 1 violates special_price <= old_price
        "start_date": ["2023-01-01", "2023-01-05", "2023-02-01", "2023-03-01"],
        "end_date": ["2023-01-02", "2023-01-01", "2023-02-10", "2023-03-05"] # Row 1 violates start <= end
    })

    critic_proposals = {
        "business_rules": [
            {"name": "price_ceiling", "pandas_expr": "special_price <= old_price", "reason": "Discounted price must not exceed original price."},
            {"name": "hallucinated_rule", "pandas_expr": "non_existent_col > 0", "reason": "Invalid column"}
        ],
        "derived_features": [
            {"name": "savings", "pandas_expr": "old_price - special_price", "reason": "Customer savings amount"},
            {"name": "broken_feature", "pandas_expr": "1 / 0_syntax_err", "reason": "Invalid math"}
        ]
    }

    validated = llm_critic.validate_critic_proposals(df, critic_proposals)
    
    # Must accept price_ceiling and savings, but silently discard hallucinated_rule and broken_feature
    actions = [v["action"] for v in validated]
    assert "fix_business_rule" in actions
    assert "derive_metric" in actions
    assert len(validated) == 2

    # Verify execution of fix_business_rule
    rule_step = [v for v in validated if v["action"] == "fix_business_rule"][0]
    cleaned_df = executor.apply_step(df, rule_step)
    assert len(cleaned_df) == 3
    assert (cleaned_df["special_price"] <= cleaned_df["old_price"]).all()

    # Verify execution of derive_metric
    derive_step = [v for v in validated if v["action"] == "derive_metric"][0]
    enriched_df = executor.apply_step(cleaned_df, derive_step)
    assert "savings" in enriched_df.columns
    assert enriched_df["savings"].iloc[0] == 20.0


def test_system1_7878_row_key_deduplication():
    """
    Simulate the exact System 1 dataset:
    7,878 rows where only 1,476 rows are unique business entities.
    Verify that key-column deduplication reduces 7,878 rows down to exactly 1,476 unique products!
    """
    n_total = 7878
    n_unique = 1476

    base_names = [f"Stag Table Tennis Racket {i}" for i in range(n_unique)]
    base_old = [float(1000 + (i * 10)) for i in range(n_unique)]
    base_special = [float(800 + (i * 8)) for i in range(n_unique)]
    base_disc = [20.0 for _ in range(n_unique)]

    indices = [i % n_unique for i in range(n_total)]
    df = pd.DataFrame({
        "Unnamed: 0": list(range(n_total)), # Unique artificial index
        "product_name": [base_names[i] for i in indices],
        "old_price": [base_old[i] for i in indices],
        "special_price": [base_special[i] for i in indices],
        "discount_percent": [base_disc[i] for i in indices]
    })

    # Exact full-row check sees 0 duplicates due to Unnamed: 0
    assert df.duplicated().sum() == 0

    # Key-column deduplication on payload columns drops exactly (7878 - 1476) duplicates
    key_cols = ["product_name", "old_price", "special_price", "discount_percent"]
    step = {"action": "remove_duplicates", "subset": key_cols}
    cleaned = executor.apply_step(df, step)
    assert len(cleaned) == n_unique


def test_analyst_sql_validation_safety():
    """Verify SQL safety validator blocks destructive SQL."""
    assert analyst_engine.validate_sql("SELECT product_name, old_price FROM dataset;")[0] is True
    assert analyst_engine.validate_sql("DROP TABLE dataset;")[0] is False
    assert analyst_engine.validate_sql("DELETE FROM dataset WHERE price < 0;")[0] is False
    assert analyst_engine.validate_sql("UPDATE dataset SET price = 0;")[0] is False
