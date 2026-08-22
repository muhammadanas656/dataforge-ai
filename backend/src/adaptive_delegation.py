"""Adaptive Delegation Router: Decides whether to use internal knowledge or consult LLM."""
import os
from src.distillation_engine import distiller
from src.knowledge_graph import knowledge
from src.rag_cache import rag
from src.utils import logger

SETTINGS = {
    "knowledge_graph_min_confidence": 0.75,
    "distilled_model_min_confidence": 0.70,
    "rag_cache_enabled": True,
    "llm_fallback_enabled": True,
}


def delegate(task_type, input_data, context=None, run_id="unknown"):
    """
    Order of preference:
    1. Knowledge Graph (accumulated cross-dataset patterns)
    2. Distilled Local Model (trained RandomForest classifier)
    3. RAG Cache (exact past LLM responses)
    4. LLM Needed (teacher consultant)
    """
    context = context or {}

    # 1. Knowledge Graph
    if task_type == "semantic_type":
        col_name = input_data.get("name", "") if isinstance(input_data, dict) else str(input_data)
        kg_result = knowledge.get_column_semantic(col_name)
        if kg_result and kg_result["confidence"] >= SETTINGS["knowledge_graph_min_confidence"]:
            logger.info(f"[delegate] Knowledge Graph hit for '{col_name}': {kg_result['semantic_type']}")
            return kg_result["semantic_type"], "knowledge_graph", kg_result["confidence"]

    # 2. Distilled Model
    distilled_result, distilled_confidence = distiller.predict(task_type, input_data)
    if distilled_result is not None and distilled_confidence >= SETTINGS["distilled_model_min_confidence"]:
        logger.info(f"[delegate] Distilled model hit for {task_type}: {distilled_result} ({distilled_confidence:.2f})")
        return distilled_result, "distilled_model", distilled_confidence

    # 3. RAG Cache
    if SETTINGS["rag_cache_enabled"]:
        cache_key = f"{task_type}:{str(input_data)[:100]}"
        cached = rag.lookup(cache_key)
        if cached:
            logger.info(f"[delegate] RAG cache hit for {task_type}")
            return cached, "rag_cache", 0.9

    # 4. LLM Consultation
    if SETTINGS["llm_fallback_enabled"]:
        return None, "llm_needed", 0.0

    return None, "no_source", 0.0


def learn_from_interaction(task_type, input_data, output_data, source="llm", confidence=1.0):
    """After any successful task execution, record and compound intelligence."""
    try:
        # Record for distillation training
        distiller.record(task_type, input_data, output_data, confidence)

        # Update knowledge graph
        if task_type == "semantic_type":
            col_name = input_data.get("name", "") if isinstance(input_data, dict) else str(input_data)
            domain = input_data.get("domain") if isinstance(input_data, dict) else None
            knowledge.add_column_semantic(col_name, str(output_data), domain, confidence)

        # Cache in RAG
        cache_key = f"{task_type}:{str(input_data)[:100]}"
        rag.store(cache_key, output_data)

        # Index in Semantic Vector Memory
        try:
            from src.semantic_memory import index_column_signature, index_learning_event
            if task_type == "semantic_type":
                col_name = input_data.get("name", "") if isinstance(input_data, dict) else str(input_data)
                domain = input_data.get("domain") if isinstance(input_data, dict) else None
                index_column_signature(col_name, str(output_data), domain)
            else:
                index_learning_event(task_type, str(input_data)[:100], output_data)
        except Exception as vec_err:
            logger.warning(f"[learn] Semantic vector index error: {vec_err}")

        logger.info(f"[learn] Recorded {task_type} from {source} (confidence={confidence:.2f})")
    except Exception as e:
        logger.warning(f"[learn] Error recording interaction: {e}")


def get_delegation_stats():
    return {
        "distillation": distiller.get_stats(),
        "knowledge_graph": knowledge.stats(),
        "settings": SETTINGS
    }
