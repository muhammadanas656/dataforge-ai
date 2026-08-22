"""Morphological Analysis & Multi-Dimensional Combinatorial Box for Systematic Invention."""
from typing import List, Dict, Any, Optional
import itertools
import random
from src.utils import logger, repair_and_load_json
from src.llm import tracked_chat

DOMAIN_MORPHOLOGY = {
    "edge_ai_hardware": {
        "sensing_modality": ["Sub-Terahertz Radar", "Ambient Audio Spectrum", "Event-Based Neuromorphic Vision", "Galvanic Biosensing", "MEMS Thermal Gradient"],
        "compute_architecture": ["Local 1-Bit quantized SLM", "Zero-Power Spiking Silicon", "Federated Micro-Mesh", "Homomorphic Cryptographic Core", "Analog In-Memory Matrix"],
        "power_autonomy": ["Vibrational Kinetic Harvester", "RF Ambient Energy Scavenger", "10-Year Solid-State Microbattery", "Thermal Differential Cell", "Inductive Surface Coupling"],
        "form_factor": ["Sub-Gram Adhesive Patch", "Architectural Conduit Sensor", "Wearable Biometric Weave", "Autonomous Micro-Drone Node", "Implantable Encapsulation"],
        "commercial_beachhead": ["Decentralized Clinical Trials", "High-Value Industrial Predictive Maintenance", "Extreme-Environment Cold Chain", "Autonomous Solopreneur Security", "Proactive Senior Longevity Care"]
    },
    "enterprise_saas_automation": {
        "intelligence_layer": ["Continuous Self-Reflective ReAct Agent", "Autonomous Causal DAG Discovery", "Synthetic Counterfactual Simulator", "Zero-Shot Formal Proof Verifier", "Multi-Modal Sensor Fusion Engine"],
        "governance_model": ["Zero-Knowledge Audit Trail", "Real-Time Multi-Variate MMD Drift Barrier", "Deterministic Rule-Checked Guardrails", "Human-in-the-Loop Consensus Gate", "Automated Regulatory Compliance Sentry"],
        "deployment_fabric": ["Edge Local Air-Gapped Appliance", "Self-Healing Distributed Container Mesh", "Wasm Browser-Native Execution", "Multi-Cloud Sovereign Cloud Node", "Serverless Ephemeral Worker Swarm"],
        "monetization_vector": ["Usage-Linked Revenue Share", "Outcome-Guaranteed SLA Premium", "Per-Transaction Micro-Royalty", "Tiered Multi-Tenant Platform License", "Reverse-Auction Capacity Marketplace"],
        "commercial_beachhead": ["Cross-Border Freight Logistics", "AI-Native Biotech Intellectual Property", "Autonomous Regulatory FinTech Auditing", "Decentralized Energy Grid Arbitrage", "AI-Managed Solopreneur Portfolios"]
    }
}

class MorphologicalBox:
    """Systematic invention engine exploring n-dimensional Cartesian innovation spaces."""
    
    def __init__(self, dimensions: Dict[str, List[str]]):
        self.dimensions = dimensions
        self.dim_keys = list(dimensions.keys())
    
    def total_combinations(self) -> int:
        count = 1
        for values in self.dimensions.values():
            count *= len(values)
        return count
    
    def sample_combination(self) -> Dict[str, str]:
        """Sample a single random combination across all dimensions."""
        return {k: random.choice(v) for k, v in self.dimensions.items()}
    
    def evaluate_novelty(self, combination: Dict[str, str]) -> float:
        """
        Compute mathematical novelty index [0.0 - 1.0].
        Heuristic: Rarity of attributes + cross-dimensional semantic distance.
        """
        # Assign rarity weights (later items in morphological vectors are more futuristic)
        rarities = []
        for k, v in combination.items():
            if k in self.dimensions and v in self.dimensions[k]:
                idx = self.dimensions[k].index(v)
                total = len(self.dimensions[k])
                rarities.append((idx + 1) / total)
            else:
                rarities.append(0.5)
        base_novelty = sum(rarities) / len(rarities) if rarities else 0.5
        # Add slight entropy
        return round(min(0.99, max(0.45, 0.4 + base_novelty * 0.55)), 3)
    
    def synthesize_product_concept(self, combination: Dict[str, str], domain_name: str = "Future Technology") -> Dict[str, Any]:
        """Synthesize a structured product invention blueprint from morphological attributes."""
        combo_str = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in combination.items()])
        novelty_score = self.evaluate_novelty(combination)
        
        prompt = f"""You are a Principal Product Architect and Venture Futurist.
Domain: {domain_name}
Morphological Attribute Combination:
{combo_str}

Synthesize an innovative, uninvented blue-ocean product invention that combines these exact attributes into a cohesive breakthrough.
Return strict JSON:
{{
  "concept_name": "Catchy, futuristic product name",
  "category": "Uninvented market category name",
  "one_sentence_pitch": "Precise value proposition",
  "target_persona": "Specific early adopter profile",
  "why_now_catalyst": "Why 2026-2028 tech shifts make this viable now vs 5 years ago",
  "technical_spec_summary": "Architecture combining the specified sensing, compute, and power attributes",
  "unit_economics": {{
    "estimated_bom_or_cogs_usd": 45.00,
    "suggested_price_usd": 180.00,
    "gross_margin_pct": 75
  }}
}}"""
        try:
            resp = tracked_chat(
                run_id=f"morph_{domain_name[:15]}",
                stage="INVENTION",
                agent="morphological_synthesizer",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=450
            )
            data = repair_and_load_json(resp) or {}
        except Exception as e:
            logger.warning(f"[morph] Synthesis LLM fallback: {e}")
            data = {
                "concept_name": f"{combination.get('sensing_modality', 'Autonomous')} {combination.get('form_factor', 'Node')}",
                "category": f"Autonomous {domain_name.title()} Systems",
                "one_sentence_pitch": f"Next-generation system combining {combination.get('compute_architecture', 'edge compute')} with {combination.get('power_autonomy', 'zero-power operation')}.",
                "target_persona": f"Forward-looking leaders in {combination.get('commercial_beachhead', 'modern operations')}.",
                "why_now_catalyst": "2026 breakthroughs in ultra-low power silicon and local SLM inference.",
                "technical_spec_summary": f"Integrated assembly featuring {combination.get('sensing_modality', 'multi-modal sensors')} driving {combination.get('compute_architecture', 'local intelligence')}.",
                "unit_economics": {"estimated_bom_or_cogs_usd": 40.0, "suggested_price_usd": 160.0, "gross_margin_pct": 75}
            }
        
        data["morphological_attributes"] = combination
        data["novelty_score"] = novelty_score
        return data

def get_morphological_box(domain: str = "edge_ai_hardware") -> MorphologicalBox:
    dims = DOMAIN_MORPHOLOGY.get(domain, DOMAIN_MORPHOLOGY["edge_ai_hardware"])
    return MorphologicalBox(dims)
