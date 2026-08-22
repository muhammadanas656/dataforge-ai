import pandas as pd
from src.remediation_memory import RemediationMemory

def _inc():
    return {"kind": "coercion_failed", "context": {"kind": "coercion_failed", "dtype": "object"}}

def test_new_arm_not_auto_selected_until_validated(tmp_path):
    m = RemediationMemory(str(tmp_path / "m.json"))
    sig = m.signature(_inc())
    pid = m.add_candidate(sig, {"op": "coerce_numeric", "params": {"column": "price"}})
    assert m.select(sig) is None
    m.update(sig, pid, True)
    assert m.select(sig) is not None

def test_thompson_prefers_good_arm(tmp_path):
    m = RemediationMemory(str(tmp_path / "m.json"))
    sig = m.signature(_inc())
    pg = m.add_candidate(sig, {"op": "coerce_numeric", "params": {"column": "price"}})
    pb = m.add_candidate(sig, {"op": "fill_mode", "params": {"column": "price"}})
    for _ in range(20):
        m.update(sig, pg, True)
    for _ in range(20):
        m.update(sig, pb, False)
    picks = [m.select(sig)[1] for _ in range(50)]
    assert picks.count(pg) > picks.count(pb)

def test_remediate_l1_bandit_skips_agent(tmp_path, monkeypatch):
    from src import remediation_engine as re_
    m = RemediationMemory(str(tmp_path / "m.json"))
    sig = m.signature(_inc())
    pid = m.add_candidate(sig, {"op": "coerce_numeric", "params": {"column": "price"}})
    m.update(sig, pid, True)
    called = {"n": 0}
    monkeypatch.setattr(re_, "propose_and_validate", lambda *a, **k: (called.__setitem__("n", called["n"] + 1), None)[1])
    out, meta = re_.remediate("run", pd.DataFrame({"price": ["1", "2"]}), _inc(), mem=m)
    assert meta["source"] == "memory_l1"
    assert called["n"] == 0
    assert out["price"].dtype != object

def test_recall_backward_compat(tmp_path):
    m = RemediationMemory(str(tmp_path / "m.json"))
    m.store(_inc(), {"op": "coerce_numeric", "params": {"column": "price"}}, True)
    assert m.recall(_inc())["op"] == "coerce_numeric"
