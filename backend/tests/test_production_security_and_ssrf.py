"""
Production Security & SSRF Protection Test Suite.
Verifies:
1. SSRFValidator blocks AWS/GCP metadata endpoints (169.254.169.254).
2. SSRFValidator blocks localhost, 127.0.0.1, ::1, and private LAN IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16).
3. SSRFValidator blocks non-HTTP schemes (file://, ftp://, gopher://, javascript:).
4. SSRFValidator allows safe public domains (example.com, google.com).
5. HTMLSanitizer strips malicious <script> tags and XSS attack vectors.
6. CredentialRedactor masks API keys and tokens in output logs.
7. AntiBotCrawler detects Cloudflare/PerimeterX challenge pages.
"""
import pytest
import asyncio
from src.security import ssrf_validator, html_sanitizer, credential_redactor
from src.crawler_engine import anti_bot_crawler
from src.compliance import legal_compliance
from src.seo_auditor import seo_auditor
from src.webradar_crawler import webradar_suite


# =====================================================================
# 1. SSRF GATES & DANGEROUS TARGET PROTECTION
# =====================================================================

def test_ssrf_blocks_aws_and_cloud_metadata():
    """Verify SSRFValidator blocks AWS/GCP link-local metadata endpoints."""
    attack_urls = [
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.169.254/computeMetadata/v1/",
        "https://169.254.169.254/latest/user-data",
        "http://metadata.google.internal/computeMetadata/v1/"
    ]
    for url in attack_urls:
        val = ssrf_validator.validate_url(url)
        assert not val.valid, f"Expected SSRF block on metadata URL: {url}"
        assert "restricted" in val.reason.lower() or "blocked" in val.reason.lower() or "ssrf" in val.reason.lower()


def test_ssrf_blocks_loopback_and_internal_lan():
    """Verify SSRFValidator blocks localhost, loopback, and private IPv4 ranges."""
    internal_urls = [
        "http://localhost:8000/api/admin",
        "http://127.0.0.1:5000/delete-all",
        "http://10.0.0.1/router-settings",
        "http://192.168.1.1/admin.html",
        "http://172.16.0.5:9000/internal"
    ]
    for url in internal_urls:
        val = ssrf_validator.validate_url(url)
        assert not val.valid, f"Expected SSRF block on internal URL: {url}"


def test_ssrf_blocks_dangerous_schemes():
    """Verify SSRFValidator blocks file://, gopher://, ftp://, and javascript: URIs."""
    dangerous_schemes = [
        "file:///etc/passwd",
        "file:///c:/windows/system32/cmd.exe",
        "gopher://127.0.0.1:6379/_flushall",
        "ftp://ftp.internal-backup.local",
        "javascript:alert(document.cookie)"
    ]
    for url in dangerous_schemes:
        val = ssrf_validator.validate_url(url)
        assert not val.valid, f"Expected scheme block on: {url}"
        assert "scheme" in val.reason.lower() or "protocol" in val.reason.lower()


def test_ssrf_allows_safe_public_domains():
    """Verify SSRFValidator permits legitimate public internet domains."""
    safe_urls = [
        "https://example.com",
        "https://google.com",
        "https://github.com",
        "http://httpbin.org/html"
    ]
    for url in safe_urls:
        val = ssrf_validator.validate_url(url)
        assert val.valid, f"Safe URL should be permitted: {url} (Reason: {val.reason})"


def test_seo_auditor_and_webradar_reject_ssrf_targets():
    """Verify SEO auditor and WebRadar refuse to crawl malicious SSRF targets."""
    res_seo = seo_auditor.audit_url("http://169.254.169.254/latest/meta-data/")
    assert res_seo["overall_seo_score"] == 0
    assert "security check failed" in res_seo.get("error", "").lower() or "blocked" in res_seo.get("error", "").lower()

    res_radar = webradar_suite.deep_audit_domain_or_url("http://127.0.0.1:8000/admin")
    assert res_radar["status"] == "blocked"
    assert res_radar["seo_audit"]["overall_seo_score"] == 0


# =====================================================================
# 2. HTML SANITIZATION & CREDENTIAL REDACTION
# =====================================================================

def test_html_sanitizer_removes_xss_scripts():
    """Verify HTMLSanitizer strips script tags and inline event handler payloads."""
    dirty_html = "<div><h3>Title</h3><script>alert('XSS')</script><img src='x' onerror='alert(1)'><p>Safe text</p></div>"
    clean = html_sanitizer.sanitize(dirty_html)
    assert "<script" not in clean
    assert "onerror" not in clean
    assert "<h3>Title</h3>" in clean
    assert "<p>Safe text</p>" in clean


def test_credential_redactor_masks_api_keys():
    """Verify CredentialRedactor replaces API keys and secrets with [REDACTED_CREDENTIAL]."""
    log_sample = (
        "Connected to service with apiKey: gsk_abcdef1234567890abcdef1234567890 "
        "and OpenAI secret sk-proj-1234567890abcdef1234567890abcdef"
    )
    redacted = credential_redactor.redact(log_sample)
    assert "gsk_abcdef" not in redacted
    assert "sk-proj" not in redacted
    assert "[REDACTED_CREDENTIAL]" in redacted


# =====================================================================
# 3. ANTI-BOT CHALLENGE DETECTION
# =====================================================================

def test_antibot_crawler_detects_challenge_pages():
    """Verify AntiBotCrawler identifies Cloudflare and PerimeterX bot challenge signatures."""
    cf_challenge_html = "<html><head><title>Just a moment...</title></head><body><div class='cf-challenge'>Checking your browser</div></body></html>"
    is_challenge = anti_bot_crawler._is_bot_challenge(403, cf_challenge_html)
    assert is_challenge is True

    normal_html = "<html><head><title>Welcome to DataForge</title></head><body><h1>Enterprise Cloud</h1></body></html>"
    is_normal = anti_bot_crawler._is_bot_challenge(200, normal_html)
    assert is_normal is False
