import pandas as pd
from src.scraper_agent import ScraperAgent, ComplianceChecker
from src.query_audit import QueryAuditLogger

def test_captcha_detection():
    agent = ScraperAgent()
    html = "<html><body><h1>Verify you are human - Cloudflare Challenge</h1></body></html>"
    assert agent._detect_captcha(html, 403) is True
    assert agent._detect_captcha("<html>Normal page content</html>", 200) is False

def test_pii_compliance_check():
    checker = ComplianceChecker()
    df = pd.DataFrame({
        "name": ["John Doe", "Jane Smith"],
        "contact": ["john@example.com", "+1 555-0198"],
        "price": [10, 20]
    })
    result = checker.check_pii(df)
    assert result["status"] == "gdpr_risk"
    assert len(result["columns"]) == 1
    assert result["columns"][0]["column"] == "contact"

def test_query_audit_retention(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_audit.db")
    monkeypatch.setattr("src.query_audit.DB_PATH", test_db)
    monkeypatch.setattr("src.query_audit.MAX_RECORDS_PER_DATASET", 50)
    
    logger = QueryAuditLogger()
    for i in range(75):
        logger.log_query(f"SELECT {i}", {}, {"runtime_ms": 1}, "test_retention_ds")
        
    recent = logger.get_recent("test_retention_ds", limit=100)
    assert len(recent) == 50
