"""
Test Suite for Autonomous Action-Taking Copilot, Tool Orchestration,
Semantic 0-Token Response Caching, and Personalization Memory.
"""
import pytest
import os
import json
import pandas as pd
from src.assistant_engine import assistant_engine, AssistantEngine

@pytest.fixture
def mock_active_dataset(tmp_path):
    """Create a sample dataset and canonical cleaning artifact for testing."""
    os.makedirs("uploads", exist_ok=True)
    csv_path = "uploads/copilot_test_data.csv"
    df = pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "mrr_amount": [100.0, 250.0, 150.0, 9999.0, 120.0],
        "churn_risk": [0, 1, 0, 1, 0]
    })
    df.to_csv(csv_path, index=False)
    return "copilot_test_data"


@pytest.mark.asyncio
async def test_copilot_autonomous_autopilot_execution(mock_active_dataset):
    """Verify that Copilot autonomously triggers Auto-Pilot on user request."""
    res = await assistant_engine.process_query(
        session_id="test_copilot_sess",
        query="Please run autopilot on my dataset"
    )
    assert res.get("tool_executed") == "run_autopilot"
    assert "Auto-Pilot Completed" in res.get("response")
    assert "action_card" in res
    assert res.get("action_card", {}).get("type") == "autopilot_complete"


@pytest.mark.asyncio
async def test_copilot_autonomous_lead_scraping_execution():
    """Verify that Copilot autonomously triggers Niche Lead Scraping from chat."""
    res = await assistant_engine.process_query(
        session_id="test_copilot_sess",
        query="Scrape leads for autonomous drone weeding"
    )
    assert res.get("tool_executed") == "extract_niche_leads"
    assert "Niche Lead Extraction" in res.get("response")
    assert "action_card" in res
    assert res.get("action_card", {}).get("type") == "leads_ready"


@pytest.mark.asyncio
async def test_copilot_autonomous_triz_execution():
    """Verify that Copilot autonomously triggers TRIZ 39x40 contradiction solver."""
    res = await assistant_engine.process_query(
        session_id="test_copilot_sess",
        query="Please resolve TRIZ contradiction between speed and energy"
    )
    assert res.get("tool_executed") == "resolve_triz"
    assert "TRIZ 39×40" in res.get("response")
    assert "action_card" in res


@pytest.mark.asyncio
async def test_copilot_autonomous_code_export_execution():
    """Verify that Copilot generates standalone pipeline code on command."""
    res = await assistant_engine.process_query(
        session_id="test_copilot_sess",
        query="Export pipeline code for my dataset"
    )
    assert res.get("tool_executed") == "export_pipeline_code"
    assert "Pipeline Code Generated" in res.get("response")


@pytest.mark.asyncio
async def test_copilot_semantic_cache_zero_token_savings():
    """Verify that recurring questions return from local semantic memory with 0 token consumption."""
    initial_saved = assistant_engine.total_tokens_saved
    
    # Query known platform capability question
    res = await assistant_engine.process_query(
        session_id="test_copilot_sess",
        query="What services does this system provide?"
    )
    assert res.get("cached") is True
    assert res.get("tokens_saved", 0) > 0
    assert assistant_engine.total_tokens_saved >= initial_saved + res.get("tokens_saved")
    assert "Autonomous Auto-Pilot" in res.get("response")


def test_copilot_personalization_profile_persistence():
    """Verify user personalization settings load, update, and persist."""
    assistant_engine.user_profile["industry"] = "Aerospace & Satellites"
    assistant_engine.user_profile["style"] = "mathematical_in_depth"
    assistant_engine._save_user_profile()

    new_engine = AssistantEngine()
    assert new_engine.user_profile.get("industry") == "Aerospace & Satellites"
    assert new_engine.user_profile.get("style") == "mathematical_in_depth"
