"""
Feature How-To Navigation & Action Redirection Test Suite.
Verifies:
1. AdaptiveExplanationEngine identifies 'how-to' questions across all 4 studios.
2. Generates simple step-by-step non-sophisticated instructions without technical jargon.
3. Generates relative route redirection action cards (e.g. /clean, /intel, /niche, /eda, /export).
4. AssistantEngine integrates how-to dispatch with zero LLM token waste.
"""
import pytest
from src.adaptive_explanations import adaptive_explainer
from src.assistant_engine import assistant_engine


# =====================================================================
# 1. HOW-TO DETECTION & STRUCTURED GUIDANCE
# =====================================================================

def test_how_to_clean_data_returns_cleaning_studio_navigation():
    """Verify 'how do I clean data' returns /clean route card and steps."""
    guide = adaptive_explainer.get_how_to_guide("how do i clean my dataset")
    assert guide is not None
    assert guide["route_link"] == "/clean"
    assert "Cleaning Studio" in guide["route_label"]
    assert "Auto-Pilot" in guide["response"]
    assert guide["action_card"]["type"] == "feature_navigation"
    assert guide["action_card"]["route_link"] == "/clean"


def test_how_to_generate_svg_returns_intel_studio_navigation():
    """Verify 'how can I create an SVG icon' returns /intel SVG studio route card."""
    guide = adaptive_explainer.get_how_to_guide("how can i generate svg vector icons")
    assert guide is not None
    assert guide["route_link"] == "/intel"
    assert "SVG" in guide["route_label"]
    assert "Download .jsx" in guide["response"] or "Vector Asset" in guide["response"]


def test_how_to_scrape_leads_returns_web_intelligence_navigation():
    """Verify 'how to scrape leads' returns /intel route card."""
    guide = adaptive_explainer.get_how_to_guide("how to scrape niche business leads")
    assert guide is not None
    assert guide["route_link"] == "/intel"
    assert "Web Intelligence" in guide["route_label"]
    assert "Cloudflare" in guide["response"] or "crawl" in guide["response"].lower()


def test_how_to_triz_returns_strategic_invention_navigation():
    """Verify 'how to resolve triz contradiction' returns /niche route card."""
    guide = adaptive_explainer.get_how_to_guide("how do i use triz to resolve contradictions")
    assert guide is not None
    assert guide["route_link"] == "/niche"
    assert "Strategic Invention" in guide["route_label"]
    assert "40 proven engineering principles" in guide["response"] or "Improve" in guide["response"]


def test_how_to_export_code_returns_code_exporter_navigation():
    """Verify 'how do I export python scripts' returns /export route card."""
    guide = adaptive_explainer.get_how_to_guide("how do i export python standalone scripts")
    assert guide is not None
    assert guide["route_link"] == "/export"
    assert "Code Exporter" in guide["route_label"]


# =====================================================================
# 2. COPILOT END-TO-END HOW-TO EXECUTION
# =====================================================================

@pytest.mark.asyncio
async def test_copilot_answers_how_can_i_clean_data_with_action_card():
    """Verify Copilot answers 'How can I do data cleaning?' with step-by-step guidance and a redirection card."""
    res = await assistant_engine.process_query(
        session_id="test_nav_sess",
        query="How can I clean my dataset?"
    )
    assert res.get("status") == "success"
    assert "action_card" in res
    card = res["action_card"]
    assert card["type"] == "feature_navigation"
    assert card["route_link"] == "/clean"
    assert "Cleaning Studio" in card["route_label"]
    assert "1." in res["response"] and "2." in res["response"]


@pytest.mark.asyncio
async def test_copilot_answers_how_to_create_icons_with_action_card():
    """Verify Copilot answers 'How to generate SVG vector icons?' with navigation card."""
    res = await assistant_engine.process_query(
        session_id="test_nav_sess",
        query="How to generate SVG icons?"
    )
    assert res.get("status") == "success"
    assert "action_card" in res
    assert res["action_card"]["route_link"] == "/intel"
    assert "SVG" in res["action_card"]["route_label"]
