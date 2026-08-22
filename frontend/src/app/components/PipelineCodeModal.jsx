"use client";
import { useState, useEffect } from "react";
import { Copy, Check, Download, Terminal, Code2, Layers, X, Loader2 } from "lucide-react";
import { Button, Badge } from "./ui";

export default function PipelineCodeModal({ datasetId, isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState("python");
  const [codeData, setCodeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!isOpen || !datasetId) return;
    setLoading(true);
    fetch(`http://localhost:8000/api/export/code/${datasetId}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setCodeData(d))
      .catch((e) => console.error("Failed to load pipeline code", e))
      .finally(() => setLoading(false));
  }, [isOpen, datasetId]);

  if (!isOpen) return null;

  const currentCode =
    activeTab === "python"
      ? codeData?.python_script || "# Loading Python code..."
      : activeTab === "sql"
      ? codeData?.sql_model || "-- Loading SQL model..."
      : codeData?.airflow_dag || "# Loading Airflow DAG...";

  const handleCopy = () => {
    navigator.clipboard.writeText(currentCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const filename =
      activeTab === "python"
        ? `dataforge_clean_${datasetId}.py`
        : activeTab === "sql"
        ? `dataforge_transform_${datasetId}.sql`
        : `dataforge_dag_${datasetId}.py`;
    const blob = new Blob([currentCode], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-4xl rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4 bg-slate-950/80">
          <div className="flex items-center gap-2.5">
            <Terminal className="text-cyan-400" size={20} />
            <div>
              <h2 className="text-sm font-bold text-slate-100">Production Pipeline Exporter</h2>
              <p className="text-[11px] text-slate-400">
                Standalone code for Dataset <span className="font-mono text-cyan-400">{datasetId}</span>
              </p>
            </div>
          </div>
          <button onClick={onClose} className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200">
            <X size={18} />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900/60 px-6 py-2">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab("python")}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                activeTab === "python" ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Code2 size={14} /> Python (Pandas)
            </button>
            <button
              onClick={() => setActiveTab("sql")}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                activeTab === "sql" ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Layers size={14} /> SQL / dbt Model
            </button>
            <button
              onClick={() => setActiveTab("airflow")}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                activeTab === "airflow" ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Terminal size={14} /> Apache Airflow DAG
            </button>
          </div>

          <div className="flex items-center gap-2">
            <Button size="xs" variant="secondary" onClick={handleCopy}>
              {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
              {copied ? "Copied" : "Copy Code"}
            </Button>
            <Button size="xs" variant="primary" onClick={handleDownload}>
              <Download size={12} /> Download File
            </Button>
          </div>
        </div>

        {/* Code Content Box */}
        <div className="flex-1 overflow-auto p-6 bg-slate-950 font-mono text-xs text-slate-300">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 text-slate-400 gap-3">
              <Loader2 className="animate-spin text-cyan-400" size={24} />
              <span>Generating standalone production pipeline code...</span>
            </div>
          ) : (
            <pre className="whitespace-pre-wrap leading-relaxed select-all">{currentCode}</pre>
          )}
        </div>
      </div>
    </div>
  );
}
