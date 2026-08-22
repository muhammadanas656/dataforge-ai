import pytest
from src.preference_learning import PreferenceLearning

def test_preference_learning_recording_and_ranking():
    learner = PreferenceLearning(workspace_id="test_pref_ws")
    learner.reset()
    
    # Record positive engagement for AI & SaaS
    learner.record_engagement("AI CRM Assistant", "AI & SaaS", "deep_dived", opportunity_score=85)
    learner.record_engagement("AI Code Reviewer", "AI & SaaS", "injected_dataset", opportunity_score=90)
    learner.record_engagement("AI Summarizer", "AI & SaaS", "cleaned", opportunity_score=80)
    
    suggestions = [
        {"niche": "Dog Chew Toys", "category": "E-Commerce", "opportunity_score": 75},
        {"niche": "AI Support Bot", "category": "AI & SaaS", "opportunity_score": 75}
    ]
    
    ranked = learner.rank_suggestions(suggestions)
    assert ranked[0]["niche"] == "AI Support Bot"
    assert ranked[0]["boosted_score"] > 75
    learner.reset()
