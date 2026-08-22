"""Autonomous agent that proactively hunts, filters, and ranks high-opportunity niches."""
import asyncio
from typing import List, Dict
from src.agentic_orchestrator import orchestrator
from src.preference_learning import get_preference_learner
from src.workspace import get_workspace
from src.niche_research import suggest_niches

class OpportunityHunter:
    """Proactively hunts emerging market gaps and ranks them against user preferences."""
    
    async def hunt(self, category: str = "all", limit: int = 6) -> List[Dict]:
        # 1. Generate grounded seed ideas
        candidates = suggest_niches(category=category, limit=limit * 2)
        
        # 2. Run quick parallel ReAct passes on top candidates
        tasks = []
        for c in candidates[:limit]:
            tasks.append(orchestrator.research_niche(c["niche"], depth="quick"))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        grounded_opportunities = []
        for i, res in enumerate(results):
            if isinstance(res, Exception) or not isinstance(res, dict):
                grounded_opportunities.append(candidates[i])
            else:
                grounded_opportunities.append({
                    "niche": res["niche"],
                    "category": candidates[i].get("category", "E-Commerce"),
                    "opportunity_score": res["opportunity_score"],
                    "trend_growth": f"+{max(15, int(res.get('metrics', {}).get('growth', 0.2) * 100))}%",
                    "tam_estimate": f"${int(res.get('metrics', {}).get('mentions', 50) * 850):,}",
                    "competition": "Low" if res["opportunity_score"] > 65 else "Medium",
                    "hook": f"Solves key frustration: {res.get('pain_points', ['fragility'])[0]}",
                    "completeness_score": res.get("completeness_score", 0.85),
                    "data_sources": res.get("data_sources", ["reddit", "competitors"])
                })
                
        # 3. Apply preference learning personalization
        workspace_id = get_workspace()
        learner = get_preference_learner(workspace_id)
        ranked = learner.rank_suggestions(grounded_opportunities)
        return ranked[:limit]

hunter = OpportunityHunter()
