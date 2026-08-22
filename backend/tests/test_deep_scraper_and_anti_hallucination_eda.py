"""
Deep Niche Lead Scraper & Anti-Hallucination EDA Grounding Test Suite.
Verifies:
1. High-penetration email, phone, and social lead scraping on user-requested niches.
2. 100% deterministic mathematical grounding of EDA narratives (Anti-Hallucination).
3. Complete payload schema parity for Next.js frontend components.
"""
import pytest
import os
import re
import numpy as np
import pandas as pd
from src.scraper_agent import scraper
from src.autopilot import run_autopilot
from src.eda_engine import run_full_eda
from src.chart_explainer import explain_chart, generate_plain_english_takeaway

def test_deep_niche_lead_and_email_scraping():
    """Verify deep email, phone, and executive contact extraction on specialized niches."""
    res = scraper.extract_niche_leads_and_contacts(
        niche="Biocompatible 3D Bone Scaffold Filaments",
        target_urls=["https://news.ycombinator.com", "https://www.producthunt.com"],
        max_pages=2
    )
    assert res["status"] == "success"
    assert "dataset_id" in res
    assert res["leads_extracted"] >= 5
    assert res["valid_emails_count"] >= 5
    assert res["penetration_rate_pct"] >= 80.0
    
    # Verify saved CSV exists in uploads
    csv_file = f"uploads/{res['filename']}"
    assert os.path.exists(csv_file)
    df_leads = pd.read_csv(csv_file)
    assert "verified_email" in df_leads.columns
    assert "phone_number" in df_leads.columns
    assert "social_profile" in df_leads.columns


def test_anti_hallucination_mathematical_eda_grounding():
    """Verify EDA statistics and chart explanations strictly match mathematical reality without LLM hallucination."""
    os.makedirs("uploads", exist_ok=True)
    csv_path = "uploads/anti_hallucination_verification_dataset.csv"
    
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        "User_ID": [f"USR_{i:04d}" for i in range(n)],
        "Annual_Spend_USD": np.random.normal(loc=5420.50, scale=1200.0, size=n).round(2),
        "Discount_Pct": np.random.uniform(0.05, 0.45, size=n).round(3),
        "Region_Tier": np.random.choice(["Tier_1_Enterprise", "Tier_2_MidMarket", "Tier_3_SMB"], p=[0.55, 0.30, 0.15], size=n),
        "Customer_Health_Score": np.random.randint(40, 100, size=n)
    })
    df.to_csv(csv_path, index=False)
    
    # Clean dataset via Auto-Pilot first
    auto_res = run_autopilot(csv_path, session_id="eda_grounding_test")
    did = auto_res["dataset_id"]
    
    # Run full EDA on canonical dataset ID
    eda_res = run_full_eda(did, force=True)
    assert eda_res is not None
    assert "results" in eda_res
    results = eda_res["results"]
    assert len(results) > 0
    
    # 1. Verify Numeric Distribution Grounding
    spend_charts = [r for r in results if "Annual_Spend_USD" in r.get("title", "") and r.get("chart_type") == "histogram"]
    assert len(spend_charts) > 0
    hist = spend_charts[0]
    stats = hist.get("stats", {})
    assert "mean" in stats
    assert "median" in stats
    
    # Verify exact math match in chart explanation
    explanation = generate_plain_english_takeaway("numeric_distribution", hist, ["Annual_Spend_USD"])
    assert "plain_meaning" in explanation
    assert str(round(stats["mean"], 1)) in explanation["plain_meaning"] or str(round(stats["median"], 1)) in explanation["plain_meaning"]
    
    # 2. Verify Dominant Categorical Grounding
    region_charts = [r for r in results if "Region_Tier" in r.get("title", "") and r.get("chart_type") == "bar"]
    assert len(region_charts) > 0
    bar = region_charts[0]
    bar_explanation = generate_plain_english_takeaway("category_breakdown", bar, ["Region_Tier"])
    assert "plain_meaning" in bar_explanation
    assert "dominant group" in bar_explanation["plain_meaning"].lower() or "distinct groups" in bar_explanation["plain_meaning"].lower()


def test_frontend_eda_payload_schema_parity():
    """Verify that every generated EDA analysis result contains all required fields for Next.js frontend rendering."""
    csv_path = "uploads/anti_hallucination_verification_dataset.csv"
    auto_res = run_autopilot(csv_path, session_id="eda_schema_test")
    did = auto_res["dataset_id"]
    
    eda_res = run_full_eda(did)
    results = eda_res.get("results", [])
    assert len(results) > 0
    
    for r in results:
        assert "chart_type" in r
        assert "title" in r
        assert "stats" in r or "chart_svg" in r or "chart_b64" in r
        
        # Verify chart type explanation
        guide = explain_chart(r.get("chart_type", "table"))
        assert "plain_name" in guide
        assert "how_to_read" in guide
        assert "best_for" in guide
