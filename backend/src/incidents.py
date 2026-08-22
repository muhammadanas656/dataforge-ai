"""
Central Incident Registry for anomalies, unhandled types, and execution rollbacks.
"""
import uuid
import os
import json
from datetime import datetime

INCIDENTS_PATH = "data/kb/incidents.json"
_REGISTRY = []

def _load():
    global _REGISTRY
    if os.path.exists(INCIDENTS_PATH):
        try:
            with open(INCIDENTS_PATH, "r", encoding="utf-8") as f:
                _REGISTRY = json.load(f)
        except Exception:
            _REGISTRY = []
    else:
        _REGISTRY = []

def _save():
    os.makedirs(os.path.dirname(INCIDENTS_PATH), exist_ok=True)
    with open(INCIDENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(_REGISTRY, f, indent=2, ensure_ascii=False)

_load()

def report_incident(kind: str, context: dict, error: str = None) -> dict:
    inc = {
        "id": uuid.uuid4().hex[:10],
        "kind": kind,
        "context": context or {},
        "error": str(error) if error else None,
        "created_at": datetime.utcnow().isoformat(),
        "resolved": False,
        "resolution": None,
        "proposal": None,
        "rejected": False
    }
    _REGISTRY.append(inc)
    _save()
    return inc

def get_incident(inc_id: str):
    for i in _REGISTRY:
        if i["id"] == inc_id:
            return i
    return None

def update_incident(inc_id: str, updates: dict):
    for i in _REGISTRY:
        if i["id"] == inc_id:
            i.update(updates)
            _save()
            return i
    return None

def mark_resolved(inc_id: str, resolution):
    for i in _REGISTRY:
        if i["id"] == inc_id:
            i["resolved"] = True
            i["resolution"] = resolution
            i["resolved_at"] = datetime.utcnow().isoformat()
            _save()
            return i
    return None

def list_incidents(unresolved_only: bool = False, limit: int = 50):
    _load()
    items = [i for i in _REGISTRY if not (unresolved_only and i.get("resolved"))]
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items[:limit]
