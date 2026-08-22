"""Cross-dataset knowledge graph for accumulated intelligence."""
import json
import os
import logging
from collections import defaultdict
from datetime import datetime


from src.workspace import get_workspace, workspace_path, ensure_workspace_dir

logger = logging.getLogger(__name__)
SCHEMA_VERSION = "1.0"


class KnowledgeGraph:
    def __init__(self, path=None, workspace_id=None):
        ensure_workspace_dir(workspace_id)
        self.path = path or workspace_path("knowledge_graph.json", workspace_id)
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        self.graph = self._load()
        if self.graph.get("schema_version") != SCHEMA_VERSION:
            logger.warning("[KG] Schema version mismatch. Archiving old graph.")
            self.graph = self._default_graph()

    def _default_graph(self):
        return {
            "schema_version": SCHEMA_VERSION,
            "domains": {},
            "columns": {},
            "cleaning_rules": [],
            "dataset_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return self._default_graph()

    def add_domain(self, domain):
        if domain not in self.graph["domains"]:
            self.graph["domains"][domain] = {
                "first_seen": datetime.now().isoformat(),
                "datasets": 0,
                "patterns": []
            }
        self.graph["domains"][domain]["datasets"] += 1
        self._save()

    def add_column_semantic(self, col_name, semantic_type, domain=None, confidence=1.0):
        if not col_name or not semantic_type:
            return
        key = str(col_name).lower().strip()
        if key not in self.graph["columns"]:
            self.graph["columns"][key] = {
                "semantic_types": {},
                "domains": [],
                "first_seen": datetime.now().isoformat(),
                "observations": 0
            }

        col = self.graph["columns"][key]
        col["observations"] += 1
        col["semantic_types"][semantic_type] = col["semantic_types"].get(semantic_type, 0.0) + confidence

        if domain and domain not in col["domains"]:
            col["domains"].append(domain)

        self._save()

    def get_column_semantic(self, col_name):
        key = str(col_name).lower().strip()
        if key not in self.graph["columns"]:
            return None

        col = self.graph["columns"][key]
        sem_types = col["semantic_types"]
        if not sem_types:
            return None

        total_weight = sum(sem_types.values())
        best_type, weight = max(sem_types.items(), key=lambda x: x[1])
        confidence = weight / total_weight if total_weight > 0 else 0.5

        return {
            "semantic_type": best_type,
            "confidence": round(confidence, 3),
            "observations": col["observations"],
            "domains": col["domains"]
        }

    def add_cleaning_rule(self, action, column_pattern, success=True, context=None):
        self.graph["cleaning_rules"].append({
            "action": action,
            "column_pattern": column_pattern,
            "success": success,
            "context": context or {},
            "learned_at": datetime.now().isoformat()
        })
        if len(self.graph["cleaning_rules"]) > 500:
            self.graph["cleaning_rules"] = self.graph["cleaning_rules"][-500:]
        self._save()

    def get_cleaning_rules(self, column_name=None):
        rules = self.graph["cleaning_rules"]
        if column_name:
            key = column_name.lower()
            rules = [r for r in rules if key in r.get("column_pattern", "").lower()]
        return rules[-20:]

    def increment_dataset_count(self):
        self.graph["dataset_count"] += 1
        self._save()

    def stats(self):
        return {
            "domains": len(self.graph["domains"]),
            "columns_learned": len(self.graph["columns"]),
            "cleaning_rules": len(self.graph["cleaning_rules"]),
            "datasets_processed": self.graph["dataset_count"],
            "updated_at": self.graph.get("updated_at", "")
        }

    def _save(self):
        self.graph["updated_at"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.graph, f, indent=2, ensure_ascii=False)


knowledge = KnowledgeGraph()
