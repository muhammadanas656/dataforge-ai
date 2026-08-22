# 📘 DataForge AI v2 — Architecture & System Guide

Welcome to **DataForge AI v2**! This document explains how the entire platform works under the hood — written with both **plain-English explanations** for fast understanding, and **technical specifications** for engineers.

---

## 🧭 Executive Summary: What is DataForge AI v2?

### In Simple Words:
> Preparing messy data manually is tedious, prone to human error, and expensive. Fully automated black-box tools often hallucinate or delete valuable rows.
>
> **DataForge AI v2 is your autonomous, governed data preparation, intelligence, and self-healing platform.**
> 1. **Big Data Scaling:** Ingests multi-GB files out-of-core using DuckDB, calculating true global statistics without memory crashes.
> 2. **Multi-Table Relational Schema:** Auto-detects foreign keys, referential integrity, and orphan rows across multiple uploaded tables, flattening them into a clean pipeline.
> 3. **The Autonomous LLM Critic:** Spots non-obvious cross-column rules (`special_price <= old_price`, `start_date <= end_date`) and derived features, validating them mathematically via dry-runs before proposals reach the user.
> 4. **Human Authority & Governance:** Every destructive step requires explicit approval. A cumulative **20% Over-Cleaning Budget** and **Impact Guardrails** prevent accidental data loss.
> 5. **Signal Preservation ("Flag, Don't Drop"):** Preserves anomaly rows for machine learning by creating binary flag columns (`is_<rule>_flag = 1`).
> 6. **The Self-Healing Learning Agent (L1 $\rightarrow$ L2 $\rightarrow$ L3):** Automatically learns from anomalies and errors. Safe micro-fixes auto-apply (L3); high-impact fixes request approval (L2); and all approved fixes are memorized (L1) to solve recurring anomalies for **0 tokens**.
> 7. **Interactive NL-to-SQL Analyst & Mode-Aware EDA:** Plain-English question answering with instant SQLite queries and thread-safe visualizations.

### The Technical Philosophy:
- **Deterministic Math = Truth** (computes statistics, calculates exact impact, executes transforms).
- **DuckDB = Scale** (zero-RAM out-of-core streaming for multi-GB files).
- **LLM = Critic & Agent** (discovers relational logic, explains anomalies, proposes remediations).
- **Validation Gate = Safety** (dry-runs LLM code against Pandas/SQLite; drops unverified hypotheses).
- **Remediation Memory = Evolution** (stores incident signatures to resolve future anomalies for $0 cost).
- **Human = Authority** (explicit permission matrix & 20% over-cleaning budget).

---

## 🏛️ System Architecture v2

```mermaid
flowchart TD
    A1[Single Large File: CSV, JSON, Parquet] --> B1[DuckDB Out-of-Core Stream]
    A2[Multi-Table Relational Files] --> B2[Relational FK & Orphan Engine]
    B2 --> B1
    
    B1 --> C[Statistical Profiler & Temporal Drift Monitor]
    C --> D[CP1: LLM Domain Classification & Grounded Red Flags]
    D --> E[Phase 2: Frugal Router & Semantic Dictionary]
    
    subgraph Frugal Cascade
        E1[Tier 1: Code Rules - 0 tokens] --> E2[Tier 2: RAG / Fuzzy Cache - 0 tokens]
        E2 --> E3[Tier 3: Compact LLM]
    end
    E --> Frugal Cascade
    
    Frugal Cascade --> CRITIC[Autonomous LLM Critic: Blind-Spot Scanner]
    CRITIC --> GATE[Pandas Mathematical Validation Gate]
    GATE --> F[Phase 3 & 4: Supervised Planning & Governance Engine]
    
    F --> G[Phase 6: Interactive Next.js Frontend]
    G --> H{User Approves Steps / Preserves Signals}
    
    H --> I[Phase 7: Safe Canonical Order Executor]
    
    subgraph Self-Healing Closed Loop
        I -- Anomaly / Rollback --> INC[Incident Registry]
        INC --> L1{L1 Memory Hit?}
        L1 -- Yes --> L1_APPLY[Apply Learned Fix - 0 Tokens]
        L1 -- No --> L2_AGENT[L2 Agent Proposal]
        L2_AGENT --> L3_CHECK{Safe Impact <= 5%?}
        L3_CHECK -- Yes --> L3_AUTO[L3 Auto-Fix & Memorize]
        L3_CHECK -- No --> L2_USER[Queue for Human Approval]
        L2_USER -- User Approves --> MEM_STORE[Store in Remediation Memory]
    end
    
    I --> J[Parquet Undo Snapshots & Post-Step Assertions]
    J --> K[Phase 8: Auditor CP4, Contract Gate & Export Pack]
    K --> L[Phase 9: Gated EDA Studio & NL Data Analyst]
    
    subgraph Async Infrastructure
        JOB_Q[Background JobQueue: 4 Workers]
        STORAGE[Persistent Storage: Local / AWS S3]
    end
```

---

## 🔬 Component Breakdown (Plain English + Technical Deep-Dive)

---

### 1. DuckDB Out-of-Core Big Data Ingestion (`ingest_big.py`, `phase1.py`)
- **Simple Explanation:** For large datasets ($>500\text{ MB}$), DataForge streams data directly into canonical Parquet using DuckDB. It calculates full-dataset counts (exact nulls, duplicates, row counts) without loading the full file into Python RAM.
- **Technical Details:**
  - `ingest_to_parquet`: Uses DuckDB `read_csv_auto`, `read_parquet`, or `read_json_auto` to stream files into `data/canonical/{id}.parquet`.
  - `profile_big`: Uses DuckDB SQL aggregates (`COUNT(*)`, `APPROX_COUNT_DISTINCT`, null aggregations) on disk.
  - `sample_from_parquet`: Samples 50,000 rows into pandas for interactive frontend exploration.

---

### 2. Multi-Table Relational Schema & Orphan Detection (`relational.py`)
- **Simple Explanation:** When users upload multiple related tables (e.g. `orders.csv` + `customers.csv`), DataForge automatically identifies primary and foreign keys, checks if references match, flags orphan records, and flattens tables for cleaning.
- **Technical Details:**
  - `detect_foreign_keys`: Matches `_id` suffix columns to candidate primary keys, requiring $>50\%$ referential integrity.
  - `orphan_counts`: Counts unreferenced child foreign keys.
  - `flatten`: Joins parent table attributes onto the primary table with collision-safe suffixes (`__{parent}`).

---

### 3. The Self-Healing Learning Agent (L1 $\rightarrow$ L2 $\rightarrow$ L3)
- **Simple Explanation:** When the system encounters an unexpected data quirk or execution error, it does not crash or give up. It logs an incident, the AI Agent suggests a safe fix, dry-runs it, and applies it. Safe micro-fixes apply automatically; dangerous ones ask you; and everything is memorized so it costs 0 tokens next time.
- **Technical Details:**
  - **`incidents.py`:** Central registry recording all pipeline exceptions, unexpected types, and rollbacks.
  - **`remediation_memory.py`:** Computes MD5 incident signatures (`kind`, `dtype`, `semantic`, `domain`, `column_pattern`). Recalls learned fixes for instant 0-token application (**L1**).
  - **`remediation_agent.py`:** Prompts the LLM with strict allowed operations (`coerce_numeric`, `coerce_date`, `fill_mode`, `clip`, `flag_outliers`, `custom_eval`, `drop_constant`, `extract_text`) and runs dry-run impact evaluation.
  - **`remediation_engine.py`:**
    - **L3 Auto-Fix:** If `drop_pct <= 5.0%` and `rows_dropped <= 500` on a non-destructive op, auto-applies and stores in memory.
    - **L2 Human Escalation:** If impact $> 5\%$ or operation is structural, queues incident in the UI for user approval.

---

### 4. Async Background Job Queue (`jobs.py`, `job_tasks.py`)
- **Simple Explanation:** Runs heavy tasks (full exploratory data analysis, large audit report generation) in background worker threads with real-time progress bars and cancellation buttons.
- **Technical Details:**
  - `JobQueue`: Threaded worker pool (4 workers) managing job states (`queued`, `running`, `done`, `error`, `cancelled`).
  - `_CancelProxy`: Allows long tasks to report fractional progress ($0.0 \rightarrow 1.0$) and check for user cancellation signals.

---

### 5. Persistent Storage Abstraction (`storage.py`)
- **Simple Explanation:** Files are saved seamlessly whether running locally on your laptop or deployed in multi-instance cloud environments (Render, AWS).
- **Technical Details:**
  - `LocalBackend`: File system operations with automatic directory creation.
  - `S3Backend`: Automatic upload and download caching via `boto3` when `S3_BUCKET` is configured.
  - `save_artifact()` / `ensure_local()`: Transparent persistence wrapper across the codebase.

---

### 6. Robust Data Coercion & Injection Shielding (`coercion.py`, `llm_context.py`)
- **Simple Explanation:** Normalizes messy real-world formats (US/EU numbers, currency symbols, boolean terms) without touching text product names, and protects the AI from prompt injection attacks embedded in dataset cells.
- **Technical Details:**
  - `coerce_series`: Detects locale decimals (`1.234,56` vs `1,234.56`), embedded currencies (`$1,200`), units (`12kg`, `50%`), and booleans (`Y/N`, `TRUE/FALSE`, `1/0`).
  - `safe_samples_for_llm`: Transiently masks PII values (`<email>`, `<phone>`) **only in prompts** (raw data remains 100% untouched) and encloses samples in `=== UNTRUSTED DATA BEGIN / END ===` delimiters.

---

### 7. Autonomous LLM Critic & Validation Gate (`llm_critic.py`)
- **Simple Explanation:** Spots non-obvious business logic violations and useful feature engineering opportunities.
- **Technical Details:**
  - Discovers multi-column relational logic (`special_price <= old_price`, `start_date <= end_date`).
  - Dry-runs expressions using Pandas `df.query()` and `df.eval()`.
  - Impact Guardrail: Automatically flags rules with $>20\%$ drop rate as `high_impact = True` and `risk = high`.

---

### 8. Interactive Natural Language AI Data Analyst (`analyst_engine.py`, `/cleaned`)
- **Simple Explanation:** An interactive assistant on the Cleaned Data page that translates plain English questions into safe SQLite `SELECT` queries with instant data tables and executive narratives.
- **Technical Details:**
  - Dynamic in-memory SQLite table reflection (`Table: dataset`).
  - Strict SQL Safety Validator: Rejects `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`, `ATTACH`, `PRAGMA`.

---

## 💻 API Reference Cheat Sheet v2

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check |
| `GET` | `/api/datasets` | List all uploaded datasets |
| `POST` | `/api/upload` | Single-file upload & Phase 1 profiling (DuckDB auto-routing for big files) |
| `POST` | `/api/ingest-multi` | Multi-table relational file upload & FK inference |
| `GET` | `/api/profile/{did}` | Retrieve statistical profile JSON |
| `GET` | `/api/data/stages/{did}`| Get available pipeline stage snapshot IDs |
| `GET` | `/api/data/{did}` | Paginated, searchable data table for any stage |
| `GET` | `/api/data/{did}/diff` | Row-level and cell-level diff vs prior stage |
| `POST` | `/api/preview/{did}` | Dry-run transformation preview on raw snapshot |
| `POST` | `/api/understand/{did}` | Run CP2 dictionary generation via Frugal Router |
| `POST` | `/api/plan/{did}` | Generate impact-scored cleaning plan with CP3 & Critic review |
| `POST` | `/api/govern/{did}` | Classify permissions, guardrails & over-cleaning budget |
| `POST` | `/api/execute/{did}` | Execute approved step IDs with Signal Preservation & undo snapshots |
| `POST` | `/api/analyst/query/{did}` | Natural language to SQL query execution on cleaned data |
| `GET` | `/api/eda/catalog/{did}` | Mode-aware recommended & dimmed analysis catalog |
| `POST` | `/api/eda/run/{did}` | Run specific statistical analysis |
| `POST` | `/api/jobs/{task_name}` | Submit asynchronous background job (`full_eda`, `generate_report`) |
| `GET` | `/api/jobs/{job_id}` | Poll background job progress and retrieve result |
| `POST` | `/api/jobs/{job_id}/cancel`| Cancel running background job |
| `GET` | `/api/incidents` | List open/resolved system incidents |
| `POST` | `/api/incidents/{id}/approve`| Approve AI remediation proposal & learn into memory |
| `POST` | `/api/incidents/{id}/reject` | Reject AI proposal & memorize negative constraint |
| `POST` | `/api/report/{did}` | Generate distribution shift, PSI/KS drift & CP4/5 audit |
| `POST` | `/api/export/{did}` | Build gated reproducible export package |
| `GET` | `/api/tokens` | Live token consumption, RAG savings & cost tracker |

---

## 🏃 Fast Start Guide

### 1. Local Development
```powershell
# Backend (Port 8000)
cd backend
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload

# Frontend (Port 3000)
cd frontend
npm run dev
```

### 2. Run Comprehensive Test Suite (62 Tests)
```powershell
cd backend
python -m pytest tests -v
```

### 3. Docker One-Command Run
```powershell
docker-compose up --build
```
Open [http://localhost:3000](http://localhost:3000) in your browser!
