"use client";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Coins, Compass, Database, Layers } from "lucide-react";
import { useDataset } from "./DatasetContext";

export default function TokenTicker() {
  const { id } = useDataset();
  const pathname = usePathname();
  const [t, setT] = useState(null);
  const [manualScope, setManualScope] = useState(null);

  // Auto-detect scope based on active route unless user manually toggles
  const autoScope = pathname?.startsWith("/research")
    ? "research"
    : pathname?.startsWith("/cleaning") || pathname?.startsWith("/eda") || pathname?.startsWith("/cleaned") || pathname?.startsWith("/report")
    ? "dataset"
    : "all";

  const activeScope = manualScope || autoScope;

  useEffect(() => {
    const load = () => {
      let url = `http://localhost:8000/api/tokens?scope=${activeScope}`;
      if (activeScope === "dataset" && id) {
        url += `&run_id=${id}`;
      }
      fetch(url)
        .then((r) => r.json())
        .then(setT)
        .catch(() => {});
    };
    load();
    const iv = setInterval(load, 3000); // 3s live refresh
    return () => clearInterval(iv);
  }, [id, activeScope, pathname]);

  if (!t) return null;

  return (
    <div className="mb-3 space-y-2 rounded-xl bg-slate-50 p-2.5 dark:bg-slate-800/80 border border-slate-200/70 dark:border-slate-700/60 text-xs">
      {/* Scope Selector Pills */}
      <div className="flex items-center justify-between border-b border-slate-200/60 dark:border-slate-700/50 pb-1.5 text-[10px]">
        <span className="font-bold text-slate-500 uppercase tracking-wider">AI Telemetry</span>
        <div className="flex gap-1 bg-slate-200/60 dark:bg-slate-900/60 p-0.5 rounded-lg">
          {[
            { id: "research", label: "Niche" },
            { id: "dataset", label: "Pipeline" },
            { id: "all", label: "All" }
          ].map((s) => (
            <button
              key={s.id}
              onClick={() => setManualScope(s.id)}
              className={`px-1.5 py-0.5 rounded-md font-semibold transition ${
                activeScope === s.id
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
              }`}
              title={s.id === "research" ? "Isolates Niche Research tokens" : s.id === "dataset" ? "Isolates Dataset Pipeline tokens" : "Total Platform tokens"}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Scope Badge & Tokens */}
      <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
        <span className="flex items-center gap-1 font-medium">
          <Coins size={12} className="text-amber-500" />
          {activeScope === "research" ? "Niche Tokens" : activeScope === "dataset" ? "Pipeline Tokens" : "Total Tokens"}
        </span>
        <span className="font-bold tabular-nums text-slate-900 dark:text-slate-100 font-mono">
          {(t.total_tokens || 0).toLocaleString()}
        </span>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
        <span>Est. Cost</span>
        <span className="tabular-nums font-semibold text-slate-700 dark:text-slate-200 font-mono">
          ${(t.estimated_cost_usd || 0).toFixed(4)}
        </span>
      </div>

      <div className="flex items-center justify-between text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
        <span>Saved (0-Tkn)</span>
        <span className="tabular-nums font-bold font-mono">
          +{(t.total_saved || 0).toLocaleString()}
        </span>
      </div>
    </div>
  );
}
