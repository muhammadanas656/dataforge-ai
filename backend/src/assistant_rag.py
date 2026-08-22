"""RAG engine for system-wide knowledge retrieval across documentation, code graph, and datasets."""
from typing import List, Dict, Optional, Any
import json
import re
import math
from pathlib import Path
from src.utils import logger

# Seeded Core Knowledge Base for Zero-Latency Local Fallback
SYSTEM_DOCS = [
    {
        "id": "doc_react_loop",
        "title": "Autonomous ReAct Loop & Critic",
        "tags": ["agent", "react", "architecture", "critic", "reflection"],
        "content": (
            "DataForge AI uses an autonomous ReAct (Reason + Act) loop with self-reflection. "
            "When a query arrives, the orchestrator formulates a multi-step plan, selects specialized subagents "
            "(Market Radar, Competitor Scraper, Persona Generator, Business Architect, Cleaning Critic), "
            "evaluates data quality, and reflects on missing information to self-heal."
        )
    },
    {
        "id": "doc_cleaning_pipeline",
        "title": "3-Checkpoint Governed Cleaning Studio",
        "tags": ["cleaning", "checkpoint", "governance", "types", "missing_values", "anomalies"],
        "content": (
            "The Cleaning Studio enforces three strict checkpoints: "
            "Checkpoint 1 (CP1) validates semantic types (email, currency, dates, categorical) using heuristic + distilled student models. "
            "Checkpoint 2 (CP2) handles missing values via smart median, mode, or MICE imputation and removes duplicate rows. "
            "Checkpoint 3 (CP3) removes multi-column numerical outliers and formats standard output tables."
        )
    },
    {
        "id": "doc_causal_eda",
        "title": "Visual EDA & Causal Inference",
        "tags": ["eda", "causal", "dag", "correlation", "granger", "hypotheses"],
        "content": (
            "Visual EDA computes statistical profiles, Pearson/Spearman correlation matrices, and Causal Directed Acyclic Graphs (DAGs). "
            "Unlike simple correlation which confuses coincidence with causation, Causal Inference uses conditional independence "
            "and Granger tests to uncover true directional drivers (e.g. why churn occurs)."
        )
    },
    {
        "id": "doc_invention_triz",
        "title": "Future Horizon & TRIZ Invention Studio",
        "tags": ["invention", "triz", "future", "trends", "morphological", "2027", "blue_ocean"],
        "content": (
            "The Future Invention Studio moves beyond incremental niche research. It uses the TRIZ Contradiction Matrix "
            "(39 engineering parameters × 40 inventive principles) and Morphological Analysis to systematically invent "
            "unprecedented blue-ocean product categories. Every invention is validated against a 2026-2030 Technology "
            "Capability Graph and a Physics/Regulatory/Economics Grounding Validator."
        )
    },
    {
        "id": "doc_copilot_analyst",
        "title": "AI Conversational Copilot & What-If Simulator",
        "tags": ["analyst", "sql", "copilot", "what_if", "simulation", "unit_economics"],
        "content": (
            "The Cleaned Data Explorer features an NL-to-SQL AI Analyst and a Predictive What-If Simulator. "
            "Users can ask complex business questions in plain English or model counterfactual scenarios "
            "(e.g. 'What if CAC drops 15% and Retention rises 4%?') to forecast revenue and margin shifts."
        )
    },
    {
        "id": "doc_distribution_drift",
        "title": "Multi-Variate Drift & Certification",
        "tags": ["drift", "ks_test", "wasserstein", "governance", "audit", "contract"],
        "content": (
            "The Audit & Governance engine calculates 2-sample Kolmogorov-Smirnov (KS) drift and multi-variate "
            "Wasserstein distances between raw and cleaned distributions. It certifies data integrity and exports "
            "production-grade YAML data contracts."
        )
    }
]

class AssistantRAG:
    """Lightweight, zero-dependency hybrid semantic RAG engine for DataForge AI."""
    
    def __init__(self):
        self.docs: List[Dict[str, Any]] = list(SYSTEM_DOCS)
        self.code_items: List[Dict[str, Any]] = []
        self.dataset_profiles: Dict[str, Dict[str, Any]] = {}
        self._index_code_catalog()
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple alphanumeric tokenizer."""
        return [w.lower() for w in re.findall(r"\w+", text) if len(w) > 2]
    
    def _index_code_catalog(self):
        """Index system functions."""
        code_entries = [
            ("triz_engine.py", "identify_contradiction", "Resolves trade-offs between two engineering parameters using TRIZ."),
            ("morphological_analysis.py", "synthesize_invention", "Generates Cartesian combinations across tech dimensions and scores novelty."),
            ("grounding_validator.py", "validate_invention", "Validates physics, regulatory timelines, and margin economics."),
            ("tech_capability_graph.py", "get_capability", "Interpolates technology capacity from 2026 to 2030+."),
            ("eda_engine.py", "compute_causal_dag", "Computes directional causal relationships and hypothesis proofs."),
            ("analyst_engine.py", "simulate_what_if", "Executes unit economic simulations and scenario modeling."),
            ("distribution_drift.py", "calculate_drift", "Computes KS-statistic and Wasserstein multi-column distance.")
        ]
        for module, func, desc in code_entries:
            self.code_items.append({
                "id": f"{module}.{func}",
                "module": module,
                "function": func,
                "description": desc,
                "content": f"Module: {module} | Function: {func} | Description: {desc}"
            })
    
    def index_dataset_profile(self, dataset_id: str, profile: Dict[str, Any]):
        """Index a dataset profile in memory."""
        self.dataset_profiles[dataset_id] = profile
    
    def retrieve(self, query: str, collection: str = "all", top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge using BM25-style keyword matching and tag boosts.
        """
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return []
        
        candidates = []
        
        # 1. Search Documentation
        if collection in ["all", "docs"]:
            for d in self.docs:
                text = f"{d['title']} {' '.join(d['tags'])} {d['content']}"
                doc_tokens = self._tokenize(text)
                overlap = sum(1 for t in query_tokens if t in doc_tokens)
                tag_boost = sum(2 for t in query_tokens if t in d['tags'])
                score = overlap + tag_boost
                if score > 0:
                    candidates.append({
                        "source": "documentation",
                        "id": d["id"],
                        "title": d["title"],
                        "content": d["content"],
                        "score": score
                    })
        
        # 2. Search Code Catalog
        if collection in ["all", "code"]:
            for c in self.code_items:
                tokens = self._tokenize(c["content"])
                overlap = sum(1 for t in query_tokens if t in tokens)
                if overlap > 0:
                    candidates.append({
                        "source": "code",
                        "id": c["id"],
                        "title": f"{c['module']} → {c['function']}",
                        "content": c["content"],
                        "score": overlap * 1.2
                    })
        
        # 3. Search Active Dataset Profiles
        if collection in ["all", "data"]:
            for did, p in self.dataset_profiles.items():
                summary = f"Dataset {did} with {p.get('total_rows', 0)} rows, columns: {', '.join(p.get('columns', []))}"
                tokens = self._tokenize(summary)
                overlap = sum(1 for t in query_tokens if t in tokens)
                if overlap > 0:
                    candidates.append({
                        "source": "data_profile",
                        "id": did,
                        "title": f"Dataset #{did} Profile",
                        "content": summary,
                        "score": overlap * 1.5
                    })
        
        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_k]

assistant_rag = AssistantRAG()
