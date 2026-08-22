"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useDataset } from "../components/DatasetContext";
import { Card, Button, Badge } from "../components/ui";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { FeatureGuide } from "../components/FeatureGuide";
import { WorkflowStepGuide } from "../components/WorkflowStepGuide";
import { Database, Brain, Wrench, Shield, CheckCircle2, Loader2, ArrowRight, Terminal } from "lucide-react";
import ReviewSection from "../ReviewSection";
import PipelineCodeModal from "../components/PipelineCodeModal";

const STAGES = [
  { name: "Ingest & Profile", icon: Database, action: "upload" },
  { name: "Understand", icon: Brain, action: "understand" },
  { name: "Plan", icon: Wrench, action: "plan" },
  { name: "Govern", icon: Shield, action: "govern" },
  { name: "Review & Execute", icon: CheckCircle2, action: "none" },
];

const STAGE_INFO = {
  1: "Profiling: computes stats, nulls, duplicates, outliers, and masks PII. No data is changed.",
  2: "Understand: the AI reads column names and statistical samples to generate a plain-language data dictionary.",
  3: "Plan: proposes AI + rule cleaning steps with exact impact; code computes numbers, AI reviews risks.",
  4: "Govern: classifies each step into an Ask-vs-Act governance matrix; destructive steps require your approval.",
};

export default function CleaningStudioPage() {
  const { id } = useDataset();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [showCodeModal, setShowCodeModal] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetch(`http://localhost:8000/api/status/${id}`)
      .then((r) => r.json())
      .then((s) => {
        setCurrentStep(s.governance ? 4 : s.plan ? 3 : s.dictionary ? 2 : 1);
      })
      .catch((err) => console.error("Failed fetching status:", err));
  }, [id]);

  const runNext = async (action, idx) => {
    if (!id) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch(`http://localhost:8000/api/${action}/${id}`, { method: "POST" });
      if (!res.ok) throw new Error(`Stage failed: ${res.statusText}`);
      setCurrentStep(idx + 1);
    } catch (e) {
      console.error(e);
      setErrorMsg(e.message || `Stage execution failed`);
    } finally {
      setLoading(false);
    }
  };

  if (!id) {
    return (
      <main className="p-8 text-center">
        <Card title="No Dataset Selected">
          <p className="text-xs text-slate-500 mb-4">Please upload or select a dataset on the Overview page to enter Cleaning Studio.</p>
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
          { href: "/cleaning", label: "Data Pipeline" },
          { label: "Cleaning Studio" },
        ]}
      />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">Cleaning Studio & Supervised Execution</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Governed data transformation pipeline. Propose, preview, approve, and execute deterministic cleaning.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="secondary" onClick={() => setShowCodeModal(true)}>
            <Terminal size={13} /> Export Code
          </Button>
          <Link href="/cleaned">
            <Button size="sm" variant="primary">
              Cleaned Data <ArrowRight size={13} />
            </Button>
          </Link>
        </div>
      </div>

      <PipelineCodeModal datasetId={id} isOpen={showCodeModal} onClose={() => setShowCodeModal(false)} />

      {/* Non-Sophisticated Workflow Guide */}
      <WorkflowStepGuide
        currentStepId="cleaning"
        pageTitle="Cleaning Studio & Supervised Execution"
        reason="Raw data is almost always messy (duplicates, negative values, missing cells, formatting mistakes). This page systematically scans and cleans your active dataset. No rows or columns are deleted without your explicit review and approval."
        priorStepText="Make sure you have an active dataset loaded from Mission Control (Upload CSV) or Market Radar (Generate 12-month dataset)."
        priorStepHref="/"
        currentActionSteps={[
          { title: "Understand & Semantic Types", detail: "Click 'Execute: Understand' to translate raw abbreviations into human-readable definitions." },
          { title: "Generate Cleaning Plan", detail: "Click 'Execute: Plan' to see AI proposed fixes for duplicates, missing values, and outliers." },
          { title: "Review Governance & Execute", detail: "Click 'Execute: Govern', review the proposed transformations, and apply the fixes." }
        ]}
        nextStepText="After cleaning your data, proceed to Visual EDA to inspect statistical charts, distributions, and correlations."
        nextStepHref="/eda"
        jargonBuster={[
          { term: "Imputation", meaning: "Filling in empty or missing numbers using the column's average or median instead of dropping rows." },
          { term: "IQR Outlier", meaning: "Extreme statistical values that fall far outside normal boundaries (e.g. a $10,000 unit price in a $50 product list)." },
          { term: "Governance Matrix (Ask vs Act)", meaning: "A safety check: non-destructive actions are auto-fixed (Act), while permanent row removals require user confirmation (Ask)." },
          { term: "Deterministic Transformation", meaning: "Clean code scripts (Python / Pandas) that run identically every time without unpredictable AI hallucination." }
        ]}
      />

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-300 rounded-xl text-xs font-semibold">
          ⚠️ {errorMsg}
        </div>
      )}

      {/* Stepper Card */}
      <Card
        title="Pipeline Progression"
        info="Each stage runs an isolated, supervised step. Destructive actions always require your human approval."
        actions={<Badge tone="slate">Dataset: {id}</Badge>}
        pad={false}
      >
        <div className="px-5 py-4">
          <div className="flex items-center">
            {STAGES.map((s, i) => (
              <div key={i} className="flex flex-1 items-center last:flex-none">
                <div className="flex flex-col items-center">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all ${
                      i < currentStep
                        ? "border-emerald-500 bg-emerald-500 text-white shadow-sm"
                        : i === currentStep
                        ? "border-indigo-600 bg-indigo-600 text-white ring-4 ring-indigo-100 dark:ring-indigo-900/50 shadow-md"
                        : "border-slate-200 bg-white text-slate-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-500"
                    }`}
                  >
                    {i < currentStep ? <CheckCircle2 size={18} /> : <s.icon size={16} />}
                  </div>
                  <span className="mt-1.5 whitespace-nowrap text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                    {s.name}
                  </span>
                </div>
                {i < STAGES.length - 1 && (
                  <div
                    className={`mx-2 mb-4 h-0.5 flex-1 rounded transition-colors ${
                      i < currentStep ? "bg-emerald-500" : "bg-slate-200 dark:bg-slate-800"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>

          {currentStep > 0 && currentStep < 5 && STAGE_INFO[currentStep] && (
            <div className="mt-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 p-3 text-xs text-slate-600 dark:text-slate-300 border border-slate-100 dark:border-slate-800/80 flex items-center gap-2">
              <span className="font-bold text-indigo-600 dark:text-indigo-400 shrink-0">Stage Context:</span>
              <span>{STAGE_INFO[currentStep]}</span>
            </div>
          )}
        </div>

        <footer className="flex h-12 items-center justify-end border-t border-slate-100 px-5 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 rounded-b-2xl">
          {currentStep > 0 && currentStep < 4 && (
            <Button
              size="sm"
              disabled={loading}
              onClick={() => runNext(STAGES[currentStep].action, currentStep)}
            >
              {loading && <Loader2 className="animate-spin" size={13} />}
              {loading ? "Running…" : `Execute: ${STAGES[currentStep].name}`}
            </Button>
          )}
        </footer>
      </Card>

      {/* Review & Approvals */}
      {currentStep >= 4 && <ReviewSection datasetId={id} />}
    </main>
  );
}
