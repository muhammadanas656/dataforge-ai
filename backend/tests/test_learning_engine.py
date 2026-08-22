import pytest
from src.distillation_engine import DistillationEngine
from src.knowledge_graph import KnowledgeGraph
from src.adaptive_delegation import delegate, learn_from_interaction


def test_distillation_records_and_trains(tmp_path):
    engine = DistillationEngine(str(tmp_path / "distill"))

    # Record 15 diverse examples to trigger local model training
    for i in range(8):
        engine.record(
            "semantic_type",
            {"name": f"price_{i}", "dtype": "float64", "samples": [10, 20]},
            "currency"
        )
    for i in range(8):
        engine.record(
            "semantic_type",
            {"name": f"category_{i}", "dtype": "object", "samples": ["electronics", "clothing"]},
            "categorical"
        )

    # Should have trained classifier
    assert "semantic_type" in engine.models

    # Should predict
    result, confidence = engine.predict(
        "semantic_type",
        {"name": "unit_price", "dtype": "float64", "samples": [15, 25]}
    )
    assert result in ["currency", "categorical"]
    assert confidence > 0.4


def test_knowledge_graph_learns_columns(tmp_path):
    kg = KnowledgeGraph(str(tmp_path / "kg.json"))

    kg.add_column_semantic("price", "currency", domain="ecommerce")
    kg.add_column_semantic("price", "currency", domain="retail")
    kg.add_column_semantic("price", "numeric_continuous", domain="science")

    result = kg.get_column_semantic("price")
    assert result["semantic_type"] == "currency"
    assert result["confidence"] > 0.5
    assert result["observations"] == 3


def test_delegation_uses_knowledge_graph(tmp_path, monkeypatch):
    kg = KnowledgeGraph(str(tmp_path / "kg.json"))
    for _ in range(10):
        kg.add_column_semantic("price", "currency", confidence=1.0)

    monkeypatch.setattr("src.adaptive_delegation.knowledge", kg)

    result, source, confidence = delegate("semantic_type", {"name": "price"})
    assert result == "currency"
    assert source == "knowledge_graph"
    assert confidence > 0.7


def test_learning_flow():
    from src.distillation_engine import distiller

    initial_count = len(distiller.examples.get("test_task", []))
    learn_from_interaction("test_task", {"input": "test"}, "output", source="llm")
    assert len(distiller.examples["test_task"]) == initial_count + 1
