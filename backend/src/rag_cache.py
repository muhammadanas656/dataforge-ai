import json
import os
from rapidfuzz import fuzz
from src.utils import logger


class ColumnCache:
    """RAG-style cache: retrieve past column descriptions before calling the LLM."""
    def __init__(self, path="data/kb/column_cache.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.entries = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
        self.string_cache = {}

    def lookup(self, col, domain="generic", threshold=85):
        if isinstance(col, str):
            return self.string_cache.get(col)

        name = col.get("name", "").lower().strip()
        kind = col.get("kind")
        for e in self.entries:
            if e["name"].lower() == name and e.get("kind") == kind:
                if e.get("domain", "generic") == domain or domain == "generic":
                    return dict(e["desc"])
        best, best_score = None, 0
        for e in self.entries:
            if e.get("domain", "generic") == domain or domain == "generic":
                s = fuzz.ratio(name, e["name"].lower())
                if s > best_score:
                    best_score, best = s, e
        if best and best_score >= threshold and best.get("kind") == kind:
            logger.info(f"  fuzzy cache hit ({best_score}%): '{name}' matches cached '{best['name']}' [{domain}]")
            return dict(best["desc"])
        return None

    def store(self, col, desc, domain="generic"):
        if isinstance(col, str):
            self.string_cache[col] = desc
            return
        self.entries.append({"name": col["name"], "kind": col.get("kind"), "desc": desc, "domain": domain})
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)


rag = ColumnCache()
