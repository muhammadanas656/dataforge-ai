"""Trains local models from LLM interactions. The system teaches itself."""
import json
import os
import pickle
import hashlib
from datetime import datetime
from collections import defaultdict
from src.utils import logger

from src.workspace import get_workspace, workspace_path, ensure_workspace_dir

DISTILL_THRESHOLD = 15
MIN_CONFIDENCE = 0.50


class DistillationEngine:
    def __init__(self, path=None):
        ensure_workspace_dir()
        self.path = path or workspace_path("distillation")
        os.makedirs(self.path, exist_ok=True)
        self.examples = defaultdict(list)
        self.models = {}
        self.stats = defaultdict(lambda: {"calls": 0, "hits": 0})
        self.load_models()

    def record(self, task_type, input_data, output_data, confidence=1.0):
        """Record an LLM interaction for potential distillation."""
        self.examples[task_type].append({
            "input": input_data,
            "output": output_data,
            "confidence": confidence,
            "ts": datetime.now().isoformat()
        })
        self.stats[task_type]["calls"] += 1

        if len(self.examples[task_type]) >= DISTILL_THRESHOLD:
            self._try_distill(task_type)

        if len(self.examples[task_type]) > 1000:
            self.examples[task_type] = self.examples[task_type][-1000:]

    def record_correction(self, task_type, input_data, correct_output):
        """User or verifier corrected the distilled model. Invalidate and retrain."""
        self.examples[task_type].append({
            "input": input_data,
            "output": correct_output,
            "confidence": 1.0,
            "ts": datetime.now().isoformat()
        })
        if task_type in self.models:
            del self.models[task_type]
            try:
                os.remove(f"{self.path}/{task_type}.pkl")
            except Exception:
                pass
        self._try_distill(task_type)

    def _extract_features(self, input_data):
        if isinstance(input_data, dict):
            parts = [
                str(input_data.get("name", "")),
                str(input_data.get("dtype", "")),
                str(input_data.get("kind", "")),
                " ".join(map(str, input_data.get("samples", [])[:5]))
            ]
            return " ".join(parts)
        return str(input_data)

    def _try_distill(self, task_type):
        examples = self.examples[task_type]
        if len(examples) < DISTILL_THRESHOLD:
            return False

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.ensemble import RandomForestClassifier

            X_text = [self._extract_features(ex["input"]) for ex in examples]
            y = [str(ex["output"]) for ex in examples]

            if len(set(y)) < 2:
                return False

            vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
            X = vectorizer.fit_transform(X_text)

            model = RandomForestClassifier(n_estimators=30, random_state=42, n_jobs=1)
            model.fit(X, y)

            self.models[task_type] = {
                "type": "classifier",
                "vectorizer": vectorizer,
                "model": model,
                "trained_at": datetime.now().isoformat(),
                "examples": len(examples),
                "classes": list(set(y))
            }

            os.makedirs(self.path, exist_ok=True)
            with open(f"{self.path}/{task_type}.pkl", "wb") as f:
                pickle.dump(self.models[task_type], f)

            logger.info(f"[distill] ✅ Trained local classifier for {task_type} on {len(examples)} examples")
            return True
        except Exception as e:
            logger.warning(f"[distill] Failed for {task_type}: {e}")
            return False

    def predict(self, task_type, input_data):
        if task_type not in self.models:
            return None, 0.0

        try:
            model_data = self.models[task_type]
            if model_data["type"] == "classifier":
                features = self._extract_features(input_data)
                X = model_data["vectorizer"].transform([features])
                prediction = model_data["model"].predict(X)[0]
                probabilities = model_data["model"].predict_proba(X)[0]
                confidence = float(max(probabilities))

                if confidence >= MIN_CONFIDENCE:
                    self.stats[task_type]["hits"] += 1
                    return prediction, confidence
        except Exception as e:
            logger.warning(f"[distill] Prediction error for {task_type}: {e}")

        return None, 0.0

    def load_models(self):
        if not os.path.exists(self.path):
            return
        for fname in os.listdir(self.path):
            task_type = fname.split(".")[0]
            if fname.endswith(".pkl"):
                try:
                    with open(f"{self.path}/{fname}", "rb") as f:
                        self.models[task_type] = pickle.load(f)
                except Exception:
                    pass

    def get_stats(self):
        return {
            "tasks_trained": list(self.models.keys()),
            "examples_recorded": {k: len(v) for k, v in self.examples.items()},
            "stats": dict(self.stats),
            "total_models": len(self.models)
        }


distiller = DistillationEngine()
