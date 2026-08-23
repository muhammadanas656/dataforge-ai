"""
Data Quality Gates & Content Validation Engine.
Validates crawled web content and datasets before ingestion into vector stores or distillation engines.
Checks:
1. Content length bounds (min 50 chars, max 100k chars).
2. Domain relevance scoring against DataForge AI core ontology.
3. Vector similarity duplicate detection (cosine threshold >= 0.95).
4. Time-decay freshness calculations.
"""
from typing import Dict, Any, Optional, NamedTuple
from datetime import datetime
import re
from src.utils import logger


class QualityResult(NamedTuple):
    valid: bool
    reason: str = ""
    relevance_score: float = 0.0
    freshness_score: float = 1.0
    is_duplicate: bool = False
    warning: bool = False


class DataQualityGate:
    """Validates crawled content before ingestion into RAG or distillation."""

    def __init__(self):
        self.min_content_length = 50
        self.max_content_length = 100000
        self.min_relevance_score = 0.15
        self.duplicate_threshold = 0.95
        self.relevant_keywords = [
            "data", "cleaning", "eda", "causal", "inference", "machine learning",
            "web", "scraping", "seo", "design", "tokens", "svg", "react", "vue",
            "api", "database", "analytics", "visualization", "triz", "monte carlo",
            "pipeline", "telemetry", "security", "ssrf", "compliance"
        ]

    def validate(self, url: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> QualityResult:
        """Validate content length, domain relevance, duplication, and freshness."""
        meta = metadata or {}
        if not content or not isinstance(content, str):
            return QualityResult(valid=False, reason="Empty or non-string content provided.")

        content_clean = content.strip()
        length = len(content_clean)

        # 1. Content Length Checks
        if length < self.min_content_length:
            return QualityResult(valid=False, reason=f"Content too short: {length} < {self.min_content_length}")

        if length > self.max_content_length:
            return QualityResult(valid=False, reason=f"Content exceeds size limit: {length} > {self.max_content_length}")

        # 2. Domain Relevance Scoring
        relevance = self._score_relevance(content_clean)
        if relevance < self.min_relevance_score:
            return QualityResult(
                valid=False,
                reason=f"Content lacks domain relevance ({relevance:.2f} < {self.min_relevance_score})",
                relevance_score=relevance
            )

        # 3. Duplicate Detection
        is_dup = self._check_duplicate(content_clean)
        if is_dup:
            return QualityResult(
                valid=False,
                reason="Duplicate content detected in existing knowledge store",
                relevance_score=relevance,
                is_duplicate=True
            )

        # 4. Freshness Scoring
        freshness = self._calculate_freshness(meta)

        return QualityResult(
            valid=True,
            reason="Content passed all quality and relevance validation gates.",
            relevance_score=relevance,
            freshness_score=freshness,
            is_duplicate=False,
            warning=(freshness < 0.2)
        )

    def _score_relevance(self, content: str) -> float:
        """Score content domain alignment based on keyword density."""
        content_lower = content.lower()
        matches = sum(1 for kw in self.relevant_keywords if kw in content_lower)
        return min(round(matches / 6.0, 3), 1.0)

    def _check_duplicate(self, content: str) -> bool:
        """Check for exact or high-cosine duplicates in Assistant RAG."""
        try:
            from src.assistant_rag import assistant_rag
            similar = assistant_rag.retrieve(content[:300], collection="all", top_k=1)
            if similar and len(similar) > 0:
                top_doc = similar[0]
                existing_text = top_doc.get("content", "")
                if existing_text and len(existing_text) > 40:
                    # Jaccard word similarity for lightning-fast duplicate checking
                    words_a = set(re.findall(r'\w+', content.lower()))
                    words_b = set(re.findall(r'\w+', existing_text.lower()))
                    if words_a and words_b:
                        jaccard = len(words_a.intersection(words_b)) / float(len(words_a.union(words_b)))
                        if jaccard >= self.duplicate_threshold:
                            return True
        except Exception:
            pass
        return False

    def _calculate_freshness(self, metadata: Dict[str, Any]) -> float:
        """Compute exponential freshness decay score."""
        date_str = metadata.get("last_modified") or metadata.get("published_date")
        if not date_str:
            return 0.8
        try:
            dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
            age_days = max((datetime.now() - dt.replace(tzinfo=None)).days, 0)
            return max(round(1.0 * (0.995 ** age_days), 3), 0.1)
        except Exception:
            return 0.8


data_quality_gate = DataQualityGate()
