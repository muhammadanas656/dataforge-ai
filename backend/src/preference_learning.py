"""Learns user preferences from engagement signals to improve future suggestions."""
import os
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from src.utils import logger
from src.workspace import workspace_path

SIGNAL_WEIGHTS = {
    'viewed': 0.1,
    'deep_dived': 0.5,
    'injected_dataset': 0.8,
    'cleaned': 1.0,
    'abandoned': -0.3,
    'skipped': -0.1
}

class PreferenceLearning:
    """Tracks user engagement and learns preferences to improve suggestions."""
    
    def __init__(self, workspace_id: str = "default"):
        self.workspace_id = workspace_id
        self.path = workspace_path("preferences.json", workspace_id)
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict:
        if not os.path.exists(self.path):
            return self._default_preferences()
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[preferences] Failed to load: {e}")
            return self._default_preferences()
    
    def _default_preferences(self) -> Dict:
        return {
            'workspace_id': self.workspace_id,
            'category_preferences': {},
            'keyword_preferences': {},
            'score_preference': {
                'preferred_range': [60.0, 85.0]
            },
            'engagement_history': [],
            'total_signals': 0,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_preferences(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.preferences['last_updated'] = datetime.now().isoformat()
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            logger.error(f"[preferences] Failed to save: {e}")
    
    def _extract_keywords(self, niche: str) -> List[str]:
        stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'to', 'of', 'in', 'on', 'at', 'by', 'with'}
        words = re.findall(r'\b[a-z]{3,}\b', niche.lower())
        return [w for w in words if w not in stop_words]
    
    def record_engagement(
        self,
        niche: str,
        category: str,
        action: str,
        opportunity_score: Optional[float] = None,
        metadata: Optional[Dict] = None
    ):
        if action not in SIGNAL_WEIGHTS:
            logger.warning(f"[preferences] Unknown action: {action}")
            return
        
        weight = SIGNAL_WEIGHTS[action]
        keywords = self._extract_keywords(niche)
        
        if category:
            current = self.preferences['category_preferences'].get(category, 0.0)
            self.preferences['category_preferences'][category] = round(current + weight, 3)
        
        for kw in keywords:
            current = self.preferences['keyword_preferences'].get(kw, 0.0)
            self.preferences['keyword_preferences'][kw] = round(current + weight, 3)
            
        if opportunity_score is not None and action in ['deep_dived', 'injected_dataset', 'cleaned']:
            pref_range = self.preferences['score_preference']['preferred_range']
            pref_range[0] = round((pref_range[0] * 0.8) + (float(opportunity_score) * 0.2), 1)
            pref_range[1] = round((pref_range[1] * 0.8) + (float(opportunity_score) * 0.2), 1)
        
        record = {
            'niche': niche,
            'category': category,
            'action': action,
            'weight': weight,
            'opportunity_score': opportunity_score,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.preferences['engagement_history'].append(record)
        if len(self.preferences['engagement_history']) > 100:
            self.preferences['engagement_history'] = self.preferences['engagement_history'][-100:]
            
        self.preferences['total_signals'] += 1
        self._save_preferences()
        logger.info(f"[preferences] Recorded {action} for '{niche}' (weight: {weight})")
    
    def calculate_preference_score(self, niche: str, category: str, opportunity_score: Optional[float] = None) -> float:
        if self.preferences['total_signals'] < 3:
            return 0.0
        
        # Apply exponential half-life time decay (0.95 ^ days_elapsed)
        decay = 1.0
        try:
            last_dt = datetime.fromisoformat(self.preferences.get('last_updated', datetime.now().isoformat()))
            days_elapsed = (datetime.now() - last_dt).total_seconds() / 86400.0
            decay = max(0.2, 0.95 ** days_elapsed)
        except Exception:
            decay = 1.0
        
        score = 0.0
        cat_pref = self.preferences['category_preferences'].get(category, 0.0) * decay
        if cat_pref != 0:
            max_cat = max(abs(v) for v in self.preferences['category_preferences'].values()) if self.preferences['category_preferences'] else 1.0
            score += (cat_pref / max(max_cat, 0.001)) * 0.3
            
        keywords = self._extract_keywords(niche)
        if keywords:
            matches = sum(self.preferences['keyword_preferences'].get(kw, 0.0) * decay for kw in keywords)
            if matches != 0:
                max_kw = max(abs(v) for v in self.preferences['keyword_preferences'].values()) if self.preferences['keyword_preferences'] else 1.0
                score += (matches / max(max_kw, 0.001)) * 0.2
                
        return max(-0.5, min(0.5, score))
    
    def rank_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        if self.preferences['total_signals'] < 3:
            return suggestions
        
        scored = []
        for s in suggestions:
            pref = self.calculate_preference_score(
                s.get('niche', ''),
                s.get('category', ''),
                s.get('opportunity_score')
            )
            base = float(s.get('opportunity_score', 50))
            boosted = min(100.0, max(0.0, round(base * (1 + pref), 1)))
            
            scored.append({
                **s,
                'preference_score': round(pref, 3),
                'boosted_score': boosted,
                'preference_reason': f"Matches your interest in {s.get('category')}" if pref > 0.05 else "Neutral"
            })
        return sorted(scored, key=lambda x: x.get('boosted_score', x.get('opportunity_score', 0)), reverse=True)
    
    def get_stats(self) -> Dict:
        return {
            'total_signals': self.preferences['total_signals'],
            'category_preferences': self.preferences['category_preferences'],
            'top_keywords': sorted(
                self.preferences['keyword_preferences'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'preferred_score_range': self.preferences['score_preference']['preferred_range'],
            'recent_engagements': self.preferences['engagement_history'][-5:],
            'last_updated': self.preferences['last_updated']
        }
    
    def reset(self):
        self.preferences = self._default_preferences()
        self._save_preferences()

_preference_instances = {}

def get_preference_learner(workspace_id: str = "default") -> PreferenceLearning:
    if workspace_id not in _preference_instances:
        _preference_instances[workspace_id] = PreferenceLearning(workspace_id)
    return _preference_instances[workspace_id]
