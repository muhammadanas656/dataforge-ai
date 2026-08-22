"""Global context manager for cross-module awareness in DataForge AI."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path

@dataclass
class UserContext:
    """Tracks user's current state across the system."""
    workspace_id: str = "default"
    active_dataset_id: Optional[str] = None
    active_module: str = "overview"  # research, cleaning, eda, analyst, report, explain, etc.
    active_page: str = "/"
    recent_actions: List[Dict[str, Any]] = field(default_factory=list)
    recent_errors: List[Dict[str, Any]] = field(default_factory=list)
    skill_level: str = "intermediate"  # beginner, intermediate, advanced
    session_start: datetime = field(default_factory=datetime.now)
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "active_dataset_id": self.active_dataset_id,
            "active_module": self.active_module,
            "active_page": self.active_page,
            "recent_actions": self.recent_actions[-10:],  # Last 10 actions
            "recent_errors": self.recent_errors[-5:],
            "skill_level": self.skill_level,
            "session_duration_minutes": (datetime.now() - self.session_start).seconds / 60.0,
            "preferences": self.preferences
        }

class ContextManager:
    """Manages global context across all modules."""
    
    def __init__(self):
        self.contexts: Dict[str, UserContext] = {}  # session_id -> context
        self.persistence_path = Path("data/contexts")
        self.persistence_path.mkdir(parents=True, exist_ok=True)
    
    def get_context(self, session_id: str = "default") -> UserContext:
        """Get or create context for a session."""
        if session_id not in self.contexts:
            self.contexts[session_id] = UserContext()
            self._load_persistent_context(session_id)
        return self.contexts[session_id]
    
    def update_context(self, session_id: str = "default", **kwargs):
        """Update context with new information."""
        ctx = self.get_context(session_id)
        for key, value in kwargs.items():
            if hasattr(ctx, key):
                setattr(ctx, key, value)
        
        # Track action
        if "action" in kwargs:
            ctx.recent_actions.append({
                "action": kwargs["action"],
                "timestamp": datetime.now().isoformat(),
                "module": ctx.active_module,
                "metadata": kwargs.get("metadata", {})
            })
            if len(ctx.recent_actions) > 50:
                ctx.recent_actions = ctx.recent_actions[-50:]
        
        # Track error
        if "error" in kwargs:
            ctx.recent_errors.append({
                "error": str(kwargs["error"]),
                "timestamp": datetime.now().isoformat(),
                "module": ctx.active_module
            })
            if len(ctx.recent_errors) > 20:
                ctx.recent_errors = ctx.recent_errors[-20:]
        
        # Infer skill level
        self.infer_skill_level(session_id)
        
        # Persist context
        self._save_persistent_context(session_id)
    
    def _load_persistent_context(self, session_id: str):
        """Load long-term preferences from disk."""
        path = self.persistence_path / f"{session_id}.json"
        if path.exists():
            try:
                data = json.load(open(path, "r", encoding="utf-8"))
                ctx = self.contexts[session_id]
                ctx.preferences = data.get("preferences", {})
                ctx.skill_level = data.get("skill_level", "intermediate")
                ctx.workspace_id = data.get("workspace_id", "default")
            except Exception:
                pass
    
    def _save_persistent_context(self, session_id: str):
        """Save long-term preferences to disk."""
        ctx = self.contexts[session_id]
        path = self.persistence_path / f"{session_id}.json"
        try:
            data = {
                "preferences": ctx.preferences,
                "skill_level": ctx.skill_level,
                "workspace_id": ctx.workspace_id,
                "last_active": datetime.now().isoformat()
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def infer_skill_level(self, session_id: str):
        """Infer user skill level from interaction patterns."""
        ctx = self.get_context(session_id)
        advanced_actions = ["custom_sql", "causal_analysis", "triz_synthesis", "multi_variate_drift", "manual_cleaning"]
        advanced_count = sum(
            1 for action in ctx.recent_actions
            if action.get("action") in advanced_actions
        )
        
        if advanced_count >= 6:
            ctx.skill_level = "advanced"
        elif advanced_count >= 2:
            ctx.skill_level = "intermediate"
        else:
            ctx.skill_level = "beginner"

context_manager = ContextManager()
