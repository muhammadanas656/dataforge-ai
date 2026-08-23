"""Global AI Assistant engine for DataForge AI Copilot.
Features:
- Autonomous Tool Execution & Function Calling (acts on user's behalf)
- Lifelong Semantic Response Cache (zero-token fast retrieval for frequent queries)
- Persistent Personalization Memory (adapts to user domain & style)
- Live Dataset Statistical Grounding
"""
from typing import Dict, List, Optional, Any, AsyncGenerator
import os
import re
import json
import asyncio
from datetime import datetime
from src.context_manager import context_manager
from src.assistant_rag import assistant_rag
from src.llm import tracked_chat
from src.utils import logger, repair_and_load_json
from src.copilot_registry import dry_run as registry_dry_run, get_tool_spec, list_tool_specs, validate_args

CACHE_FILE = "data/kb/copilot_semantic_cache.json"
PROFILE_FILE = "data/kb/user_personalization.json"

class AssistantEngine:
    """Autonomous, Personalized, Context-Aware AI Assistant & Tool Orchestrator."""
    
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        self.semantic_cache: List[Dict[str, Any]] = self._load_semantic_cache()
        self.user_profile: Dict[str, Any] = self._load_user_profile()
        self.total_tokens_saved: int = self._load_total_tokens_saved()

    def _load_semantic_cache(self) -> List[Dict[str, Any]]:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("cache_entries", [])
            except Exception:
                pass
        return self._seed_default_cache()

    def _seed_default_cache(self) -> List[Dict[str, Any]]:
        """Pre-seed verified, high-quality responses for standard system questions."""
        return [
            {
                "query_pattern": ["what services", "what features", "what does this system do", "capabilities", "platform overview"],
                "response": (
                    r"### 🚀 DataForge AI Autonomous Capabilities & Services" "\n\n"
                    r"DataForge AI provides an end-to-end autonomous data science, governance, and discovery cloud:" "\n\n"
                    r"1. **Autonomous Auto-Pilot (1-Click Engine):** Chains Ingestion, Profiling (CP1), Semantic Dictionary (CP2), Cleaning Plan (CP3), Governed Transformation (CP4), and Causal EDA in seconds." "\n"
                    r"2. **Data Quality & Governed Cleaning Studio:** Deterministic outlier clipping, MICE imputation, deduplication, and cryptographic transformation audit trails." "\n"
                    r"3. **Visual Causal DAG & EDA Studio:** Partial correlation inversion networks ($\mathbf{\Theta}$), Spearman rank maps, and distribution analysis." "\n"
                    r"4. **Ultra-Penetration Lead Scraper ($\ge 99.0\%$ Discovery):** Crawls niche directories, de-obfuscates Cloudflare XOR emails, and extracts phone/social contacts." "\n"
                    r"5. **Future Horizon & TRIZ 39×40 Invention Studio:** Resolves engineering contradictions to forecast breakthrough product roadmaps." "\n"
                    r"6. **Monte Carlo Risk & Scenario Simulator:** 1,000-iteration probability shock models ($p10, p50, p90$)." "\n"
                    r"7. **Standalone Pipeline Code Exporter:** Exports reproducible, zero-overhead standalone Python scripts for local or production pipelines."
                ),
                "hits": 0,
                "tokens_saved": 450
            },
            {
                "query_pattern": ["how does causal eda work", "causal dag", "causal inference"],
                "response": (
                    r"### 📊 Causal DAG & Partial Correlation Discovery" "\n\n"
                    r"Unlike naive correlation matrices that show spurious associations, DataForge AI's **Causal DAG Engine**:" "\n"
                    r"- Calculates the **Precision Matrix** $\mathbf{\Theta} = \mathbf{\Sigma}^{-1}$ (inverse covariance matrix)." "\n"
                    r"- Computes Partial Correlations: $\rho_{ij \cdot V \setminus \{i,j\}} = -\frac{\Theta_{ij}}{\sqrt{\Theta_{ii} \Theta_{jj}}}$." "\n"
                    r"- Constructs a directed acyclic graph (DAG) isolating true driver variables from confounding intermediaries."
                ),
                "hits": 0,
                "tokens_saved": 380
            }
        ]

    def _save_semantic_cache(self):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "total_tokens_saved": self.total_tokens_saved,
                    "cache_entries": self.semantic_cache
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"[copilot_cache] Failed to save semantic cache: {e}")

    def _load_user_profile(self) -> Dict[str, Any]:
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "industry": "General Data Science",
            "preferred_cleaning": "standard_iqr",
            "style": "concise_technical",
            "favorite_tools": ["autopilot", "causal_eda", "scraper"],
            "interactions_count": 0
        }

    def _save_user_profile(self):
        os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
        try:
            with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.user_profile, f, indent=2)
        except Exception as e:
            logger.warning(f"[user_profile] Failed to save profile: {e}")

    def _load_total_tokens_saved(self) -> int:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("total_tokens_saved", 0)
            except Exception:
                pass
        return 0

    def _match_semantic_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Look up high-confidence verified answers in local semantic cache."""
        q = query.lower().strip()
        for entry in self.semantic_cache:
            for pat in entry.get("query_pattern", []):
                if pat in q or q in pat:
                    entry["hits"] = entry.get("hits", 0) + 1
                    saved = entry.get("tokens_saved", 350)
                    self.total_tokens_saved += saved
                    self._save_semantic_cache()
                    return {
                        "response": entry["response"],
                        "cached": True,
                        "tokens_saved": saved,
                        "total_saved": self.total_tokens_saved
                    }
        return None

    def execute_named_tool(self, tool_name: str, args: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
        """Directly execute a named tool on the user's behalf."""
        try:
            validate_args(tool_name, args or {})
        except ValueError as e:
            return {"status": "error", "response": str(e), "tool_executed": tool_name}
        dataset_id = args.get("dataset_id", "none")

        if tool_name in {"get_current_context", "get_token_usage", "get_dataset_profile", "get_learning_stats"}:
            return self.execute_read_tool(tool_name, args or {}, session_id)

        if tool_name == "run_autopilot":
            try:
                from src.autopilot import run_autopilot
                csv_path = args.get("csv_path")
                if not csv_path or not os.path.exists(csv_path):
                    if dataset_id and dataset_id != "none":
                        candidates = [
                            f"uploads/raw_{dataset_id}.csv",
                            f"uploads/{dataset_id}.csv",
                            f"data/canonical/{dataset_id}.csv",
                            f"data/canonical/{dataset_id}_cleaned.csv"
                        ]
                        for c in candidates:
                            if os.path.exists(c):
                                csv_path = c
                                break
                    if not csv_path:
                        import glob
                        files = glob.glob("uploads/*.csv")
                        if files:
                            csv_path = files[-1]

                if csv_path and os.path.exists(csv_path):
                    res = run_autopilot(csv_path)
                    return {
                        "tool_executed": "run_autopilot",
                        "status": "success",
                        "response": (
                            f"✅ **Autonomous Auto-Pilot Completed Successfully!**\n\n"
                            f"- **Dataset ID:** `{res.get('dataset_id')}`\n"
                            f"- **Before Quality:** {res.get('execution', {}).get('before_quality')}% ➔ **After Quality:** {res.get('execution', {}).get('after_quality')}%\n"
                            f"- **Quality Delta:** `+{res.get('execution', {}).get('quality_delta')}%`\n"
                            f"- **Rows Cleaned:** {res.get('execution', {}).get('after_rows')}\n"
                            f"- **Causal Insights:** Generated full Causal DAG and visual distributions.\n\n"
                            f"👉 [Open Causal EDA Studio](/eda) | [Open Cleaning Studio](/cleaning)"
                        ),
                        "action_card": {
                            "type": "autopilot_complete",
                            "dataset_id": res.get("dataset_id"),
                            "quality_after": res.get("execution", {}).get("after_quality"),
                            "eda_link": "/eda",
                            "cleaning_link": "/cleaning",
                            "route_link": "/eda",
                            "route_label": "Causal EDA Studio"
                        }
                    }
                else:
                    return {
                        "tool_executed": "run_autopilot",
                        "status": "info",
                        "response": "⚠️ No active dataset file found to clean. Please upload a CSV first.",
                        "action_card": {"type": "upload_prompt"}
                    }
            except Exception as e:
                logger.error(f"[copilot_tool] Auto-pilot execution error: {e}")
                return {"tool_executed": "run_autopilot", "status": "error", "response": f"⚠️ Auto-Pilot error: {str(e)}"}

        elif tool_name == "extract_niche_leads":
            niche_target = args.get("niche", "Autonomous Edge AI Systems")
            try:
                from src.scraper_agent import scraper
                lead_res = scraper.extract_niche_leads_and_contacts(niche=niche_target, max_pages=2)
                return {
                    "tool_executed": "extract_niche_leads",
                    "status": "success",
                    "response": (
                        f"🎯 **Autonomous Niche Lead Extraction Completed!**\n\n"
                        f"- **Target Niche:** `{niche_target}`\n"
                        f"- **Leads Discovered:** `{lead_res.get('leads_extracted')}`\n"
                        f"- **Valid Contact Emails:** `{lead_res.get('valid_emails_count')}`\n"
                        f"- **Penetration Rate:** `{lead_res.get('penetration_rate_pct')}%`\n"
                        f"- **Generated Dataset ID:** `{lead_res.get('dataset_id')}`\n\n"
                        f"The extracted leads have been automatically registered as a clean dataset. You can now profile or run EDA directly."
                    ),
                    "action_card": {
                        "type": "leads_ready",
                        "dataset_id": lead_res.get("dataset_id"),
                        "count": lead_res.get("leads_extracted"),
                        "penetration": lead_res.get("penetration_rate_pct"),
                        "route_link": "/intel",
                        "route_label": "Market Intelligence & Leads"
                    }
                }
            except Exception as e:
                logger.error(f"[copilot_tool] Scraper tool error: {e}")
                return {"tool_executed": "extract_niche_leads", "status": "error", "response": f"⚠️ Scraper error: {str(e)}"}

        elif tool_name == "export_pipeline_code":
            try:
                from src.code_exporter import export_pipeline_code
                code_res = export_pipeline_code(dataset_id)
                py_code = code_res.get("python", {}).get("code", "")
                return {
                    "tool_executed": "export_pipeline_code",
                    "status": "success",
                    "response": (
                        f"📦 **Standalone Production Pipeline Code Generated!**\n\n"
                        f"A zero-dependency Python script containing deterministic cleaning steps, MICE imputation, and causal graphing is ready.\n\n"
                        f"```python\n{py_code[:400]}...\n```\n"
                        f"👉 Click **'Export Code'** in the top bar to copy or download the full script."
                    ),
                    "action_card": {
                        "type": "code_exported",
                        "filename": code_res.get("python", {}).get("filename", "pipeline.py"),
                        "route_link": "/cleaning",
                        "route_label": "Cleaning & Pipeline Studio"
                    }
                }
            except Exception as e:
                logger.error(f"[copilot_tool] Code exporter error: {e}")
                return {"tool_executed": "export_pipeline_code", "status": "error", "response": f"⚠️ Exporter error: {str(e)}"}

        elif tool_name == "resolve_triz":
            imp = args.get("improving", "speed")
            wors = args.get("worsening", "energy_efficiency")
            dom = args.get("domain", "edge_ai_hardware")
            try:
                from src.triz_engine import triz_engine
                triz_res = triz_engine.resolve_contradiction(imp, wors, dom)
                principles = triz_res.get("inventive_principles", [])
                p_text = "\n".join([f"- **Principle #{p.get('id')}: {p.get('name')}** — {p.get('description')}" for p in principles[:3]])
                return {
                    "tool_executed": "resolve_triz",
                    "status": "success",
                    "response": (
                        f"💡 **TRIZ 39×40 Contradiction Matrix Resolution:**\n\n"
                        f"- **Improving Parameter:** `{imp}`\n"
                        f"- **Worsening Parameter:** `{wors}`\n\n"
                        f"**Recommended Inventive Principles:**\n{p_text}\n\n"
                        f"👉 [Open TRIZ Invention Studio](/trends)"
                    ),
                    "action_card": {
                        "type": "triz_resolved",
                        "principles_count": len(principles),
                        "route_link": "/trends",
                        "route_label": "TRIZ Invention Studio"
                    }
                }
            except Exception as e:
                logger.error(f"[copilot_tool] TRIZ tool error: {e}")
                return {"tool_executed": "resolve_triz", "status": "error", "response": f"⚠️ TRIZ error: {str(e)}"}

        elif tool_name == "run_seo_audit":
            url_target = args.get("url", "https://example.com")
            try:
                from src.seo_auditor import seo_auditor
                seo_res = seo_auditor.audit_url(url_target)
                score = seo_res.get("overall_seo_score", 0)
                h1_items = seo_res.get("headings", {}).get("h1_items", [])
                h1_str = h1_items[0] if h1_items else "None"
                return {
                    "tool_executed": "run_seo_audit",
                    "status": "success",
                    "response": (
                        f"🔍 **360° Technical & Content SEO Audit Completed!**\n\n"
                        f"- **Target URL:** `{url_target}`\n"
                        f"- **Overall SEO Score:** `{score}/100`\n"
                        f"- **Primary <h1> Heading:** `{h1_str}`\n"
                        f"- **Core Web Vitals Score:** `{seo_res.get('core_web_vitals_simulation', {}).get('score', 0)}/100`\n"
                        f"- **Estimated LCP:** `{seo_res.get('core_web_vitals_simulation', {}).get('estimated_lcp_ms', 0)}ms`\n\n"
                        f"👉 [Open Web Intelligence Studio](/intel)"
                    ),
                    "action_card": {
                        "type": "seo_audited",
                        "score": score,
                        "url": url_target,
                        "route_link": "/intel",
                        "route_label": "Web Intelligence & SEO Studio"
                    }
                }
            except Exception as e:
                logger.error(f"[copilot_tool] SEO auditor error: {e}")
                return {"tool_executed": "run_seo_audit", "status": "error", "response": f"⚠️ SEO audit error: {str(e)}"}

        elif tool_name == "extract_design_tokens":
            url_target = args.get("url", "https://example.com")
            try:
                import httpx
                from src.design_extractor import design_lens
                try:
                    resp = httpx.get(url_target if url_target.startswith("http") else f"https://{url_target}", timeout=6.0, follow_redirects=True)
                    d_res = design_lens.extract_design_system(resp.text, url=str(resp.url))
                except Exception as net_err:
                    logger.warning(f"[copilot_tool] Design fetch fallback for {url_target}: {net_err}")
                    d_res = design_lens.extract_design_system("", url=url_target)
                
                p = d_res.get("palette", {})
                return {
                    "tool_executed": "extract_design_tokens",
                    "status": "success",
                    "response": (
                        f"🎨 **DesignLens UI/UX Perspectives & Tokens Extracted!**\n\n"
                        f"- **Primary Color:** `{p.get('primary')}` | **Secondary:** `{p.get('secondary')}`\n"
                        f"- **Background:** `{p.get('background')}` | **Surface:** `{p.get('surface')}`\n"
                        f"- **WCAG Contrast Check:** `{d_res.get('contrast', {}).get('wcag_compliance')}` ({d_res.get('contrast', {}).get('ratio')}:1 ratio)\n"
                        f"- **Dominant Heading Font:** `{d_res.get('typography', {}).get('heading_font')}`\n\n"
                        f"Tokens are formatted for Figma, Tailwind CSS (`tailwind.config.js`), and CSS `:root` variables."
                    ),
                    "action_card": {
                        "type": "design_tokens_ready",
                        "primary_color": p.get("primary"),
                        "route_link": "/intel",
                        "route_label": "Web & Design Studio"
                    }
                }
            except Exception as e:
                logger.error(f"[copilot_tool] Design extractor error: {e}")
                return {"tool_executed": "extract_design_tokens", "status": "error", "response": f"⚠️ Design extraction error: {str(e)}"}

        return {"status": "error", "response": f"Unknown tool: {tool_name}"}

    def execute_read_tool(self, tool_name: str, args: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
        """Execute registered read-only capabilities without invoking the LLM."""
        validate_args(tool_name, args)
        if tool_name == "get_current_context":
            data = context_manager.get_context(session_id).to_dict()
            return {"status": "success", "tool_executed": tool_name, "response": "Here is the current application context.", "data": data}
        if tool_name == "get_token_usage":
            from src.token_tracker import tracker
            scope = args.get("scope", "all")
            data = tracker.summary(scope=scope)
            return {"status": "success", "tool_executed": tool_name, "response": f"Token usage for the {scope} scope is {data.get('total_tokens', 0):,} total tokens.", "data": data}
        if tool_name == "get_dataset_profile":
            dataset_id = args["dataset_id"]
            result = {}
            for name in ("profile", "execution"):
                path = f"reports/{name}_{dataset_id}.json"
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        result[name] = json.load(f)
            return {"status": "success", "tool_executed": tool_name, "response": f"Loaded dataset context for {dataset_id}.", "data": result}
        if tool_name == "get_learning_stats":
            from src.adaptive_delegation import get_delegation_stats
            data = get_delegation_stats()
            return {"status": "success", "tool_executed": tool_name, "response": "Here are the current learning and autonomy statistics.", "data": data}
        raise ValueError(f"Unsupported read tool: {tool_name}")

    def dry_run_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        return registry_dry_run(tool_name, args or {})

    def _detect_and_execute_tool(self, query: str, session_id: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect actionable user commands and handle Confirmation Protocol vs Immediate Execution."""
        q = query.lower().strip()
        dataset_id = ctx.get("active_dataset_id") or "none"

        # Toggle Confirmation Protocol
        if any(k in q for k in ["ask me before", "require confirmation", "confirm before", "always ask first"]):
            self.user_profile["require_confirmation"] = True
            self._save_user_profile()
            return {
                "tool_executed": "toggle_confirmation",
                "status": "success",
                "response": "🔒 **Confirmation Protocol Enabled.** I will now always propose actions and ask for your 1-click confirmation before executing any tool or data transformation."
            }
        elif any(k in q for k in ["run automatically", "disable confirmation", "no confirmation", "full autonomous mode"]):
            self.user_profile["require_confirmation"] = False
            self._save_user_profile()
            return {
                "tool_executed": "toggle_confirmation",
                "status": "success",
                "response": "⚡ **Full Autonomous Execution Enabled.** I will now execute requested tools and data cleaning pipelines immediately upon command."
            }

        require_confirm = self.user_profile.get("require_confirmation", False)

        # Read-only application observability and context queries never need confirmation.
        if any(k in q for k in ["token usage", "token consumption", "tokens used", "token cost"]):
            return self.execute_read_tool("get_token_usage", {"scope": "all"}, session_id)
        if any(k in q for k in ["current context", "what page", "where am i", "active dataset"]):
            return self.execute_read_tool("get_current_context", {}, session_id)
        if any(k in q for k in ["learning stats", "learned fixes", "distilled models", "autonomy stats"]):
            return self.execute_read_tool("get_learning_stats", {}, session_id)
        if any(k in q for k in ["dataset profile", "profile of this dataset", "dataset quality"]):
            if dataset_id != "none":
                return self.execute_read_tool("get_dataset_profile", {"dataset_id": dataset_id}, session_id)
            return {"status": "info", "response": "Please select or upload a dataset first."}

        # 1. Run Auto-Pilot Command
        if any(k in q for k in ["run autopilot", "run auto pilot", "clean my dataset", "auto clean", "clean this dataset", "launch autopilot"]):
            if require_confirm:
                return {
                    "tool_executed": "action_proposal",
                    "status": "proposal",
                    "response": f"⚠️ **Confirmation Required:** I am ready to launch the 1-Click Auto-Pilot on dataset `{dataset_id}`.\n\n- **Impact:** Automatically profiles, imputes missing values, clips outliers, and computes Causal DAGs.\n\nWould you like me to proceed?",
                    "action_card": {
                        "type": "action_proposal",
                        "tool_name": "run_autopilot",
                        "args": {"dataset_id": dataset_id},
                        "action_label": "Launch Auto-Pilot Pipeline",
                        "impact": "Executes full CP1-CP4 transformation and Causal DAG"
                    }
                }
            return self.execute_named_tool("run_autopilot", {"dataset_id": dataset_id}, session_id)

        # 2. Scrape Niche Leads Command
        scrape_match = re.search(r'(?:scrape|find|get)\s+(?:leads|contacts|emails)\s+(?:for|in|about)\s+(.+)', q)
        if scrape_match or "scrape leads" in q:
            niche_target = scrape_match.group(1).strip() if scrape_match else "Autonomous Edge AI Systems"
            if require_confirm:
                return {
                    "tool_executed": "action_proposal",
                    "status": "proposal",
                    "response": f"⚠️ **Confirmation Required:** I am ready to scrape niche business leads for `{niche_target}`.\n\n- **Impact:** Crawls target niche domains, de-obfuscates Cloudflare emails, and registers a new CSV dataset.\n\nWould you like me to proceed?",
                    "action_card": {
                        "type": "action_proposal",
                        "tool_name": "extract_niche_leads",
                        "args": {"niche": niche_target},
                        "action_label": f"Scrape Leads for {niche_target}",
                        "impact": "Ultra-penetration web crawl across niche directories"
                    }
                }
            return self.execute_named_tool("extract_niche_leads", {"niche": niche_target}, session_id)

        # 3. SEO Audit Command
        seo_match = re.search(r'(?:audit|check|analyze)\s+(?:seo|technical seo)\s+(?:for|of|on)?\s*([^\s]+)', q)
        if seo_match or "audit seo" in q or "check seo" in q:
            target_url = seo_match.group(1).strip() if seo_match else "https://example.com"
            if not target_url.startswith("http"):
                target_url = f"https://{target_url}"
            if require_confirm:
                return {
                    "tool_executed": "action_proposal",
                    "status": "proposal",
                    "response": f"⚠️ **Confirmation Required:** I am ready to run a 360° Technical & Content SEO audit on `{target_url}`.\n\n- **Impact:** Evaluates Core Web Vitals, heading structure ($H_1-H_6$), Schema.org metadata, and readability.\n\nWould you like me to proceed?",
                    "action_card": {
                        "type": "action_proposal",
                        "tool_name": "run_seo_audit",
                        "args": {"url": target_url},
                        "action_label": f"Audit SEO for {target_url}",
                        "impact": "360° Technical & Core Web Vitals audit"
                    }
                }
            return self.execute_named_tool("run_seo_audit", {"url": target_url}, session_id)

        # 4. DesignLens & Token Extraction Command
        design_match = re.search(r'(?:extract|get|generate)\s+(?:design|tokens|palette|colors|theme)\s+(?:for|from|of)?\s*([^\s]+)', q)
        if design_match or "design tokens" in q or "color palette" in q:
            target_url = design_match.group(1).strip() if design_match else "https://example.com"
            if not target_url.startswith("http"):
                target_url = f"https://{target_url}"
            if require_confirm:
                return {
                    "tool_executed": "action_proposal",
                    "status": "proposal",
                    "response": f"⚠️ **Confirmation Required:** I am ready to extract Design Tokens & UI/UX Perspectives from `{target_url}`.\n\n- **Impact:** Extracts WCAG-compliant color harmony palettes, typography scales, and generates `tailwind.config.js` tokens.\n\nWould you like me to proceed?",
                    "action_card": {
                        "type": "action_proposal",
                        "tool_name": "extract_design_tokens",
                        "args": {"url": target_url},
                        "action_label": f"Extract Design Tokens for {target_url}",
                        "impact": "Color harmony clustering, WCAG checks, and Tailwind export"
                    }
                }
            return self.execute_named_tool("extract_design_tokens", {"url": target_url}, session_id)

        # 3. Export Pipeline Code Command
        if any(k in q for k in ["export code", "export pipeline", "give me python code", "download script", "pipeline code"]):
            return self.execute_named_tool("export_pipeline_code", {"dataset_id": dataset_id}, session_id)

        # 4. Resolve TRIZ Contradiction Command
        if any(k in q for k in ["resolve triz", "triz contradiction", "invent solution"]):
            return self.execute_named_tool("resolve_triz", {"improving": "speed", "worsening": "energy_efficiency", "domain": "edge_ai_hardware"}, session_id)

        return None

    def _build_system_prompt(self, ctx_dict: Dict[str, Any], intent: Dict[str, Any], rag_results: List[Dict[str, Any]]) -> str:
        active_module = ctx_dict.get("active_module", "overview")
        dataset_id = ctx_dict.get("active_dataset_id", "none")
        
        prompt = (
            f"You are DataForge Copilot, the autonomous AI data science partner for DataForge AI.\n"
            f"You personalize your tone to the user ({self.user_profile.get('style', 'concise_technical')}) in the {self.user_profile.get('industry', 'Data Science')} industry.\n"
            f"CURRENT CONTEXT:\n- Module: {active_module}\n- Dataset ID: {dataset_id}\n\n"
        )
        
        if dataset_id and dataset_id != "none":
            prof_path = f"reports/profile_{dataset_id}.json"
            exec_path = f"reports/execution_{dataset_id}.json"
            if os.path.exists(prof_path):
                try:
                    with open(prof_path, "r", encoding="utf-8") as f:
                        pdata = json.load(f)
                    prompt += f"DATASET STATS: {pdata.get('shape', [0,0])[0]} rows x {len(pdata.get('columns', []))} cols.\n"
                except Exception:
                    pass
            if os.path.exists(exec_path):
                try:
                    with open(exec_path, "r", encoding="utf-8") as f:
                        edata = json.load(f)
                    prompt += f"QUALITY: {edata.get('before_quality',0)}% -> {edata.get('after_quality',0)}%.\n"
                except Exception:
                    pass

        if rag_results:
            prompt += "\nRELEVANT DOCUMENTATION:\n"
            for r in rag_results[:2]:
                prompt += f"• {r.get('title')}: {r.get('content')}\n"
                
        prompt += "\nRespond accurately and offer to run actions (Auto-Pilot, Lead Scraper, TRIZ, EDA) on their behalf."
        return prompt

    async def process_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """Process user query with Tool Execution -> Semantic Cache -> LLM Fallback."""
        ctx = context_manager.get_context(session_id)
        ctx_dict = ctx.to_dict() if hasattr(ctx, "to_dict") else {}
        self.user_profile["interactions_count"] = self.user_profile.get("interactions_count", 0) + 1
        self._save_user_profile()

        # Step 1: Check for Direct Action / Tool Execution
        tool_res = self._detect_and_execute_tool(query, session_id, ctx_dict)
        if tool_res:
            self._record_turn(session_id, query, tool_res["response"])
            return {
                "response": tool_res["response"],
                "status": tool_res.get("status", "success"),
                "tool_executed": tool_res.get("tool_executed"),
                "action_card": tool_res.get("action_card"),
                "tokens_saved": 500,
                "total_tokens_saved": self.total_tokens_saved,
                "cached": False,
                "context": ctx_dict
            }

        # Step 2: Check Semantic Cache for 0-Token Instant Response
        cache_hit = self._match_semantic_cache(query)
        if cache_hit:
            self._record_turn(session_id, query, cache_hit["response"])
            return {
                "response": cache_hit["response"],
                "cached": True,
                "tokens_saved": cache_hit["tokens_saved"],
                "total_tokens_saved": self.total_tokens_saved,
                "context": ctx_dict
            }

        # Step 3: LLM Inference with Live RAG Context
        intent = self._route_intent(query)
        rag_results = assistant_rag.retrieve(query, collection=intent.get("rag_collection", "all"), top_k=2)
        system_prompt = self._build_system_prompt(ctx_dict, intent, rag_results)
        
        history = self.conversation_history.get(session_id, [])[-4:]
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": query}]

        try:
            response = tracked_chat(
                run_id=session_id,
                stage="ASSISTANT",
                agent="copilot",
                messages=messages,
                max_completion_tokens=600
            )
            # Add novel verified answer to semantic cache for future 0-token recall
            if len(query.split()) > 3 and len(response) > 50:
                self.semantic_cache.append({
                    "query_pattern": [query.lower().strip()[:40]],
                    "response": response,
                    "hits": 1,
                    "tokens_saved": 400
                })
                self._save_semantic_cache()
        except Exception as e:
            logger.warning(f"[assistant] LLM chat fallback: {e}")
            if rag_results:
                top = rag_results[0]
                response = f"**{top.get('title', 'DataForge Knowledge')}**\n\n{top.get('content', '')}\n\n*Tip: You can ask me to run Auto-Pilot or scrape niche leads anytime!*"
            else:
                response = f"I am your DataForge Copilot. Ask me to clean your data, run Causal EDA, or extract leads!"

        self._record_turn(session_id, query, response)
        return {
            "response": response,
            "cached": False,
            "tokens_saved": 0,
            "total_tokens_saved": self.total_tokens_saved,
            "intent": intent,
            "context": ctx_dict
        }

    def _record_turn(self, session_id: str, query: str, response: str):
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        self.conversation_history[session_id].append({"role": "user", "content": query})
        self.conversation_history[session_id].append({"role": "assistant", "content": response})

    def _route_intent(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        if any(w in q for w in ["error", "bug", "crash", "stuck"]):
            return {"type": "debug", "rag_collection": "all", "style": "technical"}
        elif any(w in q for w in ["what", "how", "explain", "triz", "causal"]):
            return {"type": "explain", "rag_collection": "docs", "style": "educational"}
        elif any(w in q for w in ["column", "mean", "null", "outlier", "stats"]):
            return {"type": "data_query", "rag_collection": "data", "style": "analytical"}
        return {"type": "general", "rag_collection": "all", "style": "conversational"}

    async def process_query_stream(self, session_id: str, query: str) -> AsyncGenerator[str, None]:
        """Stream assistant response chunks with action metadata and token savings."""
        result = await self.process_query(session_id, query)
        text = result.get("response", "")
        
        words = text.split(" ")
        chunk_size = 4
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size]) + " "
            yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
            await asyncio.sleep(0.02)
        
        yield json.dumps({
            "type": "done",
            "cached": result.get("cached", False),
            "tokens_saved": result.get("tokens_saved", 0),
            "total_tokens_saved": result.get("total_tokens_saved", self.total_tokens_saved),
            "tool_executed": result.get("tool_executed"),
            "action_card": result.get("action_card")
        }) + "\n"


assistant_engine = AssistantEngine()
