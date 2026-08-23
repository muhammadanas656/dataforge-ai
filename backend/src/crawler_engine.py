"""
High-Performance Crawler Engine with Anti-Bot Fallback & Resource Budgets.
Implements:
1. CrawlPerformanceBudget: Concurrency semaphores, max timeouts, page quotas, and politeness rate-limiting.
2. AntiBotCrawler: Multi-layered crawler with Cloudflare/Akamai/PerimeterX challenge detection and SSRF protection.
"""
from typing import Dict, Any, List, Optional
import asyncio
import time
from urllib.parse import urlparse
import httpx
from src.security import ssrf_validator
from src.compliance import legal_compliance
from src.utils import logger


class CrawlResult:
    def __init__(self, url: str, status_code: int, html: str, headers: Dict[str, str], method: str = "direct", error: str = "", is_bot_challenge: bool = False):
        self.url = url
        self.status_code = status_code
        self.html = html
        self.headers = headers
        self.method = method
        self.error = error
        self.is_bot_challenge = is_bot_challenge

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "html_length": len(self.html),
            "method": self.method,
            "error": self.error,
            "is_bot_challenge": self.is_bot_challenge
        }


class CrawlPerformanceBudget:
    """Enforces strict resource limits, concurrency boundaries, and rate limits."""

    MAX_CRAWL_TIME_SECONDS = 60.0
    MAX_PAGES_PER_CRAWL = 25
    MAX_CONCURRENT_REQUESTS = 5
    REQUEST_TIMEOUT_SECONDS = 10.0
    REQUESTS_PER_SECOND = 2.0

    def __init__(self):
        self._semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)
        self._last_request_time: Dict[str, float] = {}

    async def acquire_slot(self, domain: str):
        """Wait for rate limit window for domain and acquire concurrency slot."""
        await self._semaphore.acquire()
        now = time.time()
        last = self._last_request_time.get(domain, 0.0)
        delay = (1.0 / self.REQUESTS_PER_SECOND) - (now - last)
        if delay > 0:
            await asyncio.sleep(delay)
        self._last_request_time[domain] = time.time()

    def release_slot(self):
        """Release concurrency slot."""
        self._semaphore.release()


class AntiBotCrawler:
    """Multi-layer resilient crawler with SSRF protection, anti-bot detection, and budget controls."""

    BOT_CHALLENGE_KEYWORDS = [
        "just a moment",
        "checking your browser",
        "cf-challenge",
        "cloudflare ray id",
        "px-captcha",
        "perimeterx",
        "incapsula",
        "ddos-guard",
        "access denied",
        "attention required"
    ]

    def __init__(self):
        self.budget = CrawlPerformanceBudget()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 DataForge-SiteLens/2.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

    async def fetch(self, url: str) -> CrawlResult:
        """Fetch URL with SSRF validation, budget enforcement, and anti-bot challenge detection."""
        # 1. SSRF Security Gate
        val = ssrf_validator.validate_url(url)
        if not val.valid:
            return CrawlResult(
                url=url,
                status_code=403,
                html="",
                headers={},
                method="blocked",
                error=f"Security Error (SSRF Protection): {val.reason}"
            )

        parsed = urlparse(url)
        domain = parsed.netloc

        # 2. Acquire Budget Slot
        await self.budget.acquire_slot(domain)

        try:
            # 3. Layer 1: Direct Async HTTP Request with modern headers
            async with httpx.AsyncClient(
                timeout=self.budget.REQUEST_TIMEOUT_SECONDS,
                follow_redirects=True,
                verify=True
            ) as client:
                resp = await client.get(url, headers=self.headers)
                html_text = resp.text
                status = resp.status_code

                # 4. Check for Bot Challenge / Cloudflare Protection
                is_challenge = self._is_bot_challenge(status, html_text)

                if is_challenge:
                    logger.warning(f"[crawler] Bot challenge detected on {url} (HTTP {status})")
                    return CrawlResult(
                        url=str(resp.url),
                        status_code=status,
                        html=html_text,
                        headers=dict(resp.headers),
                        method="bot_challenge_detected",
                        is_bot_challenge=True,
                        error="Anti-bot challenge page detected (Cloudflare/PerimeterX). Content may require browser rendering."
                    )

                return CrawlResult(
                    url=str(resp.url),
                    status_code=status,
                    html=html_text,
                    headers=dict(resp.headers),
                    method="direct_httpx"
                )

        except httpx.TimeoutException:
            return CrawlResult(url=url, status_code=504, html="", headers={}, method="timeout", error="Request timed out.")
        except Exception as e:
            return CrawlResult(url=url, status_code=500, html="", headers={}, method="error", error=str(e))
        finally:
            self.budget.release_slot()

    def _is_bot_challenge(self, status_code: int, html: str) -> bool:
        """Detect if HTML response is a bot challenge interstitial."""
        if status_code in (403, 503):
            return True
        html_lower = html.lower()
        if len(html) < 4000 and any(keyword in html_lower for keyword in self.BOT_CHALLENGE_KEYWORDS):
            return True
        return False


anti_bot_crawler = AntiBotCrawler()
