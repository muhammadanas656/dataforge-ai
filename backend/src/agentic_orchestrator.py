"""Top-level agent that plans, executes with tool routing, reflects, and synthesizes research workflows."""
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from src.utils import logger
from src.parallel_executor import parallel_executor
from src.research_critic import critic
from src.scenario_planning import scenario_planner
from src.synthetic_data_generator import generate_comprehensive_unit_economics

class AgenticOrchestrator:
    """Orchestrates multi-step autonomous research with ReAct loops."""
    
    async def research_niche(self, niche: str, depth: str = "comprehensive", timeout: float = 90.0, min_completeness: float = 0.8) -> Dict[str, Any]:
        logger.info(f"[orchestrator] Starting ReAct research loop for '{niche}' (depth={depth})")
        
        # 1. Plan subtasks
        plan = self._plan_research(niche, depth)
        
        # 2. Execute subtasks in parallel with timeout guard
        try:
            results = await asyncio.wait_for(
                parallel_executor.execute_parallel(plan),
                timeout=timeout * 0.6
            )
        except asyncio.TimeoutError:
            logger.warning(f"[orchestrator] Primary plan execution timed out for '{niche}'")
            results = {}
        
        # 3. Reflect & Identify Gaps
        critique = critic.review_completeness(niche, results, min_completeness=min_completeness)
        
        # 4. Adaptive Follow-up if completeness < min_completeness
        if critique["completeness_score"] < min_completeness:
            logger.info(f"[orchestrator] Completeness score {critique['completeness_score']:.0%}. Executing follow-up loop...")
            followup_tasks = self._plan_followup(niche, critique["gaps"])
            if followup_tasks:
                try:
                    followup_results = await asyncio.wait_for(
                        parallel_executor.execute_parallel(followup_tasks),
                        timeout=timeout * 0.4
                    )
                    results.update(followup_results)
                    critique = critic.review_completeness(niche, results, min_completeness=min_completeness)
                except asyncio.TimeoutError:
                    logger.warning(f"[orchestrator] Follow-up execution timed out for '{niche}'")
                
        # 5. Synthesize Strategy Blueprint
        synthesis = self._synthesize(niche, results, critique)
        return synthesis
    
    def _plan_research(self, niche: str, depth: str) -> List[Dict[str, Any]]:
        return [
            {"task": "get_reddit_sentiment", "args": {"niche": niche}},
            {"task": "discover_competitors", "args": {"niche": niche}},
            {"task": "get_external_trends", "args": {"niche": niche}}
        ]
        
    def _plan_followup(self, niche: str, gaps: List[str]) -> List[Dict[str, Any]]:
        followup = []
        if "insufficient_social_data" in gaps:
            from src.niche_research import _synthetic_posts
            followup.append({"task": "get_reddit_sentiment", "args": {"niche": niche}})
        if "missing_competitor_pricing" in gaps:
            followup.append({"task": "discover_competitors", "args": {"niche": niche}})
        return followup
    
    def _synthesize(self, niche: str, results: Dict, critique: Dict) -> Dict[str, Any]:
        from src.niche_research import analyze_posts, opportunity_score, top_pain_points, generate_business_blueprint
        
        posts = results.get("get_reddit_sentiment") or []
        metrics = analyze_posts(posts) if isinstance(posts, list) and posts else {"mentions": 40, "sentiment": 0.45, "growth": 0.25, "pain_ratio": 0.35}
        score = opportunity_score(metrics)
        
        competitors = results.get("discover_competitors") or []
        trends = results.get("get_external_trends") or {}
        
        blueprint = generate_business_blueprint(niche)
        scenarios = scenario_planner.generate_scenarios(niche, {
            'units_per_month': max(30, int(metrics.get("mentions", 50) * 3)),
            'price_usd': 59.0,
            'cogs_usd': 18.0,
            'cac_usd': 16.0
        })
        
        return {
            "niche": niche,
            "opportunity_score": score,
            "metrics": metrics,
            "pain_points": top_pain_points(posts) if isinstance(posts, list) else ["High price", "Setup friction"],
            "competitors": competitors,
            "trends": trends,
            "blueprint": blueprint,
            "scenarios": scenarios,
            "critic_evaluation": critique,
            "completeness_score": critique["completeness_score"],
            "data_sources": [k for k, v in results.items() if v and not (isinstance(v, dict) and "error" in v)],
            "timestamp": datetime.now().isoformat()
        }

orchestrator = AgenticOrchestrator()
