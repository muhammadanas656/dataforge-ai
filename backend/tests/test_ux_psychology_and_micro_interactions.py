"""
UX Psychology, Micro-Interactions & Scroll Dynamics Test Suite.
Verifies:
1. UX Psychology Auditor enforces Fitts's Law (>=44px), Hick's Law, and Miller's Cognitive Rule.
2. Micro-Interaction Synthesizer generates Framer Motion spring physics and Tailwind CSS v4 classes.
3. Scroll Dynamics Engine outputs CSS Scroll-Driven Timelines and React Intersection Observer hooks.
"""
import pytest
from src.ux_psychology_and_micro_interactions import ux_interaction_engine


def test_ux_psychology_auditor_enforces_design_laws():
    """Verify Fitts's Law, Hick's Law, and cognitive load compliance."""
    # Compliant button
    audit_pass = ux_interaction_engine.audit_component_psychology(element_size_px=48, options_count=4, nested_depth=1)
    assert audit_pass.fitts_law_compliant is True
    assert audit_pass.hicks_law_score >= 0.70
    assert audit_pass.cognitive_load_index <= 0.60
    assert audit_pass.is_psychology_optimized is True

    # Tiny button violation (32px < 44px)
    audit_fail = ux_interaction_engine.audit_component_psychology(element_size_px=32, options_count=12, nested_depth=4)
    assert audit_fail.fitts_law_compliant is False
    assert len(audit_fail.recommendations) >= 2


def test_micro_interaction_synthesizer_generates_framer_motion_and_css():
    """Verify spring physics and Framer Motion micro-interaction props."""
    preset = ux_interaction_engine.get_micro_interaction("magnetic_spring_card")

    assert preset.name == "Magnetic Spring Card"
    assert "transition-all" in preset.css_classes
    assert "hover:shadow-2xl" in preset.css_classes
    assert "stiffness" in preset.physics_spring
    assert preset.physics_spring["stiffness"] == 400.0
    assert "whileHover" in preset.framer_motion_props


def test_scroll_dynamics_contract_generation():
    """Verify scroll-driven timeline CSS and React intersection hook generation."""
    contract = ux_interaction_engine.get_scroll_interaction_contract("parallax_glass_entry")

    assert contract.threshold == 0.15
    assert "@keyframes" in contract.css_scroll_timeline
    assert "IntersectionObserver" in contract.react_hook_code
    assert "useScrollFadeIn" in contract.react_hook_code
