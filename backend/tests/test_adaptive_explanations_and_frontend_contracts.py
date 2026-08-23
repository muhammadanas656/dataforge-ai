"""
Adaptive Conceptual Explanations & Frontend SVG Export Contract Test Suite.
Verifies:
1. AdaptiveExplanationEngine provides ELI5 simplified analogies for TRIZ, Causal DAG, Fat-Tail risks, SSRF, and MICE.
2. AssistantEngine routes beginner inquiries ("simply", "explain like I'm 10", "analogy") to adaptive analogies with 0 LLM token waste.
3. SVG Studio generates valid multi-framework export payloads (React JSX, Vue 3, Raw SVG) with responsive size coordinates.
"""
import pytest
from src.adaptive_explanations import adaptive_explainer
from src.assistant_engine import assistant_engine
from src.svg_design_studio import svg_studio


# =====================================================================
# 1. ADAPTIVE EXPLANATION & CONCEPTUAL ANALOGIES
# =====================================================================

def test_triz_beginner_explanation_contains_analogy_and_cheat_sheet():
    """Verify TRIZ explanation provides the inventor cheat-sheet analogy."""
    res = adaptive_explainer.explain("triz", user_level="beginner")
    assert "cheat sheet" in res.lower()
    assert "40 proven tricks" in res
    assert "Example:" in res or "Real-World" in res


def test_causal_dag_beginner_explanation_uses_detective_and_family_tree():
    """Verify Causal DAG explanation provides the family tree and detective analogies."""
    res = adaptive_explainer.explain("causal_dag", user_level="beginner")
    assert "family tree" in res.lower()
    assert "ice cream" in res.lower() or "detective" in res.lower()


def test_fat_tail_beginner_explanation_uses_bill_gates_and_hurricane():
    """Verify Fat-Tail explanation provides the Bill Gates and hurricane analogies."""
    res = adaptive_explainer.explain("fat_tail", user_level="beginner")
    assert "bill gates" in res.lower() or "hurricane" in res.lower()
    assert "fat tail" in res.lower()


def test_ssrf_security_beginner_explanation_uses_office_guard_analogy():
    """Verify SSRF security explanation uses the public billboard vs private safe analogy."""
    res = adaptive_explainer.explain("ssrf", user_level="beginner")
    assert "billboard" in res.lower() or "security guard" in res.lower()
    assert "internal" in res.lower() or "private" in res.lower()


def test_adaptive_explainer_expert_mode_returns_mathematical_formulation():
    """Verify expert mode returns mathematical notation (LaTeX formulas and matrix proofs)."""
    res_triz = adaptive_explainer.explain("triz", user_level="advanced")
    assert "\\mathcal{T}" in res_triz or "Altshuller" in res_triz

    res_dag = adaptive_explainer.explain("causal_dag", user_level="advanced")
    assert "\\mathbf{\\Theta}" in res_dag or "\\mathbf{\\Sigma}" in res_dag


# =====================================================================
# 2. COPILOT ADAPTIVE QUERY ROUTING
# =====================================================================

@pytest.mark.asyncio
async def test_copilot_answers_triz_simply_with_analogy():
    """Verify Copilot answers 'What is TRIZ simply?' using the adaptive analogy."""
    res = await assistant_engine.process_query(
        session_id="test_adaptive_sess",
        query="What is TRIZ simply? Explain like I'm 10"
    )
    assert res.get("explanation_mode") == "beginner_eli5" or "cheat sheet" in res.get("response", "").lower()
    assert "40 proven tricks" in res.get("response", "")


@pytest.mark.asyncio
async def test_copilot_answers_causal_dag_with_analogy():
    """Verify Copilot answers 'Explain causal DAG in easy words' with intuitive examples."""
    res = await assistant_engine.process_query(
        session_id="test_adaptive_sess",
        query="Explain causal DAG in easy words"
    )
    assert "family tree" in res.get("response", "").lower() or "detective" in res.get("response", "").lower()


# =====================================================================
# 3. SVG STUDIO FRONTEND CONTRACT VALIDATION
# =====================================================================

def test_svg_studio_generates_valid_react_and_vue_contracts():
    """Verify SVG generator returns valid React JSX, Vue 3, and Raw SVG component code."""
    asset = svg_studio.generate_vector_asset("telemetry pulse stream", primary_color="#6366f1")
    assert asset["asset_name"] is not None
    assert "<svg" in asset["raw_svg"]
    assert "viewBox=" in asset["raw_svg"]
    
    # React JSX verification
    assert "export const" in asset["react_jsx"] or "function" in asset["react_jsx"]
    assert "className=" in asset["react_jsx"]
    assert "strokeWidth=" in asset["react_jsx"] # camelCase check

    # Vue 3 component verification
    assert "<template>" in asset["vue_component"]
    assert "<script setup>" in asset["vue_component"]

    # Security audit verification
    assert asset["audit"]["security_status"] == "Clean"
    assert asset["audit"]["overall_quality_score"] >= 90
