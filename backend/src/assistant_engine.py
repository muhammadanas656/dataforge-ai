"""Global AI Assistant engine for DataForge AI Copilot."""
from typing import Dict, List, Optional, Any, AsyncGenerator
import json
import asyncio
from datetime import datetime
from src.context_manager import context_manager
from src.assistant_rag import assistant_rag
from src.llm import tracked_chat
from src.utils import logger, repair_and_load_json

class AssistantEngine:
    """Context-aware AI assistant powering the floating global copilot."""
    
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
    
    def _route_intent(self, query: str) -> Dict[str, Any]:
        """Route user query to appropriate intent and RAG collection."""
        q = query.lower()
        if any(w in q for w in ["error", "failed", "bug", "issue", "crash", "stuck", "exception", "broken"]):
            return {"type": "debug", "rag_collection": "all", "style": "technical", "include_errors": True}
        elif any(w in q for w in ["what is", "how does", "explain", "why", "triz", "causal", "drift", "checkpoint", "react"]):
            return {"type": "explain", "rag_collection": "docs", "style": "educational"}
        elif any(w in q for w in ["column", "row", "dataset", "profile", "distribution", "mean", "null", "outlier"]):
            return {"type": "data_query", "rag_collection": "data", "style": "analytical"}
        elif any(w in q for w in ["run", "clean", "simulate", "invent", "export", "forecast", "do"]):
            return {"type": "action", "rag_collection": "code", "style": "instructional"}
        else:
            return {"type": "general", "rag_collection": "all", "style": "conversational"}
    
    def _build_system_prompt(self, ctx_dict: Dict[str, Any], intent: Dict[str, Any], rag_results: List[Dict[str, Any]]) -> str:
        """Construct a high-context, skill-adaptive system prompt with live dataset awareness."""
        active_module = ctx_dict.get("active_module", "overview")
        dataset_id = ctx_dict.get("active_dataset_id", "none")
        skill_level = ctx_dict.get("skill_level", "intermediate")
        recent_errors = ctx_dict.get("recent_errors", [])
        
        prompt = (
            f"You are DataForge Copilot, the intelligent autonomous AI assistant and data scientist for DataForge AI.\n"
            f"You can assist with ANY feature in the system: Data Cleaning (CP1-CP4), Governance, Exploratory Data Analysis (EDA), "
            f"Causal DAGs, Statistical Hypotheses, Niche Market Research, Autonomous Web Crawling, Competitor Radar, Scenario Planning, and TRIZ Invention.\n\n"
            f"CURRENT SESSION CONTEXT:\n"
            f"- Active Module: {active_module}\n"
            f"- Active Dataset ID: {dataset_id}\n"
            f"- User Skill Level: {skill_level}\n\n"
        )
        
        # Inject Active Dataset Summary if available
        if dataset_id and dataset_id != "none":
            import os
            prof_path = f"reports/profile_{dataset_id}.json"
            eda_path = f"reports/eda_{dataset_id}.json"
            exec_path = f"reports/execution_{dataset_id}.json"
            
            prompt += f"ACTIVE DATASET CONTEXT (ID: {dataset_id}):\n"
            if os.path.exists(prof_path):
                try:
                    with open(prof_path, "r", encoding="utf-8") as f:
                        pdata = json.load(f)
                    cols = [c.get("name", "") for c in pdata.get("columns", [])]
                    prompt += f"- Dimensions: {pdata.get('shape', [0,0])[0]} rows x {len(cols)} columns\n"
                    prompt += f"- Columns: {', '.join(cols[:15])}\n"
                except Exception:
                    pass
            if os.path.exists(exec_path):
                try:
                    with open(exec_path, "r", encoding="utf-8") as f:
                        edata = json.load(f)
                    prompt += f"- Cleaning Quality: {edata.get('before_quality',0)}% -> {edata.get('after_quality',0)}% (+{edata.get('quality_delta',0)}%)\n"
                    prompt += f"- Rows After Cleaning: {edata.get('after_rows', 0)}\n"
                except Exception:
                    pass
            if os.path.exists(eda_path):
                try:
                    with open(eda_path, "r", encoding="utf-8") as f:
                        edarep = json.load(f)
                    causal = edarep.get("causal_dag", {})
                    if causal and causal.get("primary_insight"):
                        prompt += f"- Causal Driver: {causal.get('primary_insight')}\n"
                except Exception:
                    pass
            prompt += "\n"

        if intent.get("include_errors") and recent_errors:
            prompt += "RECENT SYSTEM ERRORS:\n"
            for err in recent_errors[-3:]:
                prompt += f"- [{err.get('timestamp', '')}] {err.get('error', '')}\n"
            prompt += "\n"
        
        if rag_results:
            prompt += "RELEVANT SYSTEM DOCUMENTATION & CAPABILITIES:\n"
            for r in rag_results[:3]:
                prompt += f"• [{r.get('title', 'Doc')}] {r.get('content', '')}\n"
            prompt += "\n"
        
        prompt += (
            f"RESPONSE GUIDELINES:\n"
            f"- Style: {intent.get('style', 'conversational')}.\n"
            f"- Answer any questions about the dataset, statistical distributions, causal drivers, or features thoroughly.\n"
            f"- Keep explanations clear, grounded in data, and practical.\n"
            f"- If recommending next steps, mention the specific UI button or page (e.g. 'Navigate to Visual EDA' or 'Open Cleaning Studio')."
        )
        return prompt
    
    async def process_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """Process non-streaming query."""
        ctx = context_manager.get_context(session_id)
        ctx_dict = ctx.to_dict()
        intent = self._route_intent(query)
        rag_results = assistant_rag.retrieve(query, collection=intent.get("rag_collection", "all"), top_k=3)
        system_prompt = self._build_system_prompt(ctx_dict, intent, rag_results)
        
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        history = self.conversation_history[session_id][-6:]
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": query}]
        
        try:
            response = tracked_chat(
                run_id=session_id,
                stage="ASSISTANT",
                agent="copilot",
                messages=messages,
                max_completion_tokens=600
            )
        except Exception as e:
            logger.warning(f"[assistant] LLM chat fallback: {e}")
            if rag_results:
                top = rag_results[0]
                response = f"**{top.get('title', 'DataForge Knowledge')}**\n\n{top.get('content', '')}\n\n*Tip: You can use the buttons on your current page to run automated actions.*"
            else:
                response = f"I'm here to help with DataForge AI. You are currently in the **{ctx_dict.get('active_module', 'Overview')}** module. Ask me about data cleaning, TRIZ invention, causal EDA, or dataset drift!"
        
        self.conversation_history[session_id].append({"role": "user", "content": query})
        self.conversation_history[session_id].append({"role": "assistant", "content": response})
        
        # Track action in context
        context_manager.update_context(session_id, action=f"copilot_query: {intent.get('type')}")
        
        return {
            "response": response,
            "intent": intent,
            "rag_sources": [{"title": r.get("title"), "source": r.get("source")} for r in rag_results],
            "context": ctx_dict
        }
    
    async def process_query_stream(self, session_id: str, query: str) -> AsyncGenerator[str, None]:
        """Stream assistant response chunks via NDJSON."""
        result = await self.process_query(session_id, query)
        text = result.get("response", "")
        
        # Stream chunks with slight natural cadence
        words = text.split(" ")
        chunk_size = 4
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size]) + " "
            yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
            await asyncio.sleep(0.04)
        
        yield json.dumps({
            "type": "done",
            "intent": result.get("intent"),
            "rag_sources": result.get("rag_sources")
        }) + "\n"

assistant_engine = AssistantEngine()
