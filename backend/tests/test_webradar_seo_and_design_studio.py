"""
Test Suite for Web Intelligence, 360° SEO Auditor, DesignLens UI/UX Extractor, and Deep Web Audit.
"""
import pytest
from src.seo_auditor import seo_auditor, SEOAuditor
from src.design_extractor import design_lens, DesignLensExtractor
from src.webradar_crawler import webradar_suite, WebRadarSuite
from src.assistant_engine import assistant_engine


# Sample rich mock HTML for testing
MOCK_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>QuantumFlow — Autonomous Cryogenic Analytics Platform</title>
    <meta name="description" content="Next-generation autonomous cryogenic computing and telemetry platform. Accelerate qubit coherence analysis with zero data friction.">
    <link rel="canonical" href="https://quantumflow.io">
    <meta property="og:title" content="QuantumFlow Cryogenics">
    <meta property="og:description" content="Sub-Kelvin computing analytics.">
    <meta name="twitter:card" content="summary_large_image">
    <style>
        :root {
            --brand-primary: #6366f1;
            --brand-secondary: #06b6d4;
            --bg-dark: #090d16;
            --surface-dark: #121826;
            --text-light: #f1f5f9;
            --accent-pink: #f43f5e;
        }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: #090d16;
            color: #f1f5f9;
        }
        h1, h2, h3 {
            font-family: 'Cabinet Grotesk', sans-serif;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            border-radius: 16px;
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <a href="mailto:founders@quantumflow.io">Contact Founders</a>
        </nav>
    </header>
    <main>
        <h1>Autonomous Quantum Analytics</h1>
        <h2>Sub-Kelvin Telemetry Processing</h2>
        <p>QuantumFlow provides millisecond causal discovery for multi-qubit dilution refrigerators.</p>
        <h2>Real-Time Coherence Dashboards</h2>
        <p>Monitor T1 and T2 relaxation times with deterministic MICE imputation.</p>
        <div class="hero-grid">
            <img src="/assets/hero.png" alt="Cryogenic dashboard overview">
        </div>
    </main>
</body>
</html>
"""


def test_seo_auditor_meta_and_heading_evaluation():
    """Verify SEO auditor calculates optimal scores and detects headings correctly."""
    result = seo_auditor.audit_html(MOCK_HTML, url="https://quantumflow.io")
    assert "overall_seo_score" in result
    assert result["overall_seo_score"] >= 70
    assert result["meta"]["title_status"] == "optimal"
    assert result["meta"]["description_status"] == "optimal"
    assert result["headings"]["h1_count"] == 1
    assert result["headings"]["h1_items"][0] == "Autonomous Quantum Analytics"
    assert result["headings"]["h2_count"] == 2
    assert result["social_graphs"]["has_opengraph"] is True
    assert result["social_graphs"]["has_twitter_cards"] is True


def test_seo_auditor_core_web_vitals_and_readability():
    """Verify SEO auditor estimates FCP/LCP and Flesch readability."""
    result = seo_auditor.audit_html(MOCK_HTML, url="https://quantumflow.io")
    cwv = result["core_web_vitals_simulation"]
    assert "estimated_fcp_ms" in cwv
    assert "estimated_lcp_ms" in cwv
    assert cwv["dom_elements_count"] > 0
    assert result["content_metrics"]["word_count"] > 15
    assert result["content_metrics"]["flesch_reading_ease"] >= 0.0


def test_design_lens_color_clustering_and_contrast():
    """Verify DesignLens clusters primary/secondary colors and verifies WCAG contrast."""
    result = design_lens.extract_design_system(MOCK_HTML, url="https://quantumflow.io")
    palette = result["palette"]
    assert "primary" in palette
    assert "background" in palette
    assert "surface" in palette
    assert result["contrast"]["ratio"] > 4.5
    assert result["contrast"]["wcag_compliance"] in ["AA", "AAA"]


def test_design_lens_typography_and_tokens_export():
    """Verify DesignLens extracts font families and builds valid Tailwind / CSS snippets."""
    result = design_lens.extract_design_system(MOCK_HTML, url="https://quantumflow.io")
    typo = result["typography"]
    assert typo["body_font"] == "Inter" or typo["heading_font"] == "Inter"
    
    exports = result["export_artifacts"]
    assert "tokens_json" in exports
    assert "tailwind_config_snippet" in exports
    assert "css_variables" in exports
    assert "module.exports" in exports["tailwind_config_snippet"]
    assert ":root" in exports["css_variables"]


def test_webradar_suite_unified_deep_audit():
    """Verify unified WebRadar suite executes lead extraction, SEO, and DesignLens concurrently."""
    # Test on local mock or live URL
    res = webradar_suite.deep_audit_domain_or_url("quantumflow.io", max_pages=1)
    assert "seo_audit" in res
    assert "design_lens" in res
    assert "lead_intelligence" in res
    assert "summary" in res


@pytest.mark.asyncio
async def test_copilot_executes_seo_and_design_tools_autonomously():
    """Verify Copilot executes SEO audits and Design token extractions on command."""
    assistant_engine.user_profile["require_confirmation"] = False
    assistant_engine._save_user_profile()
    
    # 1. SEO Audit trigger
    res_seo = await assistant_engine.process_query("sess_web_test", "Audit SEO for https://stripe.com")
    assert "response" in res_seo
    assert "SEO" in res_seo["response"] or "score" in res_seo["response"].lower()

    # 2. Design Tokens trigger
    res_design = await assistant_engine.process_query("sess_web_test", "Extract design tokens from https://linear.app")
    assert "response" in res_design
    assert "Tokens" in res_design["response"] or "Color" in res_design["response"]
