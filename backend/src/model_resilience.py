"""Adapts system behavior based on model quality tier."""
from src.model_quality import get_tier, get_cached_tier
from src.utils import logger

TIER_CONFIG = {
    "high": {
        "description": "Full intelligence. All features active.",
        "prompt_complexity": "rich",
        "verification_threshold": 0.95,
        "max_retries": 1,
        "trust_llm_narratives": True,
        "use_detailed_prompts": True,
        "grounding_strictness": "strict",
        "delegation_preference": ["knowledge_graph", "distilled", "rag", "llm"],
        "learning_rate": 1.0,
    },
    "mid": {
        "description": "Standard mode. Some nuances may be missed.",
        "prompt_complexity": "standard",
        "verification_threshold": 0.85,
        "max_retries": 2,
        "trust_llm_narratives": True,
        "use_detailed_prompts": True,
        "grounding_strictness": "moderate",
        "delegation_preference": ["knowledge_graph", "distilled", "rag", "llm"],
        "learning_rate": 0.8,
    },
    "low": {
        "description": "Deterministic fallbacks active for safety.",
        "prompt_complexity": "minimal",
        "verification_threshold": 0.70,
        "max_retries": 3,
        "trust_llm_narratives": False,
        "use_detailed_prompts": False,
        "grounding_strictness": "strict",
        "delegation_preference": ["knowledge_graph", "distilled", "rag", "rule_fallback", "llm"],
        "learning_rate": 0.5,
    }
}

PROMPT_TEMPLATES = {
    "high": {
        "cp2_system": (
            "You are a senior data scientist. Analyze each column deeply. "
            "Infer semantic types, business context, and suggest cleaning strategies. "
            "Return rich JSON with nuanced explanations."
        ),
        "cp3_system": (
            "Propose creative, dataset-specific cleaning steps. Consider cross-column "
            "logic, business rules, and edge cases. Explain your reasoning."
        ),
        "narrative_system": (
            "Write an insightful executive summary highlighting strategic implications, "
            "key findings, and actionable recommendations."
        ),
        "critic_system": (
            "Identify subtle cross-column logic violations, mathematical inconsistencies, "
            "and business rule violations that basic checks would miss."
        )
    },
    "mid": {
        "cp2_system": (
            "You are a data analyst. Describe each column's purpose and suggest cleaning. "
            "Return valid JSON with semantic types."
        ),
        "cp3_system": (
            "Propose standard cleaning steps for this dataset. Return valid JSON."
        ),
        "narrative_system": (
            "Summarize the data in 2-3 clear sentences."
        ),
        "critic_system": (
            "Check for obvious data quality issues: nulls, duplicates, outliers."
        )
    },
    "low": {
        "cp2_system": (
            "Output ONLY valid JSON: {'name': str, 'semantic_type': str}. No explanation."
        ),
        "cp3_system": (
            "Output ONLY valid JSON array of cleaning steps. Minimal."
        ),
        "narrative_system": (
            "Write one sentence summary."
        ),
        "critic_system": (
            "List obvious issues only. Output JSON."
        )
    }
}


def get_config():
    tier = get_tier()
    return TIER_CONFIG.get(tier, TIER_CONFIG["mid"])


def get_prompt_template(template_name):
    tier = get_tier()
    templates = PROMPT_TEMPLATES.get(tier, PROMPT_TEMPLATES["mid"])
    return templates.get(template_name, PROMPT_TEMPLATES["mid"].get(template_name, ""))


def should_trust_llm_output():
    return get_config().get("trust_llm_narratives", True)


def get_verification_threshold():
    return get_config().get("verification_threshold", 0.85)


def get_delegation_order():
    return get_config().get("delegation_preference", ["knowledge_graph", "distilled", "rag", "llm"])


def get_learning_rate():
    return get_config().get("learning_rate", 0.8)
