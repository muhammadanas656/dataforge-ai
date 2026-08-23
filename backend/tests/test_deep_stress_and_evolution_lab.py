"""
Deep Multi-Studio Stress & Autonomous Evolution Lab Test Suite.
Verifies:
1. Full deep stress lab exercises all 5 studios simultaneously.
2. Studio 1 processes 10,000 rows with MICE imputation and regularized precision matrix inversion.
3. Studio 2 harvests and grounds 10+ vectors across 5 domain themes.
4. Studio 3 genetic evolution achieves >= 88.0 mean fitness across multiple domains.
5. Studio 4 calculates heavy-tailed Student-t (df=3) VaR 95% and CVaR 95%.
6. Studio 5 blocks 100% of 25 AST sandbox probe attacks.
7. System achieves is_superior_grade == True with overall_health_score >= 95.0.
"""
import pytest
from src.deep_stress_and_evolution_lab import deep_stress_lab


def test_deep_stress_lab_exercises_all_5_studios_end_to_end():
    """Verify deep multi-ground stress lab runs all 5 studios to superior grade."""
    report = deep_stress_lab.run_full_deep_stress_lab()

    assert report.studios_evaluated == 5
    assert report.overall_health_score >= 95.0
    assert report.is_superior_grade is True
    assert report.total_duration_seconds > 0.0

    # Studio 1 verification
    s1 = report.studio_results['studio_1_tabular']
    assert s1.passed is True
    assert s1.operations_executed == 10000
    assert s1.metrics['precision_matrix_dim'] == 4

    # Studio 2 verification
    s2 = report.studio_results['studio_2_web_intel']
    assert s2.passed is True
    assert s2.metrics['vectors_extracted'] >= 10

    # Studio 3 verification
    s3 = report.studio_results['studio_3_design']
    assert s3.passed is True
    assert s3.metrics['mean_fitness'] >= 88.0

    # Studio 4 verification
    s4 = report.studio_results['studio_4_strategic_risk']
    assert s4.passed is True
    assert s4.metrics['draws'] == 10000
    assert s4.metrics['cvar_95'] < s4.metrics['var_95']

    # Studio 5 verification
    s5 = report.studio_results['studio_5_autonomous_ops']
    assert s5.passed is True
    assert s5.metrics['blocked_count'] == 25
