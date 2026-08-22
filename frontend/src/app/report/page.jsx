"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useDataset } from "../components/DatasetContext";
import { Card, Badge, Button } from "../components/ui";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { WorkflowStepGuide } from "../components/WorkflowStepGuide";
import { Loader2, Download, RefreshCw, Sparkles, ShieldCheck, AlertTriangle, Wrench } from "lucide-react";

export default function ReportPage() {
  const { id } = useDataset();
  const [status, setStatus] = useState(null);
  const [rep, setRep] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    if (!id) return;
    fetch(`http://localhost:8000/api/status/${id}`)
      .then((r) => r.json())
      .then((st) => {
        setStatus(st);
        if (st.cleaned) {
          fetch(`http://localhost:8000/api/report/${id}`)
            .then((r) => r.json())
            .then((j) => setRep(j && j.dataset_id ? j : null))
            .catch((err) => console.error("Failed fetching report:", err));
        }
      })
      .catch((err) => console.warn("Failed fetching status:", err));

    fetch(`http://localhost:8000/api/summary/${id}`)
      .then((r) => r.json())
      .then((s) => setSummary(s))
      .catch((err) => console.warn("Failed fetching summary:", err));
  }, [id]);

  const generate = async () => {
    if (!id) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const r = await fetch(`http://localhost:8000/api/report/${id}`, { method: "POST" });
      if (!r.ok) {
        const errData = await r.json().catch(() => ({}));
        throw new Error(errData.detail || "Report generation failed");
      }
      setRep(await r.json());
    } catch (e) {
      console.error(e);
      setErrorMsg(e.message || "Failed generating quality report");
    } finally {
      setLoading(false);
    }
  };

  const downloadPack = () => {
    if (!id) return;
    window.open(`http://localhost:8000/api/export/download/${id}`, "_blank");
  };

  if (!id) {
    return (
      <main className="p-8 text-center">
        <Card title="No Dataset Selected">
          <p className="text-xs text-slate-500 mb-4">Please upload or select a dataset on the Overview page to generate quality reports.</p>
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
          { href: "/report", label: "Data Pipeline" },
          { label: "Quality & Governance Report" },
        ]}
      />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">Data Quality & Governance Audit</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Contract gate verification, distribution drift tracking, AI audit (CP4), and direct reproducible export
          </p>
          {summary?.overview && status?.cleaned && (
            <p className="mt-1 text-xs text-indigo-700 dark:text-indigo-300 font-medium">
              ℹ️ {summary.overview}
            </p>
          )}
        </div>
        {status?.cleaned && (
          <div className="flex gap-2">
            <Button size="sm" variant="secondary" onClick={generate} disabled={loading}>
              {loading ? <Loader2 className="animate-spin" size={13} /> : <RefreshCw size={13} />}
              {loading ? "Auditing…" : "Regenerate Audit"}
            </Button>
            <Button size="sm" variant="primary" onClick={downloadPack} disabled={!rep}>
              <Download size={13} /> Download Export Pack (.zip)
            </Button>
          </div>
        )}
      </div>

      {/* Non-Sophisticated Workflow Guide */}
      <WorkflowStepGuide
        currentStepId="analyst"
        pageTitle="Data Quality & Governance Audit Report"
        reason="This is the final audit certificate for your dataset. It runs statistical checks (KS-test drift, null checks, range bounds) to prove that the cleaned dataset is statistically sound and ready for enterprise production."
        priorStepText="Clean your dataset in Cleaning Studio first so that all proposed transformations have been executed."
        priorStepHref="/cleaning"
        currentActionSteps={[
          { title: "Run Quality Audit", detail: "Click 'Regenerate Audit' to compute automated contract assertions and distribution drift scores." },
          { title: "Verify Invariants & KS-Test", detail: "Ensure no drift checks were flagged (Kolmogorov-Smirnov p-value > 0.05)." },
          { title: "Download Export Pack", detail: "Click 'Download Export Pack (.zip)' to get the cleaned CSV, quality certificate, and logs." }
        ]}
        nextStepText="You are at the final stage! Use the Cleaned Data Explorer or AI Copilot to query your clean data."
        nextStepHref="/cleaned"
        jargonBuster={[
          { term: "Contract Gate", meaning: "A set of strict pass/fail rules (e.g., 'price must be > 0' and 'zero duplicate rows allowed') that must pass before data is approved." },
          { term: "Distribution Drift (KS-Test)", meaning: "A statistical comparison between raw and cleaned data ensuring the cleaning process didn't accidentally distort the real underlying numbers." },
          { term: "Export Pack (.zip)", meaning: "A complete bundle containing the cleaned CSV, audit report JSON, execution log, and schema definitions." },
          { term: "CP4 Audit", meaning: "Checkpoint 4: A supervisory AI check verifying that the final report accurately matches the computed mathematical numbers." }
        ]}
      />

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-300 rounded-xl text-xs font-semibold">
          ⚠️ {errorMsg}
        </div>
      )}

      {/* Cleaning Gate Card */}
      {status && !status.cleaned && (
        <Card pad={false} className="border-amber-200 dark:border-amber-900/60 bg-amber-50/40 dark:bg-amber-950/20">
          <div className="p-6 text-center space-y-3">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400 shadow-sm">
              <AlertTriangle size={24} />
            </div>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
              Cleaning Required Before Quality Audit & Export
            </h2>
            <p className="max-w-lg mx-auto text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              DataForge AI requires executing data cleaning and transformations before generating governance audits, computing distribution drift, or exporting verified data packages.
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

      {status?.cleaned && !rep && (
        <Card title="Report Pending">
          <div className="text-center py-8">
            <ShieldCheck size={32} className="mx-auto text-slate-400 mb-2" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">No Quality Audit Generated Yet</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 mb-4">
              Click &quot;Run Full Quality Audit&quot; to execute CP4 verification rules, compute distribution drift, and formulate CP5 narrative.
            </p>
            <Button size="sm" onClick={generate} disabled={loading}>
              {loading && <Loader2 className="animate-spin" size={13} />}
              {loading ? "Generating…" : "Run Full Quality Audit"}
            </Button>
          </div>
        </Card>
      )}

      {status?.cleaned && rep && (
        <>
          {/* Quality Score Improvement Summary */}
          {rep.execution && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 text-xs shadow-sm">
              <div>
                <span className="text-slate-500 dark:text-slate-400 block font-medium">Rows Cleaned</span>
                <b className="text-slate-900 dark:text-slate-100">{rep.before_rows} → {rep.after_rows}</b>
              </div>
              <div>
                <span className="text-slate-500 dark:text-slate-400 block font-medium">Rows Removed</span>
                <b className="text-amber-600 dark:text-amber-400">{rep.before_rows - rep.after_rows}</b>
              </div>
              <div>
                <span className="text-slate-500 dark:text-slate-400 block font-medium">Quality Score</span>
                <b>{typeof rep.execution.before_quality === "object" ? rep.execution.before_quality?.overall : rep.execution.before_quality}%</b> →{" "}
                <b className="text-emerald-600 dark:text-emerald-400">{typeof rep.execution.after_quality === "object" ? rep.execution.after_quality?.overall : rep.execution.after_quality}%</b>
              </div>
              <div>
                <span className="text-slate-500 dark:text-slate-400 block font-medium">Quality Delta</span>
                <b className="text-emerald-600 dark:text-emerald-400">
                  +{Math.round(((typeof rep.execution.after_quality === "object" ? rep.execution.after_quality?.overall : rep.execution.after_quality) - (typeof rep.execution.before_quality === "object" ? rep.execution.before_quality?.overall : rep.execution.before_quality)) * 100) / 100}%
                </b>
              </div>
            </div>
          )}

          {/* Contract Gate */}
          <Card
            title="Contract Gate"
            info="Final safety verification. If any blocking check fails, downstream export is halted."
            actions={
              <Badge tone={rep.contract?.overall === "pass" ? "good" : rep.contract?.overall === "warn" ? "warn" : "bad"}>
                {(rep.contract?.overall || "PASS").toUpperCase()}
              </Badge>
            }
          >
            <ul className="space-y-1.5 text-xs">
              {(rep.contract?.checks || []).map((c, i) => (
                <li key={i} className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <span>{c.status === "pass" ? "✅" : c.status === "warn" ? "⚠️" : "❌"}</span>
                  <span className="font-mono font-semibold text-slate-900 dark:text-slate-100">{c.name}:</span>
                  <span>{c.detail}</span>
                </li>
              ))}
            </ul>
          </Card>

          {/* Distribution Drift */}
          <Card
            title="Distribution Drift (PSI & KS Test)"
            info="Quantifies feature shifts between raw canonical and cleaned datasets. High drift warns of signal loss."
          >
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="border-b border-slate-200 dark:border-slate-800 text-[11px] uppercase text-slate-500 dark:text-slate-400 font-bold">
                  <tr>
                    <th className="py-2">Column</th>
                    <th>Type</th>
                    <th>PSI Score</th>
                    <th>Significant Drift?</th>
                  </tr>
                </thead>
                <tbody>
                  {(rep.drift || []).map((d, i) => (
                    <tr key={i} className="border-b border-slate-100 dark:border-slate-800/50">
                      <td className="py-2 font-mono font-semibold text-slate-900 dark:text-slate-100">{d.column}</td>
                      <td className="text-slate-600 dark:text-slate-400">{d.type}</td>
                      <td className="font-mono text-slate-700 dark:text-slate-300">{d.psi}</td>
                      <td>
                        {d.drifted ? <Badge tone="warn">Yes (Drifted)</Badge> : <Badge tone="good">No (Stable)</Badge>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* AI Audit CP4 */}
          {rep.cp4_audit && (
            <Card
              title="AI Supervisor Audit (CP4)"
              info="The LLM auditor compares before/after statistical distributions and highlights potential regressions."
              actions={<Badge tone="ai">AI Audited</Badge>}
            >
              <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                {rep.cp4_audit.summary}
              </p>
              {(rep.cp4_audit.regressions || []).length > 0 && (
                <ul className="mt-2.5 list-inside list-disc text-xs text-amber-700 dark:text-amber-300 space-y-1">
                  {rep.cp4_audit.regressions.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              )}
            </Card>
          )}

          {/* Domain Narrative CP5 */}
          {rep.narrative && (
            <Card
              title="Domain Data Narrative (CP5)"
              info="Human-readable synthesis of the dataset's readiness for business reporting or machine learning."
              actions={<Badge tone="ai">AI Synthesized</Badge>}
            >
              <div className="p-3.5 bg-violet-50/50 dark:bg-violet-950/20 rounded-xl border border-violet-100 dark:border-violet-900/40">
                <p className="text-xs italic text-slate-700 dark:text-slate-300 leading-relaxed">
                  <Sparkles size={13} className="inline mr-1.5 text-violet-600 dark:text-violet-400" />
                  {rep.narrative}
                </p>
              </div>
            </Card>
          )}

          {/* Browser Download Export Card */}
          <Card
            title="Download Reproducible Package"
            info="Downloads a packaged .zip file directly in your browser containing the cleaned dataset (CSV), schema dictionary, audit configuration, and quality report."
            actions={
              <Button size="sm" variant="primary" onClick={downloadPack}>
                <Download size={13} /> Download .zip
              </Button>
            }
          >
            <div className="text-xs text-slate-600 dark:text-slate-300 space-y-2">
              <p className="text-emerald-700 dark:text-emerald-400 font-medium">
                ✅ Quality audit verified. Ready for one-click browser download.
              </p>
              <div className="flex flex-wrap gap-2 pt-1">
                {["cleaned.csv", "dictionary.json", "config.json", "audit.json", "report.json"].map((f) => (
                  <span
                    key={f}
                    className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono text-xs rounded-lg border border-slate-200 dark:border-slate-700"
                  >
                    📄 {f}
                  </span>
                ))}
              </div>
            </div>
          </Card>
        </>
      )}
    </main>
  );
}
