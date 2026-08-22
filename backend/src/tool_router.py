"""Dynamic tool selection with intelligent fallback chains."""
import asyncio
from typing import List, Any, Dict
from src.utils import logger

class ToolRouter:
    """Routes tasks to the best available tool with fallback chains and telemetry."""
    
    def __init__(self):
        self.tool_chains = {
            "social_sentiment": ["reddit_realtime", "synthetic_fallback"],
            "competitor_data": ["competitor_scraper", "llm_estimation"],
            "trend_data": ["google_trends", "grounded_estimate"]
        }
        self.metrics = {
            "invocations": 0,
            "rate_limit_hits": 0,
            "fallback_executions": 0,
            "tool_failures": {}
        }
    
    async def execute_with_fallback(self, task_type: str, **kwargs) -> Any:
        chain = self.tool_chains.get(task_type, ["default"])
        last_error = None
        self.metrics["invocations"] += 1
        
        for i, tool_name in enumerate(chain):
            try:
                logger.info(f"[router] Attempting {tool_name} for task '{task_type}'")
                res = await self._execute_tool(tool_name, **kwargs)
                if i > 0:
                    self.metrics["fallback_executions"] += 1
                return res
            except Exception as e:
                err_str = str(e).lower()
                if "rate limit" in err_str or "429" in err_str:
                    self.metrics["rate_limit_hits"] += 1
                    logger.warning(f"[router] Rate limit hit on {tool_name}: {e}")
                self.metrics["tool_failures"][tool_name] = self.metrics["tool_failures"].get(tool_name, 0) + 1
                logger.warning(f"[router] Tool {tool_name} failed: {e}")
                last_error = e
                continue
                
        raise Exception(f"All tools failed for {task_type}: {last_error}")
    
    async def _execute_tool(self, tool_name: str, **kwargs):
        niche = kwargs.get("niche", "Product Niche")
        
        if tool_name == "reddit_realtime":
            from src.reddit_cache import reddit_cache
            cached = reddit_cache.get(niche)
            if cached:
                return cached
            from src.niche_research import RedditSource
            posts = RedditSource().search(niche, limit=35)
            if posts:
                reddit_cache.set(niche, posts)
                return posts
            raise ValueError("No live posts returned")
            
        elif tool_name == "synthetic_fallback":
            from src.niche_research import _synthetic_posts
            return _synthetic_posts(niche, n=40)
            
        elif tool_name == "competitor_scraper":
            from src.competitor_discovery import competitor_discovery
            return competitor_discovery.discover_competitors(niche)
            
        elif tool_name == "llm_estimation":
            from src.competitor_discovery import competitor_discovery
            return competitor_discovery._suggest_competitors_via_llm(niche)
            
        elif tool_name == "google_trends":
            from src.external_integrations import google_trends
            return google_trends.get_search_volume(niche)
            
        elif tool_name == "grounded_estimate":
            return {"keyword": niche, "current_interest": 65, "trend_direction": "up"}
            
        return {}

router = ToolRouter()
