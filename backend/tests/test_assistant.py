import pytest
from src.context_manager import context_manager
from src.assistant_rag import assistant_rag
from src.assistant_engine import assistant_engine

def test_context_manager_lifecycle():
    session_id = "test_sess_001"
    context_manager.update_context(
        session_id=session_id,
        active_module="eda",
        active_dataset_id="test_ds",
        action="causal_analysis"
    )
    ctx = context_manager.get_context(session_id)
    assert ctx.active_module == "eda"
    assert ctx.active_dataset_id == "test_ds"
    assert len(ctx.recent_actions) > 0
    assert ctx.skill_level in ["beginner", "intermediate", "advanced"]

def test_assistant_rag_retrieval():
    res = assistant_rag.retrieve("How does the TRIZ invention engine work?", collection="docs")
    assert len(res) > 0
    assert any("triz" in r["content"].lower() or "invention" in r["content"].lower() for r in res)

def test_assistant_engine_intent_routing():
    intent = assistant_engine._route_intent("Why did step 4 fail with an error?")
    assert intent["type"] == "debug"
    
    intent_exp = assistant_engine._route_intent("Explain what causal DAG inference means")
    assert intent_exp["type"] == "explain"
