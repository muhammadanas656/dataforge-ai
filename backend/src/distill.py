import numpy as np
from sklearn.tree import DecisionTreeClassifier
from src.utils import logger

class LocalSurrogate:
    """Distills LLM semantic typing into a local Decision Tree."""
    def __init__(self):
        self.tree = DecisionTreeClassifier(max_depth=4)
        self.trained = False
        self.X = []
        self.y = []

    def add_sample(self, null_pct, unique_pct, length, semantic_type):
        self.X.append([float(null_pct), float(unique_pct), float(length)])
        self.y.append(semantic_type)

    def train(self):
        if len(set(self.y)) < 2 or len(self.X) < 10:
            return
        self.tree.fit(self.X, self.y)
        self.trained = True
        logger.info(f"LocalSurrogate trained on {len(self.X)} samples")

    def predict(self, null_pct, unique_pct, length):
        if not self.trained:
            return None, 0.0
        X = [[float(null_pct), float(unique_pct), float(length)]]
        pred = self.tree.predict(X)[0]
        proba = max(self.tree.predict_proba(X)[0])
        return pred, float(proba)

surrogate = LocalSurrogate()

class ThresholdAdapter:
    """Adjusts the Frugal Router's confidence threshold dynamically."""
    def __init__(self, base_threshold=0.8):
        self.base = base_threshold
        self.current = base_threshold
        self.recent_checks = []  # True = grounded, False = ungrounded

    def record_check(self, grounded):
        self.recent_checks.append(bool(grounded))
        if len(self.recent_checks) > 20:
            self.recent_checks.pop(0)
            success_rate = sum(self.recent_checks) / len(self.recent_checks)
            if success_rate > 0.95:
                self.current = min(0.95, round(self.current + 0.02, 2))  # More aggressive caching
            elif success_rate < 0.80:
                self.current = max(0.50, round(self.current - 0.05, 2))  # Force more LLM
            logger.info(f"Threshold adapted to {self.current:.2f} (success rate: {success_rate:.2f})")

adapter = ThresholdAdapter()
