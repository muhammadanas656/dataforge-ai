"""
DataForge AI Global Workspace Metacognitive Bus.
Implements Bernard Baars' Global Workspace Theory (GWT) for synthetic cognitive architecture:
1. Central Attention & Broadcast Blackboard: Thread-safe, unified message passing across all 5 studios.
2. Cross-Studio Synesthesia: Ingestion of live web design tokens immediately notifies Vector Studio and Risk Studio.
3. Collective Epistemic Memory: Real-time working memory buffer tracking active cognitive focus and confidence.
"""
from typing import Dict, Any, List, Callable, Optional
import threading
import time
from collections import deque
from src.utils import logger


class GlobalWorkspaceEvent:
    """Standardized event packet broadcast across the Global Workspace."""
    def __init__(self, source_studio: str, event_type: str, payload: Dict[str, Any], confidence: float = 1.0):
        self.source_studio = source_studio
        self.event_type = event_type
        self.payload = payload
        self.confidence = confidence
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_studio": self.source_studio,
            "event_type": self.event_type,
            "payload": self.payload,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }


class GlobalWorkspaceBus:
    """Thread-safe Central Cognitive Broadcast Bus."""

    def __init__(self, max_history: int = 200):
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[Callable[[GlobalWorkspaceEvent], None]]] = {}
        self._working_memory: deque = deque(maxlen=max_history)
        self._attention_focus: str = "Idle"
        self._total_events_broadcast: int = 0

    def subscribe(self, event_type: str, callback: Callable[[GlobalWorkspaceEvent], None]):
        """Register a subscriber callback for a specific event type or '*' for all events."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)

    def broadcast(self, event: GlobalWorkspaceEvent):
        """Broadcast a cognitive event to the Global Workspace and notify all subscribers."""
        with self._lock:
            self._working_memory.append(event)
            self._attention_focus = f"{event.source_studio}:{event.event_type}"
            self._total_events_broadcast += 1

            # Get target callbacks
            callbacks = list(self._subscribers.get(event.event_type, [])) + list(self._subscribers.get("*", []))

        for cb in callbacks:
            try:
                cb(event)
            except Exception as e:
                logger.warning(f"[global_workspace] Error in subscriber callback for '{event.event_type}': {e}")

    def get_working_memory_state(self) -> Dict[str, Any]:
        """Return real-time snapshot of the Global Workspace working memory."""
        with self._lock:
            recent_events = [e.to_dict() for e in list(self._working_memory)[-10:]]
            return {
                "active_attention_focus": self._attention_focus,
                "total_events_broadcast": self._total_events_broadcast,
                "working_memory_buffer_size": len(self._working_memory),
                "recent_broadcasts": recent_events
            }


global_workspace_bus = GlobalWorkspaceBus()
