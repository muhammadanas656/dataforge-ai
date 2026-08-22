import collections
from src.utils import logger

class FrugalRouter:
    """Escalate through tiers only while confidence < threshold."""
    def __init__(self, threshold=0.8):
        self.threshold = threshold
        self.stats = collections.Counter()

    def route(self, task, context, handlers):
        answer = None
        conf = 0.0
        tier = None
        for tier_name, fn in handlers:
            answer, conf = fn(context)
            self.stats[tier_name] += 1
            tier = tier_name
            logger.info(f"[frugal] {task}: tier={tier_name} conf={conf:.2f}")
            if conf >= self.threshold:
                break
        return {"answer": answer, "tier": tier, "confidence": round(conf, 2)}

def semantic_type_rules(col):
    """Tier-1 rules: high-confidence semantic type without any LLM."""
    name = col["name"].lower()
    kind = col.get("kind")
    up = col.get("unique_pct", 0)
    
    if kind == "numeric":
        if any(w in name for w in ("price", "cost", "amount", "salary")):
            return ("currency", 0.95)
        if any(w in name for w in ("discount", "percent", "rate", "pct")):
            return ("numeric_continuous", 0.95)
        if any(w in name for w in ("count", "qty", "quantity")):
            return ("numeric_discrete", 0.9)
        return ("numeric_continuous", 0.5)
    else:
        if up > 95 or "id" in name or "uuid" in name or "code" in name:
            return ("identifier", 0.9)
        if col.get("unique", 10**9) <= 20:
            return ("categorical", 0.9)
        return ("free_text", 0.4)

def frugal_describe(col, cache, llm_fn, router=None):
    router = router or FrugalRouter()
    
    def t1(c):
        t, conf = semantic_type_rules(c)
        use = "measure" if t in ("currency", "numeric_continuous", "numeric_discrete") else "dimension"
        return ({
            "semantic_type": t,
            "meaning": f"rule-inferred: {c['name']}",
            "pii": False,
            "suggested_use": use,
            "confidence": conf
        }, conf)
        
    def t2(c):
        d = cache.lookup(c)
        return (d, 1.0) if d else (None, 0.0)
        
    def t3(c):
        d = llm_fn(c)
        cache.store(c, d)
        return (d, d.get("confidence", 0.8))
        
    res = router.route(
        f"describe:{col['name']}",
        col,
        [("T1_rules", t1), ("T2_rag", t2), ("T3_llm", t3)]
    )
    entry = res["answer"] or {}
    entry["name"] = col["name"]
    entry["tier"] = res["tier"]
    return entry
