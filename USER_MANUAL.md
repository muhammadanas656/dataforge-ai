# DataForge AI: Complete System Manual & How It Works

Welcome to **DataForge AI** — an enterprise-grade autonomous market intelligence, data engineering, and automated exploratory data analysis platform.

---

## 🌟 What DataForge AI Offers

DataForge AI solves the two biggest bottlenecks in modern data and product development:
1. **"What to build?"** (Proactive market scouting, social listening, competitor reality checks, and Monte Carlo financial simulations).
2. **"How to clean and analyze messy data?"** (Supervised 4-stage data cleaning, KS-test distribution drift protection, automated visual charts, and streaming natural language SQL copilot).

---

## 🚀 The End-to-End User Journey

```
[1. Market Radar (/research)]
      │ (1-Click Business Blueprint & Synthetic Messy Dataset)
      ▼
[2. Mission Control (/)]
      │ (Raw CSV Ingest, Profiling & Null Inspection)
      ▼
[3. Cleaning Studio (/cleaning)]
      │ (Understand Semantic Types → AI Plan → Human Governance Approval)
      ▼
[4. Visual EDA (/eda)]
      │ (Automated Histograms, Correlation Matrices, Statistical Proofs)
      ▼
[5. Cleaned Explorer & AI Copilot (/cleaned)]
      │ (Streaming Plain-English SQL Q&A, Cell-by-Cell Diffs, .ipynb Export)
      ▼
[6. Governance Audit (/report)]
      │ (Contract Assertions, KS-Test Distribution Drift Verification, Zip Export)
```

---

## 📊 How to Read & Comprehend System Metrics

### 1. Opportunity Score (0 - 100)
- **What it measures**: The commercial viability and customer demand of a business niche.
- **Formula**:
  $$\text{Opportunity Score} = 0.30 \times \text{Demand} + 0.25 \times \text{Growth} + 0.25 \times \text{Pain Ratio} + 0.20 \times \text{Competition}$$
- **Interpretation**:
  - **$\ge 65$ (Green)**: High-opportunity market (strong organic discussion volume, high growth, and intense customer complaints about existing products).
  - **$40 - 64$ (Amber)**: Moderate opportunity.
  - **$< 40$ (Slate)**: Saturated or low-interest category.

### 2. TAM (Total Addressable Market)
- **Formula**:
  $$\text{TAM} = \text{Monthly Search Volume} \times 2\% \text{ Conversion Rate} \times \text{Target Unit Price} \times 12 \text{ Months}$$
- **Interpretation**: The realistic upper ceiling for annual revenue in this specific niche.

### 3. Monte Carlo Simulation (1,000 Iterations)
- **What it measures**: Financial risk under real-world randomness (simulating stochastic variations in customer traffic, advertising CAC, and conversion rates).
- **Interpretation**:
  - **Probability of Profit**: Percentage of the 1,000 simulated months that turned a net profit (aim for $>70\%$).
  - **P50 (Median Profit)**: The realistic expected monthly profit.
  - **P10 (Worst-Case)**: The downside risk during slow months.
  - **P90 (Best-Case)**: The viral upside scenario.
  - **Breakeven Month**: The exact month when cumulative net profits repay initial fixed startup costs.

### 4. Distribution Drift (Kolmogorov-Smirnov KS-Test)
- **What it measures**: Ensures that data cleaning operations (imputing medians, removing outliers) did not accidentally warp or distort the real-world statistical shape of your numbers.
- **Interpretation**:
  - **$p > 0.05$ (Passed)**: The cleaned distribution statistically matches the original raw distribution.
  - **$p \le 0.05$ (Warning)**: Significant distribution shift detected for audit review.

### 5. Governance Matrix (Ask vs Act)
- **Act (Auto-Executed)**: Non-destructive transformations (standardizing capitalization, trimming whitespace, imputing missing numbers via column medians).
- **Ask (Human Confirmation Required)**: Destructive transformations affecting $>5\%$ of rows (dropping outlier records or dropping entire columns).

---

## ⚡ 0-Token Knowledge Distillation

DataForge AI features a **Teacher-Student architecture**:
1. When a new column name (e.g. `cogs_usd` or `cust_age`) is first uploaded, a cloud LLM classifies its semantic type.
2. The user's confirmed decisions are stored in the local **Knowledge Graph**.
3. Once 15 interactions are recorded, DataForge automatically trains a lightweight local Random Forest classifier.
4. Future occurrences of identical or similar columns run locally on your CPU in **0.1 milliseconds** at **0 tokens** ($0.00 cost).

---

## 🛠️ API & Endpoint Quick Reference

- `GET  /api/research/suggestions`: Proactive opportunity radar suggestions.
- `POST /api/research/hunt`: Autonomous ReAct opportunity hunter.
- `GET  /api/research/deep-dive/{niche}`: Full 360-degree commercial evaluation.
- `POST /api/research/export-to-dataset`: 1-click realistic 12-month messy dataset injection.
- `POST /api/stream/analyst`: Real-time SSE streaming for plain-English SQL queries.
- `GET  /api/export/notebook/{dataset_id}`: Export reproducible `.ipynb` Jupyter Notebook.
- `GET  /api/report/{dataset_id}`: Formal quality certificate & KS-Test drift audit.
