import numpy as np
import json
import os

class ThompsonBandit:
    def __init__(self, state_path="data/kb/bandit_state.json"):
        self.path = state_path
        if os.path.exists(state_path):
            try:
                self.state = json.load(open(state_path, encoding="utf-8"))
            except Exception:
                self.state = {}
        else:
            self.state = {}

    def get_options(self, action, alternatives):
        if action not in self.state:
            self.state[action] = {alt: [1, 1] for alt in alternatives}
        for alt in alternatives:
            if alt not in self.state[action]:
                self.state[action][alt] = [1, 1]
        return self.state[action]

    def select(self, action, alternatives):
        """Select the best alternative to highlight using Thompson Sampling."""
        if not alternatives:
            return None
        options = self.get_options(action, alternatives)
        best_alt = None
        best_sample = -1.0
        for alt, (alpha, beta) in options.items():
            sample = float(np.random.beta(alpha, beta))
            if sample > best_sample:
                best_sample = sample
                best_alt = alt
        return best_alt

    def update(self, action, chosen_alt, was_picked):
        """Update the bandit based on whether the user actually clicked/picked it."""
        options = self.get_options(action, [chosen_alt])
        if was_picked:
            options[chosen_alt][0] += 1  # alpha (success)
        else:
            options[chosen_alt][1] += 1  # beta (failure/ignored)
        self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

bandit = ThompsonBandit()
