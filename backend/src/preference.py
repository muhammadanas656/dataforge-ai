import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from src.feedback import store

RISK_MAP = {"low": 0, "medium": 1, "high": 2}

class PreferenceModel:
    def __init__(self):
        self.model = HistGradientBoostingClassifier()
        self.trained = False

    def _extract_features(self, action, impact_pct, risk_level):
        act_hash = abs(hash(action)) % 100
        return [float(act_hash), float(impact_pct or 0.0), float(RISK_MAP.get(risk_level, 1))]

    def train(self):
        history = store.get_history()
        if len(history) < 5:
            return  # Not enough data yet

        X = [self._extract_features(h[0], h[1], h[2]) for h in history]
        y = [h[3] for h in history]

        # Fallback if user only ever approved or only ever rejected
        if len(set(y)) < 2:
            self.trained = False
            return

        self.model.fit(X, y)
        self.trained = True

    def score_step(self, action, impact_pct, risk_level):
        """Returns probability that the user will approve this step."""
        if not self.trained:
            return 0.5  # Neutral prior

        X = [self._extract_features(action, impact_pct, risk_level)]
        try:
            # probability of class 1 (approved)
            return float(self.model.predict_proba(X)[0][1])
        except Exception:
            return 0.5

pref_model = PreferenceModel()
