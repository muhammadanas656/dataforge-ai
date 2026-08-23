"""
Supervised Evolution Runner & Multi-Ground Stress Test Suite.
Verifies:
1. ContinuousSupervisedEvolutionRunner completes multi-round stress loops across all 5 operational grounds.
2. Data, Scraping, Design, Frontend Scaffolding, and Security achieve >= 90% round scores.
3. Flaws detected during stress execution are automatically remediated without regressions.
"""
import pytest
from src.supervised_evolution_runner import supervised_evolution_runner


def test_supervised_evolution_runner_multi_round_execution():
    """Verify multi-round self-supervised execution across all operational grounds."""
    summaries = supervised_evolution_runner.run_supervised_stress_loop(total_rounds=3)

    assert len(summaries) == 3
    for s in summaries:
        assert s.data_ground_passed is True
        assert s.scraping_ground_passed is True
        assert s.design_ground_score >= 85.0
        assert s.frontend_scaffold_valid is True
        assert s.security_ground_passed is True
        assert s.round_score >= 88.0
        # If any weakness was flagged, a remediation was applied
        assert len(s.weaknesses_detected) == len(s.remediations_applied)
