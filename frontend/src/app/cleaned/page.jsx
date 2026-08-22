"use client";
import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useDataset } from "../components/DatasetContext";
import DataInspector from "../DataInspector";
import { Card, Button, Badge, Tip } from "../components/ui";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { WorkflowStepGuide } from "../components/WorkflowStepGuide";
import {
  FileText,
  BarChart3,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Search,
  Loader2,
  Terminal,
  Database,
  Table as TableIcon,
  FileCode2
} from "lucide-react";

function AnalystQueryBox({ datasetId }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [showThinking, setShowThinking] = useState(true);
  const [thoughts, setThoughts] = useState([]);
  const [accumulatedTokens, setAccumulatedTokens] = useState(0);
  const [tokenUsage, setTokenUsage] = useState(null);
  const [streamingAnswer, setStreamingAnswer] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const SUGGESTIONS = [
    "Show top 10 most expensive items",
    "Average discount and count by category",
    "List items with discount greater than 40%",
    "Total catalog value and savings by category"
  ];

  const handleAsk = async (qText = question) => {
    const q = (qText || "").trim();
    if (!q || !datasetId) return;
    setLoading(true);
    setError(null);
    setStreamingAnswer("");
    setThoughts([]);
    setAccumulatedTokens(0);
    setTokenUsage(null);
    setShowThinking(true);
    setResult({ sql: "", narrative: "", columns: [], data: [], title: "Live Streaming Analysis", total_rows: 0 });

    try {
      const res = await fetch("http://localhost:8000/api/stream/analyst", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, dataset_id: datasetId }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Streaming query failed");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedAnswer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "thought") {
                setThoughts((prev) => [
                  ...prev,
                  {
                    step: data.step,
                    title: data.title,
                    content: data.content,
                    sql: data.sql,
                    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
                  }
                ]);
              } else if (data.type === "sql") {
                setResult((prev) => ({
                  ...prev,
                  sql: data.content,
                  columns: data.columns || prev.columns,
                  data: data.data || prev.data,
                  total_rows: data.total_rows || prev.total_rows,
                  runtime_ms: data.runtime_ms
                }));
              } else if (data.type === "answer") {
                accumulatedAnswer += data.content;
                setStreamingAnswer(accumulatedAnswer);
                if (data.accumulated_tokens) {
                  setAccumulatedTokens(data.accumulated_tokens);
                }
                setResult((prev) => ({ ...prev, narrative: accumulatedAnswer }));
              } else if (data.type === "token_usage") {
                setTokenUsage(data);
                setAccumulatedTokens(data.total_tokens);
              } else if (data.type === "error") {
                setError(data.content);
              } else if (data.type === "done") {
                if (data.total_tokens) setAccumulatedTokens(data.total_tokens);
                setResult((prev) => ({ ...prev, narrative: data.content }));
              }
            } catch (e) {
              // ignore partial chunks
            }
          }
        }
      }
    } catch (e) {
      console.error(e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title="Ask AI Data Analyst (Natural Language to SQL & Insights)"
      info="Query your cleaned dataset using plain English. The AI translates your request into safe SQL, executes it, and delivers insights."
      actions={
        <div className="flex items-center gap-2">
          {accumulatedTokens > 0 && (
            <Badge tone="ai" className="flex items-center gap-1 font-mono">
              <Sparkles size={11} />
              <span>{accumulatedTokens} tokens</span>
            </Badge>
          )}
          <Badge tone="good">Interactive Analyst</Badge>
        </div>
      }
    >
      <div className="space-y-3.5">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="flex gap-2"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={15} />
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything (e.g. 'Show top 10 most expensive products' or 'Average savings by category')..."
              className="w-full rounded-xl border border-slate-200 bg-white pl-9 pr-4 py-2 text-xs text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            />
          </div>
          <Button type="submit" size="sm" variant="primary" disabled={loading || !question.trim()}>
            {loading ? <Loader2 className="animate-spin" size={13} /> : <Sparkles size={13} />}
            {loading ? "Analyzing…" : "Ask Analyst"}
          </Button>
        </form>

        {/* Quick prompt suggestions */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <span className="text-[11px] font-semibold text-slate-400">Try asking:</span>
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setQuestion(s);
                handleAsk(s);
              }}
              className="rounded-lg border border-slate-200 bg-slate-100/70 px-2 py-0.5 text-[11px] font-medium text-slate-600 hover:border-indigo-300 hover:bg-indigo-50/50 hover:text-indigo-600 dark:border-slate-800 dark:bg-slate-800/60 dark:text-slate-300 dark:hover:border-indigo-700 dark:hover:bg-indigo-950/40 dark:hover:text-indigo-300 transition"
            >
              {s}
            </button>
          ))}
        </div>

        {error && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 dark:border-rose-900 dark:bg-rose-950/30 dark:text-rose-300">
            ⚠️ {error}
          </div>
        )}

        {/* 🧠 Live Thinking & Background Activity Dropdown Drawer */}
        {(loading || thoughts.length > 0) && (
          <div className="rounded-xl border border-indigo-100 bg-indigo-50/50 dark:border-indigo-950 dark:bg-indigo-950/20 overflow-hidden text-xs">
            <button
              type="button"
              onClick={() => setShowThinking(!showThinking)}
              className="flex w-full items-center justify-between px-3.5 py-2 text-left font-semibold text-indigo-900 dark:text-indigo-200 hover:bg-indigo-100/50 dark:hover:bg-indigo-900/30 transition"
            >
              <div className="flex items-center gap-2">
                <span className="flex h-4 w-4 items-center justify-center rounded-full bg-indigo-600 text-white text-[10px]">
                  {loading ? <Loader2 size={10} className="animate-spin" /> : "🧠"}
                </span>
                <span>
                  {loading ? "AI Reasoning & Thinking in Progress..." : "View AI Reasoning & Background Steps"}
                </span>
                {accumulatedTokens > 0 && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-bold">
                    ⚡ {accumulatedTokens} tokens accumulating
                  </span>
                )}
              </div>
              <span className="text-[11px] text-indigo-600 dark:text-indigo-400 font-medium">
                {showThinking ? "Hide Steps ▲" : "Show Steps ▼"}
              </span>
            </button>

            {showThinking && (
              <div className="p-3 border-t border-indigo-100/80 dark:border-indigo-900/40 space-y-2 font-mono text-[11px]">
                {thoughts.map((t, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-slate-700 dark:text-slate-300">
                    <span className="text-indigo-600 dark:text-indigo-400 font-bold">•</span>
                    <span className="text-slate-400 text-[10px] shrink-0">[{t.time}]</span>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">{t.title}:</span>
                    <span className="text-slate-600 dark:text-slate-300">{t.content}</span>
                  </div>
                ))}
                {loading && (
                  <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-semibold animate-pulse pt-1">
                    <Loader2 size={12} className="animate-spin" />
                    <span>Streaming live tokens and reasoning chunks...</span>
                  </div>
                )}
                {tokenUsage && (
                  <div className="pt-2 border-t border-indigo-200/50 dark:border-indigo-900/50 flex flex-wrap items-center gap-3 text-[10px] text-slate-500 font-sans">
                    <span><b>Prompt Tokens:</b> {tokenUsage.prompt_tokens}</span>
                    <span><b>Completion Tokens:</b> {tokenUsage.completion_tokens}</span>
                    <span className="text-indigo-600 dark:text-indigo-400 font-bold"><b>Total Recorded:</b> {tokenUsage.total_tokens}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Live Narrative & Query Results */}
        {result && (result.narrative || result.sql) && (
          <div className="mt-3.5 space-y-3 rounded-xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-900/60">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-2.5 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <span className="font-bold text-xs text-slate-900 dark:text-slate-100">{result.title}</span>
                {result.total_rows > 0 && <Badge tone="slate">{result.total_rows} rows</Badge>}
                {result.runtime_ms && <span className="text-[10px] text-slate-400 font-mono">({result.runtime_ms}ms)</span>}
              </div>
              {result.sql && (
                <div className="flex items-center gap-1 font-mono text-[11px] text-slate-500 bg-white dark:bg-slate-800 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                  <Terminal size={12} className="text-indigo-500" />
                  <span>{result.sql}</span>
                </div>
              )}
            </div>

            {/* Streamed Narrative Answer */}
            {result.narrative && (
              <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40">
                <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                  💡 {result.narrative}
                  {loading && <span className="inline-block ml-1 animate-pulse text-indigo-600 font-bold">▋</span>}
                </p>
              </div>
            )}

            {/* Results Table */}
            {result.data && result.data.length > 0 && (
              <div className="overflow-x-auto max-h-64 rounded-lg border border-slate-200 dark:border-slate-800">
                <table className="w-full text-left text-[11px]">
                  <thead className="sticky top-0 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold border-b border-slate-200 dark:border-slate-700">
                    <tr>
                      {result.columns.map((col, idx) => (
                        <th key={idx} className="p-2 whitespace-nowrap">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 bg-white dark:bg-slate-900">
                    {result.data.slice(0, 50).map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                        {result.columns.map((col, cIdx) => (
                          <td key={cIdx} className="p-2 text-slate-600 dark:text-slate-300 whitespace-nowrap">
                            {row[col] !== null && row[col] !== undefined ? String(row[col]) : "null"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

function CleanedContent() {
  const { id } = useDataset();
  const searchParams = useSearchParams();
  const [stage, setStage] = useState("cleaned");
  const [exec, setExec] = useState(null);

  useEffect(() => {
    const q = searchParams.get("stage");
    if (q) setStage(q);
  }, [searchParams]);

  useEffect(() => {
    if (!id) return;
    fetch(`http://localhost:8000/api/execution/${id}`)
      .then((r) => r.json())
      .then((data) => setExec(data && data.report ? data : null))
      .catch((err) => console.warn("No execution history found:", err));
  }, [id]);

  if (!id) {
    return (
      <main className="p-8 text-center">
        <Card title="No Dataset Selected">
          <p className="text-xs text-slate-500 mb-4">Please upload or select a dataset on the Overview page to explore cleaned rows.</p>
          <Link href="/"><Button size="sm">Go to Overview</Button></Link>
        </Card>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-6xl space-y-5 px-6 py-6 overflow-x-clip">
      <Breadcrumbs
        crumbs={[
          { href: "/", label: "Home" },
          { href: "/cleaned", label: "Data Pipeline" },
          { label: "Cleaned Data Explorer" },
        ]}
      />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">Cleaned Data Explorer</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Inspect post-transformation cleaned rows and view before/after diffs across stages
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            size="sm" 
            variant="secondary" 
            onClick={() => window.open(`http://localhost:8000/api/export/notebook/${id}`, '_blank')}
          >
            <FileCode2 size={13} /> Pipeline (.ipynb)
          </Button>
          <Link href="/report">
            <Button size="sm" variant="primary">
              <FileText size={13} /> Quality Report
            </Button>
          </Link>
          <Link href="/eda">
            <Button size="sm" variant="secondary">
              <BarChart3 size={13} /> EDA Report
            </Button>
          </Link>
        </div>
      </div>

      {/* Non-Sophisticated Workflow Guide */}
      <WorkflowStepGuide
        currentStepId="analyst"
        pageTitle="Cleaned Data Explorer & AI Copilot"
        reason="Here you can verify your final cleaned data, ask plain-English questions to the AI Copilot, view before/after diffs, and download production artifacts (Cleaned CSV or a 100% reproducible Jupyter Notebook)."
        priorStepText="Your dataset should be cleaned in the Cleaning Studio so you are inspecting final validated rows."
        priorStepHref="/cleaning"
        currentActionSteps={[
          { title: "Ask Plain-English Questions", detail: "Type questions like 'Show top 10 products' or 'Average discount by category' into the AI Copilot." },
          { title: "Inspect Table & Diff Dictionaries", detail: "Examine the Cleaned vs Raw tabs to verify exactly how missing numbers or anomalies were fixed." },
          { title: "Download Jupyter Notebook", detail: "Click 'Pipeline (.ipynb)' to export a production-ready Python script reproducing all cleaning steps." }
        ]}
        nextStepText="Explore statistical charts in Visual EDA, or generate a full executive audit report in Quality Report."
        nextStepHref="/eda"
        jargonBuster={[
          { term: "Streaming SSE Gateway", meaning: "Real-time AI response: the assistant streams its thinking steps and SQL queries word-by-word without browser timeouts." },
          { term: "Jupyter Notebook (.ipynb)", meaning: "A runnable Python notebook file that data scientists can execute in VS Code or Google Colab." },
          { term: "Audit Diff", meaning: "A row-by-row comparison showing what the values were before cleaning vs after cleaning." },
          { term: "Deterministic SQL", meaning: "The AI writes exact SQL database queries on SQLite so the calculations are 100% mathematically correct." }
        ]}
      />

      {/* Interactive AI Data Analyst Box */}
      <AnalystQueryBox datasetId={id} />

      {/* What changed & why Card */}
      {exec?.report && (
        <Card
          title="What Changed & Why"
          info="Every executed transformation, its before/after row impact, and specific data engineering rationale."
          actions={
            <Badge tone="good">
              Quality: {typeof exec.before_quality === "object" ? exec.before_quality?.overall : exec.before_quality}% → {typeof exec.after_quality === "object" ? exec.after_quality?.overall : exec.after_quality}%
              {exec.quality_delta !== undefined && ` (+${exec.quality_delta}%)`}
            </Badge>
          }
        >
          {exec.after_quality_breakdown && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3 text-[11px]">
              <div className="p-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block">Completeness</span>
                <span className="font-semibold">{exec.before_quality_breakdown?.completeness}% → {exec.after_quality_breakdown?.completeness}%</span>
              </div>
              <div className="p-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block">Uniqueness</span>
                <span className="font-semibold">{exec.before_quality_breakdown?.uniqueness}% → {exec.after_quality_breakdown?.uniqueness}%</span>
              </div>
              <div className="p-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block">Validity</span>
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">{exec.before_quality_breakdown?.validity}% → {exec.after_quality_breakdown?.validity}%</span>
              </div>
              <div className="p-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block">Consistency</span>
                <span className="font-semibold text-indigo-600 dark:text-indigo-400">{exec.before_quality_breakdown?.consistency}% → {exec.after_quality_breakdown?.consistency}%</span>
              </div>
            </div>
          )}

          <div className="space-y-3">
            {exec.report.filter((r) => r.applied).map((r) => (
              <div
                key={r.step_id}
                className="rounded-xl border border-slate-200 dark:border-slate-800 p-3.5 bg-slate-50/50 dark:bg-slate-800/40"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 text-xs font-bold">
                      ✓
                    </span>
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-100">
                      Step #{r.step_id}: {r.action} {r.column && `(${r.column})`}
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                      ({r.rows_before} → {r.rows_after} rows)
                    </span>
                  </div>
                  <button
                    onClick={() => setStage(`step_${r.step_id}`)}
                    className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 hover:underline"
                  >
                    Jump to stage snapshot
                  </button>
                </div>

                <div className="mt-2 space-y-1">
                  {(r.changes || []).map((c, i) => (
                    <p key={i} className="text-xs text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
                      <span className="text-slate-400">•</span>
                      <b className="font-mono text-indigo-600 dark:text-indigo-400">{c.column}</b>:
                      <span className="capitalize">{c.kind.replace("_", " ")}</span>
                      {c.count !== undefined && <span className="font-mono">({c.count})</span>}
                      <span className="text-slate-500">— {c.reason}</span>
                    </p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <DataInspector datasetId={id} defaultStage={stage} />
    </main>
  );
}

export default function CleanedDataPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-500">Loading Cleaned Data…</div>}>
      <CleanedContent />
    </Suspense>
  );
}
