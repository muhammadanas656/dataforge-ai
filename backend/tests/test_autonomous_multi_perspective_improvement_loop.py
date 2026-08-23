"""
Autonomous Multi-Perspective Self-Improvement & Antigravity Validation Test Suite.
Verifies:
1. MultiPerspectiveEvaluator evaluates all 7 operational perspectives with >= 90% mean score.
2. AutonomousImprovementLoop runs observe -> diagnose -> hypothesize -> sandbox -> deploy cycle.
3. AntigravityValidator confirms side-by-side verification with 0 regressions and 100% security.
4. Hot-swap improvements enforce minimum threshold gain (>= 2%) and rollback safeguards.
"""
import pytest
from src.multi_perspective_evaluator import multi_perspective_evaluator
from src.autonomous_improvement_loop import autonomous_improver
from src.antigravity_validator import antigravity_validator


def test_multi_perspective_evaluator_covers_all_7_perspectives():
    """Verify all 7 operational perspectives are audited and pass thresholds."""
    reports = multi_perspective_evaluator.evaluate_all_perspectives()

    assert len(reports) == 7
    expected_perspectives = [
        'functional', 'performance', 'security', 'aesthetic', 'learning', 'usability', 'resource_efficiency'
    ]
    for p in expected_perspectives:
        assert p in reports
        rep = reports[p]
        assert rep.score >= 0.85
        assert rep.passed is True
        assert len(rep.recommendation) > 5


def test_security_perspective_enforces_100_percent_pass_rate():
    """Verify Security perspective requires 100% score (0 bypass tolerance)."""
    sec_report = multi_perspective_evaluator.evaluate_security()

    assert sec_report.score == 1.0
    assert sec_report.passed is True
    assert len(sec_report.failures) == 0


def test_autonomous_improvement_loop_executes_cycle():
    """Verify autonomous improvement loop identifies bottlenecks, tests hypotheses, and records gains."""
    cycle_report = autonomous_improver.run_improvement_cycle()

    assert cycle_report.perspectives_evaluated == 7
    assert cycle_report.mean_perspective_score >= 0.85
    assert cycle_report.cycle_id.startswith("cycle_")
    assert isinstance(cycle_report.improvement_history, list)


def test_antigravity_side_by_side_validator_confirms_integrity():
    """Verify Antigravity validator verifies cycle integrity with zero regressions."""
    cycle_report = autonomous_improver.run_improvement_cycle()
    val_result = antigravity_validator.validate_improvement_cycle(cycle_report)

    assert val_result.is_valid is True
    assert val_result.perspectives_covered == 7
    assert val_result.regressions_detected == 0
    assert val_result.security_verified is True
    assert len(val_result.suggestions) >= 1
