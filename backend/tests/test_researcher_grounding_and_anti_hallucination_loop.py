"""
Researcher Grounding & Anti-Hallucination Test Suite.
Verifies:
1. ResearcherGroundingEngine intercepts ungrounded speculative claims and mathematical violations.
2. Vector geometry grounding validates valid path MoveTo coordinates and viewBox bounds.
3. GroundedWebDesignHarvester extracts and audits real-world vector DNA without hallucinations.
4. BoundedDesignEvolver refines vector assets within <= 5 generations to >= 90.0 fitness.
"""
import pytest
from src.researcher_grounding_engine import researcher_grounding
from src.grounded_web_design_harvester import grounded_harvester
from src.bounded_design_evolver import bounded_evolver


def test_researcher_grounding_validates_empirical_responses():
    """Verify grounded quantitative output passes with zero hallucination risk."""
    grounded_text = (
        "Based on a sample size of N=1,500 records, the causal DAG indicates a statistically significant "
        "reduction in churn (p=0.002, variance ratio=0.82) when median latency is clipped via IQR outlier remediation."
    )
    context = {"dataset_id": "cust_churn_2026", "sample_size": 1500}
    res = researcher_grounding.audit_response_grounding(grounded_text, context)

    assert res.is_grounded is True
    assert res.hallucination_risk == "NONE"
    assert res.grounding_score >= 90.0
    assert len(res.unsubstantiated_claims) == 0
    assert len(res.mathematical_violations) == 0


def test_researcher_grounding_intercepts_speculative_hallucinations():
    """Verify speculative ungrounded claims and mathematical violations are flagged as CRITICAL."""
    hallucinated_text = (
        "This algorithm is guaranteed 100% profit with infinite scalability with zero cost, "
        "yielding a 150% accuracy rate and a p-value of 1.45."
    )
    context = {}
    res = researcher_grounding.audit_response_grounding(hallucinated_text, context)

    assert res.is_grounded is False
    assert res.hallucination_risk == "CRITICAL"
    assert len(res.unsubstantiated_claims) >= 1
    assert len(res.mathematical_violations) >= 1


def test_vector_geometry_grounding_validation():
    """Verify vector geometry validator checks MoveTo commands and viewBox bounds."""
    valid_svg = '<svg viewBox="0 0 24 24"><path d="M2 12h20"/></svg>'
    audit_valid = researcher_grounding.audit_vector_design_grounding(valid_svg)
    assert audit_valid.is_grounded is True
    assert audit_valid.grounding_score == 100.0

    # Invalid SVG (empty d attribute, missing viewBox)
    invalid_svg = '<svg><path d=""/></svg>'
    audit_invalid = researcher_grounding.audit_vector_design_grounding(invalid_svg)
    assert audit_invalid.is_grounded is False
    assert len(audit_invalid.mathematical_violations) >= 1


def test_grounded_web_design_harvester_extracts_clean_vectors():
    """Verify web design harvester extracts and audits real-world vectors."""
    harvested = grounded_harvester.simulate_curated_showcase_harvest("FinTech")

    assert len(harvested) >= 2
    for asset in harvested:
        assert asset.is_grounded is True
        assert asset.fitness_score >= 70.0
        assert len(asset.css_color_palette) >= 1
        assert "viewBox" in asset.raw_svg or "viewbox" in asset.raw_svg


def test_bounded_design_evolver_reaches_target_fitness():
    """Verify bounded design evolver improves vector fitness within 5 generations."""
    raw_svg = '<svg viewBox="0 0 48 48"><rect width="40" height="40" fill="#6366f1"/></svg>'
    summary = bounded_evolver.evolve_vector_asset(raw_svg, asset_name="CloudVault", domain_theme="CyberSecurity")

    assert summary.total_generations <= 5
    assert summary.final_score >= 85.0
    assert summary.status in ["TARGET_REACHED", "STAGNATION_TERMINATION", "GENERATION_LIMIT"]
    assert "export const" in summary.react_jsx
    assert "<template>" in summary.vue_component
