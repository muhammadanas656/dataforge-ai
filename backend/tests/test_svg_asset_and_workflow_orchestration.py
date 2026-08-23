"""
SVG Asset Studio & Cross-Studio Workflow Orchestration Test Suite.
Verifies:
1. SVG Studio audits security (XSS scripts), accessibility (a11y), and viewBox scalability.
2. SVG Studio synthesizes React JSX, Tailwind, and Vue 3 vector component code from natural language queries.
3. SVG Studio extracts vector assets and icon symbols from raw web HTML.
4. StudioOrchestrator chains multi-studio pipelines across Tabular, Web & Design, and Strategic Invention.
5. Copilot executes SVG generation and workflow tools via AssistantEngine.
"""
import pytest
from src.svg_design_studio import svg_studio
from src.studio_orchestrator import studio_orchestrator
from src.assistant_engine import assistant_engine


# =====================================================================
# 1. SVG ASSET STUDIO & VECTOR SECURITY
# =====================================================================

def test_svg_auditor_detects_malicious_scripts_and_xss():
    """Verify SVG auditor catches XSS injections inside SVG files."""
    malicious_svg = """
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <script>alert('XSS Attack!')</script>
      <circle cx="12" cy="12" r="10" onerror="alert(1)"/>
    </svg>
    """
    res = svg_studio.audit_svg(malicious_svg)
    assert res["valid"] is True
    assert res["security_status"] == "Malicious / XSS Detected"
    assert "<script" not in res["sanitized_svg"]
    assert res["overall_quality_score"] < 60


def test_svg_auditor_checks_viewbox_and_accessibility():
    """Verify SVG auditor grades viewBox and screen-reader accessibility."""
    clean_accessible_svg = """
    <svg viewBox="0 0 24 24" role="img" aria-label="Cloud Security Shield" xmlns="http://www.w3.org/2000/svg">
      <title>Cloud Security Shield</title>
      <path d="M12 2L3 7v6c0 5 9 9 9 9s9-4 9-9V7l-9-5z"/>
    </svg>
    """
    res = svg_studio.audit_svg(clean_accessible_svg)
    assert res["security_status"] == "Clean"
    assert res["accessibility"] == "Optimal"
    assert res["has_viewbox"] is True
    assert res["overall_quality_score"] >= 90


def test_svg_generator_creates_react_and_vue_components():
    """Verify SVG generator creates typed React JSX and Vue 3 component code."""
    res = svg_studio.generate_vector_asset("data pipeline telemetry node", primary_color="#06b6d4")
    assert "raw_svg" in res
    assert "react_jsx" in res
    assert "export function" in res["react_jsx"]
    assert "strokeWidth" in res["react_jsx"]  # React camelCase JSX
    assert "vue_component" in res
    assert "<template>" in res["vue_component"]
    assert res["audit"]["security_status"] == "Clean"


def test_svg_extractor_isolates_svgs_from_html():
    """Verify SVG studio extracts and audits vector assets from web HTML."""
    sample_html = """
    <html>
      <body>
        <nav>
          <svg viewBox="0 0 24 24"><title>Nav Brand</title><circle cx="12" cy="12" r="8"/></svg>
        </nav>
        <main>
          <svg viewBox="0 0 100 100"><path d="M10 10 H 90 V 90 H 10 Z"/></svg>
        </main>
      </body>
    </html>
    """
    res = svg_studio.extract_svgs_from_html(sample_html, source_url="https://app-design.io")
    assert res["total_svgs_found"] == 2
    assert len(res["assets"]) == 2
    assert res["assets"][0]["name"] == "Nav Brand"
    assert "react_component" in res["assets"][0]


# =====================================================================
# 2. CROSS-STUDIO WORKFLOW ORCHESTRATION
# =====================================================================

@pytest.mark.asyncio
async def test_studio_orchestrator_chains_multi_studio_pipeline():
    """Verify StudioOrchestrator executes steps sequentially across Web and Invention studios."""
    workflow = [
        {"studio": "web", "action": "generate_svg", "input_data": {"query": "security shield"}, "output_key": "shield_icon"},
        {"studio": "invention", "action": "resolve_triz", "input_data": {"improving_param": "speed", "worsening_param": "complexity"}, "output_key": "triz_plan"},
        {"studio": "invention", "action": "simulate_risk", "input_data": {"base_growth": 0.25, "volatility": 0.10}, "output_key": "risk_model"}
    ]
    res = await studio_orchestrator.execute_workflow(workflow)
    assert res["status"] == "completed"
    assert res["total_steps"] == 3
    assert "shield_icon" in res["results"]
    assert "triz_plan" in res["results"]
    assert "risk_model" in res["results"]
    assert res["results"]["risk_model"]["probability_of_profit"] > 0.5


# =====================================================================
# 3. COPILOT TOOL INTEGRATION
# =====================================================================

def test_copilot_executes_svg_and_workflow_tools():
    """Verify AssistantEngine dispatches named tools for SVG generation and auditing."""
    res_gen = assistant_engine.execute_named_tool("generate_svg_asset", {"query": "neural network graph"})
    assert res_gen["status"] == "success"
    assert "Custom Vector Icon" in res_gen["response"] or "Component Generated" in res_gen["response"]

    clean_svg = "<svg viewBox='0 0 24 24'><title>Icon</title><path d='M12 2L2 22h20L12 2z'/></svg>"
    res_audit = assistant_engine.execute_named_tool("audit_svg", {"svg_code": clean_svg})
    assert res_audit["status"] == "success"
    assert "Quality Score" in res_audit["response"]
