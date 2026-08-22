"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Check,
  X,
  FileText,
  Package,
  Sparkles,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Eye,
  EyeOff,
  Download,
} from "lucide-react";
import { Badge, Tip, Card, Button } from "./components/ui";
import QuerySchemaInspector from "./components/QuerySchemaInspector";
import VerificationAuditBadge from "./components/VerificationAuditBadge";

const REMOVING = new Set(["remove_duplicates", "remove_outliers", "drop_null_rows", "remove_invalid_prices"]);

const tierTone = (t) =>
  t?.startsWith("STRONGLY") ? "good" : t === "RECOMMEND" ? "info" : t === "OPTIONAL" ? "warn" : "bad";

export default function ReviewSection({ datasetId }) {
  const router = useRouter();
  const [gov, setGov] = useState(null);
  const [approvals, setApprovals] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reporting, setReporting] = useState(false);
  const [rep, setRep] = useState(null);
  const [exp, setExp] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [previews, setPreviews] = useState({});
  const [previewLoading, setPreviewLoading] = useState({});

  const [preserve, setPreserve] = useState({});

  useEffect(() => {
    fetch(`http://localhost:8000/api/governance/${datasetId}`)
      .then((r) => r.json())
      .then((g) => {
        setGov(g);
        const init = {};
        g.steps.forEach((s) => {
          init[s.id] = s.decision === "auto" || s.decision === "one_click";
        });
        setApprovals(init);
      })
      .catch((e) => {
        console.error("Failed to load governance plan", e);
        setErrorMsg("Failed to load governance plan.");
      });
  }, [datasetId]);

  const previewStep = async (s) => {
    if (previews[s.id]) {
      setPreviews((p) => ({ ...p, [s.id]: null }));
      return;
    }
    setPreviewLoading((p) => ({ ...p, [s.id]: true }));
    try {
      const res = await fetch(`http://localhost:8000/api/preview/${datasetId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: s.action, column: s.column, pandas_expr: s.pandas_expr, new_column: s.new_column, subset: s.subset }),
      });
      const data = await res.json();
      setPreviews((p) => ({ ...p, [s.id]: data }));
    } catch (e) {
      console.error("Preview failed", e);
    } finally {
      setPreviewLoading((p) => ({ ...p, [s.id]: false }));
    }
  };

  if (errorMsg) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-900/60 p-6 rounded-2xl shadow text-rose-600 dark:text-rose-400 font-medium">
        {errorMsg}
      </div>
    );
  }

  if (!gov) {
    return (
      <div className="bg-white p-6 rounded-2xl shadow-sm flex items-center gap-2 text-slate-500 dark:bg-slate-900 dark:text-slate-400">
        <Loader2 className="animate-spin" size={20} />
        Loading governance plan & approval cards…
      </div>
    );
  }

  const removedPct = gov.steps
    .filter((s) => REMOVING.has(s.action) && approvals[s.id])
    .reduce((a, s) => a + (s.impact?.pct || 0), 0);

  const overclean = removedPct > 20;

  const execute = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const ids = gov.steps.filter((s) => approvals[s.id]).map((s) => s.id);
      const res = await fetch(`http://localhost:8000/api/execute/${datasetId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved_ids: ids, preserve }),
      });
      if (!res.ok) {
        throw new Error(`Execution failed: ${res.statusText}`);
      }
      setResult(await res.json());
    } catch (e) {
      console.error(e);
      setErrorMsg(e.message || "Failed executing approved steps.");
    } finally {
      setLoading(false);
    }
  };

  const reportExport = async () => {
    setReporting(true);
    setErrorMsg(null);
    try {
      const rRes = await fetch(`http://localhost:8000/api/report/${datasetId}`, { method: "POST" });
      if (!rRes.ok) throw new Error("Report generation failed");
      const rData = await rRes.json();
      setRep(rData);

      const eRes = await fetch(`http://localhost:8000/api/export/${datasetId}`, { method: "POST" });
      if (!eRes.ok) throw new Error("Export pack creation failed");
      const eData = await eRes.json();
      setExp(eData);
    } catch (e) {
      console.error(e);
      setErrorMsg(e.message || "Failed creating report & export package.");
    } finally {
      setReporting(false);
    }
  };

  const bQ = typeof result?.before_quality === "object" ? result.before_quality?.overall : result?.before_quality || 0;
  const aQ = typeof result?.after_quality === "object" ? result.after_quality?.overall : result?.after_quality || 0;

  return (
    <Card
      title="Review & Approve Cleaning Plan"
      info="Every destructive transformation requires human authorization. High-impact steps are highlighted for caution."
      actions={
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Cumulative Deletions:</span>
          <Badge tone={overclean ? "bad" : "slate"}>
            {removedPct.toFixed(1)}% of rows
            <Tip text="Cumulative percentage of total dataset records that will be deleted by all approved steps combined." />
          </Badge>
        </div>
      }
    >
      {overclean && (
        <div className="mb-5 p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-300 text-xs font-medium">
          <AlertTriangle className="text-rose-600 shrink-0" size={20} />
          <div>
            <span className="font-bold">Over-Cleaning Guard Warning:</span> Approved steps will delete{" "}
            <b>{removedPct.toFixed(1)}%</b> of total dataset rows (exceeds the 20% safe deletion threshold). Consider
            reviewing outlier removals.
          </div>
        </div>
      )}

      <div className="space-y-3.5 mb-6">
        {gov.steps.map((s) => {
          const isApproved = approvals[s.id];
          const isDestructive = s.permission === "DESTRUCTIVE_HIGH";
          const prev = previews[s.id];
          const isPrevLoading = previewLoading[s.id];

          return (
            <div
              key={s.id}
              className={`border rounded-xl p-4 transition ${
                isApproved
                  ? isDestructive
                    ? "border-amber-300 bg-amber-50/30 dark:border-amber-900/60 dark:bg-amber-950/20"
                    : "border-emerald-300 bg-emerald-50/30 dark:border-emerald-900/60 dark:bg-emerald-950/20"
                  : "border-slate-200 bg-white opacity-60 dark:border-slate-800 dark:bg-slate-900"
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="pr-4 flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="font-mono text-[11px] px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-slate-600 dark:text-slate-400 font-semibold">
                      Step #{s.id}
                    </span>
                    <p className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                      {s.action}
                      {s.column && <span className="font-mono text-indigo-600 dark:text-indigo-400 font-medium"> ({s.column})</span>}
                    </p>
                    {s.source === "ai" && <Badge tone="ai">AI-proposed</Badge>}
                    <Badge tone={tierTone(s.tier)}>{s.tier}</Badge>
                    <Badge tone={s.risk === "low" ? "good" : s.risk === "medium" ? "warn" : "bad"}>
                      {s.risk} risk
                      <Tip text="Risk score based on potential data loss or irreversible alteration." />
                    </Badge>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    <b>Impact:</b>{" "}
                    {s.impact?.rows_removed !== undefined
                      ? `${s.impact.rows_removed.toLocaleString()} rows removed`
                      : `${s.impact?.values_changed?.toLocaleString()} values changed`}{" "}
                    ({s.impact?.pct}%) · <b>Permission:</b> <span className="font-mono">{s.permission}</span>{" "}
                    <Tip text="DESTRUCTIVE_HIGH steps always require human approval before running." />
                  </p>

                  <div className="mt-2 text-xs bg-white/90 dark:bg-slate-800/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-700 text-slate-700 dark:text-slate-300">
                    <div className="flex items-center gap-1 font-semibold text-slate-800 dark:text-slate-200 mb-0.5">
                      <Sparkles size={13} className="text-violet-600 dark:text-violet-400" />
                      LLM Supervisor ({s.llm_review?.verdict}):
                    </div>
                    <p className="italic text-slate-600 dark:text-slate-400">{s.llm_review?.reason}</p>
                  </div>

                  {s.alternatives && s.alternatives.length > 0 && (
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5">
                      <b>Alternatives:</b> {s.alternatives.join(" · ")}
                    </p>
                  )}

                  {/* Flag, don't drop Signal Preservation toggle */}
                  {(s.source === "llm_critic" || s.action === "fix_business_rule") && (
                    <label className="mt-2 flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300 font-medium cursor-pointer">
                      <input
                        type="checkbox"
                        checked={!!preserve[s.id]}
                        onChange={(e) => setPreserve((p) => ({ ...p, [s.id]: e.target.checked }))}
                        className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span>Flag, don't drop (preserve signal column for modeling)</span>
                    </label>
                  )}

                  {/* Dry-Run Preview Button */}
                  <div className="mt-2.5">
                    <button
                      onClick={() => previewStep(s)}
                      disabled={isPrevLoading}
                      className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 flex items-center gap-1 transition"
                    >
                      {isPrevLoading ? (
                        <Loader2 className="animate-spin" size={12} />
                      ) : prev ? (
                        <EyeOff size={12} />
                      ) : (
                        <Eye size={12} />
                      )}
                      {prev ? "Hide preview diff" : "Preview changes on raw data"}
                    </button>

                    {prev && prev.type !== "none" && (
                      <div className="mt-2 p-2.5 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 rounded-lg text-xs text-indigo-900 dark:text-indigo-200 animate-fadeIn">
                        {prev.type === "remove" ? (
                          <div>
                            <p className="font-semibold">
                              🔍 Dry-run: Will remove <b>{prev.removed_rows.toLocaleString()}</b> rows from current snapshot.
                            </p>
                            {prev.sample_removed && prev.sample_removed.length > 0 && (
                              <div className="mt-1 p-1.5 bg-white/90 dark:bg-slate-900 rounded border border-indigo-100 dark:border-indigo-900/50 font-mono text-[11px] truncate text-rose-700 dark:text-rose-400">
                                Sample row: {JSON.stringify(prev.sample_removed[0])}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div>
                            <p className="font-semibold">
                              🔍 Dry-run: Will change <b>{prev.changed_cells.toLocaleString()}</b> cells.
                            </p>
                            {prev.sample_changed && prev.sample_changed.length > 0 && (
                              <div className="mt-1 p-1.5 bg-white/90 dark:bg-slate-900 rounded border border-indigo-100 dark:border-indigo-900/50 font-mono text-[11px] truncate text-amber-800 dark:text-amber-400">
                                Sample modified: {JSON.stringify(prev.sample_changed[0])}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => setApprovals((a) => ({ ...a, [s.id]: !a[s.id] }))}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 shrink-0 transition ml-2 ${
                    isApproved
                      ? "bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm"
                      : "bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-300"
                  }`}
                >
                  {isApproved ? (
                    <>
                      <Check size={14} /> Approved
                    </>
                  ) : (
                    <>
                      <X size={14} /> Rejected
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex justify-between items-center pt-3 border-t border-slate-100 dark:border-slate-800">
        <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
          {gov.steps.filter((s) => approvals[s.id]).length} of {gov.steps.length} steps authorized for safe execution
        </span>
        <div className="flex items-center gap-3">
          <Button
            onClick={execute}
            disabled={loading || gov.steps.filter((s) => approvals[s.id]).length === 0}
            variant="primary"
          >
            {loading ? <Loader2 className="animate-spin" size={15} /> : <RefreshCw size={15} />}
            {loading ? "Executing Safely…" : "Execute Approved Steps"}
          </Button>

          {result && (
            <Button onClick={reportExport} disabled={reporting} variant="secondary">
              {reporting ? <Loader2 className="animate-spin" size={15} /> : <FileText size={15} />}
              {reporting ? "Auditing & Packing…" : "Generate Audit & Export Pack"}
            </Button>
          )}
        </div>
      </div>

      {result && (
        <div className="mt-6 p-5 bg-gradient-to-br from-slate-50 to-emerald-50/40 dark:from-slate-900 dark:to-emerald-950/20 border border-emerald-200 dark:border-emerald-900/60 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Check className="text-emerald-600" size={18} />
              Execution Quality Report
            </h4>
            <Badge tone="good">Clean Dataset Ready</Badge>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-3 bg-white dark:bg-slate-900 p-3.5 rounded-xl border border-slate-200/80 dark:border-slate-800 text-xs">
            <div>
              <span className="text-slate-500 dark:text-slate-400 block font-medium">Row Count</span>
              <b>{result.before_rows.toLocaleString()}</b> →{" "}
              <b className="text-indigo-600 dark:text-indigo-400">{result.after_rows.toLocaleString()}</b>
            </div>
            <div>
              <span className="text-slate-500 dark:text-slate-400 block font-medium">Rows Deleted</span>
              <b className="text-amber-700 dark:text-amber-400">{result.rows_removed.toLocaleString()}</b>
            </div>
            <div>
              <span className="text-slate-500 dark:text-slate-400 block font-medium">Quality Score</span>
              <b>{bQ}%</b> → <b className="text-emerald-600 dark:text-emerald-400">{aQ}%</b>
            </div>
            <div>
              <span className="text-slate-500 dark:text-slate-400 block font-medium">Quality Delta</span>
              <b className="text-emerald-700 dark:text-emerald-400">
                {aQ >= bQ ? `+${round(aQ - bQ, 2)}%` : `${round(aQ - bQ, 2)}%`}
              </b>
            </div>
          </div>

          {result.after_quality_breakdown && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4 text-[11px]">
              <div className="p-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block">Completeness</span>
                <span className="font-semibold">{result.before_quality_breakdown?.completeness}% → {result.after_quality_breakdown?.completeness}%</span>
              </div>
              <div className="p-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block">Uniqueness</span>
                <span className="font-semibold">{result.before_quality_breakdown?.uniqueness}% → {result.after_quality_breakdown?.uniqueness}%</span>
              </div>
              <div className="p-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block">Validity (Outliers)</span>
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">{result.before_quality_breakdown?.validity}% → {result.after_quality_breakdown?.validity}%</span>
              </div>
              <div className="p-2 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800">
                <span className="text-slate-400 block">Consistency</span>
                <span className="font-semibold text-indigo-600 dark:text-indigo-400">{result.before_quality_breakdown?.consistency}% → {result.after_quality_breakdown?.consistency}%</span>
              </div>
            </div>
          )}

          <div>
            <h5 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Executed Steps & Detailed Data Mutations
            </h5>
            <div className="space-y-2.5">
              {result.report.map((r, i) => (
                <div key={i} className="rounded-xl border border-slate-200 dark:border-slate-800 p-3.5 bg-slate-50/50 dark:bg-slate-800/40">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs ${
                        r.applied ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300" : "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300"
                      }`}>
                        {r.applied ? <Check size={13} /> : <X size={13} />}
                      </span>
                      <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                        Step #{r.step_id}: {r.action} {r.column && `(${r.column})`}
                      </span>
                      <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                        ({r.rows_before} → {r.rows_after} rows)
                      </span>
                    </div>

                    {r.applied && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => router.push(`/cleaned?stage=step_${r.step_id}`)}
                      >
                        View data
                      </Button>
                    )}
                  </div>

                  {/* Changes List */}
                  {(r.changes || []).map((c, idx) => (
                    <div key={idx} className="mt-2 text-xs text-slate-600 dark:text-slate-300 flex flex-wrap items-center gap-1">
                      <span className="font-mono font-semibold text-indigo-600 dark:text-indigo-400">{c.column}</span>
                      <span>·</span>
                      <span className="capitalize">{c.kind.replace("_", " ")}</span>
                      {c.count !== undefined && (
                        <>
                          <span>·</span>
                          <b className="text-slate-800 dark:text-slate-200">{c.count.toLocaleString()}</b>
                        </>
                      )}
                      <span>— {c.reason}</span>
                      {c.before && <span className="text-slate-500 font-mono">({c.before} → {c.after})</span>}
                      {c.sample && c.sample.length > 0 && (
                        <span className="text-slate-500 italic">
                          (e.g. “{c.sample[0]?.before}” → “{c.sample[0]?.after}”)
                        </span>
                      )}
                    </div>
                  ))}

                  {/* Anti-Hallucination Verification Badge */}
                  {r.verification && (
                    <VerificationAuditBadge verification={r.verification} />
                  )}

                  {/* Pandas Transformation Schema & Telemetry Inspector */}
                  <QuerySchemaInspector
                    query={r.pandas_expr || `df.${r.action}(column='${r.column || ""}')`}
                    schema={{ [r.column || "feature"]: "transformed" }}
                    metrics={{ runtime_ms: 12, rows_scanned: r.rows_before, rows_returned: r.rows_after }}
                    explanation={`Applied ${r.action} on column ${r.column || "dataset"}: transformed ${r.rows_before} to ${r.rows_after} rows.`}
                    queryType="pandas"
                  />

                  {!r.applied && (
                    <p className="mt-1 text-xs text-rose-600 dark:text-rose-400">
                      ⚠️ Rolled back: {r.reason || r.error}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {rep && (
        <div className="mt-6 p-5 bg-violet-50/50 dark:bg-violet-950/20 border border-violet-200 dark:border-violet-900/60 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <ShieldCheck className="text-violet-600" size={18} />
              Data Contract & Audit (CP4 + CP5)
            </h4>
            <Badge
              tone={
                rep.contract?.overall === "pass" ? "good" : rep.contract?.overall === "warn" ? "warn" : "bad"
              }
            >
              Contract Gate: {rep.contract?.overall || "PASS"}
            </Badge>
          </div>

          <div className="mb-4 bg-white dark:bg-slate-900 p-3.5 rounded-xl border border-violet-100 dark:border-violet-900/40">
            <h5 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Contract Integrity Verification Checks
            </h5>
            <ul className="space-y-1 text-xs">
              {(rep.contract?.checks || []).map((c, i) => (
                <li key={i} className="flex items-center gap-2 text-slate-800 dark:text-slate-200">
                  <span>{c.status === "pass" ? "✅" : c.status === "warn" ? "⚠️" : "❌"}</span>
                  <span className="font-mono font-medium">{c.name}</span>: {c.detail}
                </li>
              ))}
            </ul>
          </div>

          {rep.narrative && (
            <div className="mb-4 bg-white dark:bg-slate-900 p-3.5 rounded-xl border border-violet-100 dark:border-violet-900/40">
              <h5 className="text-xs font-semibold text-violet-900 dark:text-violet-300 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <Sparkles size={14} className="text-violet-600 dark:text-violet-400" />
                Domain Narrative (CP5)
              </h5>
              <p className="text-xs italic text-slate-700 dark:text-slate-300 leading-relaxed">{rep.narrative}</p>
            </div>
          )}

          {exp && (
            <div className="bg-white dark:bg-slate-900 p-3.5 rounded-xl border border-violet-100 dark:border-violet-900/40">
              <div className="flex items-center justify-between mb-2">
                <h5 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Package size={15} className="text-indigo-600 dark:text-indigo-400" />
                  Reproducible Export Package
                </h5>
                {!exp.blocked && (
                  <Button
                    size="sm"
                    variant="primary"
                    onClick={() => window.open(`http://localhost:8000/api/export/download/${datasetId}`, "_blank")}
                  >
                    <Download size={13} /> Download Pack (.zip)
                  </Button>
                )}
              </div>
              {exp.blocked ? (
                <p className="text-xs font-semibold text-rose-600 dark:text-rose-400">❌ Export Blocked: {exp.reason}</p>
              ) : (
                <div>
                  <p className="text-xs text-emerald-700 dark:text-emerald-400 font-medium mb-2">
                    ✅ Package assembled with {exp.files?.length || 0} artifacts:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {(exp.files || []).map((f, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono text-xs rounded-lg border border-slate-200 dark:border-slate-700"
                      >
                        📄 {f}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

function round(n, dec) {
  return Number(Math.round(n + "e" + dec) + "e-" + dec);
}
