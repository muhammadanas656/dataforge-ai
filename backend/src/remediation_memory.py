import json
import os
import hashlib
import numpy as np

class RemediationMemory:
    """Per-signature contextual bandit over candidate remediations with Thompson sampling."""
    def __init__(self, path: str = "data/kb/remediations.json"):
        self.path = path
        self.data = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
        # schema: {sig: {plan_id: {"plan": ..., "alpha": float, "beta": float}}}

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        json.dump(self.data, open(self.path, "w", encoding="utf-8"), indent=2, default=str)

    def signature(self, inc) -> str:
        ctx = inc.get("context", inc) if isinstance(inc, dict) else inc
        key = {k: ctx.get(k) for k in ("kind", "dtype", "semantic", "domain") if isinstance(ctx, dict)}
        return hashlib.md5(json.dumps(key, sort_keys=True, default=str).encode()).hexdigest()

    @staticmethod
    def plan_id(plan) -> str:
        return hashlib.md5(json.dumps(plan, sort_keys=True, default=str).encode()).hexdigest()[:12]

    def candidates(self, sig: str) -> dict:
        return self.data.get(sig, {})

    def validated(self, sig: str) -> dict:
        return {p: a for p, a in self.candidates(sig).items() if a.get("alpha", 1.0) >= 2.0}

    def add_candidate(self, sig: str, plan: dict) -> str:
        pid = self.plan_id(plan)
        arms = self.data.setdefault(sig, {})
        if pid not in arms:
            arms[pid] = {"plan": plan, "alpha": 1.0, "beta": 1.0}
            self._save()
        return pid

    def update(self, sig: str, pid: str, success: bool):
        arm = self.data.setdefault(sig, {}).setdefault(pid, {"plan": None, "alpha": 1.0, "beta": 1.0})
        if success:
            arm["alpha"] += 1.0
        else:
            arm["beta"] += 1.0
        self._save()

    def select(self, sig: str):
        """Thompson-sample among validated candidate arms. Returns (plan, plan_id) or None."""
        arms = self.validated(sig)
        if not arms:
            return None
        best = None
        for pid, a in arms.items():
            s = np.random.beta(a["alpha"], a["beta"])
            if best is None or s > best[0]:
                best = (s, pid, a["plan"])
        return (best[2], best[1]) if best else None

    def best(self, sig: str):
        arms = self.validated(sig)
        if not arms:
            # Fallback to any arm if no validated arms yet
            arms = self.candidates(sig)
        if not arms:
            return None
        pid = max(arms, key=lambda p: arms[p]["alpha"] / (arms[p]["alpha"] + arms[p]["beta"]))
        return arms[pid]["plan"]

    # Backward compatibility with L1/L2
    def store(self, inc: dict, plan: dict, success: bool = True):
        sig = self.signature(inc)
        pid = self.add_candidate(sig, plan)
        self.update(sig, pid, success)

    def recall(self, inc: dict):
        return self.best(self.signature(inc))

    def stats(self) -> dict:
        n_arms = sum(len(v) for v in self.data.values())
        n_val = sum(len(self.validated(s)) for s in self.data)
        return {"signatures": len(self.data), "arms": n_arms, "validated": n_val, "learned_fixes": n_val}

memory = RemediationMemory()
