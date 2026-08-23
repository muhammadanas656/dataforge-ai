"""
WebRadar 2.0 / SiteLens — Multi-Vector Web Crawler & Intelligence Suite.
Combines:
1. Lead & Contact Harvesting (Cloudflare XOR decoding, international phones).
2. 360° Technical & Content SEO Audits (Core Web Vitals, Heading structure).
3. DesignLens UI/UX Perspective & Token Extraction (Colors, Typography, WCAG).
"""
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup
from src.scraper_agent import scraper, decode_cloudflare_email
from src.seo_auditor import seo_auditor
from src.design_extractor import design_lens
from src.utils import logger


class WebRadarSuite:
    """Unified Web Intelligence, SEO Audit, and Design Extraction Suite."""

    def deep_audit_domain_or_url(self, target: str, max_pages: int = 3) -> Dict[str, Any]:
        """Perform unified multi-vector deep audit on a domain or URL."""
        url = target if target.startswith("http") else f"https://{target}"
        
        # 1. Fetch main page HTML
        html = ""
        fetch_error = None
        try:
            headers = {"User-Agent": "DataForge-WebRadar/2.0 (Multi-Vector Intelligence Crawler)"}
            resp = httpx.get(url, timeout=12.0, headers=headers, follow_redirects=True)
            html = resp.text
            final_url = str(resp.url)
        except Exception as e:
            fetch_error = str(e)
            logger.warning(f"[webradar] Failed to fetch {url}: {e}")
            final_url = url

        # 2. Extract SEO & Performance Metrics
        if html:
            seo_results = seo_auditor.audit_html(html, url=final_url)
            design_results = design_lens.extract_design_system(html, url=final_url)
        else:
            seo_results = {"overall_seo_score": 0, "error": fetch_error}
            design_results = {"palette": design_lens.DEFAULT_FALLBACK_PALETTE, "error": fetch_error}

        # 3. Harvest Business Leads & Contacts
        lead_results = scraper.extract_niche_leads_and_contacts(
            niche=target,
            target_urls=[final_url],
            max_pages=max_pages
        )

        return {
            "target": target,
            "resolved_url": final_url,
            "status": "success" if html else "partial_failure",
            "seo_audit": seo_results,
            "design_lens": design_results,
            "lead_intelligence": lead_results,
            "summary": {
                "seo_score": seo_results.get("overall_seo_score", 0),
                "leads_found_count": lead_results.get("leads_extracted") if isinstance(lead_results.get("leads_extracted"), int) else len(lead_results.get("leads_extracted", [])),
                "wcag_compliance": design_results.get("contrast", {}).get("wcag_compliance", "Unknown"),
                "dominant_font": design_results.get("typography", {}).get("heading_font", "Inter")
            }
        }


webradar_suite = WebRadarSuite()
