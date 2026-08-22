import os
import time
import pandas as pd
import numpy as np
from src import ingest_big, relational, jobs, storage, incidents, remediation_ops, remediation_memory, remediation_engine

def test_duckdb_ingest_and_profile(tmp_path):
    csv_file = tmp_path / "big_sample.csv"
    pd.DataFrame({
        "price": [10.0, 20.0, 30.0, 40.0] * 250,
        "name": ["Alpha", "Beta", "Gamma", "Delta"] * 250
    }).to_csv(csv_file, index=False)

    pq_out = str(tmp_path / "big_sample.parquet")
    res = ingest_big.ingest_to_parquet(str(csv_file), pq_out)
    assert res == pq_out
    assert os.path.exists(pq_out)

    prof = ingest_big.profile_big(pq_out)
    assert prof["total_rows"] == 1000
    assert prof["total_columns"] == 2
    sample = ingest_big.sample_from_parquet(pq_out, n=50)
    assert len(sample) == 50


def test_relational_detection_and_flatten():
    customers = pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})
    orders = pd.DataFrame({
        "order_id": [101, 102, 103, 104],
        "customers_id": [1, 2, 999, 3],  # 999 is an orphan
        "total": [50.0, 75.0, 100.0, 120.0]
    })
    tables = {"customers": customers, "orders": orders}

    fks = relational.detect_foreign_keys(tables)
    assert len(fks) == 1
    assert fks[0]["child"] == "orders"
    assert fks[0]["parent"] == "customers"
    assert fks[0]["integrity"] == 0.75  # 3 of 4 match

    orphans = relational.orphan_counts(tables, fks)
    assert orphans[0]["orphans"] == 1
    assert orphans[0]["orphan_pct"] == 25.0

    flat = relational.flatten(tables, fks, primary="orders")
    assert "name" in flat.columns
    assert len(flat) == 4
    assert flat.loc[flat["order_id"] == 103, "name"].isna().all()


def test_async_jobs_queue_lifecycle():
    q = jobs.JobQueue(max_workers=2)

    def sample_task(x, y, cancel=None):
        if cancel:
            cancel.set_progress(0.5, "halfway")
        return x * y

    job = q.submit("multiply", sample_task, {"x": 6, "y": 7})
    for _ in range(50):
        if job.status in (jobs.Status.DONE, jobs.Status.ERROR):
            break
        time.sleep(0.02)

    assert job.status == jobs.Status.DONE
    assert job.result == 42
    assert job.progress == 1.0


def test_storage_backend_local_and_caching(tmp_path):
    backend = storage.LocalBackend(str(tmp_path))
    src = tmp_path / "test_artifact.json"
    src.write_text('{"status": "ok"}')

    uri = backend.write_file(str(src), "reports/test_artifact.json")
    assert "reports/test_artifact.json" in uri.replace("\\", "/")
    assert backend.exists("reports/test_artifact.json")
    assert backend.read_file("reports/test_artifact.json") == b'{"status": "ok"}'


def test_remediation_l1_l2_l3_loop(tmp_path, monkeypatch):
    mem_file = str(tmp_path / "remediations.json")
    mem = remediation_memory.RemediationMemory(mem_file)

    # 1. Test L3 safe auto-remediation
    df = pd.DataFrame({"status": ["active", "active", None, "active"]})
    incident = {"kind": "null_violation", "context": {"column": "status", "dtype": "object"}}

    # Mock agent proposal to return safe fill_mode
    def mock_chat(*args, **kwargs):
        return '{"op": "fill_mode", "params": {"column": "status"}, "reason": "fill missing status"}'

    monkeypatch.setattr("src.remediation_agent.tracked_chat", mock_chat)

    fixed_df, meta = remediation_engine.remediate("test_run_1", df, incident, mem=mem)
    assert meta["source"] == "auto_l3"
    assert fixed_df["status"].isna().sum() == 0  # Mode filled!
    assert mem.recall(incident) is not None  # Learned into memory!

    # 2. Test L1 instant memory recall (0 tokens) on identical incident
    df2 = pd.DataFrame({"status": [None, "active", "active"]})
    fixed_df2, meta2 = remediation_engine.remediate("test_run_2", df2, incident, mem=mem)
    assert meta2["source"] == "memory_l1"
    assert fixed_df2["status"].isna().sum() == 0

    # 3. Test L2 escalation on high impact
    df_high = pd.DataFrame({"price": [10.0] * 80 + [-50.0] * 20})
    incident_high = {"kind": "negative_prices", "context": {"column": "price", "dtype": "float64"}}

    def mock_chat_drop(*args, **kwargs):
        return '{"op": "custom_eval", "params": {"expr": "price > 0", "new": "is_valid"}, "reason": "flag invalid"}'

    monkeypatch.setattr("src.remediation_agent.tracked_chat", mock_chat_drop)
    _, meta3 = remediation_engine.remediate("test_run_3", df_high, incident_high, mem=mem)
    assert meta3["source"] == "needs_approval_l2"
    assert "incident_id" in meta3


def test_list_datasets_filters_to_uploads():
    from src.api import list_datasets
    res = list_datasets()
    assert "datasets" in res
    uploaded_files = set(os.listdir("uploads")) if os.path.exists("uploads") else set()
    for d in res["datasets"]:
        assert d["filename"] in uploaded_files

