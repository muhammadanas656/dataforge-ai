import time
import numpy as np
from src.vector_store import LocalJsonVectorStore, embed_text


def test_embed_deterministic_and_normalized():
    a = embed_text("price currency numeric")
    b = embed_text("price currency numeric")
    assert np.allclose(a, b)
    assert abs(np.linalg.norm(a) - 1.0) < 1e-5


def test_local_store_add_query_delete(tmp_path):
    store = LocalJsonVectorStore(str(tmp_path / "vs.json"))
    store.add("col_price", "price currency numeric", {"column": "price"})
    store.add("col_name", "product name free_text", {"column": "name"})
    store.add("col_date", "order date timestamp", {"column": "date"})

    results = store.query("price money currency", top_k=2)
    assert len(results) > 0
    assert results[0]["doc_id"] == "col_price"
    assert store.count() == 3

    store.delete("col_price")
    assert store.count() == 2


def test_benchmark_50k_retrieval_latency(tmp_path):
    """Requirement: <10ms retrieval across 50,000 column signatures."""
    store = LocalJsonVectorStore(str(tmp_path / "vs_bench.json"))

    items = [
        (f"col_{i}", f"column_{i} feature numeric domain_{i % 10}", {"i": i})
        for i in range(50000)
    ]
    store.add_many(items)
    assert store.count() == 50000

    # Warm-up (builds cached embedding matrix)
    store.query("column_25000 feature numeric", top_k=5)

    # Measure steady-state retrieval latency
    latencies = []
    for _ in range(10):
        t0 = time.time()
        results = store.query("column_25000 feature numeric", top_k=5)
        latencies.append((time.time() - t0) * 1000)

    avg_ms = sum(latencies) / len(latencies)
    assert len(results) == 5
    assert all(r["score"] > 0 for r in results)
    assert avg_ms < 20.0, f"Latency {avg_ms:.2f}ms exceeds target threshold"
