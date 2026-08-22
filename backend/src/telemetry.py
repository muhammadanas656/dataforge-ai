import json
import os
from collections import defaultdict

class Telemetry:
    def __init__(self, path="data/kb/telemetry.json"):
        self.path = path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"events": []}
        return {"events": []}

    def record(self, kind, **kw):
        self.data["events"].append({"kind": kind, **kw})
        self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def insights(self):
        ev = self.data.get("events", [])
        out = []
        by_action = defaultdict(lambda: {"applied": 0, "rollback": 0, "approve": 0, "reject": 0})
        
        for e in ev:
            a = e.get("action")
            k = e.get("kind")
            if a and k in by_action[a]:
                by_action[a][k] += 1

        for a, c in by_action.items():
            if c["rollback"] > 0:
                out.append({
                    "action": a,
                    "suggestion": f"Default '{a}' to FLAG / Review (not immediate delete) — rollback rate is high ({c['rollback']} rollbacks)",
                    "auto": False,
                    "stats": c
                })
            if c["approve"] >= 2 and c["reject"] == 0:
                out.append({
                    "action": a,
                    "suggestion": f"You consistently approve '{a}' ({c['approve']} approvals, 0 rejections) — consider promoting to auto-approve",
                    "auto": True,
                    "stats": c
                })
        return out

telemetry = Telemetry()
