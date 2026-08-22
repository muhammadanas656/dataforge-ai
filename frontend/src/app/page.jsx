"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { uploadFile } from "./api";
import { useDataset } from "./components/DatasetContext";
import { Card, StatTile, Badge, Button } from "./components/ui";
import WebScraperModal from "./components/WebScraperModal";
import { Upload, Loader2, Wrench, BarChart3, Database, FileText, PlusCircle, X, Globe, Sparkles, Play, CheckCircle2 } from "lucide-react";
import DatasetSummary from "./DatasetSummary";
import { WorkflowStepGuide } from "./components/WorkflowStepGuide";

export default function Overview() {
  const { id, setId, refresh } = useDataset();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [profile, setProfile] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [autopilotLoading, setAutopilotLoading] = useState(false);
  const [autopilotResult, setAutopilotResult] = useState(null);

  const handleRunAutopilot = async () => {
    if (!id) return;
    setAutopilotLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch("http://localhost:8000/api/autopilot/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: id })
      });
      if (!res.ok) throw new Error("Auto-Pilot run failed");
      const data = await res.json();
      setAutopilotResult(data);
      const statRes = await fetch(`http://localhost:8000/api/status/${id}`);
      if (statRes.ok) setStatus(await statRes.json());
    } catch (e) {
      console.error(e);
      setErrorMsg(e.message || "Auto-Pilot execution failed");
    } finally {
      setAutopilotLoading(false);
    }
  };

  const [showUpload, setShowUpload] = useState(false);
  const [showScraper, setShowScraper] = useState(false);

  useEffect(() => {
    setShowUpload(!id);
  }, [id]);

  useEffect(() => {
    if (!id) {
      setStatus(null);
      setProfile(null);
      return;
    }
    fetch(`http://localhost:8000/api/status/${id}`)
      .then((r) => r.json())
      .then(setStatus)
      .catch((err) => console.error("Failed to fetch status", err));

    fetch(`http://localhost:8000/api/profile/${id}`)
      .then((r) => r.json())
      .then(setProfile)
      .catch((err) => console.error("Failed to fetch profile", err));
  }, [id]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await uploadFile(file);
      setId(res.dataset_id);
      await refresh();
      setShowUpload(false);
      const profRes = await fetch(`http://localhost:8000/api/profile/${res.dataset_id}`);
      if (profRes.ok) setProfile(await profRes.json());
      const statRes = await fetch(`http://localhost:8000/api/status/${res.dataset_id}`);
      if (statRes.ok) setStatus(await statRes.json());
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-6xl space-y-5 px-6 py-6 overflow-x-clip">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight">Overview & Mission Control</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Autonomous data intelligence, governance, and quality assurance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant={showScraper ? "primary" : "secondary"} onClick={() => setShowScraper((s) => !s)}>
            <Globe size={13} /> {showScraper ? "Hide Web Scraper" : "Scrape from Web"}
          </Button>

          {id && (
            <Button size="sm" variant="secondary" onClick={() => setShowUpload((s) => !s)}>
              {showUpload ? (
                <>
                  <X size={13} /> Cancel
                </>
              ) : (
                <>
                  <PlusCircle size={13} /> + Add another dataset
                </>
              )}
            </Button>
          )}
          {id && (
            <>
              <Link href="/cleaning">
                <Button size="sm" variant="primary">
                  <Wrench size={13} /> Cleaning Studio
                </Button>
              </Link>
              <Link href="/eda">
                <Button size="sm" variant="secondary">
                  <BarChart3 size={13} /> EDA Report
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Non-Sophisticated Workflow Guide */}
      <WorkflowStepGuide
        currentStepId="overview"
        pageTitle="Mission Control & Data Ingest"
        reason="This is your command center. You come here to upload your raw CSV data, scrape product tables directly from any webpage, or inspect the overall health score of your active dataset."
        priorStepText="If you don't have a dataset yet, you can discover high-opportunity market ideas and auto-generate synthetic unit economics datasets from the Market Radar page."
        priorStepHref="/research"
        currentActionSteps={[
          { title: "Upload Raw CSV / Web Scrape", detail: "Drag & drop your CSV file below or click 'Scrape from Web' to extract HTML tables." },
          { title: "Review Quality Health", detail: "Check overall column completeness, detected types, and row count." },
          { title: "Switch Active Datasets", detail: "Use the top dataset switcher if you've uploaded multiple files." }
        ]}
        nextStepText="Once your dataset is uploaded and profiled, open the Cleaning Studio to fix duplicates, missing values, and anomalies."
        nextStepHref="/cleaning"
        jargonBuster={[
          { term: "Dataset ID", meaning: "A unique 8-character fingerprint for your uploaded data file." },
          { term: "Profiling", meaning: "Automatically scanning your file to detect column data types, missing values, and statistics." },
          { term: "Payload Duplicates", meaning: "Rows that share identical values across key identifying columns even if timestamps differ." },
          { term: "Multi-Tenant Workspace", meaning: "Isolated project folders so data from different clients or projects never mix." }
        ]}
      />

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-300 rounded-xl text-xs font-semibold">
          ⚠️ {errorMsg}
        </div>
      )}

      {showScraper && (
        <div className="animate-fadeIn">
          <WebScraperModal onClose={() => setShowScraper(false)} />
        </div>
      )}

      {showUpload && !showScraper && (
        <label className="flex h-56 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-white transition hover:border-indigo-500 hover:bg-indigo-50/40 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-indigo-500 dark:hover:bg-slate-800/60 shadow-sm animate-fadeIn">
          <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600 dark:bg-indigo-900/40 dark:text-indigo-400 shadow-sm">
            <Upload size={20} />
          </div>
          <p className="text-sm font-bold">
            {id ? "Upload another dataset" : "Drop a dataset to begin"}
          </p>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            CSV · JSON · Excel · Parquet · or custom source plugins
          </p>
          <input type="file" className="hidden" onChange={handleUpload} />
          {loading && <Loader2 className="mt-3 animate-spin text-indigo-600" size={18} />}
        </label>
      )}

      {id && (
        <>
          {/* Status Bar */}
          {status && (
            <Card title="Pipeline Execution Status" pad={false}>
              <div className="flex flex-wrap items-center justify-between gap-3 p-5">
                <div className="flex flex-wrap gap-2">
                  {Object.entries(status).map(([k, v]) => (
                    <Badge key={k} tone={v ? "good" : "slate"}>
                      {k}: {v ? "done" : "pending"}
                    </Badge>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Link href="/data">
                    <Button size="sm" variant="secondary">
                      <Database size={13} /> View Raw Data
                    </Button>
                  </Link>
                  <Link href="/report">
                    <Button size="sm" variant="secondary">
                      <FileText size={13} /> Quality Report
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          )}

          {/* Autonomous Zero-Touch Auto-Pilot Card */}
          <Card className="border-cyan-500/40 bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 p-5 shadow-lg">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Sparkles className="text-cyan-400" size={16} />
                  <h3 className="text-sm font-bold text-slate-100">Autonomous Zero-Touch Auto-Pilot</h3>
                  <Badge variant="cyan" size="xs">1-Click Pipeline</Badge>
                </div>
                <p className="text-xs text-slate-400 max-w-xl">
                  Automatically chains Profiling (CP1) → Semantic Dict (CP2) → Cleaning Plan (CP3) → Governed Execution (CP4) → Visual EDA & Causal DAG in a single autonomous run.
                </p>
              </div>
              <div className="flex items-center gap-3">
                {status?.cleaned && (
                  <Link href="/eda">
                    <Button size="sm" variant="secondary">
                      <BarChart3 size={13} /> View Causal EDA
                    </Button>
                  </Link>
                )}
                <Button
                  size="sm"
                  variant="primary"
                  onClick={handleRunAutopilot}
                  disabled={autopilotLoading}
                >
                  {autopilotLoading ? <Loader2 size={13} className="animate-spin" /> : <Play size={13} />}
                  <span>{autopilotLoading ? "Running Auto-Pilot..." : "Launch Auto-Pilot"}</span>
                </Button>
              </div>
            </div>

            {autopilotResult && (
              <div className="mt-4 rounded-xl border border-cyan-800/40 bg-cyan-950/20 p-3.5 text-xs animate-fadeIn">
                <div className="flex items-center gap-2 font-bold text-cyan-300 mb-2">
                  <CheckCircle2 size={14} className="text-emerald-400" />
                  <span>Auto-Pilot Completed in {autopilotResult.elapsed_seconds}s</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 font-mono text-[11px] text-slate-300">
                  <div className="rounded bg-slate-900/80 p-2">
                    <span className="text-slate-500">Quality:</span> {autopilotResult.quality_improvement?.before}% → {autopilotResult.quality_improvement?.after}% (+{autopilotResult.quality_improvement?.delta}%)
                  </div>
                  <div className="rounded bg-slate-900/80 p-2">
                    <span className="text-slate-500">Causal Insight:</span> {autopilotResult.causal_primary_driver}
                  </div>
                  <div className="rounded bg-slate-900/80 p-2">
                    <span className="text-slate-500">Hypotheses:</span> {autopilotResult.eda_summary?.hypotheses_count} tested
                  </div>
                  <div className="rounded bg-slate-900/80 p-2">
                    <span className="text-slate-500">Stages:</span> 5 / 5 Completed
                  </div>
                </div>
              </div>
            )}
          </Card>

          {/* Key Stat Tiles */}
          {profile && (
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <StatTile
                label="Total Rows"
                value={profile.total_rows?.toLocaleString() || 0}
                tone="neutral"
                info="Canonical row count from raw ingest snapshot."
              />
              <StatTile
                label="Total Columns"
                value={profile.total_columns || 0}
                tone="neutral"
                info="Schema fields detected."
              />
              <StatTile
                label="Duplicates"
                value={`${profile.duplicate_pct || 0}%`}
                tone={(profile.duplicate_pct || 0) > 0 ? "warn" : "good"}
                info="Exact identical records detected."
              />
              <StatTile
                label="PII Flags"
                value={Object.keys(profile.pii || {}).length}
                tone={Object.keys(profile.pii || {}).length > 0 ? "warn" : "good"}
                info="Sensitive columns masked before LLM transmission."
              />
            </div>
          )}

          {/* Dataset Understandability Summary */}
          <DatasetSummary datasetId={id} />
        </>
      )}
    </main>
  );
}
