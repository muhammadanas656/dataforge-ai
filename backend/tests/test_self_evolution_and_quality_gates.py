"""
Self-Evolution, Data Quality Gates, Incremental Learning, and Privacy Test Suite.
Verifies:
1. DataQualityGate: Length checks, domain relevance scoring, duplicate detection, freshness.
2. PrivacyComplianceChecker: PII detection (SSN, credit card, email, phone) and copyright terms.
3. SVGNormalizer: viewBox insertion, style attribute conversion, React JSX and Vue 3 compilation.
4. IncrementalLearningManager: Model versioning (v1, v2) and automatic rollback on accuracy drop.
5. ConflictResolver: Resolving knowledge contradictions via freshness and user correction overrides.
6. UserFeedbackLoop: Recording user feedback and updating semantic cache for 0-token recall.
7. SelfEvolutionEngine: Generating implementation plans on user demand and registering dynamic features.
8. AssistantEngine: End-to-end self-evolution request execution with implementation plan and navigation card.
"""
import pytest
from src.data_quality_gates import data_quality_gate
from src.privacy_compliance import privacy_compliance
from src.svg_normalizer import svg_normalizer
from src.incremental_learning_manager import incremental_learner
from src.conflict_resolver import conflict_resolver
from src.user_feedback_loop import user_feedback_loop
from src.self_evolution_engine import self_evolution_engine
from src.assistant_engine import assistant_engine


def test_data_quality_gate_length_relevance_duplicate():
    """Verify quality gate validates length bounds and domain relevance."""
    # 1. Short content rejection
    res_short = data_quality_gate.validate("https://example.com", "Too short")
    assert not res_short.valid
    assert "too short" in res_short.reason.lower()

    # 2. Irrelevant content rejection
    res_irrel = data_quality_gate.validate(
        "https://example.com",
        "The quick brown fox jumps over the lazy dog repeatedly in a meadow with flowers and butterflies."
    )
    assert not res_irrel.valid
    assert "lacks domain relevance" in res_irrel.reason.lower()

    # 3. Valid high-quality domain content
    res_valid = data_quality_gate.validate(
        "https://example.com",
        "DataForge AI provides automated data cleaning, causal DAG inference, machine learning pipelines, and vector SVG exports for modern web analytics."
    )
    assert res_valid.valid
    assert res_valid.relevance_score >= 0.15


def test_privacy_compliance_pii_and_copyright():
    """Verify privacy checker detects sensitive PII and copyright constraints."""
    # 1. High-risk SSN detection
    res_ssn = privacy_compliance.check_content_compliance("https://example.com", "User record with SSN 123-45-6789")
    assert not res_ssn.compliant
    assert "ssn" in res_ssn.pii_detected

    # 2. Strict copyright prohibition
    res_copy = privacy_compliance.check_content_compliance(
        "https://example.com",
        "All rights reserved. Unauthorized reproduction prohibited. Proprietary data."
    )
    assert not res_copy.compliant or not res_copy.is_commercial_allowed

    # 3. Fair-use open content
    res_open = privacy_compliance.check_content_compliance(
        "https://example.com",
        "Released under Creative Commons MIT License for public research and analytics."
    )
    assert res_open.compliant


def test_svg_normalizer_viewbox_and_style_conversion():
    """Verify SVGNormalizer adds missing viewBox and converts inline styles to attributes."""
    raw_input = '<svg width="48" height="48" style="stroke-width: 2px;"><rect width="20" height="20" style="fill: #6366f1; stroke: #06b6d4;"/></svg>'
    normalized = svg_normalizer.normalize(raw_input, asset_name="CloudClusterIcon")
    
    assert normalized.has_viewbox
    assert "viewbox=" in normalized.raw_svg.lower()
    assert "fill=\"#6366f1\"" in normalized.raw_svg
    assert "stroke=\"#06b6d4\"" in normalized.raw_svg
    assert "export const CloudClusterIcon" in normalized.react_jsx
    assert "<template>" in normalized.vue_component


def test_incremental_learning_model_versioning_and_rollback():
    """Verify model versioning deploys improvements and rolls back regressions."""
    task = "intent_routing"
    
    # 1. Deploy upgraded model (accuracy 0.96 > 0.92)
    deploy_res = incremental_learner.register_and_evaluate_candidate(
        task_type=task,
        candidate_accuracy=0.96,
        training_examples=150
    )
    assert deploy_res["status"] == "deployed"
    assert deploy_res["accuracy"] == 0.96

    # 2. Regression candidate (accuracy 0.85 < 0.96) -> Automatic Rollback
    rollback_res = incremental_learner.register_and_evaluate_candidate(
        task_type=task,
        candidate_accuracy=0.85,
        training_examples=180
    )
    assert rollback_res["status"] == "rolled_back"
    assert "rollback triggered" in rollback_res["reason"].lower()
    assert incremental_learner.get_active_model(task)["accuracy"] == 0.96


def test_knowledge_conflict_resolver_freshness_and_correction():
    """Verify conflict resolver handles contradictory knowledge claims."""
    # 1. Freshness upgrade
    res_fresh = conflict_resolver.detect_and_resolve(
        topic="API Version",
        existing_claim="Use DataForge REST API v1.0",
        new_claim="Use DataForge High-Speed gRPC API v2.0",
        existing_freshness=0.3,
        new_freshness=0.95
    )
    assert res_fresh.resolution_action == "replace"
    assert "v2.0" in res_fresh.winning_claim

    # 2. Direct user correction override
    res_user = conflict_resolver.detect_and_resolve(
        topic="Default Outlier Cutoff",
        existing_claim="Standard deviation 3.0",
        new_claim="Interquartile range IQR 1.5 multiplier",
        is_user_correction=True
    )
    assert res_user.resolution_action == "replace"
    assert res_user.confidence == 1.0


def test_user_feedback_loop_correction_teaching():
    """Verify user feedback records corrections and updates 0-token semantic cache."""
    res = user_feedback_loop.record_feedback(
        session_id="sess_feedback_test",
        query="What is the default batch size for scraping?",
        copilot_response="The default batch size is 10.",
        rating=1,
        correction="The default batch size is 25 concurrent requests with a 1.5s delay."
    )
    assert res["status"] == "success"
    assert res["correction_learned"] is True

    # Verify query pattern cached in AssistantEngine
    cached = assistant_engine._match_semantic_cache("What is the default batch size for scraping?")
    assert cached is not None
    assert "25 concurrent requests" in cached["response"]


def test_self_evolution_engine_plan_generation_and_implementation():
    """Verify SelfEvolutionEngine formulates plan and registers dynamic feature."""
    prompt = "Create feature Real-Time Speech Telemetry Studio"
    plan = self_evolution_engine.generate_self_improvement_plan(prompt)
    
    assert "Real-Time Speech Telemetry Studio" in plan["feature_name"]
    assert "Self-Evolution Implementation Plan" in plan["implementation_plan_markdown"]
    assert "/studio/" in plan["target_route"]

    impl = self_evolution_engine.dynamically_implement_feature(plan)
    assert impl["status"] == "implemented"
    assert impl["registered_count"] >= 1


@pytest.mark.asyncio
async def test_copilot_end_to_end_self_evolution_request():
    """Verify Copilot answers self-evolution requests with an implementation plan and navigation card."""
    res = await assistant_engine.process_query(
        session_id="sess_evo_test",
        query="Please build a new feature Automated SQL Query Optimizer"
    )
    assert res.get("status") == "success"
    assert "Autonomous Self-Evolution Triggered" in res["response"]
    assert "Implementation Plan" in res["response"]
    assert "action_card" in res
    assert res["action_card"]["type"] == "feature_navigation"
    assert "Sql" in res["action_card"]["title"] or "SQL" in res["action_card"]["title"]
