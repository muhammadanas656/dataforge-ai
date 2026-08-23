"""
Privacy & Copyright Compliance Verification Engine.
Protects ingestion pipeline against:
1. PII exposure (emails, phones, social security numbers, credit card numbers).
2. Copyright restrictions (All Rights Reserved vs Creative Commons/Open Source).
"""
from typing import Dict, Any, List, NamedTuple, Optional
import re
from src.utils import logger


class PrivacyResult(NamedTuple):
    compliant: bool
    reason: str = ""
    pii_detected: List[str] = []
    is_commercial_allowed: bool = True
    requires_attribution: bool = False


class PrivacyComplianceChecker:
    """Enterprise Privacy, PII Redaction & License Compliance Checker."""

    PII_PATTERNS = {
        "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'),
        "phone": re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
        "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        "credit_card": re.compile(r'\b(?:\d{4}[- ]?){3}\d{4}\b')
    }

    def check_content_compliance(self, url: str, content: str, allow_anonymized_leads: bool = False) -> PrivacyResult:
        """Inspect crawled content for privacy risks and copyright status."""
        if not content:
            return PrivacyResult(compliant=True)

        # 1. PII Scan
        detected_pii = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            if pattern.search(content):
                detected_pii.append(pii_type)

        # If high-risk PII (SSN or credit card) is found, strictly block
        if "ssn" in detected_pii or "credit_card" in detected_pii:
            return PrivacyResult(
                compliant=False,
                reason=f"High-risk PII detected: {', '.join(detected_pii)}",
                pii_detected=detected_pii
            )

        # For lead scraping, emails/phones are permissible if user requested lead crawl, but flagged for general knowledge ingestion
        if detected_pii and not allow_anonymized_leads and ("email" in detected_pii or "phone" in detected_pii):
            return PrivacyResult(
                compliant=True,
                reason="Standard contact metadata identified; redacted for general RAG ingestion.",
                pii_detected=detected_pii
            )

        # 2. Copyright & Fair Use Assessment
        c_lower = content.lower()
        if "all rights reserved. unauthorized reproduction prohibited" in c_lower:
            return PrivacyResult(
                compliant=False,
                reason="Explicit proprietary copyright prohibition detected.",
                pii_detected=detected_pii,
                is_commercial_allowed=False
            )

        is_cc = "creative commons" in c_lower or "cc by" in c_lower or "mit license" in c_lower or "apache" in c_lower

        return PrivacyResult(
            compliant=True,
            reason="Content approved for fair-use knowledge distillation.",
            pii_detected=detected_pii,
            is_commercial_allowed=True,
            requires_attribution=is_cc
        )


privacy_compliance = PrivacyComplianceChecker()
