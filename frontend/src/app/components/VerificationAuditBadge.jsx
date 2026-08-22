"use client";
import { useState } from "react";
import { ShieldCheck, AlertTriangle, ChevronDown, ChevronUp, CheckCircle2, XCircle } from "lucide-react";
import { Badge } from "./ui";

export default function VerificationAuditBadge({ verification, narrativeVerification }) {
  const [open, setOpen] = useState(false);

  if (!verification && !narrativeVerification) return null;

  const isVerified = (verification?.verified !== false) && (narrativeVerification?.verified !== false);
  const checks = verification?.checks || [];

  return (
    <div className="mt-2.5 rounded-xl border border-slate-200/80 bg-white dark:border-slate-800 dark:bg-slate-900 shadow-sm overflow-hidden text-xs">
      <div 
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between p-2.5 cursor-pointer select-none hover:bg-slate-50 dark:hover:bg-slate-800/50 transition"
      >
        <div className="flex items-center gap-2">
          {isVerified ? (
            <ShieldCheck size={15} className="text-emerald-600 dark:text-emerald-400" />
          ) : (
            <AlertTriangle size={15} className="text-amber-500" />
          )}
          <span className="font-semibold text-slate-800 dark:text-slate-200 text-[11px]">
            {isVerified ? "Anti-Hallucination Verified" : "Verification Warning Detected"}
          </span>
          <Badge tone={isVerified ? "good" : "bad"}>
            {isVerified ? "100% Ground-Truth Match" : "Flagged"}
          </Badge>
        </div>

        <div className="flex items-center gap-1 text-[10px] text-slate-500">
          <span>{open ? "Hide Audit Details" : "View Mathematical Proof"}</span>
          {open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
        </div>
      </div>

      {open && (
        <div className="p-3 border-t border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-950/40 space-y-2.5 text-[11px]">
          {/* Step / Chart Fidelity Checks */}
          {checks.length > 0 && (
            <div>
              <span className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                Invariant & Distribution Checks:
              </span>
              <div className="space-y-1">
                {checks.map((chk, i) => (
                  <div key={i} className="flex items-center justify-between p-1.5 rounded bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800">
                    <span className="font-medium text-slate-700 dark:text-slate-300 capitalize">{chk.name?.replace(/_/g, " ")}</span>
                    <div className="flex items-center gap-1.5">
                      {chk.distance !== undefined && <span className="text-[10px] text-slate-500 font-mono">dist={chk.distance}</span>}
                      {chk.passed ? (
                        <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-semibold text-[10px]">
                          <CheckCircle2 size={12} /> Passed
                        </span>
                      ) : (
                        <span className="text-rose-600 flex items-center gap-1 font-semibold text-[10px]">
                          <XCircle size={12} /> {chk.reason || "Failed"}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Narrative Grounding Audit */}
          {narrativeVerification && (
            <div className="p-2 rounded bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50">
              <span className="font-bold text-indigo-900 dark:text-indigo-200 block mb-1">
                Narrative Grounding Integrity:
              </span>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-[10px]">
                {narrativeVerification.verified 
                  ? "All numerical claims and entity rankings were mathematically grounded against dataframe values."
                  : `Discrepancy detected in narrative claims: ${narrativeVerification.unverified_numbers?.join(", ") || "unverified values"}.`}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
