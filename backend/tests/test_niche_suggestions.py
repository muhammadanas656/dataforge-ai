import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.niche_research import suggest_niches, generate_and_inject_dataset, generate_business_blueprint


def test_suggest_niches_grounded_scores():
    suggestions = suggest_niches(category="E-Commerce", limit=4)
    assert len(suggestions) <= 4
    assert len(suggestions) > 0
    for s in suggestions:
        assert "niche" in s
        assert "category" in s
        assert "opportunity_score" in s
        assert 0.0 <= s["opportunity_score"] <= 100.0
        assert "trend_growth" in s
        assert "tam_estimate" in s
        assert "hook" in s


def test_suggest_niches_category_filter():
    suggestions = suggest_niches(category="AI & SaaS", limit=3)
    assert len(suggestions) > 0
    assert any("AI" in s["category"] or "SaaS" in s["category"] for s in suggestions)


def test_generate_and_inject_dataset(tmp_path, monkeypatch):
    monkeypatch.setattr("src.niche_research.save_artifact", lambda x: x)
    res = generate_and_inject_dataset("Ergonomic Split Keyboard")
    assert "dataset_id" in res
    assert res["rows"] >= 50
    assert res["columns"] >= 10
    assert "filename" in res


def test_generate_business_blueprint():
    bp = generate_business_blueprint("Cold Plunge Water Chiller", category="E-Commerce")
    assert "business_name" in bp
    assert "model_archetype" in bp
    assert "pricing_tiers" in bp
    assert len(bp["pricing_tiers"]) >= 3
    assert "gtm_channels" in bp
    assert len(bp["gtm_channels"]) >= 1


def test_submit_job_body_parsing():
    client = TestClient(app)
    # Testing that JSON body with "niche" is accepted without 422 or missing param error
    resp = client.post("/api/jobs/research", json={"niche": "Smart Ultrasonic Cleaner", "avg_price": 60})
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert data["status"] in ("queued", "running", "done")


def test_api_research_suggestions_endpoint():
    client = TestClient(app)
    resp = client.get("/api/research/suggestions?category=all&limit=4")
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0


def test_api_research_blueprint_endpoint():
    client = TestClient(app)
    resp = client.post("/api/research/blueprint", json={"niche": "B2B Notion Invoicing", "category": "AI & SaaS"})
    assert resp.status_code == 200
    data = resp.json()
    assert "model_archetype" in data
    assert "pricing_tiers" in data
