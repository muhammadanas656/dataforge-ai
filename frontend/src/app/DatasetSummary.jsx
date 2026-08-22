"use client";
import { useEffect, useState } from "react";
import { Card, Badge, Tip } from "./components/ui";
import { AlertTriangle } from "lucide-react";

const SEM = {
  identifier: "slate",
  categorical: "info",
  currency: "good",
  numeric_continuous: "info",
  numeric_discrete: "info",
  date: "ai",
  free_text: "slate",
  contact_info: "bad",
};

export default function DatasetSummary({ datasetId }) {
  const [s, setS] = useState(null);

  useEffect(() => {
    if (!datasetId) return;
    fetch(`http://localhost:8000/api/summary/${datasetId}`)
      .then((r) => r.json())
      .then(setS)
      .catch((err) => console.error("Failed to load dataset summary", err));
  }, [datasetId]);

  if (!s || !s.columns?.length) return null;

  return (
    <Card
      title="Dataset Overview & Purpose"
      info="A plain-language explanation of what this data is, why it matters, and what each column means."
      pad={false}
    >
      {/* Overview & Reason Block */}
      <div className="space-y-3 border-b border-slate-100 p-5 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <Badge tone="ai">Domain: {s.domain}</Badge>
          {s.confidence != null && (
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              confidence {Math.round(s.confidence * 100)}%
            </span>
          )}
        </div>
        {s.overview && (
          <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
            {s.overview}
          </p>
        )}
        {s.reason && (
          <div className="rounded-xl bg-indigo-50/70 p-3.5 text-xs sm:text-sm text-indigo-900 dark:bg-indigo-950/30 dark:text-indigo-200 border border-indigo-100 dark:border-indigo-900/40">
            <span className="font-bold">Why it matters: </span>
            <span>{s.reason}</span>
          </div>
        )}
      </div>

      <div className="space-y-4 p-5">
        {s.red_flags?.length > 0 && (
          <div className="rounded-xl bg-amber-50 p-3.5 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/40">
            <div className="mb-1.5 flex items-center gap-1.5 text-xs font-bold text-amber-800 dark:text-amber-300">
              <AlertTriangle size={14} className="text-amber-600" />
              Ingest Red Flags & Observations:
            </div>
            <ul className="list-inside list-disc text-xs text-amber-700 dark:text-amber-400 space-y-0.5">
              {s.red_flags.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="overflow-x-auto border border-slate-100 dark:border-slate-800 rounded-xl">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50 dark:bg-slate-800/80 uppercase tracking-wider text-slate-500 dark:text-slate-400 font-bold">
                <th className="py-2.5 px-3">Column</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">What it means</th>
                <th className="py-2.5 px-3">Suggested Use</th>
                <th className="py-2.5 px-3">PII</th>
              </tr>
            </thead>
            <tbody>
              {s.columns.map((c, i) => (
                <tr
                  key={i}
                  className="border-b border-slate-50 dark:border-slate-800/50 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/10 transition"
                >
                  <td className="py-2.5 px-3 font-mono font-semibold text-slate-900 dark:text-slate-100">
                    {c.name}
                  </td>
                  <td className="py-2.5 px-3">
                    <Badge tone={SEM[c.semantic_type] || "slate"}>
                      {c.semantic_type}
                    </Badge>
                  </td>
                  <td className="py-2.5 px-3 text-slate-700 dark:text-slate-300">
                    {c.meaning}
                  </td>
                  <td className="py-2.5 px-3 text-slate-500 dark:text-slate-400">
                    {c.suggested_use}
                  </td>
                  <td className="py-2.5 px-3">
                    {c.pii ? (
                      <Badge tone="bad">masked</Badge>
                    ) : (
                      <span className="text-slate-400 font-mono">clean</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  );
}
