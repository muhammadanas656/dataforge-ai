"use client";
import { useEffect, useState } from "react";
import { Card, StatTile, Badge, Button } from "../components/ui";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { Brain, Activity, Database, TrendingUp, Sparkles, Loader2, CheckCircle2 } from "lucide-react";
import { WorkflowStepGuide } from "../components/WorkflowStepGuide";

export default function LearningPage() {
  const [stats, setStats] = useState(null);
  const [kg, setKg] = useState(null);
  const [distilling, setDistilling] = useState(false);
  const [distillStatus, setDistillStatus] = useState("");

  const load = () => {
    fetch("http://localhost:8000/api/learning/stats")
      .then((r) => r.json())
      .then(setStats)
      .catch((e) => console.warn(e));

    fetch("http://localhost:8000/api/learning/knowledge-graph")
      .then((r) => r.json())
      .then(setKg)
      .catch((e) => console.warn(e));
  };

  useEffect(() => {
    load();
  }, []);

  const handleForceDistill = async (taskType) => {
    setDistilling(true);
    setDistillStatus("");
    try {
      const res = await fetch("http://localhost:8000/api/learning/distill", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_type: taskType }),
      });
      const data = await res.json();
      setDistillStatus(data.status === "trained" ? "Local model trained successfully!" : "Need at least 15 recorded interactions.");
      load();
    } catch (e) {
      setDistillStatus("Distillation failed: " + e.message);
    } finally {
      setDistilling(false);
    }
  };

  if (!stats) {
    return (
      <main className="mx-auto max-w-6xl p-8 text-center text-xs text-slate-500">
        <Loader2 className="animate-spin inline-block mr-2" size={16} />
        Loading autonomy & distillation telemetry…
      </main>
    );
  }

  const dist = stats.distillation || {};
  const graph = stats.knowledge_graph || {};

  return (
    <main className="mx-auto max-w-6xl space-y-5 px-6 py-6 overflow-x-clip">
      <Breadcrumbs
        crumbs={[
          { href: "/", label: "Home" },
          { href: "/learning", label: "System & Autonomy" },
          { label: "Learning Activity" },
        ]}
      />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Brain size={22} className="text-indigo-600 dark:text-indigo-400" />
            Autonomous Learning & Distillation Engine
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Teacher-student adaptive delegation: The LLM teaches, local models distill, and token dependency shrinks to zero
          </p>
        </div>

        <Badge tone="ai">Compounding Intelligence Active</Badge>
      </div>

      {/* Non-Sophisticated Workflow Guide */}
      <WorkflowStepGuide
        currentStepId="overview"
        pageTitle="Autonomous Learning & Distillation Engine"
        reason="This engine makes DataForge AI faster and cheaper over time. Every time you clean a dataset, the system remembers the approved rules and trains small local AI models so future identical columns cost 0 tokens and run in 0.1ms."
        priorStepText="Run cleaning or EDA on at least 1-2 datasets so the system has real examples to learn from."
        priorStepHref="/cleaning"
        currentActionSteps={[
          { title: "Inspect Knowledge Graph", detail: "See which column names (e.g. 'retail_price', 'cust_id') the system has memorized." },
          { title: "Review Distillation Progress", detail: "Check how close the system is to training a local model (needs ~15 examples)." },
          { title: "Force Distill (When Ready)", detail: "Click 'Train Local Model' to convert recorded LLM steps into an ultra-fast local classifier." }
        ]}
        nextStepText="Return to Mission Control to process new datasets using your distilled 0-token models."
        nextStepHref="/"
        jargonBuster={[
          { term: "Knowledge Distillation", meaning: "Training a small, free, ultra-fast local machine learning model to mimic a large expensive cloud LLM." },
          { term: "Teacher-Student Delegation", meaning: "The big cloud AI acts as the 'teacher' solving hard problems, while the local code is the 'student' taking notes." },
          { term: "Knowledge Graph", meaning: "A structured memory network mapping column names to their verified data types and cleaning rules." },
          { term: "0-Token Resolution", meaning: "Solving a data cleaning problem locally on your machine without making any API calls to OpenAI/Groq." }
        ]}
      />

      {/* Summary Stat Tiles */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatTile
          label="Distilled Models"
          value={dist.total_models || 0}
          info="Local random forest classifiers trained directly from LLM interactions."
        />
        <StatTile
          label="Learned Column Schemas"
          value={graph.columns_learned || 0}
          info="Column semantics accumulated and resolved across processed datasets."
        />
        <StatTile
          label="Learned Cleaning Rules"
          value={graph.cleaning_rules || 0}
          info="High-conviction data transformations cached for 0-token instant reuse."
        />
        <StatTile
          label="Datasets Processed"
          value={graph.datasets_processed || 0}
          info="Total learning opportunities compounding cross-dataset memory."
        />
      </div>

      {/* Distillation Progress Card */}
      <Card
        title="Local Model Distillation Progress"
        info="When 15 interactions are recorded for a task type, DataForge AI automatically trains a local Scikit-Learn model to handle future queries at 0 tokens."
        actions={
          <Button
            size="sm"
            variant="secondary"
            onClick={() => handleForceDistill("semantic_type")}
            disabled={distilling}
          >
            {distilling ? <Loader2 className="animate-spin" size={13} /> : <Sparkles size={13} />}
            {distilling ? "Training..." : "Trigger Model Distillation"}
          </Button>
        }
      >
        <div className="space-y-3 text-xs">
          {distillStatus && (
            <div className="p-2.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 text-indigo-900 dark:text-indigo-200">
              {distillStatus}
            </div>
          )}

          {Object.entries(dist.examples_recorded || {}).length === 0 ? (
            <p className="text-slate-500 italic py-2">
              No task examples recorded yet. Run profiling or cleaning in the studio to start autonomous distillation.
            </p>
          ) : (
            <div className="space-y-3">
              {Object.entries(dist.examples_recorded).map(([task, count]) => {
                const isTrained = (dist.tasks_trained || []).includes(task);
                const progress = Math.min((count / 15) * 100, 100);
                return (
                  <div key={task} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-slate-800 dark:text-slate-200 capitalize">
                        {task.replace(/_/g, " ")}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-500 font-mono text-[11px]">{count}/15 examples</span>
                        {isTrained ? (
                          <Badge tone="good">✅ Local Model Active (0 Tokens)</Badge>
                        ) : (
                          <Badge tone="warn">Gathering Examples</Badge>
                        )}
                      </div>
                    </div>
                    <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${isTrained ? "bg-emerald-500" : "bg-indigo-600"}`}
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </Card>

      {/* Cross-Dataset Knowledge Graph */}
      <Card
        title="Cross-Dataset Knowledge Graph"
        info="Accumulated cross-domain column semantics and learned transformations."
      >
        <div className="grid gap-4 md:grid-cols-2 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700 space-y-2">
            <h4 className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <Database size={14} className="text-indigo-600" /> Domains Encountered
            </h4>
            {kg && Object.keys(kg.domains || {}).length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {Object.keys(kg.domains).map((d) => (
                  <Badge key={d} tone="info">{d}</Badge>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 italic">No specific domains categorized yet.</p>
            )}
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/70 dark:border-slate-700 space-y-2">
            <h4 className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <TrendingUp size={14} className="text-emerald-600" /> Recent Column Semantics
            </h4>
            {kg && Object.keys(kg.columns || {}).length > 0 ? (
              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {Object.entries(kg.columns).slice(-6).map(([name, info]) => (
                  <div key={name} className="flex items-center justify-between text-[11px] p-1.5 rounded bg-white dark:bg-slate-900 border border-slate-200/50 dark:border-slate-800">
                    <span className="font-mono font-bold text-slate-700 dark:text-slate-300">{name}</span>
                    <div className="flex gap-1">
                      {Object.keys(info.semantic_types || {}).map((t) => (
                        <Badge key={t} tone="slate">{t}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 italic">No column patterns recorded yet.</p>
            )}
          </div>
        </div>
      </Card>
    </main>
  );
}
