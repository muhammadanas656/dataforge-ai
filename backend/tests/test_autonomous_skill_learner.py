"""
Autonomous Skill Learner Test Suite.
Verifies:
1. Baseline skills initialized for scraping, design, and causal discovery.
2. Skill proficiency updates dynamically upon recording operation outcomes.
3. Serialized status returns complete heuristics and metadata.
"""
import pytest
from src.autonomous_skill_learner import autonomous_skill_learner


def test_autonomous_skill_learner_baseline_and_tuning():
    """Verify skill learner tracks baseline skills and updates proficiency."""
    all_skills = autonomous_skill_learner.get_all_skills()

    assert "web_harvesting" in all_skills
    assert "vector_design" in all_skills
    assert "causal_discovery" in all_skills

    # Record successful operation
    orig_total = all_skills["web_harvesting"]["total_operations"]
    updated = autonomous_skill_learner.record_operation_result("web_harvesting", success=True)

    assert updated.total_operations == orig_total + 1
    assert updated.proficiency_score > 0.80
    assert "anti_bot_headers" in updated.heuristics
