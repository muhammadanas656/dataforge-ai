from src import research_automation as ra

def test_detect_alerts_returns_list():
    alerts = ra.detect_alerts()
    assert isinstance(alerts, list)

def test_swot_keys_defaulted(monkeypatch):
    monkeypatch.setattr(ra, "tracked_chat", lambda *a, **k: '{"strengths":["Solid community demand"]}')
    s = ra.generate_swot("test_run", "yoga mat")
    for k in ("strengths", "weaknesses", "opportunities", "threats"):
        assert k in s
        assert isinstance(s[k], list)

def test_weekly_digest(monkeypatch):
    monkeypatch.setattr(ra, "tracked_chat", lambda *a, **k: '{"summary":"Top niche opportunities and price shifts synthesized."}')
    d = ra.weekly_report("test_weekly")
    assert "alerts" in d
    assert "top_opportunities" in d
    assert "summary" in d
    assert len(d["summary"]) > 0
