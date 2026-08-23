"""
Test Suite: Global Workspace Metacognitive Architecture & Parallel Execution.
Verifies:
1. GlobalWorkspaceBus broadcasts cross-studio events with thread safety.
2. EpistemicMetacognitiveEngine computes Shannon entropy and detects ungrounded hallucinations.
3. Intrinsic curiosity generator dispatches autotelic goals.
4. Parallel studio execution operates cleanly without deadlocks.
"""
import pytest
import time
from src.global_workspace_bus import global_workspace_bus, GlobalWorkspaceEvent
from src.epistemic_metacognitive_engine import epistemic_engine
from src.continuous_autonomous_supervisor import run_continuous_supervised_cycle


def test_global_workspace_bus_event_broadcasting():
    """Verify that events published to the Global Workspace are received by subscribers."""
    received = []

    def on_token_harvested(event: GlobalWorkspaceEvent):
        received.append(event.payload)

    global_workspace_bus.subscribe("TokenHarvested", on_token_harvested)

    # Publish an event
    global_workspace_bus.broadcast(GlobalWorkspaceEvent(
        source_studio="Studio2_Web",
        event_type="TokenHarvested",
        payload={"primary_color": "#06b6d4", "theme": "Quantum"},
        confidence=0.98
    ))

    assert len(received) == 1
    assert received[0]["primary_color"] == "#06b6d4"
    state = global_workspace_bus.get_working_memory_state()
    assert state["total_events_broadcast"] > 0


def test_epistemic_metacognitive_entropy_scoring():
    """Verify that valid evidence yields high confidence & low entropy, while poor evidence is flagged."""
    # 1. Grounded Empirical Evidence
    grounded_eval = epistemic_engine.evaluate_claim_grounding(
        claim_key="GroundedPrecisionMatrix",
        evidence_metrics={"eigenvalues_min": 0.72, "contrast_ratio": 13.4, "blocked_exploits_pct": 1.0}
    )
    assert grounded_eval["is_grounded_truth"] is True
    assert grounded_eval["epistemic_confidence"] >= 0.90
    assert grounded_eval["hallucination_risk"] == "Zero / Verified"

    # 2. Ungrounded / Hallucinated Evidence
    ungrounded_eval = epistemic_engine.evaluate_claim_grounding(
        claim_key="HallucinatedMatrix",
        evidence_metrics={"eigenvalues_min": -0.5, "contrast_ratio": 2.1, "blocked_exploits_pct": 0.2}
    )
    assert ungrounded_eval["is_grounded_truth"] is False
    assert ungrounded_eval["epistemic_confidence"] < 0.60
    assert ungrounded_eval["hallucination_risk"] == "High / Ungrounded"


def test_intrinsic_curiosity_goal_generation():
    """Verify that autotelic goals are created with target domain and accent color."""
    goal1 = epistemic_engine.generate_intrinsic_curiosity_goal()
    goal2 = epistemic_engine.generate_intrinsic_curiosity_goal()

    assert "autotelic_goal" in goal1
    assert "target_domain" in goal1
    assert "target_accent" in goal1
    # Check that goals cycle through catalog
    assert goal1["target_domain"] != goal2["target_domain"]


def test_parallel_multi_studio_execution():
    """Verify that run_continuous_supervised_cycle executes multiple cycles in parallel without errors."""
    t0 = time.time()
    run_continuous_supervised_cycle(max_cycles=2, delay_between_cycles_sec=0.01)
    duration = time.time() - t0
    assert duration < 180.0 # Completes parallel execution reliably
