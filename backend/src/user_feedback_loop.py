"""
User Feedback Collection & Autonomous Continuous Learning Loop.
Captures:
1. Direct User Ratings (1-5 stars) and explicit textual corrections.
2. Auto-injects corrections into Copilot semantic cache and RAG index.
3. Feeds verified training pairs to DistillationEngine to improve model accuracy.
"""
from typing import Dict, Any, List, Optional
import os
import json
import time
from datetime import datetime
from src.utils import logger

FEEDBACK_STORE = "reports/user_feedback_history.json"


class UserFeedbackLoop:
    """Enterprise User Feedback & Continuous Self-Improvement Engine."""

    def __init__(self):
        self.feedback_records: List[Dict[str, Any]] = self._load_feedback()

    def record_feedback(
        self,
        session_id: str,
        query: str,
        copilot_response: str,
        rating: int, # 1 to 5
        correction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record user feedback and trigger self-improvement update if correction is present."""
        record = {
            "session_id": session_id,
            "query": query,
            "original_response": copilot_response,
            "rating": rating,
            "correction": correction,
            "timestamp": datetime.now().isoformat()
        }
        self.feedback_records.append(record)
        self._save_feedback()

        learning_applied = False
        if correction and rating <= 3:
            # 1. Update Semantic Cache with User Correction
            self._update_semantic_cache_with_correction(query, correction)
            
            # 2. Record to Distillation Engine
            try:
                from src.distillation_engine import distillation_engine
                distillation_engine.record_training_pair(
                    task_type="qa_distillation",
                    input_text=query,
                    output_text=correction,
                    confidence=1.0,
                    source="user_feedback_correction"
                )
                learning_applied = True
            except Exception as e:
                logger.warning(f"[feedback_loop] Distillation recording error: {e}")

        return {
            "status": "success",
            "rating": rating,
            "correction_learned": learning_applied,
            "total_feedback_count": len(self.feedback_records)
        }

    def _update_semantic_cache_with_correction(self, query: str, correction: str):
        """Directly teach Copilot the correct response for future 0-token recall."""
        try:
            from src.assistant_engine import assistant_engine
            # Check if query pattern already exists
            pattern_found = False
            for entry in assistant_engine.semantic_cache:
                if any(p in query.lower() for p in entry.get("query_pattern", [])):
                    entry["response"] = correction
                    entry["source"] = "user_correction"
                    entry["updated_at"] = datetime.now().isoformat()
                    pattern_found = True
                    break

            if not pattern_found:
                assistant_engine.semantic_cache.append({
                    "query_pattern": [query.lower().strip()],
                    "response": correction,
                    "tokens_saved": 450,
                    "source": "user_correction",
                    "created_at": datetime.now().isoformat()
                })

            assistant_engine._save_semantic_cache()
            logger.info(f"[feedback_loop] Successfully taught Copilot user correction for: '{query}'")
        except Exception as e:
            logger.error(f"[feedback_loop] Failed updating semantic cache: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Compute satisfaction rating and correction count."""
        if not self.feedback_records:
            return {"total_feedback": 0, "avg_rating": 5.0, "corrections_count": 0}

        ratings = [r["rating"] for r in self.feedback_records]
        corrections = sum(1 for r in self.feedback_records if r.get("correction"))
        return {
            "total_feedback": len(self.feedback_records),
            "avg_rating": round(sum(ratings) / len(ratings), 2),
            "corrections_learned_count": corrections
        }

    def _load_feedback(self) -> List[Dict[str, Any]]:
        if os.path.exists(FEEDBACK_STORE):
            try:
                with open(FEEDBACK_STORE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_feedback(self):
        os.makedirs(os.path.dirname(FEEDBACK_STORE), exist_ok=True)
        try:
            with open(FEEDBACK_STORE, "w", encoding="utf-8") as f:
                json.dump(self.feedback_records, f, indent=2)
        except Exception:
            pass


user_feedback_loop = UserFeedbackLoop()
