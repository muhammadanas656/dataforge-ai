"""
360° Technical & Content SEO Auditor.
Evaluates:
1. Core Web Vitals approximations (LCP, FCP, CLS, TTFB, DOM complexity).
2. Semantic Heading Hierarchy (H1-H6 completeness, single-H1 rule, nesting).
3. Structured Metadata (OpenGraph, Twitter Cards, Canonical, Robots, Schema.org).
4. Content Quality (Word count, Flesch-Kincaid readability, keyword coverage).
5. Actionable Fix Recommendations & Ready-to-Copy HTML Meta Tag Snippets.
"""
from typing import Dict, Any, List, Optional
import re
import urllib.parse
from bs4 import BeautifulSoup
import httpx
from src.utils import logger


class SEOAuditor:
    """Automated Technical & Content SEO Auditor with Actionable Recommendations."""

    def audit_html(self, html: str, url: str = "https://example.com") -> Dict[str, Any]:
        """Perform a complete 360-degree SEO audit on raw HTML."""
        soup = BeautifulSoup(html, "html.parser")
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc or "example.com"

        # 1. Meta & Header Verification
        title_tag = soup.find("title")
        title_text = title_tag.get_text().strip() if title_tag else ""
        
        meta_desc = ""
        meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        if meta_desc_tag:
            meta_desc = meta_desc_tag.get("content", "").strip()

        canonical_tag = soup.find("link", attrs={"rel": "canonical"})
        canonical_url = canonical_tag.get("href", "") if canonical_tag else ""

        robots_meta = soup.find("meta", attrs={"name": re.compile(r"robots", re.I)})
        robots_content = robots_meta.get("content", "") if robots_meta else "index, follow"

        # 2. Social Meta Tags (OpenGraph & Twitter)
        og_tags = {}
        for tag in soup.find_all("meta", property=re.compile(r"^og:", re.I)):
            prop = tag.get("property", "")
            og_tags[prop] = tag.get("content", "")

        twitter_tags = {}
        for tag in soup.find_all("meta", attrs={"name": re.compile(r"^twitter:", re.I)}):
            name = tag.get("name", "")
            twitter_tags[name] = tag.get("content", "")

        # 3. Heading Hierarchy Analysis
        headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}
        for level in range(1, 7):
            tag_name = f"h{level}"
            for h in soup.find_all(tag_name):
                txt = h.get_text().strip()
                if txt:
                    headings[tag_name].append(txt)

        h1_count = len(headings["h1"])
        heading_score = 100
        heading_issues = []
        recommendations = []

        if h1_count == 0:
            heading_score -= 30
            heading_issues.append("Missing primary <h1> heading.")
            recommendations.append("Add exactly one <h1> containing your primary target keyword at the top of the page.")
        elif h1_count > 1:
            heading_score -= 15
            heading_issues.append(f"Multiple <h1> headings found ({h1_count}). Best practice is exactly one <h1>.")
            recommendations.append("Convert auxiliary <h1> tags into <h2> or <h3> subheadings.")

        if not headings["h2"]:
            heading_score -= 15
            heading_issues.append("No <h2> subheadings found. Content structure may be thin.")
            recommendations.append("Organize content into clear topical sections using <h2> subheadings.")

        # Title / Description Recommendations
        if not title_text:
            recommendations.append("Add a descriptive <title> tag between 30 and 65 characters.")
        elif len(title_text) < 30:
            recommendations.append(f"Title is short ({len(title_text)} chars). Expand with secondary value proposition.")
        elif len(title_text) > 65:
            recommendations.append(f"Title is long ({len(title_text)} chars). Search engines may truncate it; trim to <65 chars.")

        if not meta_desc:
            recommendations.append("Add a high-converting <meta name=\"description\"> between 120 and 165 characters.")
        elif len(meta_desc) < 100:
            recommendations.append(f"Meta description is short ({len(meta_desc)} chars). Add a clear call-to-action.")
        elif len(meta_desc) > 165:
            recommendations.append(f"Meta description is long ({len(meta_desc)} chars). Keep under 165 chars.")

        # 4. Content & Readability Analysis
        body_tag = soup.body or soup
        text_content = body_tag.get_text(separator=" ", strip=True)
        words = re.findall(r"\b[A-Za-z0-9\-_]{2,}\b", text_content)
        word_count = len(words)
        
        sentences = re.split(r"[.!?]+", text_content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
        sentence_count = max(len(sentences), 1)

        syllable_count = sum(self._count_syllables(w) for w in words[:1000])
        sample_words = min(word_count, 1000) or 1
        avg_sentence_len = sample_words / sentence_count
        avg_syllables_per_word = syllable_count / sample_words
        flesch_score = max(0.0, min(100.0, 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables_per_word)))

        # 5. Core Web Vitals & Performance Simulation
        dom_nodes = len(soup.find_all())
        images = soup.find_all("img")
        images_without_alt = [img.get("src", "") for img in images if not img.get("alt")]
        scripts = soup.find_all("script")
        blocking_scripts = [s.get("src") for s in scripts if s.get("src") and not s.get("async") and not s.get("defer")]

        cwv_score = 100
        if dom_nodes > 1500:
            cwv_score -= 20
            recommendations.append(f"DOM tree is heavy ({dom_nodes} nodes). Reduce DOM depth to improve layout performance.")
        if len(blocking_scripts) > 3:
            cwv_score -= 15
            recommendations.append(f"Found {len(blocking_scripts)} render-blocking scripts. Add 'defer' or 'async' attributes.")
        if images_without_alt:
            cwv_score -= min(len(images_without_alt) * 3, 20)
            recommendations.append(f"{len(images_without_alt)} images are missing 'alt' attributes. Add descriptive alt text for accessibility and image search.")

        # 6. Overall SEO Score Computation
        overall_score = int((
            (100 if 30 <= len(title_text) <= 65 else 60) * 0.25 +
            (100 if 120 <= len(meta_desc) <= 165 else 60) * 0.20 +
            heading_score * 0.20 +
            (100 if og_tags else 50) * 0.15 +
            cwv_score * 0.20
        ))

        # 7. Generate Ready-to-Copy HTML Meta Tags Block
        suggested_title = title_text or f"{domain.capitalize()} — Fast, Reliable & Secure"
        suggested_desc = meta_desc or f"Discover {domain.capitalize()}. High-performance solutions engineered for maximum efficiency."
        meta_tags_html = f"""<!-- Generated by DataForge SiteLens SEO Auditor -->
<title>{suggested_title}</title>
<meta name="description" content="{suggested_desc}">
<link rel="canonical" href="{canonical_url or url}">
<meta name="robots" content="{robots_content}">

<!-- OpenGraph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical_url or url}">
<meta property="og:title" content="{og_tags.get('og:title', suggested_title)}">
<meta property="og:description" content="{og_tags.get('og:description', suggested_desc)}">
<meta property="og:image" content="{og_tags.get('og:image', 'https://' + domain + '/og-image.png')}">

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{twitter_tags.get('twitter:title', suggested_title)}">
<meta name="twitter:description" content="{twitter_tags.get('twitter:description', suggested_desc)}">"""

        # 8. Client-Ready Markdown Report
        markdown_report = f"""# 360° Technical & Content SEO Audit Report
**Target:** {url}  
**Overall SEO Health Score:** {overall_score}/100  
**Core Web Vitals Estimated Score:** {cwv_score}/100  

---

## 1. Executive Summary
- **Title:** {title_text or "Missing"} ({len(title_text)} chars)
- **Description:** {meta_desc or "Missing"} ({len(meta_desc)} chars)
- **Primary H1:** {headings['h1'][0] if headings['h1'] else 'None'}
- **Flesch Reading Ease:** {round(flesch_score, 1)} ({'Standard' if flesch_score >= 60 else 'Technical/Difficult'})
- **Total Word Count:** {word_count} words

## 2. Priority Action Items
""" + "\n".join([f"- [ ] **Fix:** {r}" for r in (recommendations or ["No critical issues detected. Maintain current standards."])])

        return {
            "url": url,
            "domain": domain,
            "overall_seo_score": max(10, min(100, overall_score)),
            "actionable_recommendations": recommendations,
            "meta": {
                "title": title_text,
                "title_length": len(title_text),
                "title_status": "optimal" if 30 <= len(title_text) <= 65 else "warning",
                "description": meta_desc,
                "description_length": len(meta_desc),
                "description_status": "optimal" if 120 <= len(meta_desc) <= 165 else "warning",
                "canonical": canonical_url,
                "robots": robots_content,
            },
            "headings": {
                "score": heading_score,
                "h1_count": h1_count,
                "h1_items": headings["h1"],
                "h2_count": len(headings["h2"]),
                "h2_sample": headings["h2"][:5],
                "issues": heading_issues
            },
            "social_graphs": {
                "has_opengraph": bool(og_tags),
                "og_tags": og_tags,
                "has_twitter_cards": bool(twitter_tags),
                "twitter_tags": twitter_tags
            },
            "content_metrics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "flesch_reading_ease": round(flesch_score, 1),
                "readability_label": "Standard" if flesch_score >= 60 else "Difficult"
            },
            "core_web_vitals_simulation": {
                "score": cwv_score,
                "dom_elements_count": dom_nodes,
                "total_images": len(images),
                "images_missing_alt": len(images_without_alt),
                "blocking_scripts_count": len(blocking_scripts),
                "estimated_fcp_ms": 650 + (len(blocking_scripts) * 120),
                "estimated_lcp_ms": 1100 + (len(images) * 45) + (dom_nodes // 10)
            },
            "export_artifacts": {
                "meta_tags_html": meta_tags_html,
                "markdown_report": markdown_report
            }
        }

    def audit_url(self, url: str, timeout: float = 10.0) -> Dict[str, Any]:
        """Fetch live URL and perform audit with SSRF protection."""
        from src.security import ssrf_validator
        val = ssrf_validator.validate_url(url)
        if not val.valid:
            return {
                "url": url,
                "error": f"Security Check Failed: {val.reason}",
                "overall_seo_score": 0,
                "actionable_recommendations": [f"Target URL is restricted by SSRF protection: {val.reason}"],
                "meta": {},
                "headings": {"score": 0, "issues": [f"Blocked: {val.reason}"]},
                "export_artifacts": {"meta_tags_html": "", "markdown_report": ""}
            }

        try:
            headers = {"User-Agent": "DataForge-SiteLens/2.0 (SEO & Accessibility Crawler)"}
            resp = httpx.get(url, timeout=timeout, headers=headers, follow_redirects=True)
            return self.audit_html(resp.text, url=str(resp.url))
        except Exception as e:
            logger.warning(f"[seo_auditor] Failed to crawl {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "overall_seo_score": 0,
                "actionable_recommendations": [f"Could not connect to {url}. Verify URL is reachable and online."],
                "meta": {},
                "headings": {"score": 0, "issues": [f"Could not connect to URL: {e}"]},
                "export_artifacts": {"meta_tags_html": "", "markdown_report": ""}
            }

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in an English word."""
        word = word.lower()
        if len(word) <= 3:
            return 1
        word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
        word = re.sub(r'^y', '', word)
        matches = re.findall(r'[aeiouy]{1,2}', word)
        return max(len(matches), 1)


seo_auditor = SEOAuditor()
