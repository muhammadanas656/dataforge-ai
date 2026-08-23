"""
Knowledge Conflict Detection & Resolution Engine.
Identifies contradictions between newly ingested crawled knowledge, user corrections, and existing RAG vectors.
"""
from typing import Dict, Any, List, Optional, NamedTuple
from datetime import datetime
from src.utils import logger


class ConflictItem(NamedTuple):
    topic: str
    existing_claim: str
    new_claim: str
    existing_freshness: float
    new_freshness: float
    resolution_action: str
    winning_claim: str
    confidence: float


class ConflictResolver:
    """Detects and resolves conflicting knowledge claims in Assistant RAG."""

    def detect_and_resolve(
        self,
        topic: str,
        existing_claim: str,
        new_claim: str,
        existing_freshness: float = 0.5,
        new_freshness: float = 0.9,
        is_user_correction: bool = False
    ) -> ConflictItem:
        """Evaluate conflicting statements and determine resolution strategy."""
        ex_clean = existing_claim.strip()
        new_clean = new_claim.strip()

        # Direct User Correction always overrides with 1.0 confidence
        if is_user_correction:
            return ConflictItem(
                topic=topic,
                existing_claim=ex_clean,
                new_claim=new_clean,
                existing_freshness=existing_freshness,
                new_freshness=1.0,
                resolution_action="replace",
                winning_claim=new_clean,
                confidence=1.0
            )

        # Freshness strategy: newer crawl updates older crawl
        if new_freshness > existing_freshness:
            return ConflictItem(
                topic=topic,
                existing_claim=ex_clean,
                new_claim=new_clean,
                existing_freshness=existing_freshness,
                new_freshness=new_freshness,
                resolution_action="replace",
                winning_claim=new_clean,
                confidence=0.88
            )

        # Both valid: preserve versioned multi-context
        versioned_claim = f"[Legacy/v1] {ex_clean} | [Updated/v2] {new_clean}"
        return ConflictItem(
            topic=topic,
            existing_claim=ex_clean,
            new_claim=new_clean,
            existing_freshness=existing_freshness,
            new_freshness=new_freshness,
            resolution_action="version",
            winning_claim=versioned_claim,
            confidence=0.75
        )


conflict_resolver = ConflictResolver()
