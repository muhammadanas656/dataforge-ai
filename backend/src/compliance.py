"""
Legal & Crawl Compliance Engine.
Implements:
1. LegalComplianceChecker: Parses target domain robots.txt using urllib.robotparser.
2. TermsOfServiceAdvisor: Inspects public /terms and /tos for automated scraping prohibitions.
"""
from typing import Dict, Any, Optional
import urllib.robotparser
from urllib.parse import urlparse
import httpx
from src.security import ssrf_validator
from src.utils import logger


class ComplianceResult:
    def __init__(self, allowed: bool, crawl_delay: Optional[float] = None, reason: str = "", warning: bool = False):
        self.allowed = allowed
        self.crawl_delay = crawl_delay
        self.reason = reason
        self.warning = warning

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "crawl_delay": self.crawl_delay,
            "reason": self.reason,
            "warning": self.warning
        }


class LegalComplianceChecker:
    """Verifies domain crawling permissions against robots.txt and Terms of Service."""

    USER_AGENT = "DataForgeAI/2.0 (+https://dataforge.ai/bot; bot@dataforge.ai)"

    async def check_robots_txt(self, url: str, timeout: float = 5.0) -> ComplianceResult:
        """Check if target URL is allowed by domain robots.txt."""
        val = ssrf_validator.validate_url(url)
        if not val.valid:
            return ComplianceResult(allowed=False, reason=f"Security check failed: {val.reason}")

        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                resp = await client.get(robots_url, headers={"User-Agent": self.USER_AGENT})
                if resp.status_code == 404:
                    return ComplianceResult(
                        allowed=True,
                        reason="robots.txt returned 404; crawling permitted by standard convention."
                    )
                elif resp.status_code != 200:
                    return ComplianceResult(
                        allowed=True,
                        warning=True,
                        reason=f"robots.txt returned HTTP {resp.status_code}; proceeding with standard politeness."
                    )

                rp = urllib.robotparser.RobotFileParser()
                rp.parse(resp.text.splitlines())

                allowed = rp.can_fetch(self.USER_AGENT, url)
                crawl_delay = rp.crawl_delay(self.USER_AGENT)

                if not allowed:
                    return ComplianceResult(
                        allowed=False,
                        reason=f"Crawling disallowed by robots.txt rule for user agent '{self.USER_AGENT}'."
                    )

                return ComplianceResult(
                    allowed=True,
                    crawl_delay=crawl_delay,
                    reason="Crawling verified and permitted by robots.txt."
                )
        except Exception as e:
            logger.warning(f"[compliance] robots.txt check failed for {robots_url}: {e}")
            return ComplianceResult(
                allowed=True,
                warning=True,
                reason=f"Could not connect to robots.txt: {e}. Defaulting to polite crawl."
            )

    async def check_terms_of_service(self, url: str, timeout: float = 5.0) -> ComplianceResult:
        """Inspect common /terms or /tos endpoints for automated access restrictions."""
        val = ssrf_validator.validate_url(url)
        if not val.valid:
            return ComplianceResult(allowed=False, reason=f"Security check failed: {val.reason}")

        parsed = urlparse(url)
        domain = parsed.netloc
        candidates = [f"{parsed.scheme}://{domain}/terms", f"{parsed.scheme}://{domain}/tos"]

        prohibitions = ["unauthorized scraping", "automated extraction", "harvesting data", "reverse engineering"]

        for cand in candidates:
            try:
                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    resp = await client.get(cand, headers={"User-Agent": self.USER_AGENT})
                    if resp.status_code == 200:
                        text_lower = resp.text.lower()
                        found = [p for p in prohibitions if p in text_lower]
                        if found:
                            return ComplianceResult(
                                allowed=True,
                                warning=True,
                                reason=f"Terms of Service mentions: {', '.join(found)}. Ensure compliance with site policy."
                            )
                        return ComplianceResult(
                            allowed=True,
                            reason="No explicit automated scraping prohibition detected in /terms."
                        )
            except Exception:
                continue

        return ComplianceResult(
            allowed=True,
            reason="Terms of service endpoint not found; proceeding with polite crawl."
        )


legal_compliance = LegalComplianceChecker()
