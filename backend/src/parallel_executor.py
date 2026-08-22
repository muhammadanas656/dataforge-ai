"""Execute independent research subtasks in parallel."""
import asyncio
from typing import List, Dict, Any
from src.utils import logger

class ParallelExecutor:
    """Coordinates concurrent subtask execution with timeout and error containment."""
    
    async def execute_parallel(self, tasks: List[Dict[str, Any]], timeout: float = 45.0) -> Dict[str, Any]:
        logger.info(f"[parallel] Executing {len(tasks)} subtasks in parallel")
        async_tasks = []
        for task_spec in tasks:
            task_name = task_spec["task"]
            args = task_spec.get("args", {})
            async_tasks.append(self._execute_single(task_name, **args))
            
        try:
            results_list = await asyncio.wait_for(
                asyncio.gather(*async_tasks, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning("[parallel] Global parallel execution timed out")
            results_list = [{"error": "Timeout"}] * len(tasks)
            
        results = {}
        for i, task_spec in enumerate(tasks):
            name = task_spec["task"]
            res = results_list[i]
            if isinstance(res, Exception):
                results[name] = {"error": str(res)}
            else:
                results[name] = res
        return results
    
    async def _execute_single(self, task_name: str, **kwargs):
        from src.tool_router import router
        if task_name == "get_reddit_sentiment":
            return await router.execute_with_fallback("social_sentiment", **kwargs)
        elif task_name == "discover_competitors":
            return await router.execute_with_fallback("competitor_data", **kwargs)
        elif task_name == "get_external_trends":
            return await router.execute_with_fallback("trend_data", **kwargs)
        return {}

parallel_executor = ParallelExecutor()
