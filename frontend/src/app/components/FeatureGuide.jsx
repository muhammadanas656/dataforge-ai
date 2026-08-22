"use client";
import { useState } from "react";
import { HelpCircle, ChevronDown, ChevronUp, Sparkles, CheckCircle2, Lightbulb } from "lucide-react";

export function FeatureGuide({ title, description, whyUse, steps = [], examples = [] }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-2xl border border-indigo-100 bg-gradient-to-r from-indigo-50/80 to-violet-50/60 dark:border-indigo-900/50 dark:from-indigo-950/20 dark:to-violet-950/20 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between px-4 py-2.5 text-left text-xs font-semibold text-indigo-900 hover:text-indigo-700 dark:text-indigo-200 dark:hover:text-indigo-100 transition"
      >
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm">
            <HelpCircle size={12} />
          </span>
          <span>How to use {title} · Plain English Guide & Purpose</span>
        </div>
        <div className="flex items-center gap-1 text-[11px] font-medium text-indigo-600 dark:text-indigo-400">
          <span>{open ? "Hide Guide" : "View Instructions"}</span>
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </button>

      {open && (
        <div className="border-t border-indigo-100/80 px-4 py-3.5 dark:border-indigo-900/40 text-xs space-y-3 animate-fadeIn">
          {/* Plain English Purpose */}
          <div className="space-y-1">
            <h4 className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <Sparkles size={13} className="text-indigo-600 dark:text-indigo-400" />
              What this feature does (In Simple Words)
            </h4>
            <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
              {description}
            </p>
          </div>

          {/* Why to use it */}
          {whyUse && (
            <div className="rounded-xl bg-white/80 p-2.5 dark:bg-slate-900/80 border border-indigo-100/60 dark:border-indigo-900/40">
              <h5 className="font-bold text-indigo-900 dark:text-indigo-200 flex items-center gap-1 text-[11px] mb-0.5">
                <Lightbulb size={12} className="text-amber-500" />
                Why you should use this
              </h5>
              <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                {whyUse}
              </p>
            </div>
          )}

          {/* 3 Step Instructions */}
          {steps.length > 0 && (
            <div className="space-y-1.5 pt-1">
              <h5 className="font-bold text-slate-800 dark:text-slate-200 text-[11px]">
                Simple Step-by-Step Instructions:
              </h5>
              <div className="grid gap-2 sm:grid-cols-3">
                {steps.map((step, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 space-y-1"
                  >
                    <div className="flex items-center gap-1.5">
                      <span className="flex h-4 w-4 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 text-[10px] font-bold">
                        {idx + 1}
                      </span>
                      <span className="font-bold text-[11px] text-slate-800 dark:text-slate-200">
                        {step.title}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-normal">
                      {step.detail}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Examples */}
          {examples.length > 0 && (
            <div className="pt-1">
              <span className="text-[11px] font-bold text-slate-700 dark:text-slate-300 mr-2">
                Helpful Examples:
              </span>
              <div className="inline-flex flex-wrap gap-1.5 mt-1">
                {examples.map((ex, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded-lg bg-indigo-100/60 text-indigo-900 dark:bg-indigo-950/60 dark:text-indigo-200 font-mono text-[10px]"
                  >
                    "{ex}"
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
