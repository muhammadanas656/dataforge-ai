"""
Ultra-Penetration Lead Scraper & Contact De-obfuscation Test Suite.
Tests:
1. Cloudflare XOR email de-obfuscation.
2. Base64 & HTML entity obfuscated contact recovery.
3. Multi-Domain niche penetration rate (>=95% to 100%) across 5 unseen frontier niches.
"""
import pytest
import os
import re
import pandas as pd
from src.scraper_agent import ScraperAgent, scraper

def test_cloudflare_xor_email_deobfuscation():
    """Verify decoding of Cloudflare XOR-encrypted email hex tokens."""
    # Encode "hello@quantum.ai" with XOR key 0x5a
    raw_email = "hello@quantum.ai"
    key = 0x5a
    hex_str = f"{key:02x}" + "".join([f"{(ord(c) ^ key):02x}" for c in raw_email])
    
    decoded = ScraperAgent.decode_cloudflare_email(hex_str)
    assert decoded == raw_email


def test_obfuscated_html_lead_extraction(monkeypatch):
    """Verify recovery of contacts from dirty HTML containing Cloudflare tags, Base64 attributes, and mailto links."""
    sample_dirty_html = """
    <html>
      <body>
        <h1>Aether Dynamics Aerospace</h1>
        <p>Contact our leadership team below:</p>
        <span data-email="Zm91bmRlcnNAYWV0aGVyZ2xvYmFsLmlv">Protected Email 1</span>
        <a href="/cdn-cgi/l/email-protection" data-cfemail="422b2c242d0223212f276c212d2f">Protected Email 2</a>
        <a href="mailto:invest@aetherdynamics.com?subject=Inquiry">Direct Investor Relations</a>
        <a href="/contact">Visit Contact Office</a>
        <a href="https://linkedin.com/company/aether-aerospace">LinkedIn Org</a>
        <p>Call us at +1 (800) 555-0199 or UK +44 20 7946 0991</p>
      </body>
    </html>
    """

    class MockResponse:
        status_code = 200
        text = sample_dirty_html

    monkeypatch.setattr(scraper.session, "get", lambda url, timeout=10: MockResponse())

    res = scraper.extract_niche_leads_and_contacts(
        niche="Aether Dynamics Aerospace",
        target_urls=["https://aetherdynamics.internal"],
        max_pages=1
    )

    assert res["status"] == "success"
    assert res["leads_extracted"] >= 3
    assert res["penetration_rate_pct"] >= 95.0
    
    csv_file = f"uploads/{res['filename']}"
    assert os.path.exists(csv_file)
    df = pd.read_csv(csv_file)
    emails = df["verified_email"].tolist()
    assert any("aether" in e.lower() for e in emails)


@pytest.mark.parametrize("niche_name", [
    "Quantum Cryogenic Qubit Substrates",
    "Autonomous Deep-Sea Mineral Mining ROVs",
    "AI Genomic Variant Discovery Platforms",
    "Solid-State Battery Ceramic Electrolytes",
    "Space Station Microgravity Bioprinters"
])
def test_frontier_niches_penetration_guarantee(niche_name):
    """Stress test 5 diverse unseen high-tech niche domains to verify >=95% penetration and zero-loss contact delivery."""
    res = scraper.extract_niche_leads_and_contacts(
        niche=niche_name,
        target_urls=["https://news.ycombinator.com", "https://www.producthunt.com"],
        max_pages=2
    )
    assert res["status"] == "success"
    assert res["leads_extracted"] >= 5
    assert res["valid_emails_count"] >= 5
    assert res["penetration_rate_pct"] >= 95.0
    
    # Confirm dataset is registered and profileable
    assert "dataset_id" in res
    csv_path = f"uploads/{res['filename']}"
    assert os.path.exists(csv_path)
    
    df = pd.read_csv(csv_path)
    assert not df.empty
    assert "verified_email" in df.columns
    assert "social_profile" in df.columns
    assert "phone_number" in df.columns
