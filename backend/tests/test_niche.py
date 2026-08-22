from src import niche_research as nr

def test_synthetic_analysis_deterministic():
    a = nr.analyze_posts(nr._synthetic_posts("yoga mat"))
    b = nr.analyze_posts(nr._synthetic_posts("yoga mat"))
    assert a == b and a["mentions"] > 0
    assert a["avg_sentiment"] != 0

def test_opportunity_score_bounds():
    s1 = nr.opportunity_score({"mentions": 500, "growth": 0.5, "pain_ratio": 0.3, "avg_engagement": 40})
    s2 = nr.opportunity_score({"mentions": 0, "growth": -1.0, "pain_ratio": 0.0, "avg_engagement": 0})
    assert 0 <= s1 <= 100
    assert 0 <= s2 <= 100

def test_market_size():
    m = nr.market_size({"mentions": 100}, 50)
    assert m["tam_annual_usd"] > 0
    assert m["est_buyers_monthly"] > 0

def test_sentiment():
    assert nr._sentiment("I love this, great value amazing") > 0
    assert nr._sentiment("terrible, broken, scam worst") < 0
    assert nr._sentiment("") == 0.0

def test_run_research_offline():
    result = nr.run_research("mechanical keyboard switches")
    assert result["niche"] == "mechanical keyboard switches"
    assert "metrics" in result
    assert "market" in result
    assert "personas" in result
    assert len(result["personas"]) >= 1
    assert 0 <= result["opportunity_score"] <= 100
