# ⚡ DataForge AI — Autonomous Governed Data Preparation & Systematic Invention Platform

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS%20v4-38B2AC?logo=tailwind_css)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **DataForge AI** is an enterprise-grade autonomous data engineering, exploratory data analysis (EDA), and systematic market innovation studio. It pairs mathematical invariants and causal inference with frugal LLM orchestration to clean messy data, discover actionable insights, and invent breakthrough concepts with zero hallucinations.

---

## 🌟 Key Architecture & Capabilities

### 1. 🧭 Autonomous Governed Cleaning Studio (CP1 → CP4)
- **CP1 Profiler**: Automatic out-of-core ingestion via DuckDB and Pandas with type fingerprinting.
- **CP2 Data Dictionary Author**: Multi-tier frugal semantic inference (`T1_rules` → `T2_rag` → `T3_llm`).
- **CP3 Plan Formulator & Blind-Spot Scanner**: Generates deterministic IQR, null, and duplicate remediation with LLM Critic review.
- **CP4 Governance & Executor**: Contract gating, reversible transformations, and audit logs.

### 2. 📊 Exploratory Data Analysis & Causal Discovery
- **Multi-Representation EDA**: Interactive histograms, box plots, Pareto charts, and scatter plots with plain-English narratives.
- **Causal Inference Engine**: Automated Directed Acyclic Graph (DAG) discovery with conditional dependence mapping.
- **Statistical Hypothesis Engine**: Formal hypothesis testing with ANOVA $p$-values and Cohen's $d$ effect sizes.
- **Counterfactual Simulator**: What-if counterfactual scenario modeling.

### 3. 💡 Future Horizon & Systematic Invention Studio (2026–2030+)
- **TRIZ Contradiction Matrix**: 39×40 contradiction resolution for domain-bridging synthesis.
- **Morphological Analysis**: Combinatorial box exploring cross-domain dimensions.
- **Grounding & Guardrail Validation**: First-principles physical, regulatory, and unit economics validation.
- **Adversarial Skeptic Critic**: Hardened venture-capital level risk stress testing.

### 4. 🤖 Global AI Copilot (`AssistantWidget`)
- Zero-latency semantic RAG engine aware of the active dataset, workspace, and route context.
- Streaming real-time answers and deep-dive troubleshooting.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- A Groq, OpenAI, Gemini, or Anthropic API key

---

### 1. Clone the Repository

```bash
git clone https://github.com/muhammadanas656/dataforge-ai.git
cd dataforge-ai
```

---

### 2. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and insert your API key:
# api_key=your_api_key_here

uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be active at `http://localhost:8000`. API documentation available at `http://localhost:8000/docs`.

---

### 3. Frontend Setup (Next.js)

```bash
cd ../frontend
npm install
cp .env.example .env.local

npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🌐 Deploying to Vercel & Cloud

### 1. Deploy Frontend to Vercel
1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "feat: Initial DataForge AI release"
   git branch -M main
   git remote add origin https://github.com/muhammadanas656/dataforge-ai.git
   git push -u origin main
   ```
2. In [Vercel](https://vercel.com/):
   - Click **Import Project** and select `dataforge-ai`.
   - Set **Root Directory** to `frontend`.
   - Add the Environment Variable:
     - `NEXT_PUBLIC_API_URL` = `https://your-backend-api.onrender.com` (or your deployed backend URL).
   - Click **Deploy**.

### 2. Deploy Backend to Render / Railway / Fly.io
- Deploy the `backend/` directory using Python 3.11+.
- Start Command: `uvicorn src.api:app --host 0.0.0.0 --port $PORT`
- Set Environment Variables:
  - `api_provider` = `groq` (or `openai`)
  - `api_key` = `<YOUR_KEY>`
  - `api_model` = `openai/gpt-oss-20b`

---

## ⚙️ Configuration & Environment Variables

| Variable | Description | Default |
|---|---|---|
| `api_provider` | AI Provider (`groq`, `openai`, `gemini`, `anthropic`) | `groq` |
| `api_key` | Secret API key for AI Provider | Required |
| `api_model` | Active LLM model name | `openai/gpt-oss-20b` |
| `NEXT_PUBLIC_API_URL` | Frontend pointer to Backend FastAPI server | `http://localhost:8000` |

---

## 🧪 Testing & Verification

Run backend unit and integration test suites:

```bash
cd backend
pytest tests/ -v
```

Run frontend production build verification:

```bash
cd frontend
npm run build
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
