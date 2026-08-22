import pytest
from src.agentic_orchestrator import AgenticOrchestrator
from src.research_critic import ResearchCritic
from src.tool_router import ToolRouter

@pytest.mark.asyncio
async def test_tool_router():
    router = ToolRouter()
    posts = await router.execute_with_fallback("social_sentiment", niche="Ergonomic Split Keyboard")
    assert isinstance(posts, list)
    assert len(posts) > 0

def test_research_critic_completeness():
    critic = ResearchCritic()
    incomplete_res = {"get_reddit_sentiment": [{"id": 1}]}
    critique = critic.review_completeness("Ergonomic Keyboard", incomplete_res)
    assert critique["completeness_score"] < 0.8
    assert "insufficient_social_data" in critique["gaps"]

@pytest.mark.asyncio
async def test_agentic_orchestrator_react_loop():
    orchestrator = AgenticOrchestrator()
    result = await orchestrator.research_niche("Ergonomic Split Keyboard", depth="quick")
    assert "niche" in result
    assert "opportunity_score" in result
    assert "blueprint" in result
    assert "scenarios" in result
    assert "completeness_score" in result
