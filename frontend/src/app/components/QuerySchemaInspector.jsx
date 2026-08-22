"use client";
import { useState } from "react";
import { Database, Terminal, Clock, Rows, Copy, Check, ChevronDown, ChevronUp, ShieldCheck } from "lucide-react";
import { Badge } from "./ui";

export default function QuerySchemaInspector({ query, schema, metrics, explanation, queryType = "sql" }) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!query && !schema) return null;

  const handleCopy = () => {
    if (query) {
      navigator.clipboard.writeText(query);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="mt-3 rounded-xl border border-slate-200 bg-white/95 dark:border-slate-800 dark:bg-slate-900/90 shadow-sm overflow-hidden text-xs">
      <div 
        onClick={() => setOpen(!open)} 
        className="flex items-center justify-between p-3 cursor-pointer select-none hover:bg-slate-50 dark:hover:bg-slate-800/60 transition"
      >
        <div className="flex items-center gap-2">
          {queryType === "sql" ? (
            <Database size={14} className="text-sky-600 dark:text-sky-400" />
          ) : (
            <Terminal size={14} className="text-emerald-600 dark:text-emerald-400" />
          )}
          <span className="font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider text-[11px]">
            {queryType} Query & Schema Inspector
          </span>
          {metrics?.runtime_ms && (
            <Badge tone="ai">{metrics.runtime_ms} ms</Badge>
          )}
        </div>
        <div className="flex items-center gap-2 text-slate-500">
          <span className="text-[11px] font-medium hidden sm:inline">
            {open ? "Hide Execution Details" : "View Code & Schema Details"}
          </span>
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </div>

      {open && (
        <div className="p-3.5 border-t border-slate-100 dark:border-slate-800 space-y-3 bg-slate-50/50 dark:bg-slate-950/40">
          {/* Plain English Explanation */}
          {explanation && (
            <div className="flex items-start gap-2 p-2.5 rounded-lg bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50 text-indigo-950 dark:text-indigo-200">
              <ShieldCheck size={14} className="mt-0.5 text-indigo-600 shrink-0" />
              <div className="text-[11px] leading-relaxed">
                <span className="font-bold">Summary: </span>
                <span>{explanation}</span>
              </div>
            </div>
          )}

          {/* Executed Code / SQL Query */}
          {query && (
            <div>
              <div className="flex items-center justify-between mb-1 text-[11px] font-semibold text-slate-600 dark:text-slate-400">
                <span>Executed {queryType.toUpperCase()} Code</span>
                <button 
                  onClick={handleCopy}
                  className="flex items-center gap-1 text-[10px] text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400"
                >
                  {copied ? <Check size={11} className="text-emerald-600" /> : <Copy size={11} />}
                  {copied ? "Copied" : "Copy Code"}
                </button>
              </div>
              <pre className="p-2.5 rounded-lg bg-slate-900 text-slate-100 font-mono text-[11px] overflow-x-auto border border-slate-800 shadow-inner">
                <code>{query}</code>
              </pre>
            </div>
          )}

          {/* Schema & Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {schema && Object.keys(schema).length > 0 && (
              <div className="p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800">
                <div className="font-bold text-[11px] text-slate-700 dark:text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <Database size={12} className="text-sky-600" /> Table Column Schemas
                </div>
                <div className="max-h-36 overflow-y-auto space-y-1 pr-1">
                  {Object.entries(schema).map(([col, dtype]) => (
                    <div key={col} className="flex justify-between items-center text-[10px] py-0.5 border-b border-slate-100 dark:border-slate-800/60">
                      <span className="font-medium text-slate-800 dark:text-slate-200">{col}</span>
                      <span className="font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">{String(dtype)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {metrics && (
              <div className="p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 space-y-2">
                <div className="font-bold text-[11px] text-slate-700 dark:text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <Clock size={12} className="text-emerald-600" /> Execution Telemetry
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="p-1.5 rounded bg-slate-50 dark:bg-slate-800/60">
                    <span className="text-[10px] text-slate-500 block">Runtime</span>
                    <span className="font-semibold">{metrics.runtime_ms || 0} ms</span>
                  </div>
                  <div className="p-1.5 rounded bg-slate-50 dark:bg-slate-800/60">
                    <span className="text-[10px] text-slate-500 block">Rows Scanned</span>
                    <span className="font-semibold">{metrics.rows_scanned || 0}</span>
                  </div>
                  <div className="p-1.5 rounded bg-slate-50 dark:bg-slate-800/60">
                    <span className="text-[10px] text-slate-500 block">Rows Returned</span>
                    <span className="font-semibold">{metrics.rows_returned || 0}</span>
                  </div>
                  <div className="p-1.5 rounded bg-slate-50 dark:bg-slate-800/60">
                    <span className="text-[10px] text-slate-500 block">Token Overhead</span>
                    <span className="font-semibold">{metrics.tokens || 0} tok</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
