"use client";
import { useState } from "react";
import { Card, Badge } from "./ui";
import { ChevronDown, ChevronUp, ShieldCheck, AlertTriangle, Sparkles, BarChart2, Table as TableIcon } from "lucide-react";
import { MplChart, DataTable } from "../ChartRenderer";

export function InsightCard({ chart, viewMode = "chart", onToggleView }) {
  const [showDeepStats, setShowDeepStats] = useState(false);
  const brief = chart.executive_brief || {};
  const verification = chart.verification || {};
  const isVerified = verification.verified !== false;

  return (
    <Card
      title={chart.title}
      info={chart.insight}
      pad={false}
      actions={
        <div className="flex items-center gap-2">
          {onToggleView && (
            <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700">
              <button
                onClick={() => onToggleView("chart")}
                className={`px-2 py-0.5 text-xs font-semibold rounded flex items-center gap-1 transition ${
                  viewMode === "chart"
                    ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-indigo-400"
                    : "text-slate-500 hover:text-slate-800 dark:text-slate-400"
                }`}
              >
                <BarChart2 size={12} /> Chart
              </button>
              <button
                onClick={() => onToggleView("table")}
                className={`px-2 py-0.5 text-xs font-semibold rounded flex items-center gap-1 transition ${
                  viewMode === "table"
                    ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-indigo-400"
                    : "text-slate-500 hover:text-slate-800 dark:text-slate-400"
                }`}
              >
                <TableIcon size={12} /> Table
              </button>
            </div>
          )}
          <Badge tone={isVerified ? "good" : "bad"} className="flex items-center gap-1">
            {isVerified ? <ShieldCheck size={12} /> : <AlertTriangle size={12} />}
            {isVerified ? "Mathematically Verified" : "Discrepancy Detected"}
          </Badge>
        </div>
      }
    >
      {/* 1. The Visual Representation (Chart or Interactive Table) */}
      <div className="p-4 bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800">
        {chart.error ? (
          <p className="text-xs text-rose-600 font-semibold">{chart.error}</p>
        ) : viewMode === "table" ? (
          <DataTable data={chart.data} />
        ) : (
          <MplChart result={chart} />
        )}
      </div>

      {/* 2. Standardized Plain-English Executive Brief */}
      <div className="p-4 border-b border-slate-100 dark:border-slate-800 bg-indigo-50/60 dark:bg-indigo-950/20">
        <div className="flex items-center gap-1.5 text-indigo-900 dark:text-indigo-200 font-bold text-xs mb-1">
          <Sparkles size={13} className="text-indigo-600 dark:text-indigo-400" />
          <span>Executive Business Takeaway (Plain-English)</span>
        </div>
        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
          {brief.key_insight || chart.insight || "Analyze the visual distribution above for patterns and outliers."}
        </p>
      </div>

      {/* 3. Deep Statistical Proof & Hypothesis Verification (Progressive Disclosure) */}
      <div className="p-3 bg-slate-50/60 dark:bg-slate-900/40 rounded-b-2xl">
        <button
          onClick={() => setShowDeepStats(!showDeepStats)}
          className="flex w-full items-center justify-between text-xs font-semibold text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition"
        >
          <span className="flex items-center gap-1.5">
            📊 View Mathematical Statistical Proof & Verification Invariants
          </span>
          {showDeepStats ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        {showDeepStats && (
          <div className="mt-3 space-y-2 text-xs font-mono text-slate-600 dark:text-slate-400 border-t border-slate-200/60 dark:border-slate-800 pt-2.5 animate-fadeIn">
            {brief.statistical_verdict && (
              <div className="flex items-center justify-between p-1.5 rounded bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800">
                <span className="font-semibold text-slate-700 dark:text-slate-300">Statistical Test Verdict:</span>
                <span className="text-indigo-600 dark:text-indigo-400 font-bold">{brief.statistical_verdict}</span>
              </div>
            )}
            {chart.statistical_brief &&
              Object.entries(chart.statistical_brief).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between p-1.5 rounded bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800">
                  <span className="text-slate-500 capitalize">{k.replace(/_/g, " ")}:</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{v}</span>
                </div>
              ))}
            {chart.advanced_stats &&
              Object.entries(chart.advanced_stats).map(([k, v]) => (
                <div key={k} className="flex items-center justify-between p-1.5 rounded bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800">
                  <span className="text-slate-500 capitalize">{k.replace(/_/g, " ")}:</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{typeof v === "number" ? v.toFixed(3) : String(v)}</span>
                </div>
              ))}
          </div>
        )}
      </div>
    </Card>
  );
}
