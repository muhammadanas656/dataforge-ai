"use client";
import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useDataset } from "../components/DatasetContext";
import {
  ArrowLeft,
  Loader2,
  Sparkles,
  RefreshCw,
  BarChart2,
  Table as TableIcon,
  Download,
  AlertTriangle,
  Wrench,
  Activity,
} from "lucide-react";
import { Card, Badge, Button, Tip } from "../components/ui";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { FeatureGuide } from "../components/FeatureGuide";
import { WorkflowStepGuide } from "../components/WorkflowStepGuide";
import { InsightCard } from "../components/InsightCard";
import { MplChart, DataTable } from "../ChartRenderer";
import VerificationAuditBadge from "../components/VerificationAuditBadge";

function PlainEnglishDefinitionBox({ plainEnglish, result }) {
  if (!plainEnglish && !result) return null;
  const pe = plainEnglish || {};
  const what = pe.what_is_this || result.beginner_summary;
  const meaning = pe.plain_meaning || result.insight;
  const takeaway = pe.practical_takeaway;

  return (
    <div className="mt-3.5 rounded-xl border border-emerald-200/80 bg-emerald-50/60 p-3.5 dark:border-emerald-900/50 dark:bg-emerald-950/20 text-xs">
      <div className="flex items-center gap-1.5 font-bold text-emerald-900 dark:text-emerald-200 mb-2">
        <Sparkles size={14} className="text-emerald-600 dark:text-emerald-400" />
        <span className="text-[12px]">Plain-English Definition & What This Means (Non-Technical Guide)</span>
      </div>

      <div className="space-y-2 text-[11px] leading-relaxed text-slate-700 dark:text-slate-300">
        {what && (
          <div className="flex items-start gap-1.5">
            <span className="font-bold text-emerald-800 dark:text-emerald-300 shrink-0">📖 What is this:</span>
            <span>{what}</span>
          </div>
        )}
        {meaning && (
          <div className="flex items-start gap-1.5">
            <span className="font-bold text-emerald-800 dark:text-emerald-300 shrink-0">💡 In Simple Terms:</span>
            <span>{meaning}</span>
          </div>
        )}
        {takeaway && (
          <div className="flex items-start gap-1.5">
            <span className="font-bold text-emerald-800 dark:text-emerald-300 shrink-0">🎯 Practical Takeaway:</span>
            <span>{takeaway}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function StatisticalBriefBox({ brief, stats }) {
  if (!brief && !stats) return null;
  return (
    <div className="mt-3.5 rounded-xl border border-indigo-100 bg-indigo-50/50 p-3 dark:border-indigo-900/40 dark:bg-indigo-950/20 text-xs">
      <div className="flex items-center gap-1.5 font-bold text-indigo-900 dark:text-indigo-200 mb-1.5">
        <Activity size={13} className="text-indigo-600 dark:text-indigo-400" />
        <span>Executive Statistical Brief</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-[11px] text-slate-700 dark:text-slate-300">
        {brief &&
          Object.entries(brief).map(([k, v]) => (
            <div key={k} className="rounded-lg bg-white/70 p-2 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800">
              <span className="font-semibold text-slate-500 dark:text-slate-400 capitalize block">
                {k.replace(/_/g, " ")}:
              </span>
              <span className="font-medium text-slate-800 dark:text-slate-200">{v}</span>
            </div>
          ))}
      </div>
    </div>
  );
}

function ChartExplanation({ result }) {
  const e = result.chart_explanation;
  if (!e) return null;

  return (
    <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800/60">
      <div className="mb-2.5 flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300">
          Chart Type: {e.plain_name}
        </span>
      </div>

      <div className="grid gap-3.5 text-xs md:grid-cols-2">
        <div>
          <p className="font-bold text-slate-800 dark:text-slate-100">What is this?</p>
          <p className="mt-1 text-slate-600 dark:text-slate-300 leading-relaxed">{e.simple_definition}</p>
        </div>

        <div>
          <p className="font-bold text-slate-800 dark:text-slate-100">Why was it used?</p>
          <p className="mt-1 text-slate-600 dark:text-slate-300 leading-relaxed">{result.why_selected || e.why_used}</p>
        </div>

        <div>
          <p className="font-bold text-slate-800 dark:text-slate-100">How do I read it?</p>
          <p className="mt-1 text-slate-600 dark:text-slate-300 leading-relaxed">{e.how_to_read}</p>
        </div>

        <div>
          <p className="font-bold text-slate-800 dark:text-slate-100">What does it help with?</p>
          <ul className="mt-1 list-inside list-disc text-slate-600 dark:text-slate-300 space-y-0.5">
            {(e.helps_with || []).map((x, i) => (
              <li key={i}>{x}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function EDAReportContent() {
  const { id } = useDataset();
  const [status, setStatus] = useState(null);
  const [results, setResults] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [view, setView] = useState({});
  const [learningMode, setLearningMode] = useState(true);
  const [exporting, setExporting] = useState(false);

  // Causal Inference & Hypotheses State
  const [causalData, setCausalData] = useState(null);
  const [hypotheses, setHypotheses] = useState([]);

  useEffect(() => {
    // Reset state whenever active dataset ID switches
    setStatus(null);
    setResults([]);
    setSummary(null);
    setErrorMsg(null);
    setCausalData(null);
    setHypotheses([]);

    if (!id) return;

    const controller = new AbortController();
    const { signal } = controller;

    const fetchStatusAndData = async () => {
      try {
        const stRes = await fetch(`http://localhost:8000/api/status/${id}`, { signal });
        if (!stRes.ok) return;
        const st = await stRes.json();
        setStatus(st);

        const sumRes = await fetch(`http://localhost:8000/api/summary/${id}`, { signal });
        if (sumRes.ok) {
          setSummary(await sumRes.json());
        }

        if (st.cleaned) {
          setLoading(true);
          const edaRes = await fetch(`http://localhost:8000/api/eda/report/${id}`, { signal });
          if (edaRes.status === 400) {
            const err = await edaRes.json();
            setErrorMsg(err.detail || "Dataset must be cleaned before running EDA.");
            setStatus((prev) => ({ ...prev, cleaned: false }));
          } else if (edaRes.ok) {
            const data = await edaRes.json();
            setResults(data.results || []);
          }

          // Fetch Causal DAG & Statistical Hypotheses
          fetch(`http://localhost:8000/api/eda/causal/${id}`, { signal })
            .then((r) => (r.ok ? r.json() : null))
            .then((d) => setCausalData(d))
            .catch(() => {});

          fetch(`http://localhost:8000/api/eda/hypotheses/${id}`, { signal })
            .then((r) => (r.ok ? r.json() : null))
            .then((d) => setHypotheses(d?.hypotheses || []))
            .catch(() => {});

          setLoading(false);
        }
      } catch (err) {
        if (err.name !== "AbortError") {
          console.warn("EDA fetch error:", err);
          setLoading(false);
        }
      }
    };

    fetchStatusAndData();

    return () => {
      controller.abort();
    };
  }, [id]);

  const generate = async () => {
    if (!id) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const r = await fetch(`http://localhost:8000/api/eda/full/${id}?force=true`, { method: "POST" });
      if (r.status === 400) {
        const err = await r.json();
        setErrorMsg(err.detail || "Dataset must be cleaned before running EDA.");
        setStatus((prev) => ({ ...prev, cleaned: false }));
        return;
      }
      if (!r.ok) throw new Error("Failed to generate EDA");
      const d = await r.json();
      setResults(d.results || []);
    } catch (e) {
      console.error("Failed to generate EDA report:", e);
      setErrorMsg(e.message);
    } finally {
      setLoading(false);
    }
  };

  const exportEDA = () => {
    if (!id) return;
    window.open(`http://localhost:8000/api/eda/download/${id}`, "_blank");
  };

  if (!id) {
    return (
      <main className="p-8 text-center">
        <Card title="No Dataset Selected">
          <p className="text-xs text-slate-500 mb-4">Please upload or select a dataset on the Overview page to generate EDA reports.</p>
          <Link href="/"><Button size="sm">Go to Overview</Button></Link>
        </Card>
      </main>
    );
  }

  const insights = results.filter((r) => r.insight).slice(0, 5);

  return (
    <div key={id} className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors duration-200 overflow-x-clip">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/90">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft size={14} /> Back
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <Sparkles size={16} className="text-violet-600 dark:text-violet-400" />
              <h1 className="text-sm font-bold tracking-tight">AI-Suggested EDA Report</h1>
            </div>
          </div>

          {status?.cleaned && (
            <div className="flex items-center gap-3">
              <label className="hidden sm:flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-slate-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={learningMode}
                  onChange={(e) => setLearningMode(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                Explain charts
                <Tip text="Toggle educational guidance explaining why each chart representation was selected and how to read it." />
              </label>

              <Button size="sm" variant="secondary" onClick={exportEDA} disabled={exporting || loading}>
                {exporting ? <Loader2 className="animate-spin" size={13} /> : <Download size={13} />}
                {exporting ? "Exporting…" : "Export HTML/PDF"}
              </Button>

              <Button size="sm" variant="primary" onClick={generate} disabled={loading}>
                {loading ? <Loader2 className="animate-spin" size={13} /> : <RefreshCw size={13} />}
                {loading ? "Analyzing…" : "Regenerate"}
              </Button>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-5 px-4 py-6 sm:px-6">
        <Breadcrumbs
          crumbs={[
            { href: "/", label: "Home" },
            { href: "/eda", label: "Analysis" },
            { label: "EDA Studio" },
          ]}
        />

        {/* Non-Sophisticated Workflow Guide */}
        <WorkflowStepGuide
          currentStepId="eda"
          pageTitle="Visual Exploratory Data Analysis (EDA)"
          reason="This is where raw numbers become clear visual stories. The AI automatically plots histograms, category market shares, and price correlations so you can understand patterns, customer segments, and revenue drivers at a glance."
          priorStepText="Your active dataset MUST be cleaned first in the Cleaning Studio so that charts don't show corrupted or duplicate numbers."
          priorStepHref="/cleaning"
          currentActionSteps={[
            { title: "Inspect Insight Cards", detail: "Read the bold business takeaways and examine the chart distributions for each column." },
            { title: "Toggle Chart vs Table", detail: "Click 'Table' on any card to view the underlying summary numbers or 'Proof' to see mathematical validation." },
            { title: "Export Notebook / Report", detail: "Download a reproducible Jupyter notebook or HTML summary of the entire visual analysis." }
          ]}
          nextStepText="Ready to ask custom questions? Move to the AI Copilot to ask plain-English questions about your cleaned numbers."
          nextStepHref="/analyst"
          jargonBuster={[
            { term: "Histogram", meaning: "A bar chart showing how frequently different values occur (e.g. how many products cost between $20 and $40)." },
            { term: "Correlation Matrix", meaning: "A heatmap table showing which variables move together (e.g. does higher discount lead to higher unit sales?)." },
            { term: "HHI (Herfindahl Index)", meaning: "A score from 0 to 1 measuring how concentrated sales are in just a few top products versus evenly spread." },
            { term: "P-Value & Chi-Square", meaning: "A statistical sanity check confirming that a detected trend is real, not just random luck." }
          ]}
        />
        {/* Cleaning Gate Card */}
        {status && !status.cleaned && (
          <Card pad={false} className="border-amber-200 dark:border-amber-900/60 bg-amber-50/40 dark:bg-amber-950/20">
            <div className="p-6 text-center space-y-3">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400 shadow-sm">
                <AlertTriangle size={24} />
              </div>
              <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Cleaning Required Before EDA Analysis
              </h2>
              <p className="max-w-lg mx-auto text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                DataForge AI strictly enforces that exploratory data analysis (statistical distributions, category concentrations, and correlation matrices) operates on <b>clean, validated data</b> rather than raw noisy snapshots.
              </p>
              <div className="pt-2">
                <Link href="/cleaning">
                  <Button variant="primary" size="md">
                    <Wrench size={14} /> Open Cleaning Studio to Clean Data
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        )}

        {errorMsg && status?.cleaned && (
          <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-300 rounded-xl text-xs font-semibold">
            ⚠️ {errorMsg}
          </div>
        )}

        {summary?.overview && status?.cleaned && (
          <Card pad={false}>
            <div className="p-4 space-y-2">
              <div className="flex items-center gap-2">
                <Badge tone="ai">Domain: {summary.domain}</Badge>
                <Badge tone="good">Validated Clean Data</Badge>
              </div>
              <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                {summary.overview}
              </p>
              {summary.reason && (
                <div className="rounded-xl bg-indigo-50/70 p-3 text-xs text-indigo-900 dark:bg-indigo-950/30 dark:text-indigo-200 border border-indigo-100 dark:border-indigo-900/40">
                  <span className="font-bold">Why it matters: </span>
                  <span>{summary.reason}</span>
                </div>
              )}
            </div>
          </Card>
        )}

        {loading && status?.cleaned && (
          <Card>
            <div className="flex items-center gap-2.5 text-xs text-slate-500 dark:text-slate-400 font-medium py-2">
              <Loader2 className="animate-spin text-indigo-600" size={16} />
              The AI is computing statistical companions, educational explanations, and multi-representation analyses on your clean data…
            </div>
          </Card>
        )}

        {/* 🧬 Causal Drivers & Automated Hypotheses Proofs */}
        {causalData && status?.cleaned && (
          <Card
            title="Causal Directed Acyclic Graph (DAG) & Statistical Proofs"
            info="Discovers true directional cause-and-effect relationships and validates propositions using formal hypothesis testing."
            actions={<Badge tone="good">Causal Graph Verified</Badge>}
          >
            <div className="space-y-4 text-xs">
              {/* Primary Causal Insight Box */}
              <div className="p-3.5 rounded-xl bg-violet-50/70 dark:bg-violet-950/30 border border-violet-100 dark:border-violet-900/40">
                <span className="font-bold text-violet-900 dark:text-violet-200 block text-xs">
                  🎯 Directional Causal Driver:
                </span>
                <p className="text-slate-700 dark:text-slate-300 text-xs mt-1 leading-relaxed">
                  {causalData.primary_insight}
                </p>
              </div>

              {/* Causal Edges List */}
              {causalData.edges && causalData.edges.length > 0 && (
                <div className="space-y-1.5">
                  <span className="font-bold text-slate-700 dark:text-slate-300 text-[11px] block">
                    Discovered Directional Pathways:
                  </span>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {causalData.edges.map((e, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between gap-2"
                      >
                        <div className="space-y-0.5">
                          <span className="font-bold text-indigo-600 dark:text-indigo-400">
                            {e.source} → {e.target}
                          </span>
                          <p className="text-[10px] text-slate-500">{e.interpretation}</p>
                        </div>
                        <span className="text-[10px] font-mono font-bold text-emerald-600 dark:text-emerald-400 shrink-0">
                          {e.confidence_pct}% conf
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Automated Statistical Hypotheses */}
              {hypotheses && hypotheses.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                  <span className="font-bold text-slate-800 dark:text-slate-200 text-xs block">
                    🧪 Automated Statistical Hypothesis Tests:
                  </span>
                  <div className="space-y-2">
                    {hypotheses.map((h, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 space-y-1"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="font-bold text-slate-800 dark:text-slate-200">{h.hypothesis}</span>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold font-mono ${
                            h.verdict.includes("SUPPORTED")
                              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300"
                              : "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300"
                          }`}>
                            {h.verdict}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600 dark:text-slate-300">
                          <b>Actionable Takeaway:</b> {h.actionable_takeaway}
                        </p>
                        <span className="text-[10px] font-mono text-slate-400 block">
                          Test: {h.test_type} | p-value: {h.p_value} | statistic: {h.test_statistic}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {insights.length > 0 && !loading && status?.cleaned && (
          <Card
            title="Executive Summary & Key Takeaways"
            info="The most prominent data patterns, correlations, and anomalies detected across your features."
            actions={<Badge tone="ai">AI Synthesized</Badge>}
          >
            <ul className="space-y-2.5 text-xs">
              {insights.map((r, i) => (
                <li key={i} className="flex items-start gap-2.5 text-slate-700 dark:text-slate-300">
                  <Sparkles size={14} className="mt-0.5 shrink-0 text-violet-600 dark:text-violet-400" />
                  <span className="leading-relaxed">
                    <b className="text-slate-900 dark:text-slate-100">{r.title}:</b> {r.insight}
                  </span>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {!loading &&
          status?.cleaned &&
          results.map((r, i) => (
            <InsightCard
              key={i}
              chart={r}
              viewMode={view[i] || "chart"}
              onToggleView={(v) => setView((p) => ({ ...p, [i]: v }))}
            />
          ))}
      </main>
    </div>
  );
}

export default function EDAReport() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-500">Loading EDA Report…</div>}>
      <EDAReportContent />
    </Suspense>
  );
}
