"""
Multimodal Causal DAG & Production Monitoring Test Suite.
Verifies:
1. MultimodalCausalEngine flattens nested JSON payloads and arrays into tabular matrices.
2. MultimodalCausalEngine computes graph topology features (PageRank, degrees, clustering).
3. MultimodalCausalEngine computes regularized Precision Matrix (Theta = Sigma^-1) for Causal DAGs.
4. ProductionMonitor records API latencies, calculates p50/p95/p99 percentiles, and tracks error rates.
"""
import pytest
import pandas as pd
import numpy as np
from src.multimodal_causal import multimodal_causal
from src.production_monitor import production_monitor


# =====================================================================
# 1. MULTIMODAL CAUSAL DAG INGESTION
# =====================================================================

def test_json_flattening_nested_trees():
    """Verify MultimodalCausalEngine flattens nested dictionaries and numeric lists."""
    sample_json = [
        {"user": {"id": "u1", "age": 28}, "telemetry": {"latency_ms": 120, "payload_kb": 4.5}, "tags": ["a", "b"]},
        {"user": {"id": "u2", "age": 35}, "telemetry": {"latency_ms": 95, "payload_kb": 2.1}, "tags": ["c"]},
        {"user": {"id": "u3", "age": 42}, "telemetry": {"latency_ms": 210, "payload_kb": 8.9}, "tags": ["a", "d", "e"]}
    ]
    df = multimodal_causal.flatten_nested_json(sample_json)
    assert not df.empty
    assert "user_age" in df.columns
    assert "telemetry_latency_ms" in df.columns
    assert "tags_count" in df.columns
    assert df["user_age"].dtype in [np.int64, np.float64, int, float]


def test_graph_topology_causal_features():
    """Verify MultimodalCausalEngine converts graph edges into nodal causal feature vectors."""
    edges = [
        {"source": "node_A", "target": "node_B", "weight": 2.5},
        {"source": "node_A", "target": "node_C", "weight": 1.0},
        {"source": "node_B", "target": "node_C", "weight": 3.0},
        {"source": "node_C", "target": "node_D", "weight": 1.5}
    ]
    df_graph = multimodal_causal.graph_to_tabular_features(edges)
    assert not df_graph.empty
    assert "node_id" in df_graph.columns
    assert "in_degree" in df_graph.columns
    assert "pagerank_estimate" in df_graph.columns
    assert len(df_graph) == 4


def test_multimodal_causal_dag_precision_matrix():
    """Verify MultimodalCausalEngine computes Precision Matrix and isolates partial correlations."""
    np.random.seed(42)
    # Synthetic causal chain: X -> Y -> Z
    x = np.random.normal(10, 2, 50)
    y = 2.0 * x + np.random.normal(0, 0.5, 50)
    z = 1.5 * y + np.random.normal(0, 0.5, 50)
    w = np.random.normal(5, 1, 50) # Independent control

    df = pd.DataFrame({"driver_x": x, "mediator_y": y, "outcome_z": z, "noise_w": w})
    dag_res = multimodal_causal.compute_multimodal_causal_dag(df)
    
    assert dag_res["status"] == "success"
    assert dag_res["feature_count"] == 4
    assert len(dag_res["causal_edges"]) > 0
    # X and Y should show strong partial correlation
    xy_edge = next((e for e in dag_res["causal_edges"] if (e["source"] == "driver_x" and e["target"] == "mediator_y") or (e["source"] == "mediator_y" and e["target"] == "driver_x")), None)
    assert xy_edge is not None
    assert abs(xy_edge["partial_correlation"]) > 0.3


# =====================================================================
# 2. PRODUCTION OBSERVABILITY & TELEMETRY MONITORING
# =====================================================================

def test_production_monitor_records_and_computes_percentiles():
    """Verify ProductionMonitor computes p50, p95, and p99 latency distributions."""
    # Seed latencies
    latencies = [12.0, 15.0, 18.0, 22.0, 25.0, 30.0, 45.0, 80.0, 150.0, 320.0]
    for lat in latencies:
        production_monitor.record_request(latency_ms=lat, status_code=200)

    # Record error and SSRF block
    production_monitor.record_request(latency_ms=5.0, status_code=403, is_ssrf_block=True)
    production_monitor.record_request(latency_ms=50.0, status_code=500)

    health = production_monitor.get_health_metrics()
    assert health["status"] in ["healthy", "degraded"]
    assert health["total_requests"] >= 10
    assert health["security_telemetry"]["ssrf_blocks_intercepted"] >= 1
    assert health["latency_profiling_ms"]["p50"] > 0
    assert health["latency_profiling_ms"]["p99"] >= health["latency_profiling_ms"]["p50"]
