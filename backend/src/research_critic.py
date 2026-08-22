"""Critic agent that self-reflects on research completeness and flags actionable data gaps."""
from typing import Dict, List
from src.utils import logger

class ResearchCritic:
    """Reviews multi-source research artifacts, calculates completeness score, and flags gaps."""
    
    def review_completeness(self, niche: str, results: Dict, min_completeness: float = 0.8) -> Dict:
        logger.info(f"[critic] Reviewing completeness for '{niche}' (min_threshold={min_completeness:.0%})")
        gaps = []
        recommendations = []
        
        # 1. Social listening check
        social = results.get("get_reddit_sentiment")
        if not social or (isinstance(social, list) and len(social) < 15):
            gaps.append("insufficient_social_data")
            recommendations.append("Gather additional forum discussions or expand search keywords.")
            
        # 2. Competitor check
        comps = results.get("discover_competitors")
        if not comps or (isinstance(comps, list) and len(comps) < 2):
            gaps.append("missing_competitor_pricing")
            recommendations.append("Scrape competitor product tier pages to ground pricing benchmarks.")
            
        # 3. External trends check
        trends = results.get("get_external_trends")
        if not trends or not trends.get("current_interest"):
            gaps.append("missing_trend_validation")
            recommendations.append("Validate seasonal keyword volume trajectory via search indices.")
            
        total_checks = 3
        passed_checks = total_checks - len(gaps)
        score = round(passed_checks / total_checks, 2)
        
        return {
            "completeness_score": score,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "gaps": gaps,
            "recommendations": recommendations,
            "verdict": "Comprehensive" if score >= min_completeness else ("Moderate" if score >= min_completeness * 0.75 else "Needs Follow-Up")
        }

critic = ResearchCritic()
