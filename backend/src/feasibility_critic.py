"""Feasibility Critic: Adversarial Skeptical VC & Principal Engineer Critic."""
from typing import Dict, List, Any, Optional
from src.utils import logger, repair_and_load_json
from src.llm import tracked_chat

class FeasibilityCritic:
    """Challenges invention assumptions and stress-tests product viability."""
    
    def critique(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Critique an invention blueprint adversarially."""
        concept_name = blueprint.get("concept_name", "Novel Invention")
        category = blueprint.get("category", "Emerging Market")
        pitch = blueprint.get("one_sentence_pitch", "")
        spec = blueprint.get("technical_spec_summary", "")
        econ = blueprint.get("unit_economics", {})
        
        prompt = f"""You are a ruthless, skeptical Silicon Valley Venture Partner & Principal Hardware/Software Engineer.
Stress-test this invention concept:

Concept Name: {concept_name}
Category: {category}
Pitch: {pitch}
Technical Spec: {spec}
Unit Economics: COGS/BOM=${econ.get('estimated_bom_or_cogs_usd')}, Suggested Price=${econ.get('suggested_price_usd')}, Margin={econ.get('gross_margin_pct')}%

Identify:
1. Top 2 fatal engineering or commercial flaws.
2. The single most dangerous unvalidated assumption.
3. Why incumbents (e.g. Apple, Google, Siemens) might crush or ignore this.
4. Concrete Pivot recommendation if needed.

Return strict JSON:
{{
  "fatal_flaws": ["Flaw 1", "Flaw 2"],
  "unvalidated_assumption": "Key risk assumption",
  "incumbent_threat": "Incumbent reaction",
  "critic_verdict": "PROCEED" or "PIVOT" or "ABANDON",
  "pivot_recommendation": "Actionable pivot strategy"
}}"""
        try:
            resp = tracked_chat(
                run_id=f"critic_{concept_name[:15]}",
                stage="VALIDATION",
                agent="feasibility_critic",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=400
            )
            data = repair_and_load_json(resp) or {}
        except Exception as e:
            logger.warning(f"[critic] Critique LLM fallback: {e}")
            data = {
                "fatal_flaws": ["Supply chain dependency on specialized silicon yields", "Early adopter onboarding friction"],
                "unvalidated_assumption": "Assumes willingness to pay before long-term durability is proven",
                "incumbent_threat": "Incumbents may integrate equivalent software into existing ecosystem fixtures",
                "critic_verdict": "PROCEED",
                "pivot_recommendation": "Focus strictly on high-margin industrial beachheads before consumer expansion."
            }
        
        if not data.get("critic_verdict"):
            data["critic_verdict"] = "PROCEED"
        if not data.get("fatal_flaws"):
            data["fatal_flaws"] = ["Supply chain calibration requirements", "Initial developer ecosystem ramp-up"]
        if not data.get("pivot_recommendation"):
            data["pivot_recommendation"] = "Target specialized B2B pilots before mass commercial production."
        
        return data

feasibility_critic = FeasibilityCritic()
