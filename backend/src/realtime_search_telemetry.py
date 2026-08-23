"""
Real-Time Web Search & Crawler Telemetry Broadcast Engine.
Tracks and streams live real-time operational status of:
1. Individual websites currently being searched/crawled.
2. Active pipeline stage (SSRF Pre-Flight, DOM Extraction, Quality Gates, Distillation).
3. Live bandwidth, thread concurrency, and vector tokens discovered.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque
import threading
from src.utils import logger


class RealtimeSearchTelemetry:
    """Enterprise Real-Time Web Crawler and Search Status Broadcaster."""

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
        self.active_searches: Dict[str, Dict[str, Any]] = {}
        self.total_sites_searched = 0
        self.total_bandwidth_kb = 0.0
        self.total_tokens_discovered = 0
        self._lock = threading.Lock()

    def record_search_event(
        self,
        url: str,
        stage: str = "SSRF Pre-Flight Check",
        tokens_found: int = 0,
        bytes_downloaded: int = 0
    ) -> Dict[str, Any]:
        """Record live event for an individual target website."""
        with self._lock:
            now_iso = datetime.now().isoformat()
            kb = round(bytes_downloaded / 1024.0, 2)
            self.total_bandwidth_kb += kb
            self.total_tokens_discovered += tokens_found

            event_data = {
                "url": url,
                "stage": stage,
                "tokens_found": tokens_found,
                "bandwidth_kb": kb,
                "timestamp": now_iso
            }

            self.active_searches[url] = event_data
            self.history.append(event_data)
            self.total_sites_searched += 1

            return event_data

    def finish_search_event(self, url: str, status: str = "completed"):
        """Mark search event complete for an individual target website."""
        with self._lock:
            if url in self.active_searches:
                self.active_searches[url]["status"] = status
                self.active_searches[url]["completed_at"] = datetime.now().isoformat()

    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        """Return real-time snapshot for UI dashboards and streaming SSE."""
        with self._lock:
            recent_events = list(self.history)[-10:]
            current_active = list(self.active_searches.values())[-5:]
            return {
                "status": "online",
                "total_sites_searched": self.total_sites_searched,
                "total_bandwidth_kb": round(self.total_bandwidth_kb, 2),
                "total_tokens_discovered": self.total_tokens_discovered,
                "active_targets_count": len(self.active_searches),
                "current_active_searches": current_active,
                "recent_search_feed": recent_events,
                "timestamp": datetime.now().isoformat()
            }


search_telemetry = RealtimeSearchTelemetry()
