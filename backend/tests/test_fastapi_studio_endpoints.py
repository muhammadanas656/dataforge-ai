"""
FastAPI 5-Studio Endpoints Integration Test Suite.
Verifies that all frontend studio endpoints are registered and respond with 200 OK:
1. POST /api/design/invent
2. POST /api/design/multi-proportion
3. POST /api/export/browser-download
4. GET /api/learning/telemetry
5. POST /api/learning/evolve
"""
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_api_design_invent():
    """Verify design invention endpoint returns full vector & preview metadata."""
    res = client.post("/api/design/invent", json={
        "asset_name": "TestVault",
        "domain_theme": "FinTech",
        "accent_color": "#06b6d4"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["asset_name"] == "TestVault"
    assert "<svg" in data["svg_code"]
    assert "React" in data["react_jsx"]
    assert data["wcag_aaa_compliant"] is True
    assert data["fitness_score"] >= 90.0


def test_api_design_multi_proportion():
    """Verify multi-proportion endpoint returns HTML viewer and specs."""
    sample_svg = '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="20" fill="#6366f1"/></svg>'
    res = client.post("/api/design/multi-proportion", json={
        "asset_name": "TestIcon",
        "svg_markup": sample_svg
    })
    assert res.status_code == 200
    data = res.json()
    assert "proportions" in data
    assert "square_1x1" in data["proportions"]
    assert "<!DOCTYPE html>" in data["interactive_viewer_html"]


def test_api_browser_download():
    """Verify browser download endpoint returns attachment header and content."""
    res = client.post("/api/browser/download", json={
        "content": "<svg viewBox='0 0 64 64'></svg>",
        "filename": "icon",
        "file_format": "svg"
    })
    assert res.status_code == 200
    cd = res.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert "icon.svg" in cd


def test_api_learning_telemetry():
    """Verify learning telemetry returns live 7-perspective health scores."""
    res = client.get("/api/learning/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "skill_proficiency" in data
    assert "perspective_scores" in data
    assert data["passed"] is True


def test_api_learning_evolve():
    """Verify manual frontend evolution trigger executes and returns report."""
    res = client.post("/api/learning/evolve", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["passed"] is True
    assert "summary" in data
