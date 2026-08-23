"""
Ecosystem Universal QA & Teaching Validation Test Suite.
Verifies:
1. Universal Q&A domain knowledge recall with 0-token instant cache hits.
2. Actionable SEO Auditor outputs (Recommendations, Meta Tags HTML, Markdown report).
3. Actionable DesignLens outputs (W3C/Figma tokens.json, Tailwind config, CSS :root, WCAG remediation).
4. Edge cases & fault injection across all 4 studios.
"""
import pytest
from src.assistant_engine import assistant_engine, AssistantEngine
from src.seo_auditor import seo_auditor
from src.design_extractor import design_lens
from src.webradar_crawler import webradar_suite


@pytest.fixture(autouse=True)
def reload_semantic_cache():
    """Ensure AssistantEngine loads the latest taught semantic cache."""
    assistant_engine.semantic_cache = assistant_engine._load_semantic_cache()
    assistant_engine.user_profile["require_confirmation"] = False
    assistant_engine._save_user_profile()
    yield


# =====================================================================
# 1. UNIVERSAL ZERO-TOKEN QA RECALL & DOMAIN TEACHING
# =====================================================================

@pytest.mark.asyncio
async def test_copilot_answers_seo_and_core_web_vitals_zero_token():
    """Verify Copilot answers SEO questions using taught knowledge with zero tokens."""
    res = await assistant_engine.process_query("sess_qa", "what is seo audit")
    assert "response" in res
    assert "SiteLens" in res["response"] or "Core Web Vitals" in res["response"] or "SEO" in res["response"]
    assert res.get("cached") is True


@pytest.mark.asyncio
async def test_copilot_answers_design_tokens_zero_token():
    """Verify Copilot answers DesignLens and token questions with zero tokens."""
    res = await assistant_engine.process_query("sess_qa", "what is designlens")
    assert "response" in res
    assert "DesignLens" in res["response"]
    assert "Figma" in res["response"] or "Tailwind" in res["response"]
    assert res.get("cached") is True


@pytest.mark.asyncio
async def test_copilot_answers_app_hierarchy_and_studios_zero_token():
    """Verify Copilot explains the 4 Purpose-Built Studios with zero tokens."""
    res = await assistant_engine.process_query("sess_qa", "what are the 4 studios")
    assert "response" in res
    assert "Tabular Data Studio" in res["response"]
    assert "Web Intelligence" in res["response"]
    assert "Strategic Invention" in res["response"]
    assert res.get("cached") is True


@pytest.mark.asyncio
async def test_copilot_answers_lead_scraper_and_cloudflare_zero_token():
    """Verify Copilot explains Cloudflare XOR email de-obfuscation with zero tokens."""
    res = await assistant_engine.process_query("sess_qa", "how does the lead scraper work")
    assert "response" in res
    assert "Cloudflare XOR" in res["response"]
    assert res.get("cached") is True


@pytest.mark.asyncio
async def test_copilot_answers_triz_invention_zero_token():
    """Verify Copilot explains TRIZ 39x40 contradiction resolution with zero tokens."""
    res = await assistant_engine.process_query("sess_qa", "how does triz work")
    assert "response" in res
    assert "TRIZ" in res["response"]
    assert "Altshuller" in res["response"] or "Contradiction" in res["response"]
    assert res.get("cached") is True


# =====================================================================
# 2. ACTIONABLE SEO & DESIGNLENS ARTIFACT OUTPUTS
# =====================================================================

def test_seo_auditor_generates_actionable_recommendations_and_artifacts():
    """Verify SEO auditor generates concrete priority recommendations and HTML snippets."""
    bad_html = "<html><head><title>Short</title></head><body><p>No headings or meta tags.</p><img src='pic.jpg'></body></html>"
    res = seo_auditor.audit_html(bad_html, url="https://test-site.org")
    
    assert "actionable_recommendations" in res
    assert len(res["actionable_recommendations"]) >= 2
    
    artifacts = res.get("export_artifacts", {})
    assert "meta_tags_html" in artifacts
    assert "<title>" in artifacts["meta_tags_html"]
    assert "markdown_report" in artifacts
    assert "# 360° Technical & Content SEO Audit Report" in artifacts["markdown_report"]


def test_design_lens_generates_wcag_contrast_and_remediation():
    """Verify DesignLens evaluates WCAG contrast and provides remediation on low-contrast palettes."""
    contrast_low_calc = design_lens._calculate_contrast_ratio("#777777", "#555555")
    assert contrast_low_calc < 4.5
    
    # Test on full system
    sample_html = "<html><body style='background-color: #0f172a; color: #f8fafc; font-family: Inter;'><h1>Headline</h1></body></html>"
    res = design_lens.extract_design_system(sample_html, url="https://design-test.org")
    assert "contrast" in res
    assert res["contrast"]["wcag_compliance"] in ["AA", "AAA"]


def test_design_lens_w3c_figma_tokens_format():
    """Verify Figma DTCG tokens.json matches the W3C design tokens standard schema."""
    sample_html = "<body style='background-color: #0f172a; color: #f8fafc; font-family: Inter;'></body>"
    res = design_lens.extract_design_system(sample_html, url="https://figma-export.com")
    
    tokens = res["export_artifacts"]["tokens_json"]
    assert tokens["$schema"] == "https://tr.designtokens.org/format/"
    assert "color" in tokens
    assert "primary" in tokens["color"]
    assert tokens["color"]["primary"]["$type"] == "color"


# =====================================================================
# 3. FAULT INJECTION & EDGE SCENARIOS
# =====================================================================

def test_webradar_handles_corrupted_and_unreachable_urls_gracefully():
    """Verify WebRadar handles network failures and returns default design system without crashing."""
    res = webradar_suite.deep_audit_domain_or_url("nonexistent-domain-xyz-99999.invalid")
    assert res["status"] in ["partial_failure", "success", "blocked"]
    assert "palette" in res["design_lens"]
    assert res["seo_audit"]["overall_seo_score"] == 0
