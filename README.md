# ⚡ DataForge AI — Enterprise Multi-Modal Autonomous Intelligence & Design Cloud

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-160%2F160%20Passed%20(100%25)-brightgreen)](https://github.com/muhammadanas656/dataforge-ai)
[![Security](https://img.shields.io/badge/Security-AST%20Hardened%20Sandbox-blue)](https://github.com/muhammadanas656/dataforge-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **DataForge AI** is an enterprise-grade autonomous data intelligence, causal discovery, systematic TRIZ invention, and generative vector design cloud. It securely learns from real-world web data under strict quality and privacy gates, distills insights into local zero-token memory, generates working code in a sandboxed runtime, and invents future design systems with typed React JSX and Vue 3 exports.

---

## 🌟 Core Architectural Subsystems

### 1. 🧭 Autonomous Governed Cleaning Studio (CP1 → CP4)
- **CP1 Profiler:** Out-of-core streaming ingestion via DuckDB and Pandas with type fingerprinting.
- **CP2 Data Dictionary Author:** Frugal semantic inference (`T1_rules` → `T2_rag` → `T3_llm`).
- **CP3 Plan Formulator & Blind-Spot Scanner:** Deterministic IQR outlier clipping, MICE multivariate chained regression imputation, and duplicate remediation with LLM Critic review.
- **CP4 Governance & Executor:** Contract gating, reversible transactions, and immutable audit logs.

### 2. 📊 Exploratory Data Analysis & Causal DAG Studio
- **Multi-Representation EDA:** Mathematical histograms, box plots, Pareto charts, and scatter plots.
- **Causal DAG Discovery:** Automated Directed Acyclic Graph (DAG) discovery via regularized precision matrix inversion ($\mathbf{\Theta} = (\mathbf{\Sigma} + \lambda \mathbf{I})^{-1}$) with conditional dependence mapping.
- **Multimodal Causal Flattening:** Deep recursive JSON tree flattening with PageRank graph topological feature extraction.
- **Statistical Hypothesis Engine:** Formal hypothesis testing with ANOVA $p$-values and Cohen's $d$ effect sizes.

### 3. 💡 Strategic Invention & Risk Studio (2026–2030+)
- **TRIZ Contradiction Matrix:** Altshuller's 39×40 contradiction resolution for domain-bridging trade-off elimination.
- **Neural Contradiction Engine:** Resolves modern AI tradeoffs (MoE vs dense latency, vLLM paged attention vs memory, ZK rollups vs prover latency).
- **Fat-Tail & Heavy-Tailed Risk Engine:** Models extreme volatility via Student-t ($df=3$) and Pareto distributions with Value at Risk (VaR 95%) and Expected Shortfall (CVaR).

### 4. 🌐 Closed-Loop Real-World Learning & WebRadar Studio
- **Enterprise SSRF Protection:** Pre-flight socket DNS validator blocking AWS/GCP metadata (`169.254.169.254`), private subnets, and loopbacks.
- **Data Quality Gates:** Validates content bounds ($50 \le \text{chars} \le 100,000$), domain relevance ($\ge 0.15$), duplicate Jaccard similarity ($\ge 0.95$), and exponential freshness decay.
- **Privacy Compliance:** Intercepts and blocks high-risk PII (SSNs, credit cards) and verifies copyright licensing.
- **Incremental Learning & Model Rollback:** Manages versioned model snapshots (v1, v2) with automatic rollback if accuracy drops by $>5\%$.
- **Knowledge Conflict Resolver:** Resolves contradicting claims using freshness and direct user feedback overrides.

### 5. 🎨 Generative Trend Invention & Design Studio
- **Morphological Cross-Synthesis:** Combines surface physics (Liquid Glassmorphism, Quantum Neumorphism), lighting models (Volumetric Glow, Chromatic Dispersion), and geometric topologies (Fractal Bento, 2.5D Isometric Depth).
- **TRIZ Design Operators:** Principles #1 (Segmentation), #15 (Dynamicity), #19 (Periodic Glow), and #35 (Parameter Inversion).
- **Validated 6D SVG Fitness & Human Calibration:** Scores vector assets across Validity (20%), WCAG AAA Accessibility (20%), HSL Harmony (15%), Complexity (15%), Scalability (15%), and Performance (15%) with confirmed human aesthetic correlation ($r \ge 0.75$).
- **Multi-Framework Export:** Compiles vector assets to typed React JSX (with camelCase bindings `strokeWidth`), Vue 3 `<template>`/`<script setup>` SFCs, and W3C/Figma DTCG Token JSON.

### 6. 🛡️ AST Sandbox Security & Executable Self-Evolution
- **10/10 Bypass Vectors Blocked:** Deep AST static analysis blocking `importlib`, `ctypes`, `pickle`, `__import__`, dunder traversal (`__subclasses__`), and malicious string literals.
- **Dynamic Executable Code:** Synthesizes, compiles, and executes verified Python functions on user demand inside thread timeout bounds (max 3.0s).

### 7. 🤖 Global AI Copilot & Scenario Value Reasoner
- **Scenario Impact Reasoner:** Decomposes queries into **Direct Business ROI**, **Real-World Walkthrough**, **Critical Mistake Avoided**, and clickable workspace redirection cards (`/clean`, `/intel`, `/niche`, `/eda`, `/export`).
- **Zero-Token Memory Cache:** Sub-50ms instant recall saving $>1,000$ tokens per workflow.
- **3-Tier Adaptive Explanations:** Real-time toggle between **Simple Mode (ELI5 Analogies)** and **Technical Deep-Dive**.

---

## 🧪 Master Test Suite (160 / 160 Tests Passing)

```bash
cd backend
python -m pytest tests/ -v
```

| Test Suite File | Tests | Key Focus | Status |
|---|---|---|---|
| `test_visual_coherence_and_production_completion.py` | 6 | Human aesthetic calibration (r>=0.75), deep TRIZ, E2E export, WCAG AAA | ✅ 6/6 |
| `test_hardened_security_and_novel_evolution_loop.py` | 6 | 10 sandbox bypasses, 6D SVG fitness, privacy telemetry, TRIZ output validation | ✅ 6/6 |
| `test_generative_design_invention_and_trend_creation.py` | 4 | Generative trend invention, TRIZ operators, Figma tokens, SVG self-evolution | ✅ 4/4 |
| `test_sandbox_security_and_design_screenshot_loop.py` | 7 | Sandbox AST blocking, execution timeout, live search telemetry, visual refiner | ✅ 7/7 |
| `test_scenario_reasoning_and_autonomous_eval_loop.py` | 7 | Scenario impact reasoning, executable self-evolution, benchmark loop | ✅ 7/7 |
| `test_self_evolution_and_quality_gates.py` | 8 | Self-evolution plans, quality gates, PII, model rollback, user feedback | ✅ 8/8 |
| `test_real_world_internet_crawl_learning_and_design_loop.py` | 7 | SSRF crawl, RAG ingestion, distillation, SVG React code, Causal DAG | ✅ 7/7 |
| `test_how_to_navigation_and_redirection.py` | 7 | Step-by-step guidance, relative route buttons, /clean, /intel, /niche | ✅ 7/7 |
| `test_adaptive_explanations_and_frontend_contracts.py` | 8 | ELI5 analogies, TRIZ cheat sheet, SVG export contracts | ✅ 8/8 |
| `test_neural_contradictions_and_fat_tails.py` | 5 | Modern AI/ZK tradeoffs, Student-t fat tails, VaR 95% | ✅ 5/5 |
| `test_multimodal_causal_and_monitoring.py` | 4 | Nested JSON flattening, graph PageRank, health monitor | ✅ 4/4 |
| `test_production_security_and_ssrf.py` | 8 | SSRF gates, AWS metadata blocking, sanitization | ✅ 8/8 |
| `test_svg_asset_and_workflow_orchestration.py` | 6 | SVG generation, React/Vue code, workflow orchestration | ✅ 6/6 |
| `test_ecosystem_universal_qa_and_teaching.py` | 9 | Universal QA, 0-token cache, actionable outputs | ✅ 9/9 |
| `test_webradar_seo_and_design_studio.py` | 6 | 360° SEO, DesignLens, Core Web Vitals, Token Export | ✅ 6/6 |
| `test_autonomous_copilot_unseen_frontier_and_scraping_stress.py` | 12 | Unseen Copilot queries, JSON-in-CSV, multi-lingual | ✅ 12/12 |
| `test_extreme_edge_cases_and_boundary_hardening.py` | 15 | 100% NaNs, singular matrices, 10k injection, CP1-CP4 | ✅ 15/15 |
| `test_autonomous_copilot_and_token_cache.py` | 7 | Zero-token cache hits, session state, token savings | ✅ 7/7 |
| `test_ultra_penetration_scraper_and_enrichment.py` | 7 | Cloudflare XOR, international phones, 80%+ rate | ✅ 7/7 |
| `test_deep_scraper_and_anti_hallucination_eda.py` | 3 | Mathematical grounding, causal validation | ✅ 3/3 |
| `test_adversarial_stress_and_hardening.py` | 5 | Corrupted datasets, high-payload stress | ✅ 5/5 |
| `test_autopilot_and_copilot_resilience.py` | 3 | Autopilot orchestration, multi-turn dialogue | ✅ 3/3 |
| `real_data_ingest_test.py` | 5 | Real-world telemetry, healthcare, financial data | ✅ 5/5 |
| `test_niche_innovation_resilience.py` | 5 | TRIZ 39×40 synthesis, Monte Carlo distributions | ✅ 5/5 |
| **Total** | **160** | **100% Enterprise Pass Rate** | **✅ 160/160** |

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/muhammadanas656/dataforge-ai.git
cd dataforge-ai
```

### 2. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

pip install -r requirements.txt
cp .env.example .env

uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```
API docs available at `http://localhost:8000/docs`.

### 3. Frontend Setup (Next.js 14)
```bash
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📜 Documentation Directory Map

- **System Architecture & Subsystems:** [`docs/ARCHITECTURE_AND_SYSTEM_GUIDE.md`](file:///c:/skills%20development/learning%20datascience/DataForge%20AI/docs/ARCHITECTURE_AND_SYSTEM_GUIDE.md)
- **Legal, Intellectual Property & Standards:** [`docs/LEGAL_AND_DESIGN_STANDARDS.md`](file:///c:/skills%20development/learning%20datascience/DataForge%20AI/docs/LEGAL_AND_DESIGN_STANDARDS.md)
- **User Guide & Workflow Manual:** [`USER_MANUAL.md`](file:///c:/skills%20development/learning%20datascience/DataForge%20AI/USER_MANUAL.md)
- **System Specifications:** [`docs/SPEC_V3_LOCKED.md`](file:///c:/skills%20development/learning%20datascience/DataForge%20AI/docs/SPEC_V3_LOCKED.md)

---

## 📄 License
Released under the [MIT License](LICENSE).
