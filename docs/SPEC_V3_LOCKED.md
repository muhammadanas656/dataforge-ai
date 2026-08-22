# 📘 DataForge AI — Final MVP Specification v3.0 (LOCKED, FINAL)

**Status: FINAL. This document is the complete blueprint. Everything to be built is listed here. After this, we build.**

---

## 1. Vision & Principles

> Upload **any** dataset (CSV/JSON/Excel/Parquet/future plugins) → the tool normalizes it, profiles it, the LLM *understands* it, proposes a cleaning plan with exact impact, **you approve each destructive action**, it executes safely, exports a gated clean dataset, and finishes with an **intelligent, mode-aware EDA Studio** — with **live token/cost visibility**, and the tool **learns + gets cheaper** over time.

- **Code = hands** (execute, compute). **LLM = brain** (understand, supervise). **RAG = memory**. **Learning = adaptation**. **Human = authority.**
- **Statistics are the source of truth.** The LLM interprets; it never asserts an unverified number.
- **Format-agnostic core.** Inputs are plugins; the pipeline never changes.

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────┐
│ NEXT.JS FRONTEND: upload+preview | stepper | approvals | │
│ diff viewer | dictionary editor | chat | token dashboard │
│ audit | resume | explain-tooltips | representation toggle│
└──────────────────────────┬───────────────────────────────┘
            REST + progress stream
┌──────────────────────────▼───────────────────────────────┐
│ FASTAPI: orchestrator + job queue + checkpoints          │
│ AGENT GOVERNANCE: least-privilege + ask-vs-act           │
├──────────────┬─────────────────┬─────────────────────────┤
│ T1 Rules+ML  │ T2 RAG (local)  │ T3 LLM (Groq, 5 CPs)    │
│ $0           │ ~$0             │ frugal + cached         │
├──────────────┴─────────────────┴─────────────────────────┤
│ TOKEN TRACKER · GROUNDING VERIFIER · DRIFT MONITOR       │
│ LEARNING LAYER (preference/bandit/distill/prompts)       │
├──────────────────────────────────────────────────────────┤
│ SQLite + canonical snapshots + token_log + KB + models   │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Pipeline (9 Stages) — Full Feature List

| # | Stage | Features |
|---|---|---|
| 1 | **Agile Multi-Format Ingest** | **Source Registry** (`BaseSource` contract): CSV · JSON (flatten/explode) · Excel (sheets) · Parquet · TSV · *(plugin: web/API/DB)*. Auto-detect router (magic bytes + extension + sniff). Canonical normalization → typed DataFrame + schema metadata + snapshot (Parquet internal, CSV portable). Size/path guards, encoding+delimiter sniff, preview-before-commit, schema fingerprint, type-safety/coercion report, currency detect |
| 2 | **Profile** | stats/nulls/exact-dupes; outliers IQR+**IsolationForest**; near-dupes **fuzzy**; PII regex; adaptive sampling + chunking |
| 3 | **Understand** | data dictionary (semantic type, meaning, PII flag, confidence); domain detection; **PII masked before LLM**; summarized context; RAG-cached |
| 4 | **Plan (Context-Aware)** | consumes `mode` + comparison result; rules generate steps; **impact by code**; leakage detector; imputation incl **KNN**; recommendation scoring+tiers+risk+reasoning+alternatives; RAG past-plans; preference-model ranking; bandit alternative |
| 5 | **Review** | approval cards (impact, risk, tier, alternatives, why); cumulative impact budget + over-cleaning warning; approve/reject/modify |
| 6 | **Execute** | run approved in order; post-step validation gates; auto-rollback; per-step snapshots (undo); lineage |
| 7 | **Report** | before/after Quality Score; distribution-shift/cleaning-bias check; domain narrative (cached/surrogate); what-changed-and-why |
| 8 | **Export** | data-contract gates (block/warn); pack: cleaned CSV + dictionary + re-runnable config + audit + HTML report; versioned |
| 9 | **EDA Studio (Mode-Aware)** | **Modes:** Single · **Compare** (schema diff, row delta, per-column PSI/KS drift, category/metric deltas → change-driven recs) · *(Segment v2)*. Analysis catalog (enabled vs **dimmed-but-usable** + reason); chart conversions (inappropriate dimmed); one-click **Full EDA**; stat companions (tests+effect sizes); per-chart insights + narrative; **alterable representation** (chart/table/narrative per insight, comparison visuals); server-side aggregation; small-sample/over-plot guards; export charts+report+config |

---

## 4. Intelligence Layer

- **T1 Rules+Stats+ML ($0):** profiling, types, outliers, imputation, fuzzy-dedup, leakage, drift, PII.
- **T2 RAG (local):** cached descriptions, playbooks, recipes, past plans, user corrections. Retrieve first.
- **T3 LLM (Groq):** only on T1/T2 miss. Checkpoints **CP1** ingest · **CP2** profile · **CP3** plan · **CP4** audit · **CP5** narrative.
- **Frugal Router:** Rules→Stats→Small→RAG→Big LLM; escalate only if confidence<threshold.
- **Grounding Verifier:** LLM factual claims checked vs computed stats; contradictions rejected/relabeled "interpretation."
- **Drift Monitor:** PSI/KS raw↔cleaned + run↔run + A↔B (compare mode); alert/block on threshold.
- **Graceful degradation:** LLM outage → auto local-only mode.

---

## 5. Agent Governance

| Permission | Allows | Human? |
|---|---|---|
| READ | inspect/query/explain | No |
| TRANSFORM low | reversible, tiny | No (logged) |
| TRANSFORM med | reversible, impactful | One-click |
| DESTRUCTIVE high | irreversible | **Mandatory+impact** |

**Ask-vs-Act** risk=f(reversibility, %affected, sensitivity). **Roles:** Orchestrator·Profiler·Understanding·Cleaning·Analyst·Auditor·Reporter. Separation of duties.

---

## 6. Safety / Robustness (12-pt + extras)

PII mask · target-leakage · cleaning-leakage · schema-drift · silent-failure gates+rollback · over-cleaning budget · cleaning-bias · type-coercion · encoding · reproducibility+versioning · snapshots/undo · export contract gates. **Extras:** resumable state, async jobs, chunking, parsing, local-only, seeds, unit tests, observability, sample-dataset onboarding.

---

## 7. Recommendation Engine (Context-Aware)

Tiers (STRONGLY→NOT) = benefit − risk − impact-caution. Each: risk level, reasoning (why), **alternatives with trade-offs**. Ranked by learned preference model; alternative surfaced by bandit. **Adapts to analysis mode** (cleaning recs vs change-driven recs).

---

## 8. Token Observability

`TokenTracker` logs `{run, stage, cp, agent, model, prompt, completion, total, cached, saved}` → `token_log`; cost via price table; `GET /api/tokens`. **Dashboard:** live total · per-stage bar · per-agent · cache savings · est. cost · run history · budget alerts. **Budget:** first run ≈14–22K tokens; repeat ≈3–5K.

---

## 9. Module A — Grounding + Frugal (cross-cutting)
Frugal Router + Grounding Verifier + Drift Monitor wrapping all LLM calls (§4).

## 10. Module B — Self-Extension + Self-Awareness
Plugin contract (`BaseSource`/`BaseAnalysis`) — **same contract as ingestion sources**; LLM-assisted plugin draft → sandbox+tests → human approve → register · **user-code fallback** · telemetry self-insights → approved default-tuning · retrieval learning · resource efficiency (MiniLM ~80MB, on-disk, LRU, summaries).

## 11. Module C — Adaptive Learning + Efficiency (progressive)
Preference model (approve/reject→rank) · self-distillation (approved LLM outputs→local surrogate) · prompt self-refinement (accept/reject log→LLM rewrites→human approve) · bandit alternatives · threshold adaptation · adaptive sampling · active learning. **Activates once feedback accumulates; works day 1.**

---

## 12. Frontend (Next.js)
upload+preview · stepper(live) · approval cards · diff viewer · dictionary editor(feeds RAG) · chat(Analyst) · token dashboard · audit timeline · resume · explain-tooltips · representation toggle (chart/table/narrative) · mode selector (Single/Compare).

## 13. Tech Stack
Next.js · FastAPI · pandas/sklearn/scipy/rapidfuzz · sentence-transformers+on-disk store · Groq(Llama3) · SQLite · Plotly · Docker · Render.

---

## 14. Build Phases (13)

| # | Phase | Done Looks Like |
|---|---|---|
| 1 | Setup + **agile multi-format ingest** + profiling (CP1) | any file → canonical snapshot + profile JSON + preview |
| 2 | Understand + domain + PII (CP2) + RAG | dictionary+domain, PII masked, cached |
| 3 | Context-aware Plan + impact + leakage + recommendations (CP3) | plan w/ impact, tiers, alternatives |
| 4 | Governance (permissions + ask-vs-act) | risk-classified steps, escalation live |
| 5 | FastAPI + async + checkpoints + TokenTracker | API live, tokens logged |
| 6 | Next.js frontend (all widgets + mode selector + representation toggle) | interactive pipeline + token dashboard |
| 7 | Execute + Auditor (CP4) + rollback + snapshots | validated, undo-able execution |
| 8 | Report + gated export (CP5) | quality score, narrative, contract-gated pack |
| 9 | EDA Studio (Single + Compare + Full EDA) | catalog, insights, comparison visuals, chart export |
| 10 | Tests + Docker + deploy | green tests, one-command, public URL |
| 11 | Module A | cascade, verified claims, drift alerts |
| 12 | Module B | sandboxed plugin registered, telemetry insights |
| 13 | Module C | preference/bandit/distill active, cost curve ↓ |

---

## 15. Exclusions (v2) + Capability Ladder + Definition of Done

**Excluded now:** streaming · DB connectors · team collab · Segment mode · active-learning-retraining · **L4 autonomous core self-rewrite**.
**Ladder:** L1 grounded/frugal ✅ · L2 sandboxed plugins ✅ · L3 approved self-tuning ✅ · L3.5 learns+gets cheaper ✅ · L4 ❌ deferred.
**Done when:** upload any file → normalized+profiled+understood+planned → approve destructive steps w/ full impact → safe execute w/ rollback → contract-gated export → one-click intelligent EDA (single or compare) → live token/cost → add new source via sandboxed plugin → every LLM claim grounded, every run reproducible, and the tool measurably cheaper+smarter with use.

---
---

# 📖 In Plain Words: What The Tool Does, Step By Step

**Step 1 — You drop in a file.**
It can be CSV, Excel, JSON, or anything else you add later (even a website scraper). The tool figures out the format by itself, converts it into one standard shape, and shows you a quick preview before doing anything. It also tells you things like "this file has 7,878 rows, 682 are repeats, and this column has missing values."

**Step 2 — It understands your data.**
It reads the column names and sample values and tells you what each column actually is (a price? a person's name? a date? an email?). It guesses what kind of business/data this is (shop, hospital, bank, sports…). And it hides private info (names, emails, phones) before the AI ever sees it.

**Step 3 — It writes a cleaning plan.**
For every problem it found (repeats, missing values, weird numbers), it proposes a fix and tells you **exactly what will happen** if you apply it — like "this will delete 682 rows (8.6% of your data)." It also tells you what it recommends, what's optional, and what NOT to do — and why. It even gives you alternative options with their trade-offs.

**Step 4 — You decide.**
You see each fix as a card with its impact. You approve, reject, or change it. **Nothing is ever deleted or changed without your permission.**

**Step 5 — It cleans safely.**
It applies only what you approved, one step at a time. After each step it checks that the step actually did what it promised. If something goes wrong, it automatically undoes it. You can also undo any step yourself.

**Step 6 — It shows you the result.**
A before/after report: how much cleaner the data got, whether anything got accidentally skewed, and a plain-language summary written for your type of data.

**Step 7 — It exports with a final safety check.**
You get: the clean file, a dictionary explaining every column, a log of everything that was done, and a report. Before handing it over, it runs a final check to make sure the output isn't broken.

**Step 8 — It analyzes and explains.**
It suggests charts and analyses that make sense for your data. Irrelevant ones are greyed out (but you can still click them). One button runs a full analysis. Every chart comes with a statistical proof and a one-line plain-language insight. You can switch any insight between chart, table, or written text. And you can **compare two files** to see what changed between them.

**All the time, in the background:**
- It shows you **how much AI it used** (tokens and cost), live.
- It **double-checks the AI with math** — the AI is never allowed to state a wrong number as fact.
- If the AI service goes down, it **keeps working** using its local tools.
- It **learns from your choices**, so over time it recommends better and uses less AI (cheaper).
- It can **grow new abilities** (like web scraping) by adding small plugins — without breaking anything.

---

# 🟢 What The Tool Is Capable Of (Simple List)

- Accepts any file format and turns it into one standard shape.
- Explains what your data means, column by column.
- Finds problems (repeats, missing, weird values, private info, hidden leaks).
- Proposes fixes with exact impact — and never acts without your OK.
- Cleans safely, with automatic undo and checks after every step.
- Protects private information before the AI sees anything.
- Catches AI mistakes using math, so nothing false reaches your data.
- Compares two datasets and explains what changed.
- Makes charts, runs a full analysis with one click, and writes plain-language summaries.
- Shows AI cost live, and gets cheaper and smarter the more you use it.
- Can learn new abilities (plugins) safely, without breaking itself.

---

**Spec v3.0 is FINAL and LOCKED.** We build Phases 1→13 in order, testing each.
