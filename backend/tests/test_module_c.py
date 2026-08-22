import numpy as np
import os
from src.preference import PreferenceModel
from src.bandit import ThompsonBandit
from src.distill import LocalSurrogate, ThresholdAdapter
from src.feedback import store

def test_preference_model_neutral_without_data():
    m = PreferenceModel()
    assert m.score_step("remove_duplicates", 5.0, "low") == 0.5

def test_bandit_explores():
    test_path = "data/kb/test_bandit.json"
    if os.path.exists(test_path):
        os.unlink(test_path)
    b = ThompsonBandit(test_path)
    alts = ["fill median", "drop rows", "add indicator"]
    # Run 100 times, should pick all at least once
    picks = set(b.select("test_action", alts) for _ in range(100))
    assert len(picks) > 1

def test_bandit_converges():
    test_path = "data/kb/test_bandit.json"
    b = ThompsonBandit(test_path)
    alts = ["A", "B"]
    # Reward "B" heavily
    for _ in range(50):
        b.update("test_action_converge", "B", True)
        b.update("test_action_converge", "A", False)
    # B should be picked almost always now
    picks = [b.select("test_action_converge", alts) for _ in range(20)]
    assert picks.count("B") > 15
    if os.path.exists(test_path):
        os.unlink(test_path)

def test_surrogate_distillation():
    s = LocalSurrogate()
    # Feed it some fake LLM outputs
    for _ in range(10):
        s.add_sample(0.0, 99.0, 10, "identifier")
        s.add_sample(50.0, 5.0, 20, "categorical")
    s.train()
    pred, conf = s.predict(0.0, 99.0, 10)
    assert pred == "identifier"

def test_threshold_adapter():
    a = ThresholdAdapter(0.8)
    # Simulate perfect grounding
    for _ in range(25):
        a.record_check(True)
    assert a.current > 0.8  # Should increase threshold to save tokens
