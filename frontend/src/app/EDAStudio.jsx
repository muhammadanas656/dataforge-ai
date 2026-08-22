"use client";
import { useEffect, useState } from "react";
import { Play, Sparkles, EyeOff, Table as TableIcon, AlignLeft, BarChart2, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { MplChart, DataTable } from "./ChartRenderer";
import { Card, Badge, Tip, Button } from "./components/ui";

const TYPE_OUTPUT = {
  numeric_distribution: "Histogram + spread, skew & normality stats",
  category_breakdown: "Bar chart of group sizes + concentration",
  correlation: "Correlation matrix table of numeric fields",
  numeric_relationship: "Scatter plot + Spearman ρ & p-value",
  numeric_by_category: "Grouped means/medians + ANOVA p-value",
  top_n: "Ranked top-20 bar + share of total",
  plugin: "Custom plugin output",
};

export default function EDAStudio({ datasetId }) {
  const [catalog, setCatalog] = useState(null);
  const [results, setResults] = useState([]);
  const [selectedView, setSelectedView] = useState({});
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState({});

  useEffect(() => {
    if (!datasetId) return;
    fetch(`http://localhost:8000/api/eda/catalog/${datasetId}`)
      .then((r) => r.json())
      .then(setCatalog)
      .catch((err) => console.error("Failed to load EDA catalog:", err));
  }, [datasetId]);

  const runAnalysis = async (a) => {
    setBusy((b) => ({ ...b, [a.id]: true }));
    try {
      const res = await fetch(`http://localhost:8000/api/eda/run/${datasetId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          analysis_id: a.id,
          chart_type: a.default_chart,
        }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      setResults((p) => [data, ...p.filter((item) => item.title !== data.title)]);
      setSelectedView((p) => ({ ...p, [data.title]: data.chart_type === "table" ? "table" : "chart" }));
    } catch (e) {
      setResults((p) => [
        {
          title: a.title,
          chart_type: "table",
          data: [],
          insight: "",
          error: `Couldn't run this analysis: ${e.message}`,
        },
        ...p,
      ]);
    } finally {
      setBusy((b) => ({ ...b, [a.id]: false }));
    }
  };

  const runFullEDA = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/eda/full/${datasetId}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      setResults(data.results || []);
      const views = {};
      (data.results || []).forEach((r) => (views[r.title] = r.chart_type === "table" ? "table" : "chart"));
      setSelectedView(views);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (!catalog) {
    return (
      <div className="bg-white p-6 rounded-2xl shadow-sm mt-6 flex items-center gap-2 text-slate-500 dark:bg-slate-900 dark:text-slate-400">
        <Loader2 className="animate-spin" size={18} />
        Loading EDA Analysis Catalog…
      </div>
    );
  }

  return (
    <Card
      title="Intelligent EDA Studio"
      info="Explore distributions, correlations, rankings, and statistical companions on your clean data."
      actions={
        <Button
          onClick={runFullEDA}
          disabled={loading}
          size="sm"
          className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-md"
        >
          {loading ? <Loader2 className="animate-spin" size={13} /> : <Sparkles size={13} />}
          {loading ? "Computing Full EDA…" : "1-Click Full EDA"}
        </Button>
      }
    >
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-5 pb-3 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <Badge tone="info">{catalog.rows.toLocaleString()} cleaned rows</Badge>
          <Badge tone="slate">{catalog.columns} columns</Badge>
          <Badge tone="ai">{catalog.analyses.length} analysis cards</Badge>
        </div>
      </div>

      {/* Analysis Catalog Grid */}
      <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
        Analysis Catalog (AI-Proposed & Standard Options)
      </h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 mb-8">
        {catalog.analyses.map((a) => {
          const isBusy = busy[a.id];
          return (
            <div
              key={a.id}
              className={`border rounded-xl p-4 transition flex flex-col justify-between ${
                a.source === "ai"
                  ? "border-purple-200 bg-purple-50/40 hover:bg-purple-50/70 dark:border-purple-900/60 dark:bg-purple-950/20 dark:hover:bg-purple-950/40"
                  : a.recommended
                  ? "border-indigo-200 bg-indigo-50/40 hover:bg-indigo-50/70 dark:border-indigo-900/60 dark:bg-indigo-950/20 dark:hover:bg-indigo-950/40"
                  : "border-slate-200 bg-slate-50/60 opacity-70 hover:opacity-100 dark:border-slate-800 dark:bg-slate-900/40"
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2">
                  <p className="font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                    {!a.recommended && <EyeOff size={14} className="text-amber-500" />}
                    {a.title}
                  </p>
                  <div className="flex items-center gap-1.5">
                    {a.source === "ai" && <Badge tone="ai">AI-proposed</Badge>}
                    <Badge tone={a.recommended ? "info" : "warn"}>
                      {a.recommended ? "Recommended" : "Dimmed"}
                    </Badge>
                  </div>
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{a.why}</p>

                <div className="mt-2 space-y-1 text-xs text-slate-600 dark:text-slate-300">
                  <p>
                    <b>Expected output:</b> {a.expected_output || TYPE_OUTPUT[a.type] || "Structured summary view"}
                  </p>
                  <p>
                    <b>Why this matters:</b> {a.beginner_hint || a.why}
                  </p>
                </div>

                {!a.recommended && (
                  <div className="mt-2 rounded-xl bg-amber-50 dark:bg-amber-950/20 p-2.5 text-xs text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-900/40">
                    Not strongly recommended: {a.dim_reason}
                    <br />
                    <span className="text-[11px] text-amber-600 dark:text-amber-400">You can still run it to explore the data.</span>
                  </div>
                )}
              </div>

              <div className="flex justify-between items-center mt-3 pt-2.5 border-t border-slate-200/60 dark:border-slate-800/80">
                <span className="text-[11px] text-slate-400 dark:text-slate-500 font-mono">
                  Views: {a.chart_options.join(" · ")}
                </span>

                <Button
                  onClick={() => runAnalysis(a)}
                  disabled={isBusy || loading}
                  variant="primary"
                  size="sm"
                >
                  {isBusy ? <Loader2 className="animate-spin" size={12} /> : <Play size={12} />}
                  {isBusy ? "Running…" : "Run"}
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Rendered Analysis Results */}
      {results.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <CheckCircle className="text-emerald-600" size={18} />
              Generated Insights & Visualizations ({results.length})
            </h4>
          </div>

          {results.map((r, idx) => {
            const view = selectedView[r.title] || (r.chart_type === "table" ? "table" : "chart");

            return (
              <div key={idx} className="border border-slate-200 dark:border-slate-800 rounded-2xl p-5 bg-white dark:bg-slate-900 shadow-sm">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
                  <div>
                    <h5 className="font-bold text-slate-900 dark:text-white text-base">{r.title}</h5>
                    {r.insight && <p className="text-xs text-slate-600 dark:text-slate-400 italic mt-0.5">{r.insight}</p>}
                  </div>

                  {/* Alterable Representation Toggle */}
                  {!r.error && (
                    <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 shrink-0">
                      <button
                        onClick={() => setSelectedView((prev) => ({ ...prev, [r.title]: "chart" }))}
                        className={`px-2.5 py-1 text-xs font-semibold rounded-lg flex items-center gap-1 transition ${
                          view === "chart"
                            ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-indigo-400"
                            : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200"
                        }`}
                      >
                        <BarChart2 size={13} /> Chart
                      </button>
                      <button
                        onClick={() => setSelectedView((prev) => ({ ...prev, [r.title]: "table" }))}
                        className={`px-2.5 py-1 text-xs font-semibold rounded-lg flex items-center gap-1 transition ${
                          view === "table"
                            ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-indigo-400"
                            : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200"
                        }`}
                      >
                        <TableIcon size={13} /> Table
                      </button>
                      <button
                        onClick={() => setSelectedView((prev) => ({ ...prev, [r.title]: "narrative" }))}
                        className={`px-2.5 py-1 text-xs font-semibold rounded-lg flex items-center gap-1 transition ${
                          view === "narrative"
                            ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-indigo-400"
                            : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200"
                        }`}
                      >
                        <AlignLeft size={13} /> Narrative
                      </button>
                    </div>
                  )}
                </div>

                {r.error ? (
                  <div className="rounded-xl bg-rose-50 dark:bg-rose-950/30 p-3.5 border border-rose-200 dark:border-rose-900/50 flex items-center gap-2 text-xs font-semibold text-rose-700 dark:text-rose-300">
                    <AlertCircle size={15} />
                    {r.error}
                  </div>
                ) : (
                  <>
                    {view === "chart" && <MplChart result={r} />}
                    {view === "table" && <DataTable data={r.data} />}
                    {view === "narrative" && (
                      <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
                        <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-semibold mb-3">
                          💡 {r.insight}
                        </p>
                        {r.stats && (
                          <div>
                            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-1">
                              Statistical Proofs & Companions:
                            </span>
                            <pre className="p-3 bg-slate-900 text-emerald-400 rounded-lg text-xs font-mono overflow-x-auto border border-slate-800">
                              {JSON.stringify(r.stats, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
