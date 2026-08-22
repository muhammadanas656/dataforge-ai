"""TRIZ (Theory of Inventive Problem Solving) Systematic Contradiction & Invention Engine."""
from typing import List, Dict, Any, Optional
import random
from src.utils import logger, repair_and_load_json
from src.llm import tracked_chat

TRIZ_PARAMETERS = {
    "speed": "Speed of operation, processing latency, or transaction throughput",
    "energy_efficiency": "Power consumption, battery drain, or thermal loss",
    "reliability": "Probability of failure-free uptime, data integrity, and precision",
    "adaptability": "Ability to adapt dynamically to shifting conditions or noisy inputs",
    "complexity": "Number of interrelated moving parts, dependencies, or algorithmic layers",
    "cost": "Manufacturing, computational token overhead, or operational cost",
    "autonomy": "Degree of zero-human-in-the-loop operation and automated recovery",
    "privacy": "Data sovereignty, local zero-leakage execution, and encryption",
    "personalization": "Tailored customization for unique individual or enterprise personas",
    "durability": "Longevity, resistance to model decay, or hardware wear-and-tear"
}

TRIZ_PRINCIPLES = {
    1: {"name": "Segmentation", "description": "Divide an object or system into independent sub-components or micro-agents."},
    2: {"name": "Taking Out", "description": "Extract the interfering, heavy, or sensitive part (e.g. cloud compute) and isolate locally."},
    3: {"name": "Local Quality", "description": "Transition from homogeneous to specialized structures where each part fulfills tailored functions."},
    10: {"name": "Prior Action", "description": "Perform required transformations in advance (e.g. pre-computed cached embeddings)."},
    13: {"name": "The Other Way Round", "description": "Invert the action or process (e.g. bring the model to data instead of data to model)."},
    15: {"name": "Dynamics", "description": "Make the object, prompt, or architecture continuously self-adjusting to real-time telemetry."},
    17: {"name": "Another Dimension", "description": "Move from single-vector to multi-dimensional tensor or spatial/temporal coordinates."},
    24: {"name": "Intermediary", "description": "Use an intermediate carrier agent, surrogate model, or distillation proxy."},
    28: {"name": "Mechanics Substitution", "description": "Replace brittle mechanical/static logic with sensory, probabilistic, or neural fields."},
    35: {"name": "Parameter Changes", "description": "Change physical/mathematical state (e.g. quantize FP32 to 2-bit or shift from batch to stream)."},
    40: {"name": "Composite Materials", "description": "Blend heterogeneous materials or algorithms into a single synergetic composite."}
}

CONTRADICTION_MATRIX = {
    "speed": {
        "reliability": [10, 28, 35],
        "cost": [1, 15, 17],
        "energy_efficiency": [2, 13, 28],
        "complexity": [1, 24, 35]
    },
    "reliability": {
        "complexity": [1, 3, 15],
        "cost": [10, 13, 28],
        "speed": [10, 24, 35]
    },
    "adaptability": {
        "complexity": [15, 17, 35],
        "reliability": [3, 28, 40],
        "cost": [1, 15, 35]
    },
    "privacy": {
        "personalization": [2, 17, 40],
        "adaptability": [1, 13, 35],
        "cost": [2, 24, 35]
    },
    "autonomy": {
        "reliability": [1, 10, 15],
        "complexity": [2, 24, 40],
        "cost": [10, 15, 28]
    }
}

class TRIZEngine:
    """Systematic invention engine applying classical and algorithmic TRIZ."""
    
    def get_parameters(self) -> Dict[str, str]:
        return TRIZ_PARAMETERS
    
    def identify_contradiction(self, improving_param: str, worsening_param: str) -> Dict[str, Any]:
        """Look up contradiction resolution principles."""
        imp = improving_param.lower()
        wors = worsening_param.lower()
        
        principles_ids = CONTRADICTION_MATRIX.get(imp, {}).get(wors, [1, 15, 35])
        principles = [
            {"id": pid, "name": TRIZ_PRINCIPLES[pid]["name"], "description": TRIZ_PRINCIPLES[pid]["description"]}
            for pid in principles_ids if pid in TRIZ_PRINCIPLES
        ]
        
        return {
            "improving": imp,
            "worsening": wors,
            "contradiction_statement": f"Improving '{imp}' inherently worsens or strains '{wors}'.",
            "principles": principles,
            "principle_ids": principles_ids
        }
    
    def resolve_contradiction(self, improving_param: str, worsening_param: str, domain: str, context: str = "") -> Dict[str, Any]:
        """Apply TRIZ principles to invent an engineering and product breakthrough."""
        contra = self.identify_contradiction(improving_param, worsening_param)
        top_principle = contra["principles"][0] if contra["principles"] else {"id": 1, "name": "Segmentation", "description": "Divide system"}
        
        prompt = f"""You are a Master TRIZ Inventive Engineer.
Domain: {domain}
Context: {context}
Technical Contradiction: Improving '{improving_param}' strains '{worsening_param}'.
Selected TRIZ Principle #{top_principle.get('id')}: {top_principle.get('name')} ({top_principle.get('description')})

Invent a novel, concrete product or architectural mechanism that resolves this exact contradiction.
Return strict JSON:
{{
  "mechanism_name": "Short creative invention name",
  "inventive_breakthrough": "2-3 sentences detailing how the TRIZ principle eliminates the trade-off",
  "defensibility_moat": "Why competitors cannot easily replicate this without this architecture",
  "target_application": "Concrete commercial or industrial use case"
}}"""
        try:
            resp = tracked_chat(
                run_id=f"triz_{improving_param}_{worsening_param}"[:30],
                stage="INVENTION",
                agent="triz_solver",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=350
            )
            data = repair_and_load_json(resp) or {}
        except Exception as e:
            logger.warning(f"[triz] Resolution LLM fallback: {e}")
            data = {
                "mechanism_name": f"Adaptive {top_principle.get('name')} Core for {domain}",
                "inventive_breakthrough": f"Applies TRIZ Principle #{top_principle.get('id')} ({top_principle.get('name')}) to dynamically decouple {improving_param} from {worsening_param} using an intermediate micro-dispatch layer.",
                "defensibility_moat": "Proprietary algorithmic dispatch topology and low-latency state caching.",
                "target_application": f"High-throughput enterprise {domain} operations."
            }
        
        return {
            "contradiction": contra,
            "applied_principle": top_principle,
            "invention": data
        }

triz_engine = TRIZEngine()
