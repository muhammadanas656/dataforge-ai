"""
Autonomous Auto-Pilot Pipeline Orchestrator.
Chains Ingestion -> Profiling (CP1) -> Data Dictionary (CP2) -> Cleaning Plan (CP3) ->
Governed Execution (CP4) -> EDA Studio -> Causal Inference DAG in a single zero-touch run.
"""
import os
import json
import time
from typing import Dict, Any, Optional
import pandas as pd
from src.utils import logger
from src import phase1, cp2, cp3, governance, executor, eda_engine
from src.context_manager import context_manager

def run_autopilot(file_path_or_url: str, session_id: str = "default", cancel=None) -> Dict[str, Any]:
    """Execute complete zero-touch autonomous data cleaning and intelligence pipeline."""
    start_time = time.time()
    logger.info(f"[autopilot] Starting zero-touch pipeline for: {file_path_or_url}")
    
    stages = []
    
    # 1. Phase 1: Ingestion & Profiling
    if cancel and hasattr(cancel, "set_progress"):
        cancel.set_progress(0.15, "Phase 1: Ingesting & Profiling Schema...")
    prof = phase1.run_phase1(file_path_or_url)
    dataset_id = prof["dataset_id"]
    stages.append({
        "stage": "Phase 1: Profiling",
        "status": "completed",
        "rows": prof.get("shape", [0,0])[0],
        "columns": len(prof.get("columns", [])),
        "encoding": prof.get("encoding", "utf-8")
    })
    
    # 2. Phase 2: Frugal Data Dictionary
    if cancel and hasattr(cancel, "set_progress"):
        cancel.set_progress(0.35, "Phase 2: Formulating Semantic Data Dictionary...")
    dict_res = cp2.run_cp2(dataset_id)
    stages.append({
        "stage": "Phase 2: Semantic Data Dictionary",
        "status": "completed",
        "columns_classified": len(dict_res.get("dictionary", [])) if isinstance(dict_res, dict) else len(prof.get("columns", []))
    })
    
    # 3. Phase 3: Cleaning Plan & Critic
    if cancel and hasattr(cancel, "set_progress"):
        cancel.set_progress(0.55, "Phase 3: Synthesizing Cleaning Plan & Critic Review...")
    plan_res = cp3.run_cp3(dataset_id)
    stages.append({
        "stage": "Phase 3: Cleaning Plan",
        "status": "completed",
        "proposed_steps": len(plan_res.get("steps", []))
    })
    
    # 4. Phase 4: Governance & Deterministic Execution
    if cancel and hasattr(cancel, "set_progress"):
        cancel.set_progress(0.75, "Phase 4: Executing Governed Transformation...")
    gov_res = governance.run_governance(dataset_id)
    exec_res = executor.execute_plan(dataset_id)
    stages.append({
        "stage": "Phase 4: Governed Execution",
        "status": "completed",
        "quality_before": exec_res.get("before_quality", 0),
        "quality_after": exec_res.get("after_quality", 0),
        "quality_delta": exec_res.get("quality_delta", 0),
        "rows_retained": exec_res.get("after_rows", 0)
    })
    
    # 5. Phase 5: Visual EDA & Causal DAG Inference
    if cancel and hasattr(cancel, "set_progress"):
        cancel.set_progress(0.90, "Phase 5: Discovering Causal Drivers & Statistical Hypotheses...")
    eda_res = eda_engine.run_full_eda(dataset_id, force_refresh=True)
    causal_dag = eda_res.get("causal_dag", {})
    hypotheses = eda_res.get("hypotheses", [])
    stages.append({
        "stage": "Phase 5: Visual EDA & Causal DAG",
        "status": "completed",
        "causal_drivers_found": len(causal_dag.get("edges", [])),
        "hypotheses_evaluated": len(hypotheses)
    })
    
    elapsed = round(time.time() - start_time, 2)
    
    # Update Session Context
    context_manager.update_context(
        session_id=session_id,
        active_dataset_id=dataset_id,
        active_module="eda",
        action="autopilot_completed"
    )
    
    summary = {
        "status": "success",
        "dataset_id": dataset_id,
        "filename": os.path.basename(file_path_or_url),
        "elapsed_seconds": elapsed,
        "stages": stages,
        "quality_improvement": {
            "before": exec_res.get("before_quality", 0),
            "after": exec_res.get("after_quality", 0),
            "delta": exec_res.get("quality_delta", 0)
        },
        "causal_primary_driver": causal_dag.get("primary_insight", "No single dominant driver discovered."),
        "cleaned_paths": exec_res.get("cleaned_path", {}),
        "eda_summary": {
            "distributions": len(eda_res.get("distributions", {})),
            "hypotheses_count": len(hypotheses)
        }
    }
    
    logger.info(f"[autopilot] Pipeline completed successfully for {dataset_id} in {elapsed}s: Quality {exec_res.get('before_quality', 0)}% -> {exec_res.get('after_quality', 0)}%")
    return summary
