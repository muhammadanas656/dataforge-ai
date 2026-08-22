"use client";
import { useState } from "react";
import Link from "next/link";
import {
  Compass,
  Database,
  Wrench,
  BarChart3,
  Bot,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Sparkles,
  BookOpen,
  Info
} from "lucide-react";

export const PIPELINE_STEPS = [
  {
    step: 1,
    id: "research",
    label: "1. Market Radar",
    short: "Market Radar",
    href: "/research",
    icon: Compass,
    summary: "Discover high-margin niches & validate demand with live Reddit & competitor data."
  },
  {
    step: 2,
    id: "overview",
    label: "2. Mission Control",
    short: "Ingest & Status",
    href: "/",
    icon: Database,
    summary: "Upload raw CSV files or view profile quality health for your active dataset."
  },
  {
    step: 3,
    id: "cleaning",
    label: "3. Cleaning Studio",
    short: "Cleaning Studio",
    href: "/cleaning",
    icon: Wrench,
    summary: "Review duplicates, fix negative numbers, fill missing values, and verify transformations."
  },
  {
    step: 4,
    id: "eda",
    label: "4. Visual EDA",
    short: "Visual EDA",
    href: "/eda",
    icon: BarChart3,
    summary: "Inspect distributions, correlations, box plots, and export reproducible Jupyter notebooks."
  },
  {
    step: 5,
    id: "analyst",
    label: "5. AI Analyst",
    short: "AI Copilot",
    href: "/analyst",
    icon: Bot,
    summary: "Ask plain-English questions, get instant SQL/Python calculations & streaming chart answers."
  }
];

export function WorkflowStepGuide({
  currentStepId = "overview",
  pageTitle,
  reason,
  priorStepText,
  priorStepHref,
  currentActionSteps = [],
  nextStepText,
  nextStepHref,
  jargonBuster = []
}) {
  const [open, setOpen] = useState(false);

  const currentIdx = PIPELINE_STEPS.findIndex((s) => s.id === currentStepId);
  const currentStep = PIPELINE_STEPS[currentIdx] || PIPELINE_STEPS[1];

  return (
    <div className="rounded-2xl border border-indigo-200/80 bg-gradient-to-br from-indigo-50/90 via-slate-50 to-purple-50/60 dark:border-indigo-900/60 dark:from-indigo-950/30 dark:via-slate-900 dark:to-purple-950/20 shadow-sm overflow-hidden text-xs">
      {/* Top Interactive Workflow Pipeline Stepper */}
      <div className="flex flex-wrap items-center justify-between border-b border-indigo-100 dark:border-indigo-900/40 px-4 py-2.5 bg-white/70 dark:bg-slate-900/70">
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 scrollbar-none">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1 hidden sm:inline">
            Workflow:
          </span>
          {PIPELINE_STEPS.map((s, idx) => {
            const Icon = s.icon;
            const isCurrent = s.id === currentStepId;
            const isPast = idx < currentIdx;

            return (
              <div key={s.id} className="flex items-center">
                <Link
                  href={s.href}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-xl font-semibold text-[11px] transition ${
                    isCurrent
                      ? "bg-indigo-600 text-white shadow-sm font-bold scale-105"
                      : isPast
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900/50 hover:bg-emerald-100"
                      : "text-slate-500 hover:text-slate-800 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                  }`}
                  title={s.summary}
                >
                  <Icon size={12} />
                  <span>{s.short}</span>
                  {isPast && <CheckCircle2 size={10} className="text-emerald-600 dark:text-emerald-400" />}
                </Link>
                {idx < PIPELINE_STEPS.length - 1 && (
                  <span className="text-slate-300 dark:text-slate-700 mx-1">→</span>
                )}
              </div>
            );
          })}
        </div>

        {/* Toggle Guide Details */}
        <button
          onClick={() => setOpen(!open)}
          className="flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 transition ml-auto mt-1 sm:mt-0"
        >
          <HelpCircle size={13} />
          <span>{open ? "Hide Workflow Instructions" : "How this step works & Prior Checklist"}</span>
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* Expanded Workflow & Step Instructions */}
      {open && (
        <div className="p-4 space-y-4 animate-fadeIn">
          {/* Reason / Purpose in Plain English */}
          <div className="space-y-1">
            <h4 className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5 text-xs">
              <Sparkles size={14} className="text-indigo-600 dark:text-indigo-400" />
              1. What is the Purpose of this Page? (Plain English)
            </h4>
            <p className="text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
              {reason}
            </p>
          </div>

          {/* 2-Column Checklist: Prior vs Next */}
          <div className="grid gap-3 sm:grid-cols-2">
            {/* What to do prior */}
            <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200/80 dark:bg-amber-950/20 dark:border-amber-900/40 space-y-1.5">
              <span className="font-bold text-amber-900 dark:text-amber-200 flex items-center gap-1.5 text-[11px]">
                <ArrowLeft size={13} /> What you should have done before this step:
              </span>
              <p className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                {priorStepText || "No strict prerequisite. You can start directly on this screen."}
              </p>
              {priorStepHref && (
                <Link
                  href={priorStepHref}
                  className="inline-flex items-center gap-1 font-bold text-amber-800 dark:text-amber-300 hover:underline text-[11px] pt-1"
                >
                  ← Go back to prerequisite step
                </Link>
              )}
            </div>

            {/* Where to go next */}
            <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-200/80 dark:bg-emerald-950/20 dark:border-emerald-900/40 space-y-1.5">
              <span className="font-bold text-emerald-900 dark:text-emerald-200 flex items-center gap-1.5 text-[11px]">
                <ArrowRight size={13} /> Where to go after finishing here:
              </span>
              <p className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                {nextStepText || "Proceed to the next module in the top navigation bar."}
              </p>
              {nextStepHref && (
                <Link
                  href={nextStepHref}
                  className="inline-flex items-center gap-1 font-bold text-emerald-700 dark:text-emerald-300 hover:underline text-[11px] pt-1"
                >
                  Proceed to next step →
                </Link>
              )}
            </div>
          </div>

          {/* Action Steps on this current page */}
          {currentActionSteps.length > 0 && (
            <div className="space-y-1.5">
              <h5 className="font-bold text-slate-800 dark:text-slate-200 text-[11px] flex items-center gap-1">
                <CheckCircle2 size={13} className="text-indigo-600" />
                Action Checklist for this Page:
              </h5>
              <div className="grid gap-2 sm:grid-cols-3">
                {currentActionSteps.map((step, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 space-y-1"
                  >
                    <div className="flex items-center gap-1.5">
                      <span className="flex h-4 w-4 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 text-[10px] font-bold">
                        {idx + 1}
                      </span>
                      <span className="font-bold text-[11px] text-slate-900 dark:text-slate-100">
                        {step.title}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-600 dark:text-slate-400 leading-normal">
                      {step.detail}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Jargon Buster / Demystifying complex technical terms */}
          {jargonBuster.length > 0 && (
            <div className="pt-2 border-t border-indigo-100 dark:border-indigo-900/40 space-y-1.5">
              <h5 className="font-bold text-slate-800 dark:text-slate-200 text-[11px] flex items-center gap-1">
                <BookOpen size={12} className="text-violet-600" />
                Jargon Buster (Plain English Glossary for this Screen):
              </h5>
              <div className="grid gap-2 sm:grid-cols-2">
                {jargonBuster.map((term, i) => (
                  <div
                    key={i}
                    className="p-2 rounded-lg bg-white/70 dark:bg-slate-900/70 border border-slate-200/60 dark:border-slate-800 text-[10px]"
                  >
                    <b className="text-indigo-700 dark:text-indigo-300">{term.term}:</b>{" "}
                    <span className="text-slate-600 dark:text-slate-400">{term.meaning}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
