"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, StatTile, Badge, Button } from "../components/ui";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { useDataset } from "../components/DatasetContext";
import {
  BookOpen,
  Brain,
  Activity,
  Coins,
  ShieldCheck,
  HelpCircle,
  Compass,
  Database,
  Wrench,
  BarChart3,
  Bot,
  Sparkles,
  ArrowRight,
  TrendingUp,
  CheckCircle2,
  AlertTriangle,
  FileCode2,
  Layers,
  Zap,
  DollarSign
} from "lucide-react";

const USER_JOURNEY_STEPS = [
  {
    step: 1,
    title: "1. Market Radar & Opportunity Hunting",
    route: "/research",
    icon: Compass,
    summary: "Discover what business or product to build before touching any data.",
    howItWorks: "The autonomous ReAct agent scans social channels (Reddit, forums), measures customer complaints, scrapes competitor prices, and estimates Total Addressable Market (TAM).",
    howToRead: "Look at the Opportunity Score (0-100). Scores above 60 indicate strong demand with unmet customer frustrations. Click 'Blueprint' to see 3-tier pricing and customer acquisition channels.",
    actionItem: "Click 'Open in Cleaning Studio' inside any blueprint to auto-generate a realistic 12-month messy financial dataset."
  },
  {
    step: 2,
    title: "2. Mission Control & Data Ingest",
    route: "/",
    icon: Database,
    summary: "Upload raw spreadsheets or scrape data tables directly from websites.",
    howItWorks: "Scans your raw CSV or HTML tables, detects column types, flags missing values, calculates duplicate percentages, and assigns a unique Dataset ID.",
    howToRead: "Review the Quality Health Score. Red flags indicate high null percentages or duplicate entries that need cleaning.",
    actionItem: "Select an active dataset from the top switcher, then click 'Cleaning Studio' to begin."
  },
  {
    step: 3,
    title: "3. Governed Cleaning Studio",
    route: "/cleaning",
    icon: Wrench,
    summary: "Systematically fix duplicates, negative numbers, and outliers with human approval.",
    howItWorks: "Runs a 4-stage pipeline: (1) Ingest, (2) Understand semantic types, (3) Plan transformations, and (4) Apply governance safety checks.",
    howToRead: "Check the Governance Matrix. Non-destructive actions (imputing medians, standardizing casing) are auto-executed ('Act'). Permanent row removals require your explicit click ('Ask').",
    actionItem: "Click 'Execute: Understand' → 'Execute: Plan' → 'Execute: Govern' to generate a mathematically cleaned table."
  },
  {
    step: 4,
    title: "4. Visual Exploratory Data Analysis (EDA)",
    route: "/eda",
    icon: BarChart3,
    summary: "Turn raw numbers into automated visual charts, distributions, and executive insights.",
    howItWorks: "Plots histograms, category market shares, and price correlation matrices. Automatically runs mathematical sanity checks (p-values and Chi-square tests).",
    howToRead: "Read the bold takeaway at the top of each card. Click 'Table' to see exact underlying row counts or 'Proof' to verify p-values.",
    actionItem: "Download the reproducible Jupyter Notebook (.ipynb) or move to the Cleaned Data Explorer."
  },
  {
    step: 5,
    title: "5. Cleaned Explorer & AI Copilot",
    route: "/cleaned",
    icon: Bot,
    summary: "Ask plain-English questions, view before/after row diffs, and export production code.",
    howItWorks: "The AI Copilot writes exact SQLite queries and streams its thinking process word-by-word via a real-time SSE gateway.",
    howToRead: "Type natural questions like 'Show top 10 most expensive products' or 'Average discount by category' to get instant mathematical charts and SQL.",
    actionItem: "Inspect the raw-vs-cleaned row diffs to confirm every cell change, then export the Cleaned CSV."
  },
  {
    step: 6,
    title: "6. Data Quality & Governance Audit",
    route: "/report",
    icon: ShieldCheck,
    summary: "Receive a formal mathematical quality certificate and statistical drift verification.",
    howItWorks: "Tests strict contract invariants (e.g. 'price > 0') and applies the Kolmogorov-Smirnov (KS-Test) to prove cleaning didn't warp underlying distributions.",
    howToRead: "Look for 'Distribution Drift: Passed (p > 0.05)'. This confirms that statistical trends in the cleaned table perfectly match the real world.",
    actionItem: "Click 'Download Export Pack (.zip)' to obtain the cleaned dataset, audit JSON, and execution logs."
  }
];

const COMPREHENSION_GUIDE = [
  {
    title: "Opportunity Score (0 - 100)",
    concept: "Measures whether a business niche is worth pursuing.",
    formula: "Opportunity = 30% Demand Volume + 25% Growth Velocity + 25% Pain-Point Ratio + 20% Competition Density",
    howToInterpret: "Scores ≥ 65 are Prime Opportunities (high demand, strong growth, clear customer complaints to fix). Scores 40-64 are Moderate. Scores < 40 are Saturated or Low-Demand."
  },
  {
    title: "Total Addressable Market (TAM)",
    concept: "The estimated total yearly dollar spending available in this specific niche.",
    formula: "TAM = Monthly Search Volume × 2% Organic Conversion Rate × Target Unit Price × 12 Months",
    howToInterpret: "Gives a grounded ceiling for yearly potential revenue. E.g. 50,000 monthly searches at $50/unit = $600,000/yr niche market."
  },
  {
    title: "Monte Carlo Simulation (1,000 Iterations)",
    concept: "Stochastically models real-world financial randomness across volume, conversion, and acquisition cost.",
    formula: "Simulates 1,000 randomized business months with Gaussian variance around customer volume, CAC, and price.",
    howToInterpret: "Look at 'Probability of Profit' (aim for >70%) and 'P50 Expected Monthly Profit' (the realistic median outcome). P10 shows worst-case risk, while P90 shows best-case viral upside."
  },
  {
    title: "Distribution Drift (KS-Test)",
    concept: "Guarantees that cleaning data didn't accidentally distort the true underlying facts.",
    formula: "Two-sample Kolmogorov-Smirnov test comparing raw vs cleaned numerical distributions.",
    howToInterpret: "A p-value > 0.05 means PASSED (the data shape is preserved). A p-value < 0.05 flags significant drift that warrants review."
  },
  {
    title: "Governance Matrix (Ask vs Act)",
    concept: "The safety rulebook that prevents AI from silently destroying important data.",
    formula: "Classifies actions into L1 (formatting), L2 (imputation), and L3 (destructive deletions).",
    howToInterpret: "'Act' means safe operations are applied automatically. 'Ask' means any permanent row removal affecting >5% of records requires your manual approval."
  },
  {
    title: "Teacher-Student Knowledge Distillation",
    concept: "How DataForge AI gets faster and cheaper the more you use it.",
    formula: "Large cloud LLM (Teacher) labels difficult edge cases → Local machine learning model (Student) trains on approved fixes.",
    howToInterpret: "Once 15 examples of a column type are recorded, the system distills a local random forest classifier that resolves identical future columns in 0.1ms at $0 cost (0 tokens)."
  }
];

const GLOSSARY = [
  ["Profile", "Automated statistical inspection of raw data: row count, null percentages, duplicate detection, and numeric bounds."],
  ["Semantic Type", "What a column actually means in real life (e.g. 'cogs_usd' is Currency, 'zip' is Postal Code, 'dt' is Timestamp)."],
  ["Data Dictionary", "Plain-language semantic classification, data type tagging, and business context suggested for every column."],
  ["Imputation", "Filling empty or missing values using mathematical column medians or category modes instead of dropping entire rows."],
  ["IQR Outliers", "Extreme statistical spikes (Interquartile Range) that fall far outside normal data boundaries."],
  ["Governance Gate", "Safety classification (L1/L2/L3). Destructive transformations affecting >5% of rows require explicit human approval."],
  ["Grounding Sandbox", "Every AI narrative statement and numerical claim is mathematically checked against true computed stats before display."],
  ["ReAct Loop", "Reason-Act-Observe cycle: The autonomous agent plans subtasks, calls data tools, reflects on missing data, and iterates."],
  ["RAG Cache", "Semantic embedding and exact-match cache of past LLM reasoning so identical questions cost 0 tokens."],
  ["Drift Detection (KS-Test)", "Two-sample Kolmogorov-Smirnov test guarding against unintended statistical distortion during data cleaning."],
  ["Contract Gate", "Final assertion checks before export to ensure cleaned tables fulfill production expectations."],
  ["0-Token Resolution", "Solving a data cleaning problem locally on your machine without making any API calls to OpenAI or Groq."],
  ["SSE Streaming", "Server-Sent Events: Real-time word-by-word streaming of AI thinking and SQL execution without browser timeouts."],
  ["Jupyter Notebook (.ipynb)", "A complete, self-contained Python script replicating all cleaning and visualization steps in Google Colab or VS Code."]
];

const AGENTS = [
  ["ReAct Orchestrator", "READ / WRITE (supervisory)", "Coordinates multi-step research plans, routes tools, and triggers follow-ups if data is incomplete."],
  ["Profiler Engine", "READ ONLY", "Computes deterministic distributions, row counts, null rates, and outlier boundaries using native Python."],
  ["Understanding Engine", "READ ONLY", "Infers semantic types and business context via teacher-student delegation."],
  ["Cleaning Executor", "TRANSFORM (supervised)", "Executes approved Python operations in an isolated sandbox."],
  ["Verification Sandbox", "AUDIT / READ ONLY", "Applies KS-test drift checks and invariant validations before approving exports."],
  ["Reporter Engine", "READ ONLY", "Synthesizes grounded executive summaries, SWOT matrices, and quality audit certificates."]
];

export default function ExplainPage() {
  const { id } = useDataset();
  const [tab, setTab] = useState("guide");
  const [tokenScope, setTokenScope] = useState("all");
  const [tokens, setTokens] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [learning, setLearning] = useState(null);

  useEffect(() => {
    let url = `http://localhost:8000/api/tokens?scope=${tokenScope}`;
    if (tokenScope === "dataset" && id) {
      url += `&run_id=${id}`;
    }
    fetch(url)
      .then((r) => r.json())
      .then(setTokens)
      .catch((e) => console.warn("Failed fetching tokens:", e));

    fetch("http://localhost:8000/api/incidents?unresolved=true")
      .then((r) => r.json())
      .then((d) => setIncidents(d.incidents || []))
      .catch(() => {});
    fetch("http://localhost:8000/api/learning")
      .then((r) => r.json())
      .then(setLearning)
      .catch(() => {});
  }, [id, tab, tokenScope]);

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-6 py-6 overflow-x-clip text-xs">
      <Breadcrumbs
        crumbs={[
          { href: "/", label: "Home" },
          { href: "/explain", label: "System & Autonomy" },
          { label: "How It Works & Master Guide" },
        ]}
      />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <HelpCircle size={22} className="text-indigo-600 dark:text-indigo-400" />
            How It Works & Complete System Manual
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            End-to-end user journey, metric comprehension guide, plain-language glossary, and autonomous architecture
          </p>
        </div>
        <Badge tone="good">Master Documentation Hub</Badge>
      </div>

      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 text-xs">
        {[
          { id: "guide", label: "🚀 End-to-End User Journey", icon: Compass },
          { id: "metrics", label: "📊 How to Read Metrics & Scores", icon: BarChart3 },
          { id: "glossary", label: "📖 Plain-English Glossary", icon: BookOpen },
          { id: "agents", label: "🛡️ Multi-Agent Permissions", icon: ShieldCheck },
          { id: "distillation", label: "⚡ 0-Token Distillation", icon: Activity },
          { id: "cost", label: "💰 Token Economics", icon: Coins },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2.5 font-semibold border-b-2 transition ${
              tab === t.id
                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 font-bold"
                : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
            }`}
          >
            <t.icon size={14} />
            {t.label}
          </button>
        ))}
      </div>

      {/* TAB 1: User Journey */}
      {tab === "guide" && (
        <div className="space-y-4">
          <Card
            title="Complete Lifecycle: From Raw Idea to Certified Clean Dataset"
            info="Step-by-step instructions showing what happens at each stage of the DataForge AI pipeline."
          >
            <div className="space-y-4 pt-1">
              {USER_JOURNEY_STEPS.map((s) => {
                const Icon = s.icon;
                return (
                  <div
                    key={s.step}
                    className="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2.5 shadow-sm"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-2.5">
                      <div className="flex items-center gap-2">
                        <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold text-xs shadow-sm">
                          <Icon size={14} />
                        </span>
                        <h3 className="font-bold text-sm text-slate-900 dark:text-slate-100">{s.title}</h3>
                      </div>
                      <Link href={s.route}>
                        <Button size="sm" variant="secondary" className="text-[11px] py-1 h-7">
                          Open Screen <ArrowRight size={11} />
                        </Button>
                      </Link>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 text-xs">
                      <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 space-y-1">
                        <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider block">
                          What it does:
                        </span>
                        <p className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                          {s.howItWorks}
                        </p>
                      </div>

                      <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 space-y-1">
                        <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider block">
                          How to comprehend:
                        </span>
                        <p className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                          {s.howToRead}
                        </p>
                      </div>

                      <div className="p-2.5 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 space-y-1">
                        <span className="text-[10px] font-bold text-indigo-900 dark:text-indigo-200 uppercase tracking-wider block">
                          Your action item:
                        </span>
                        <p className="text-slate-800 dark:text-slate-200 text-[11px] font-medium leading-relaxed">
                          {s.actionItem}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>
      )}

      {/* TAB 2: Metric Comprehension */}
      {tab === "metrics" && (
        <div className="space-y-4">
          <Card
            title="Metric Comprehension & Mathematical Formula Guide"
            info="Understand exactly how scores, simulations, and statistical tests are computed."
          >
            <div className="grid gap-3.5 sm:grid-cols-2 pt-1">
              {COMPREHENSION_GUIDE.map((m, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2.5 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">{m.title}</h4>
                    <Badge tone="ai">Verified Math</Badge>
                  </div>
                  <p className="text-[11px] text-slate-600 dark:text-slate-300">{m.concept}</p>

                  <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 font-mono text-[10px] text-indigo-700 dark:text-indigo-300 border border-slate-200/60 dark:border-slate-700">
                    <span className="text-slate-400 font-bold block mb-0.5">Formula / Method:</span>
                    {m.formula}
                  </div>

                  <div className="p-2.5 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 text-[11px] text-slate-700 dark:text-slate-300">
                    <span className="font-bold text-emerald-900 dark:text-emerald-200 block mb-0.5">
                      💡 How to Interpret:
                    </span>
                    {m.howToInterpret}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* TAB 3: Glossary */}
      {tab === "glossary" && (
        <Card
          title="DataForge AI Plain-English Glossary"
          info="Every key concept translated into clear, non-technical definitions."
        >
          <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
            {GLOSSARY.map(([term, def], i) => (
              <div key={i} className="py-3 first:pt-0 last:pb-0 space-y-0.5">
                <dt className="font-bold text-slate-900 dark:text-slate-100 text-xs flex items-center gap-1.5">
                  <CheckCircle2 size={12} className="text-indigo-600" />
                  {term}
                </dt>
                <dd className="text-slate-600 dark:text-slate-300 leading-relaxed text-[11px] pl-4">{def}</dd>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* TAB 4: Multi-Agent Matrix */}
      {tab === "agents" && (
        <Card
          title="Multi-Agent Permission Matrix & Principle of Least Privilege"
          info="No single agent can both propose and destructively execute without sandbox verification."
        >
          <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
            {AGENTS.map(([name, perm, desc], i) => (
              <div key={i} className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <p className="font-bold text-slate-900 dark:text-slate-100">{name}</p>
                  <p className="text-slate-600 dark:text-slate-400 text-[11px]">{desc}</p>
                </div>
                <Badge tone={perm.includes("supervisory") ? "ai" : perm.includes("ONLY") ? "good" : "warn"}>
                  {perm}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* TAB 5: Distillation & Autonomy */}
      {tab === "distillation" && (
        <div className="space-y-4">
          <Card
            title="0-Token Local Knowledge Distillation"
            info="High-conviction transformations accumulated and trained locally to reduce API costs to zero."
          >
            <div className="grid gap-3 sm:grid-cols-3 mb-4">
              <StatTile label="Distilled Models" value={learning?.validated || 0} tone="good" />
              <StatTile label="Learned Column Schemas" value={learning?.signatures || 0} />
              <StatTile label="Cached Cleaning Rules" value={learning?.learned_fixes || 0} />
            </div>

            <div className="p-3.5 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 space-y-2 text-[11px] text-slate-700 dark:text-slate-300">
              <span className="font-bold text-indigo-900 dark:text-indigo-200">
                ⚡ How the 0-Token Shrinkage Curve Works:
              </span>
              <p className="leading-relaxed">
                When you first upload a column like <code className="bg-white dark:bg-slate-900 px-1 py-0.5 rounded font-mono">cogs_usd</code>, the system queries the cloud LLM to infer its semantic type. Once 15 user-confirmed decisions are accumulated, DataForge trains a local Random Forest classifier. Future appearances of identical or similar columns run locally on your CPU in <b>0.1 milliseconds</b> at <b>0 tokens</b>.
              </p>
            </div>
          </Card>
        </div>
      )}

      {/* TAB 6: Token Economics */}
      {tab === "cost" && (
        <Card
          title="Token Economics & Autonomy Telemetry"
          info="Real-time breakdown of tokens consumed, local 0-token savings, and operational cloud API costs."
          actions={
            <div className="flex gap-1.5">
              {[
                { id: "all", label: "All Platform Activity" },
                { id: "research", label: "Market Research Only" },
                { id: "dataset", label: "Dataset Pipeline Only" },
              ].map((s) => (
                <button
                  key={s.id}
                  onClick={() => setTokenScope(s.id)}
                  className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition ${
                    tokenScope === s.id
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300"
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          }
        >
          <div className="space-y-5 pt-1 text-xs">
            {/* 4 Core Metric Tiles */}
            <div className="grid gap-3 sm:grid-cols-4">
              <StatTile
                label="Total Tokens Consumed"
                value={tokens?.total_tokens?.toLocaleString() || 0}
                tone="ai"
              />
              <StatTile
                label="0-Token Cache Savings"
                value={`${(tokens?.total_saved || 0).toLocaleString()} tkns`}
                tone="good"
              />
              <StatTile
                label="Local Cache Hit Rate"
                value={`${tokens?.cache_hit_rate_pct || 0}%`}
              />
              <StatTile
                label="Estimated API Cost"
                value={`$${(tokens?.estimated_cost_usd || 0).toFixed(4)}`}
                tone="good"
              />
            </div>

            {/* Explanatory Scope Banner */}
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between gap-3 text-[11px]">
              <div>
                <span className="font-bold text-slate-900 dark:text-slate-100">
                  Current Filter: {tokenScope === "research" ? "🧭 Market & Niche Research Only" : tokenScope === "dataset" ? "🧹 Dataset Cleaning & Governance Only" : "🌐 Total Platform Telemetry"}
                </span>
                <p className="text-slate-500 mt-0.5">
                  {tokenScope === "research"
                    ? "Isolates token consumption strictly for niche scouting, competitor scraping, persona generation, and blueprints."
                    : tokenScope === "dataset"
                    ? "Isolates token consumption for data profiling, transformation planning, and supervisor approvals."
                    : "Aggregates end-to-end token consumption across both research and dataset governance."}
                </p>
              </div>
              <Badge tone="good">{tokens?.by_stage?.length || 0} Stages Logged</Badge>
            </div>

            {/* Detailed Stage Table */}
            {tokens?.by_stage && tokens.by_stage.length > 0 ? (
              <div className="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                <table className="w-full text-left text-[11px]">
                  <thead className="bg-slate-100 dark:bg-slate-800/80 font-bold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700">
                    <tr>
                      <th className="py-2.5 px-3">Pipeline Stage / Subsystem</th>
                      <th className="py-2.5 px-3">Prompt (In)</th>
                      <th className="py-2.5 px-3">Completion (Out)</th>
                      <th className="py-2.5 px-3">Total Tokens</th>
                      <th className="py-2.5 px-3">0-Token Saved</th>
                      <th className="py-2.5 px-3 text-right">Executions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono">
                    {tokens.by_stage.map((s, idx) => (
                      <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                        <td className="py-2.5 px-3 font-bold text-slate-800 dark:text-slate-200 font-sans">
                          {s.stage === "RESEARCH" ? "🧭 Market Scouting & Blueprints" : s.stage === "UNDERSTAND" ? "🔍 Semantic Profiling (CP1)" : s.stage === "PLAN" ? "🛠️ Transformation Planning (CP2)" : s.stage === "GOVERN" ? "🛡️ Governance Review (CP3)" : s.stage === "ANALYST" ? "🤖 Natural Language Copilot" : s.stage}
                        </td>
                        <td className="py-2.5 px-3 text-slate-600 dark:text-slate-400">{(s.prompt_tokens || 0).toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-slate-600 dark:text-slate-400">{(s.completion_tokens || 0).toLocaleString()}</td>
                        <td className="py-2.5 px-3 font-bold text-indigo-600 dark:text-indigo-400">{s.total.toLocaleString()}</td>
                        <td className="py-2.5 px-3 font-bold text-emerald-600 dark:text-emerald-400">{s.tokens_saved.toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-right text-slate-500 font-sans">{s.calls}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-500 text-center py-4 italic">
                No token records found for this scope. Run niche research or cleaning to see live telemetry.
              </p>
            )}
          </div>
        </Card>
      )}
    </main>
  );
}
