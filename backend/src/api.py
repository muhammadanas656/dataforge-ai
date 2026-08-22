from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import shutil
import glob
import pandas as pd
from src import phase1, cp2, cp3, governance, executor, reporter, eda_engine, security
from src.utils import logger
from src.token_tracker import tracker

app = FastAPI(title="DataForge AI", version="0.9")

# Enable CORS so Next.js (port 3000) can talk to FastAPI (port 8000)
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.workspace import set_workspace, reset_workspace, DEFAULT_WORKSPACE, list_workspaces, ensure_workspace_dir, get_workspace

class WorkspaceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        wid = (
            request.headers.get("X-Workspace-Id")
            or request.query_params.get("workspace")
            or DEFAULT_WORKSPACE
        )
        try:
            set_workspace(wid)
        except ValueError as e:
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": str(e)}, status_code=400)
        try:
            response = await call_next(request)
            return response
        finally:
            reset_workspace()

app.add_middleware(WorkspaceMiddleware)

os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("exports", exist_ok=True)
os.makedirs("data/canonical", exist_ok=True)


def _safe_did(did: str) -> str:
    try:
        return security.validate_dataset_id(did)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _load(kind: str, did: str):
    clean_id = _safe_did(did)
    p = f"reports/{kind}_{clean_id}.json"
    if not os.path.exists(p):
        raise HTTPException(status_code=404, detail=f"Report '{kind}' for dataset '{clean_id}' not found")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _safe(kind: str, did: str):
    clean_id = _safe_did(did)
    p = f"reports/{kind}_{clean_id}.json"
    if not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _require_cleaned(did: str):
    clean_id = _safe_did(did)
    cleaned_path = f"data/canonical/{clean_id}_cleaned.csv"
    if not os.path.exists(cleaned_path):
        raise HTTPException(
            status_code=400,
            detail="Dataset has not been cleaned yet. Please complete cleaning in Cleaning Studio before accessing downstream analytics or reports."
        )


@app.get("/health")
def health():
    return {"status": "ok", "service": "DataForge AI Orchestrator"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    safe_name = security.sanitize_filename(file.filename)
    file_path = f"uploads/{safe_name}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run Phase 1 immediately upon upload
    profile = phase1.run_phase1(file_path)
    return {
        "message": "Ingest complete",
        "dataset_id": profile["dataset_id"],
        "filename": safe_name
    }


@app.post("/api/ingest")
def ingest(payload: dict):
    if "path" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'path' in request body")
    profile = phase1.run_phase1(payload["path"])
    return {"dataset_id": profile["dataset_id"], "source": profile.get("source"), "shape": profile.get("shape")}


@app.get("/api/datasets")
def list_datasets():
    uploaded_files = set()
    if os.path.exists("uploads"):
        uploaded_files = {f for f in os.listdir("uploads") if os.path.isfile(os.path.join("uploads", f))}

    seen_files = {}
    for p in glob.glob("reports/profile_*.json"):
        try:
            prof = json.load(open(p, encoding="utf-8"))
            did = prof.get("dataset_id")
            fname = prof.get("filename")

            # Only include datasets whose source file actually exists in uploads/
            if not fname or fname not in uploaded_files:
                continue

            cleaned_exists = os.path.exists(f"data/canonical/{did}_cleaned.csv")
            entry = {
                "id": did,
                "filename": fname,
                "rows": prof.get("total_rows"),
                "columns": prof.get("total_columns"),
                "cleaned": cleaned_exists,
                "created_at": prof.get("created_at", "")
            }
            if fname not in seen_files or entry["created_at"] > seen_files[fname]["created_at"]:
                seen_files[fname] = entry
        except Exception:
            continue

    # If any file in uploads/ has not been profiled yet, auto-profile it
    for fname in uploaded_files:
        if fname not in seen_files:
            try:
                prof = phase1.run_phase1(os.path.join("uploads", fname))
                did = prof.get("dataset_id")
                seen_files[fname] = {
                    "id": did,
                    "filename": fname,
                    "rows": prof.get("total_rows"),
                    "columns": prof.get("total_columns"),
                    "cleaned": False,
                    "created_at": prof.get("created_at", "")
                }
            except Exception as e:
                logger.warning(f"Could not auto-profile upload file {fname}: {e}")

    items = list(seen_files.values())
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"datasets": items}


@app.get("/api/profile/{did}")
def get_profile(did: str):
    return _load("profile", did)


def _meaning_for(col, sem):
    base = {
        "currency": f"An amount of money ({col['name']}).",
        "numeric_continuous": f"A measured numeric value ({col['name']}).",
        "numeric_discrete": f"A count or whole number ({col['name']}).",
        "identifier": f"A unique label identifying each record ({col['name']}).",
        "categorical": f"A group/category each record belongs to ({col['name']}).",
        "free_text": f"Free-form descriptive text ({col['name']}).",
        "date": f"A date or timestamp ({col['name']}).",
    }.get(sem, f"A data field ({col['name']}).")
    return base


def _fallback_columns(profile):
    from src.frugal import semantic_type_rules
    pii = profile.get("pii") or {}
    cols = []
    for c in profile.get("columns", []):
        t, _ = semantic_type_rules(c)
        cols.append({
            "name": c["name"],
            "semantic_type": t,
            "meaning": _meaning_for(c, t),
            "suggested_use": "measure" if t in ("currency", "numeric_continuous", "numeric_discrete") else "dimension",
            "pii": bool(pii.get(c["name"]))
        })
    return cols


@app.get("/api/summary/{did}")
def summary(did: str):
    clean_id = _safe_did(did)
    cp1 = _safe("cp1", clean_id)
    dic = _safe("dictionary", clean_id)
    prof = _safe("profile", clean_id)
    columns = dic.get("dictionary") or (_fallback_columns(prof) if prof else [])
    domain = dic.get("domain") or cp1.get("domain", "generic")
    rows = prof.get("total_rows", 0)
    ncols = prof.get("total_columns", 0)
    dup = prof.get("duplicate_pct", 0)
    pii = len(prof.get("pii") or {}) if prof else 0
    purpose = cp1.get("purpose") or "It records operational records for analysis."
    overview = (f"This is a {domain} dataset with {rows:,} rows and {ncols} columns. {purpose} "
                f"It currently contains {dup}% duplicate rows and {pii} column(s) with potential personal data.")
    reason = cp1.get("next_step_hint") or cp1.get("purpose") or "Use it to understand and improve your data quality."
    return {
        "domain": domain,
        "purpose": cp1.get("purpose"),
        "confidence": cp1.get("confidence"),
        "red_flags": cp1.get("red_flags", []),
        "next_step": cp1.get("next_step_hint"),
        "overview": overview,
        "reason": reason,
        "columns": columns,
        "playbook": dic.get("playbook", {})
    }


@app.post("/api/understand/{did}")
def understand(did: str):
    clean_id = _safe_did(did)
    profile_path = f"reports/profile_{clean_id}.json"
    if not os.path.exists(profile_path):
        raise HTTPException(status_code=404, detail=f"Profile for {clean_id} not found")
    cp2.run_cp2(profile_path)
    return _load("dictionary", clean_id)


@app.post("/api/plan/{did}")
def plan(did: str):
    clean_id = _safe_did(did)
    profile_path = f"reports/profile_{clean_id}.json"
    if not os.path.exists(profile_path):
        raise HTTPException(status_code=404, detail=f"Profile for {clean_id} not found")
    cp3.run_cp3(profile_path)
    return _load("plan", clean_id)


@app.post("/api/govern/{did}")
def govern(did: str):
    clean_id = _safe_did(did)
    plan_path = f"reports/plan_{clean_id}.json"
    if not os.path.exists(plan_path):
        raise HTTPException(status_code=404, detail=f"Plan for {clean_id} not found")
    governance.run_governance(plan_path)
    return _load("governance", clean_id)


@app.get("/api/governance/{did}")
def get_governance(did: str):
    return _load("governance", did)


@app.post("/api/execute/{did}")
def execute(did: str, payload: dict):
    clean_id = _safe_did(did)
    if "approved_ids" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'approved_ids' in request body")
    gov = _load("governance", clean_id)
    return executor.run_execution(clean_id, payload["approved_ids"], gov, preserve=payload.get("preserve"))


@app.get("/api/status/{did}")
def status(did: str):
    clean_id = _safe_did(did)
    return {
        "profile": os.path.exists(f"reports/profile_{clean_id}.json"),
        "dictionary": os.path.exists(f"reports/dictionary_{clean_id}.json"),
        "plan": os.path.exists(f"reports/plan_{clean_id}.json"),
        "governance": os.path.exists(f"reports/governance_{clean_id}.json"),
        "cleaned": os.path.exists(f"data/canonical/{clean_id}_cleaned.csv"),
        "report": os.path.exists(f"reports/report_{clean_id}.json")
    }


@app.get("/api/execution/{did}")
def get_execution(did: str):
    return _safe("execution", did) or {}


@app.get("/api/report/{did}")
def get_report(did: str):
    _require_cleaned(did)
    return _safe("report", did) or {}


@app.post("/api/report/{did}")
def report(did: str):
    _require_cleaned(did)
    return reporter.run_report(did)


@app.post("/api/export/{did}")
def export(did: str):
    _require_cleaned(did)
    return reporter.export_pack(did)


@app.get("/api/export/download/{did}")
def download_export(did: str):
    clean_id = _safe_did(did)
    _require_cleaned(clean_id)
    zip_path = f"exports/{clean_id}_export.zip"
    if not os.path.exists(zip_path):
        res = reporter.export_pack(clean_id)
        if res.get("blocked"):
            raise HTTPException(status_code=400, detail=res.get("reason", "Export blocked by contract gate"))
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Export archive could not be located")
    return FileResponse(
        zip_path,
        filename=f"dataforge_export_{clean_id}.zip",
        media_type="application/zip"
    )


@app.get("/api/eda/download/{did}")
def download_eda(did: str):
    clean_id = _safe_did(did)
    _require_cleaned(clean_id)
    html_path = f"exports/{clean_id}/eda_report.html"
    if not os.path.exists(html_path):
        eda_exporter.render_eda_html(clean_id)
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="EDA report could not be generated")
    return FileResponse(
        html_path,
        filename=f"dataforge_eda_{clean_id}.html",
        media_type="text/html"
    )


# --- EDA Studio Endpoints (Gated for Cleaned Data) ---
@app.get("/api/eda/report/{did}")
def get_eda_report(did: str):
    clean_id = _safe_did(did)
    _require_cleaned(clean_id)
    return eda_engine.run_full_eda(clean_id, force_refresh=False)


@app.get("/api/eda/catalog/{did}")
def eda_catalog(did: str):
    clean_id = _safe_did(did)
    _require_cleaned(clean_id)
    return eda_engine.build_catalog(clean_id)


@app.post("/api/eda/run/{did}")
def eda_run(did: str, payload: dict):
    clean_id = _safe_did(did)
    _require_cleaned(clean_id)
    if "analysis_id" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'analysis_id' in request body")
    return eda_engine.run_analysis(
        clean_id,
        payload["analysis_id"],
        payload.get("chart_type")
    )


@app.post("/api/eda/full/{did}")
def eda_full(did: str, force: bool = False):
    clean_id = _safe_did(did)
    _require_cleaned(clean_id)
    return eda_engine.run_full_eda(clean_id, force_refresh=force)


from src import eda_exporter


@app.post("/api/eda/export/{did}")
def eda_export(did: str):
    _require_cleaned(did)
    return eda_exporter.render_eda_html(did)


@app.post("/api/eda/compare")
def eda_compare(payload: dict):
    if "left_id" not in payload or "right_id" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'left_id' or 'right_id'")
    _require_cleaned(payload["left_id"])
    _require_cleaned(payload["right_id"])
    return eda_engine.compare_datasets(
        payload["left_id"],
        payload["right_id"]
    )


# --- Plugin & Telemetry Endpoints ---
from src import plugin_sandbox, plugin_drafter, plugins
from src.telemetry import telemetry


@app.post("/api/plugins/draft")
def p_draft(p: dict):
    if "request" not in p:
        raise HTTPException(status_code=400, detail="Missing 'request'")
    return {"code": plugin_drafter.draft(p.get("run_id", "draft"), p["request"])}


@app.post("/api/plugins/validate")
def p_validate(p: dict):
    if "code" not in p:
        raise HTTPException(status_code=400, detail="Missing 'code'")
    return plugin_sandbox.smoke_test(p["code"])


@app.post("/api/plugins/register")
def p_register(p: dict):
    if "name" not in p or "code" not in p:
        raise HTTPException(status_code=400, detail="Missing 'name' or 'code'")
    return {"path": plugin_sandbox.register(p["name"], p["code"])}


@app.get("/api/telemetry/insights")
def t_insights():
    return telemetry.insights()


# --- Cache Management Endpoint ---
@app.post("/api/cache/clear")
def clear_cache():
    from src.rag import memory_store
    memory_store.clear()
    return {"status": "cleared", "message": "RAG vector and semantic caches invalidated"}


# --- Module C: Adaptive Learning & Feedback Endpoints ---
from src.feedback import store
from src.preference import pref_model
from src.bandit import bandit


@app.post("/api/feedback")
def record_feedback(payload: dict):
    store.log(
        payload.get("run_id", "default"),
        payload["action"],
        payload.get("column_name", ""),
        payload.get("impact_pct", 0.0),
        payload.get("risk_level", "low"),
        payload.get("approved", True)
    )
    pref_model.train()  # Retrain preference model
    telemetry.record("approve" if payload.get("approved", True) else "reject", action=payload["action"])
    return {"status": "logged"}


@app.post("/api/bandit/select")
def select_alternative(payload: dict):
    if "action" not in payload or "alternatives" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'action' or 'alternatives'")
    return {"highlighted": bandit.select(payload["action"], payload["alternatives"])}


@app.post("/api/bandit/update")
def update_bandit(payload: dict):
    if "action" not in payload or "chosen_alt" not in payload or "was_picked" not in payload:
        raise HTTPException(status_code=400, detail="Missing parameters")
    bandit.update(payload["action"], payload["chosen_alt"], payload["was_picked"])
    return {"status": "updated"}


# --- Data Inspector Endpoints ---
from src import data_view


@app.get("/api/data/stages/{did}")
def get_stages(did: str):
    clean_id = _safe_did(did)
    return {"stages": data_view.get_available_stages(clean_id)}


@app.get("/api/data/{did}")
def get_data(did: str, stage: str = "raw", page: int = 1, page_size: int = 50, search: str = ""):
    clean_id = _safe_did(did)
    safe_page = max(1, page)
    safe_page_size = min(max(1, page_size), 500)
    return data_view.data_view(clean_id, stage=stage, page=safe_page, page_size=safe_page_size, search=search)


@app.get("/api/data/{did}/diff")
def get_diff(did: str, stage: str = "cleaned"):
    clean_id = _safe_did(did)
    return data_view.data_diff(clean_id, stage=stage)


from src import analyst_engine


@app.post("/api/preview/{did}")
def preview(did: str, payload: dict):
    """Dry-run a single step on the raw dataset snapshot and return what WOULD change without modifying data."""
    clean_id = _safe_did(did)
    prof = json.load(open(f"reports/profile_{clean_id}.json", encoding="utf-8"))
    df = pd.read_csv(prof["snapshot"]["csv"])
    after = executor.apply_step(df, payload)
    return data_view.diff_stages(df, after)


@app.post("/api/analyst/query/{did}")
def analyst_query(did: str, payload: dict):
    """Execute natural language analytical questions against cleaned dataset with automatic SQL and chart generation."""
    clean_id = _safe_did(did)
    _require_cleaned(clean_id)
    if "question" not in payload or not payload["question"].strip():
        raise HTTPException(status_code=400, detail="Missing 'question' string in request body")
    try:
        return analyst_engine.query_dataset(clean_id, payload["question"].strip())
    except Exception as e:
        logger.error(f"Analyst query error for {clean_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tokens")
def tokens(run_id: str = None, stage: str = None, scope: str = "all"):
    clean_id = _safe_did(run_id) if run_id else None
    return tracker.summary(run_id=clean_id, stage=stage, scope=scope)


# --- v2: Multi-Table Relational Ingest ---
@app.post("/api/ingest-multi")
async def ingest_multi(files: list[UploadFile] = File(...)):
    paths = []
    for f in files:
        safe = security.sanitize_filename(f.filename)
        path = f"uploads/{safe}"
        with open(path, "wb") as buf:
            shutil.copyfileobj(f.file, buf)
        paths.append(path)
    return phase1.run_phase1_multi(paths)


# --- v2: Background Async Jobs ---
from src.jobs import queue as job_queue
from src import job_tasks


@app.post("/api/jobs/{task_name}")
def submit_job(task_name: str, payload: dict = Body(default_factory=dict)):
    if task_name not in job_tasks.REGISTRY:
        raise HTTPException(status_code=404, detail=f"Unknown job task: {task_name}")
    fn = job_tasks.REGISTRY[task_name]
    job = job_queue.submit(task_name, fn, payload or {})
    return {"job_id": job.id, "status": job.status.value}


@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    j = job_queue.get(job_id)
    if not j:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return j.to_dict()


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    return {"cancelled": job_queue.cancel(job_id)}


@app.get("/api/jobs")
def list_jobs(limit: int = 20):
    return {"jobs": job_queue.list(limit)}


# --- v2: Incidents & Remediation Learning Agent ---
from src import incidents, storage
from src.remediation_memory import memory as rem_memory
from src.remediation_ops import apply_plan as rem_apply_plan


@app.get("/api/incidents")
def get_incidents(unresolved: bool = False, limit: int = 50):
    return {"incidents": incidents.list_incidents(unresolved_only=unresolved, limit=limit)}


@app.post("/api/incidents/{inc_id}/approve")
def approve_incident(inc_id: str, payload: dict):
    inc = incidents.get_incident(inc_id)
    if not inc or not inc.get("proposal"):
        raise HTTPException(status_code=404, detail="Incident or proposal not found")

    dataset_id = _safe_did(payload.get("dataset_id"))
    plan = inc["proposal"]
    csv_path = storage.ensure_local(f"data/canonical/{dataset_id}_cleaned.csv")
    if not csv_path or not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Cleaned dataset not found")

    df = pd.read_csv(csv_path)
    df = rem_apply_plan(df, plan)
    df.to_csv(csv_path, index=False)
    storage.save_artifact(csv_path)

    # Reward the bandit arm
    sig = inc.get("sig") or rem_memory.signature(inc)
    pid = inc.get("plan_id") or rem_memory.add_candidate(sig, plan)
    rem_memory.update(sig, pid, True)

    incidents.mark_resolved(inc_id, {"resolution": "approved_by_user", "plan": plan, "sig": sig, "plan_id": pid})
    return {"status": "applied_and_learned", "impact": plan.get("impact"), "plan_id": pid}


@app.post("/api/incidents/{inc_id}/reject")
def reject_incident(inc_id: str):
    inc = incidents.get_incident(inc_id)
    if inc and inc.get("proposal"):
        plan = inc["proposal"]
        sig = inc.get("sig") or rem_memory.signature(inc)
        pid = inc.get("plan_id") or rem_memory.add_candidate(sig, plan)
        rem_memory.update(sig, pid, False)
    incidents.update_incident(inc_id, {"rejected": True, "resolved": True, "resolution": "rejected_by_user"})
    return {"status": "rejected_and_memorized"}


# --- Query Audit & Schema Inspector Endpoints ---
from src.query_audit import audit_logger


@app.get("/api/queries/recent")
def recent_queries(dataset_id: str = None, limit: int = 100):
    clean_id = _safe_did(dataset_id) if dataset_id else None
    return {"queries": audit_logger.get_recent(clean_id, limit=limit)}


# --- Agentic Dynamic Web Scraper Endpoints ---
from src.scraper_agent import scraper, compliance


@app.post("/api/scrape/start")
def start_scrape(payload: dict):
    if "url" not in payload or not payload["url"].strip():
        raise HTTPException(status_code=400, detail="Missing target 'url' in request body")
    
    url = payload["url"].strip()
    max_pages = min(max(1, payload.get("max_pages", 5)), 50)
    proxy = payload.get("proxy")

    def scrape_task(job_id=None):
        tos_check = compliance.check_tos(url)
        df, stats = scraper.scrape(url, max_pages=max_pages, proxy=proxy)
        
        if stats.get("status") == "blocked_captcha":
            return {
                "status": "blocked_captcha",
                "tos_check": tos_check,
                "stats": stats,
                "reason": stats.get("reason")
            }
            
        pii_check = compliance.check_pii(df) if not df.empty else {"status": "clean", "columns": []}
        domain = url.split("//")[-1].split("/")[0].replace(".", "_")
        csv_path, prof = scraper.save_scraped_data(df, domain) if not df.empty else (None, None)
        
        return {
            "status": "success" if not df.empty else "empty",
            "csv_path": csv_path,
            "dataset_id": prof["dataset_id"] if prof else None,
            "profile": prof,
            "tos_check": tos_check,
            "pii_check": pii_check,
            "stats": stats
        }

    job = job_queue.submit("scrape", scrape_task, {"url": url, "max_pages": max_pages})
    return {"job_id": job.id, "status": job.status.value}


@app.post("/api/scrape/preview")
def preview_scrape(payload: dict):
    if "url" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'url'")
    url = payload["url"].strip()
    tos_check = compliance.check_tos(url)
    df, stats = scraper.scrape(url, max_pages=1, proxy=payload.get("proxy"))
    return {
        "url": url,
        "tos_check": tos_check,
        "rows_found": len(df),
        "columns": list(df.columns) if not df.empty else [],
        "preview_data": df.head(10).to_dict(orient="records") if not df.empty else [],
        "stats": stats
    }


# --- Niche Research & Social Listening Endpoints ---
from src import niche_research, competitor_intel, research_automation


@app.get("/api/research/suggestions")
def get_niche_suggestions(category: str = "all", limit: int = 6, force_refresh: bool = False):
    return {"suggestions": niche_research.suggest_niches(category=category, limit=limit)}


@app.post("/api/research/hunt")
async def hunt_opportunities(payload: dict = Body(default_factory=dict)):
    from src.opportunity_hunter import hunter
    category = payload.get("category", "all")
    limit = int(payload.get("limit", 6))
    opportunities = await hunter.hunt(category=category, limit=limit)
    return {"opportunities": opportunities, "count": len(opportunities)}


@app.get("/api/research/deep-dive/{niche}")
def get_deep_dive(niche: str):
    return niche_research.generate_deep_dive_product(niche)


@app.post("/api/research/agentic-deep-dive")
async def agentic_deep_dive(payload: dict = Body(default_factory=dict)):
    from src.agentic_orchestrator import orchestrator
    niche = payload.get("niche", "Product Niche")
    depth = payload.get("depth", "comprehensive")
    return await orchestrator.research_niche(niche, depth=depth)


@app.get("/api/research/competitors/{niche}")
def get_competitors(niche: str):
    from src.competitor_discovery import competitor_discovery
    return {"niche": niche, "competitors": competitor_discovery.discover_competitors(niche)}


@app.get("/api/research/scenarios/{niche}")
def get_scenarios(niche: str, units: int = 100, price: float = 50.0, category: str = "E-Commerce"):
    from src.scenario_planning import scenario_planner
    return scenario_planner.generate_scenarios(niche, {'units_per_month': units, 'price_usd': price}, category=category)


@app.post("/api/research/inject-dataset")
@app.post("/api/research/export-to-dataset")
def inject_niche_dataset(payload: dict = Body(default_factory=dict)):
    niche = payload.get("niche", "Product Niche")
    dataset_type = payload.get("dataset_type", "comprehensive")
    res = niche_research.generate_and_inject_dataset(niche, dataset_type=dataset_type)
    return {
        "status": "success",
        "primary_dataset": res,
        "total_rows": res.get("rows", 180),
        "quality_issues_injected": res.get("quality_issues_injected", True),
        **res
    }


@app.post("/api/research/blueprint")
def create_business_blueprint(payload: dict = Body(default_factory=dict)):
    niche = payload.get("niche", "Market Opportunity")
    category = payload.get("category", "E-Commerce")
    return niche_research.generate_business_blueprint(niche, category=category)


@app.post("/api/research/track-engagement")
def track_engagement(payload: dict = Body(default_factory=dict)):
    from src.preference_learning import get_preference_learner
    from src.workspace import get_workspace
    learner = get_preference_learner(get_workspace())
    learner.record_engagement(
        niche=payload.get("niche", "Niche"),
        category=payload.get("category", "E-Commerce"),
        action=payload.get("action", "viewed"),
        opportunity_score=payload.get("opportunity_score")
    )
    return {"status": "recorded"}


@app.get("/api/research/preferences")
def get_preferences():
    from src.preference_learning import get_preference_learner
    from src.workspace import get_workspace
    learner = get_preference_learner(get_workspace())
    return learner.get_stats()


@app.post("/api/research/preferences/reset")
def reset_preferences():
    from src.preference_learning import get_preference_learner
    from src.workspace import get_workspace
    learner = get_preference_learner(get_workspace())
    learner.reset()
    return {"status": "reset"}


@app.get("/api/research/cache/stats")
def cache_stats():
    from src.reddit_cache import reddit_cache
    return reddit_cache.stats()


@app.post("/api/research/cache/clear")
def clear_reddit_cache():
    from src.reddit_cache import reddit_cache
    reddit_cache.clear()
    return {"status": "cleared"}


@app.get("/api/research/list")
def research_list():
    return {"research": niche_research.list_research()}


@app.get("/api/research/{rid}")
def research_get(rid: str):
    r = niche_research.get_research(rid)
    if not r:
        raise HTTPException(status_code=404, detail="Research report not found")
    return r


@app.post("/api/research/swot")
def research_swot(payload: dict):
    rid = payload.get("research_id")
    r = niche_research.get_research(rid) if rid else None
    niche = payload.get("niche") or (r["niche"] if r else "Market Opportunity")
    return research_automation.generate_swot(rid or "swot", niche, r)


# --- Competitor Intelligence & Tracking Endpoints ---
@app.get("/api/intel/list")
def intel_list():
    return {"competitors": competitor_intel._load_reg()}


@app.get("/api/intel/{cid}")
def intel_get(cid: str):
    r = competitor_intel.get_intel(cid)
    if not r:
        raise HTTPException(status_code=404, detail="Competitor intel report not found")
    return r


@app.post("/api/intel/track")
def intel_track(payload: dict):
    url = payload.get("url")
    name = payload.get("name", "")
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in payload")
    job = job_queue.submit("intel_track", competitor_intel.track, {"url": url, "name": name})
    return {"job_id": job.id, "status": job.status.value}


@app.post("/api/intel/{cid}/refresh")
def intel_refresh(cid: str):
    reg = [r for r in competitor_intel._load_reg() if r["id"] == cid]
    if not reg:
        raise HTTPException(status_code=404, detail="Competitor not found in registry")
    job = job_queue.submit("intel_track", competitor_intel.track, {"url": reg[0]["url"], "name": reg[0]["name"]})
    return {"job_id": job.id, "status": job.status.value}


@app.post("/api/intel/reviews")
def intel_reviews(payload: dict):
    reviews = payload.get("reviews", [])
    return competitor_intel.analyze_reviews(reviews)


# --- Research Automation & Alert Endpoints ---
@app.get("/api/alerts")
def get_alerts():
    return {"alerts": research_automation.detect_alerts()}


@app.post("/api/research/weekly")
def run_weekly():
    job = job_queue.submit("weekly", research_automation.weekly_report, {"run_id": "weekly"})
    return {"job_id": job.id, "status": job.status.value}


@app.get("/api/research/weekly/latest")
def get_latest_weekly():
    return research_automation.latest_weekly() or {}


# --- Learning Activity & Distillation Endpoints ---
from src.adaptive_delegation import get_delegation_stats
from src.distillation_engine import distiller
from src.knowledge_graph import knowledge
from src.model_quality import probe_model, get_cached_tier, get_tier
from src.model_resilience import get_config, get_prompt_template

SETTINGS_PATH = "data/settings.json"


def _load_settings():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(SETTINGS_PATH):
        try:
            return json.load(open(SETTINGS_PATH, encoding="utf-8"))
        except Exception:
            pass
    return {"provider": "groq", "fallback": "none", "auto_l3": True, "alert_threshold": 65}


def _save_settings(s):
    os.makedirs("data", exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)


@app.get("/api/learning")
@app.get("/api/learning/stats")
def api_learning_stats():
    stats = get_delegation_stats()
    # Flatten for quick frontend StatTile reads
    return {
        "learned_fixes": stats["knowledge_graph"]["cleaning_rules"],
        "signatures": stats["knowledge_graph"]["columns_learned"],
        "validated": stats["distillation"]["total_models"],
        **stats
    }


@app.get("/api/learning/knowledge-graph")
def api_knowledge_graph():
    return knowledge.graph


@app.post("/api/learning/distill")
def api_force_distill(payload: dict):
    task_type = payload.get("task_type", "semantic_type")
    success = distiller._try_distill(task_type)
    return {"status": "trained" if success else "insufficient_examples"}


# --- Model Resilience & Settings Endpoints ---
@app.get("/api/settings")
def api_get_settings():
    s = _load_settings()
    # Mask api_key if present for UI safety
    key = s.get("api_key") or os.getenv("api_key") or os.getenv("GROQ_API_KEY") or ""
    masked_key = (key[:4] + "••••••••" + key[-4:]) if len(key) >= 8 else ("••••••••" if key else "")
    return {
        **s,
        "api_key_masked": masked_key,
        "has_key": bool(key)
    }


@app.post("/api/settings")
def api_update_settings(payload: dict):
    s = _load_settings()
    # If the user sent a new real key (not masked), update it
    if "api_key" in payload and "••••••••" not in payload["api_key"]:
        s["api_key"] = payload["api_key"]
        os.environ["api_key"] = payload["api_key"]
    for k in ["provider", "model", "fallback", "auto_l3", "alert_threshold", "api_url"]:
        if k in payload:
            s[k] = payload[k]
    _save_settings(s)
    return {"status": "ok", "settings": s}


@app.post("/api/settings/test-key")
def api_test_key(payload: dict = Body(default_factory=dict)):
    from src.llm import test_connection
    provider = payload.get("provider", "groq")
    key = payload.get("api_key") or os.getenv("api_key") or os.getenv("GROQ_API_KEY") or ""
    model = payload.get("model", "openai/gpt-oss-20b" if provider == "groq" else "gpt-4o-mini")
    res = test_connection(provider=provider, api_key=key, model=model)
    return res


@app.get("/api/model/tier")
def api_get_tier():
    cached = get_cached_tier()
    if cached:
        return cached
    return {"tier": "mid", "score": 2.0, "percentage": 66.7, "message": "Model not probed yet"}


@app.get("/api/model/probe")
def api_probe_model():
    return probe_model("probe_run")


@app.get("/api/model/config")
def api_model_config():
    return {
        "config": get_config(),
        "tier": get_tier(),
        "templates": {
            "cp2": get_prompt_template("cp2_system"),
            "cp3": get_prompt_template("cp3_system"),
            "narrative": get_prompt_template("narrative_system")
        }
    }


# --- Phase 4.1: Reproducible Jupyter Notebook Export ---
from src.notebook_export import generate_notebook
import nbformat
from fastapi.responses import Response, StreamingResponse


@app.get("/api/export/notebook/{dataset_id}")
def export_notebook(dataset_id: str):
    did = _safe_did(dataset_id)
    _require_cleaned(did)
    try:
        nb = generate_notebook(did)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    nb_json = nbformat.writes(nb)
    return Response(
        content=nb_json,
        media_type="application/x-ipynb+json",
        headers={"Content-Disposition": f"attachment; filename=dataforge_pipeline_{did}.ipynb"}
    )


# --- Phase 4.2: Realtime SSE Streaming Gateway ---
from src.stream_gateway import stream_analyst_response


@app.post("/api/stream/analyst")
async def stream_analyst(payload: dict):
    question = payload.get("question")
    dataset_id = payload.get("dataset_id")

    if not question or not dataset_id:
        raise HTTPException(status_code=400, detail="Missing question or dataset_id")

    did = _safe_did(dataset_id)
    _require_cleaned(did)

    return StreamingResponse(
        stream_analyst_response(question, did),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/stream/research")
async def api_stream_research(payload: dict = Body(default_factory=dict)):
    """Real-time SSE streaming for autonomous niche research & market intelligence."""
    from src.stream_gateway import stream_niche_research
    niche = payload.get("niche", "").strip()
    if not niche:
        raise HTTPException(status_code=400, detail="Missing 'niche' query in payload")
    
    avg_price = float(payload.get("avg_price", 50.0))
    category = payload.get("category", "All")

    return StreamingResponse(
        stream_niche_research(niche, avg_price=avg_price, category=category),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# --- Phase 4.4: Multi-Tenant Workspace Tenancy Endpoints ---
@app.get("/api/workspaces")
def api_workspaces():
    return {"workspaces": list_workspaces(), "active": get_workspace()}


@app.post("/api/workspaces/{workspace_id}")
def api_create_workspace(workspace_id: str):
    try:
        set_workspace(workspace_id)
        ensure_workspace_dir(workspace_id)
        return {"status": "created", "workspace_id": workspace_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Phase 6.0: Global AI Assistant & Context Endpoints ---
from src.assistant_engine import assistant_engine
from src.context_manager import context_manager


@app.post("/api/assistant/query")
async def assistant_query(payload: dict = Body(...)):
    session_id = payload.get("session_id", "default")
    query = payload.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query'")
    result = await assistant_engine.process_query(session_id, query)
    return result


@app.post("/api/assistant/stream")
async def assistant_stream(payload: dict = Body(...)):
    session_id = payload.get("session_id", "default")
    query = payload.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query'")
    return StreamingResponse(
        assistant_engine.process_query_stream(session_id, query),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.post("/api/context/update")
def api_update_context(payload: dict = Body(...)):
    session_id = payload.get("session_id", "default")
    context_manager.update_context(session_id, **payload)
    return {"status": "success", "context": context_manager.get_context(session_id).to_dict()}


@app.get("/api/context/current")
def api_get_context(session_id: str = "default"):
    return context_manager.get_context(session_id).to_dict()


# --- Phase 6.1: Future Intelligence & Systematic Invention Endpoints ---
from src.triz_engine import triz_engine
from src.tech_capability_graph import tech_capability_graph
from src.invention_pipeline import invention_pipeline


@app.get("/api/trends/parameters")
def get_triz_parameters():
    return {"parameters": triz_engine.get_parameters()}


@app.post("/api/trends/triz-resolve")
def resolve_triz(payload: dict = Body(...)):
    imp = payload.get("improving", "speed")
    wors = payload.get("worsening", "energy_efficiency")
    dom = payload.get("domain", "edge_ai_hardware")
    return triz_engine.resolve_contradiction(imp, wors, dom)


@app.post("/api/trends/invent")
def synthesize_invention(payload: dict = Body(...)):
    dom = payload.get("domain", "edge_ai_hardware")
    yr = int(payload.get("target_year", 2028))
    imp = payload.get("improving", "speed")
    wors = payload.get("worsening", "energy_efficiency")
    return invention_pipeline.synthesize_invention(
        domain=dom, target_year=yr, improving_param=imp, worsening_param=wors
    )


@app.post("/api/stream/invent")
async def stream_invention_endpoint(payload: dict = Body(...)):
    dom = payload.get("domain", "edge_ai_hardware")
    yr = int(payload.get("target_year", 2028))
    imp = payload.get("improving", "speed")
    wors = payload.get("worsening", "energy_efficiency")
    return StreamingResponse(
        invention_pipeline.stream_invention(domain=dom, target_year=yr, improving_param=imp, worsening_param=wors),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.get("/api/trends/tech-capability")
def get_tech_capability(tech: str = "edge_ai_silicon", year: int = 2027):
    return tech_capability_graph.get_capability(tech, year)


# --- Phase 6.2: Causal EDA & What-If Simulation Endpoints ---
from src.eda_engine import compute_causal_dag, generate_statistical_hypotheses
from src.analyst_engine import simulate_what_if


@app.get("/api/eda/causal/{dataset_id}")
def api_eda_causal(dataset_id: str):
    did = _safe_did(dataset_id)
    cleaned_path = f"data/canonical/{did}_cleaned.csv"
    if not os.path.exists(cleaned_path):
        raise HTTPException(status_code=404, detail="Dataset not found or not cleaned")
    df = pd.read_csv(cleaned_path)
    return compute_causal_dag(df)


@app.get("/api/eda/hypotheses/{dataset_id}")
def api_eda_hypotheses(dataset_id: str):
    did = _safe_did(dataset_id)
    cleaned_path = f"data/canonical/{did}_cleaned.csv"
    if not os.path.exists(cleaned_path):
        raise HTTPException(status_code=404, detail="Dataset not found or not cleaned")
    df = pd.read_csv(cleaned_path)
    return {"hypotheses": generate_statistical_hypotheses(df)}


@app.post("/api/analyst/simulate")
def api_analyst_simulate(payload: dict = Body(...)):
    did = _safe_did(payload.get("dataset_id"))
    prompt = payload.get("prompt", "")
    adjustments = payload.get("adjustments", {})
    try:
        return simulate_what_if(did, prompt, adjustments)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))







