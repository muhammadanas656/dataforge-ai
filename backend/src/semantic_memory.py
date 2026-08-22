"""Semantic search layer over the pluggable Vector Store."""
from src.vector_store import vector_store


def index_column_signature(col_name, semantic_type, domain=None):
    """Index a learned column meaning for future semantic retrieval."""
    if not col_name:
        return
    doc_id = f"col::{(domain or 'generic').lower()}::{col_name.lower()}"
    text = f"{col_name} {semantic_type} {domain or 'generic'}"
    vector_store.add(doc_id, text, metadata={
        "column": col_name,
        "semantic_type": semantic_type,
        "domain": domain or "generic"
    })


def index_learning_event(task_type, input_summary, output):
    """Index distillation/learning events for cross-dataset retrieval."""
    doc_id = f"learn::{task_type}::{hash(input_summary) & 0xFFFFFFFF}"
    text = f"{task_type} {input_summary} {output}"
    vector_store.add(doc_id, text, metadata={
        "task_type": task_type,
        "output": str(output)
    })


def find_similar(query_text, top_k=5):
    """Semantic similarity search across all indexed knowledge."""
    return vector_store.query(query_text, top_k=top_k)
