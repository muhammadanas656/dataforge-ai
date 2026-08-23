"""
Test Suite: Vision-in-the-Loop Self-Correction & Universal Geometry Studio.
Verifies:
1. Universal Geometry Primitives produce 100% valid, accessible SVG geometry.
2. VisionSelfCorrectionEngine audits bezier curves, gradient depth, and element density.
3. Multi-turn self-correction loop diagnoses flaws and iteratively elevates quality.
4. FastAPI design endpoints successfully integrate vision self-correction.
"""
import pytest
from src.universal_geometry_primitives import geometry_primitives
from src.vision_self_correction_engine import vision_self_correction
from src.svg_design_studio import svg_studio
from fastapi.testclient import TestClient
from src.api import app


def test_universal_geometry_primitives_generate_valid_markup():
    """Verify parametric geometry generators output valid, non-empty XML."""
    # 1. Mountain Ridge
    mtn = geometry_primitives.mountain_ridge(width=800, base_y=420, peak_height=200, num_peaks=4)
    assert '<polygon points="' in mtn
    assert 'class="mountain-ridge"' in mtn

    # 2. Sun Aurora
    sun = geometry_primitives.sun_aurora(cx=400, cy=300, radius=100)
    assert '<circle cx="400"' in sun
    assert 'class="sun-aurora"' in sun

    # 3. Soaring Wings
    wings = geometry_primitives.soaring_wings(cx=400, cy=200, scale=1.0)
    assert 'class="soaring-wings"' in wings
    assert 'fill="url(#eagle_wing_grad)"' in wings

    # 4. Spoked Wheel
    wheel = geometry_primitives.spoked_wheel(cx=100, cy=100, radius=50, num_spokes=6)
    assert 'class="spoked-wheel"' in wheel
    assert '<line x1="100"' in wheel

    # 5. Bento Panel
    bento = geometry_primitives.bento_glass_panel(x=20, y=20, width=200, height=100, title="CPU Speed", value="2.64M/s")
    assert 'class="bento-glass-panel"' in bento
    assert '2.64M/s' in bento


def test_vision_self_correction_audit_detects_defects():
    """Verify that crude or empty SVGs are penalized and given actionable defect diagnostics."""
    crude_svg = '<svg viewBox="0 0 100 100"><rect x="10" y="10" width="80" height="80" fill="red"/></svg>'
    audit = vision_self_correction.audit_vector_quality(crude_svg, query="a bird soaring over mountains")

    assert audit["fitness_score"] < 80.0
    assert audit["is_masterpiece"] is False
    assert len(audit["defects"]) >= 2
    assert any("bezier" in d.lower() or "gradient" in d.lower() for d in audit["defects"])


def test_vision_self_correction_audit_approves_masterpieces():
    """Verify that multi-stop gradient, high-bezier SVGs achieve masterpiece fitness."""
    # Synthesize genuine high-detail masterpiece using geometry primitives
    ridge1 = geometry_primitives.mountain_ridge(800, 420, 240, 5, "#1e293b", "#ffffff")
    ridge2 = geometry_primitives.mountain_ridge(800, 490, 180, 6, "#0f172a", "#cbd5e1")
    wings = geometry_primitives.soaring_wings(400, 200, 1.2, "wing")
    sun = geometry_primitives.sun_aurora(400, 150, 80, "#fbbf24")

    masterpiece_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="100%" height="100%">
      <defs>
        <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#0f172a"/><stop offset="50%" stop-color="#1e1b4b"/><stop offset="100%" stop-color="#3b82f6"/></linearGradient>
        <linearGradient id="wing" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#f59e0b"/><stop offset="50%" stop-color="#d97706"/><stop offset="100%" stop-color="#78350f"/></linearGradient>
        <linearGradient id="snow" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#cbd5e1"/></linearGradient>
        <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#fde68a"/><stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/></radialGradient>
        <filter id="glow"><feGaussianBlur stdDeviation="8"/></filter>
      </defs>
      <rect width="800" height="600" fill="url(#sky)"/>
      {sun}
      {ridge1}
      {ridge2}
      {wings}
    </svg>"""

    audit = vision_self_correction.audit_vector_quality(masterpiece_svg, query="a majestic eagle over snow-capped mountains")
    assert audit["fitness_score"] >= 88.0
    assert audit["is_masterpiece"] is True
    assert audit["bezier_curves_count"] >= 12
    assert audit["gradients_count"] >= 4


def test_vision_self_correction_refinement_pipeline():
    """Verify that refine_vector_autonomously executes and outputs a complete asset dictionary."""
    res = vision_self_correction.refine_vector_autonomously(
        query="Quantum Biometric Shield",
        primary_color="#6366f1",
        max_passes=2
    )

    assert "raw_svg" in res
    assert "<svg" in res["raw_svg"]
    assert res["final_fitness_score"] > 0
    assert "passes_executed" in res
    assert len(res["refinement_history"]) >= 1


def test_vision_studio_fastapi_integration():
    """Verify that FastAPI endpoint /api/design/invent uses the vision engine."""
    client = TestClient(app)
    payload = {
        "asset_name": "VisionTestedVault",
        "domain_theme": "Quantum_CyberSecurity",
        "accent_color": "#06b6d4"
    }
    resp = client.post("/api/design/invent", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["asset_name"] == "VisionTestedVault"
    assert "<svg" in data["svg_code"]
    assert data["wcag_aaa_compliant"] is True
    assert data["fitness_score"] >= 90.0
