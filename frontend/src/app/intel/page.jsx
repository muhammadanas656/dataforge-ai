"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, Button, Badge } from "../components/ui";
import { useJob } from "../hooks/useJob";
import { WorkflowStepGuide } from "../components/WorkflowStepGuide";
import { Radar, Loader2, Globe, Sparkles, ArrowRight, ShieldCheck, TrendingUp, Layers } from "lucide-react";

export default function IntelPage() {
  const [list, setList] = useState([]);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");

  const job = useJob("intel_track", { url: "", name: "" }, { autoStart: false });

  const loadList = () => {
    fetch("http://localhost:8000/api/intel/list")
      .then((r) => r.json())
      .then((d) => setList(d.competitors || []))
      .catch((e) => console.warn("Failed loading competitors:", e));
  };

  useEffect(() => {
    loadList();
  }, []);

  useEffect(() => {
    if (job.status === "done") {
      loadList();
    }
  }, [job.status]);

  return (
    <main className="mx-auto max-w-6xl space-y-5 px-6 py-6 overflow-x-clip">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Radar size={22} className="text-indigo-600 dark:text-indigo-400" />
            Competitor Intelligence & Price Tracking
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Automated catalog scraping, pricing fluctuation monitoring, aspect review NLP, and feature gap matrices
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone="ai">Dynamic Scraping Engine</Badge>
        </div>
      </div>

      {/* Non-Sophisticated Workflow Guide */}
      <WorkflowStepGuide
        currentStepId="research"
        pageTitle="Competitor Intelligence & Price Tracking"
        reason="This screen allows you to track and scrape real competitor websites. It monitors what products they sell, tracks their live prices over time, and analyzes their customer reviews to highlight weaknesses you can exploit."
        priorStepText="Use Market Radar first to discover which competitors exist in your niche before adding their URLs here."
        priorStepHref="/research"
        currentActionSteps={[
          { title: "Enter Competitor Info", detail: "Type the brand name and paste their store or product catalog website URL." },
          { title: "Trigger Scrape & Track", detail: "Click 'Track Competitor' to extract pricing ranges, SKU lists, and reviews." },
          { title: "Review Feature Matrix", detail: "Compare features side-by-side to find missing capabilities or uncompetitive pricing." }
        ]}
        nextStepText="Use competitor price ranges to calibrate unit economics in Market Radar or inject realistic datasets into Cleaning Studio."
        nextStepHref="/research"
        jargonBuster={[
          { term: "Catalog Scraping", meaning: "Automatically reading a competitor's public webpage to find product names, prices, and stock levels." },
          { term: "Aspect Review NLP", meaning: "Using natural language processing to separate customer reviews into specific categories like 'Quality', 'Shipping', or 'Customer Service'." },
          { term: "Feature Gap Matrix", meaning: "A comparison table showing which features your product has that competitors lack." },
          { term: "Price Elasticity", meaning: "How sensitive customers are to price increases or discounts in this market." }
        ]}
      />

      {/* Competitor Tracker Launcher */}
      <Card
        title="Track a New Competitor Catalog"
        info="Scrapes live product offerings, baseline pricing, and ratings to establish a competitive benchmark."
        actions={<Badge tone="good">Continuous Benchmarks</Badge>}
      >
        <div className="space-y-3 text-xs">
          <div className="flex flex-wrap gap-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Competitor Brand (e.g. Manduka Yoga, Keychron, Bose)"
              className="h-9 w-full sm:w-56 rounded-xl border border-slate-200 px-3 text-xs focus:ring-2 focus:ring-indigo-500 dark:border-slate-800 dark:bg-slate-900 text-slate-900 dark:text-slate-100"
            />
            <div className="relative flex-1 min-w-[240px]">
              <Globe size={14} className="absolute left-3 top-2.5 text-slate-400" />
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://competitor.com/catalog or https://amazon.com/store/..."
                className="h-9 w-full rounded-xl border border-slate-200 pl-9 pr-3 text-xs focus:ring-2 focus:ring-indigo-500 dark:border-slate-800 dark:bg-slate-900 text-slate-900 dark:text-slate-100"
              />
            </div>
            <Button
              variant="primary"
              size="md"
              onClick={() => job.start({ name: name.trim(), url: url.trim() })}
              disabled={job.status === "running" || !url.trim()}
            >
              {job.status === "running" ? <Loader2 className="animate-spin" size={14} /> : <Sparkles size={14} />}
              {job.status === "running" ? "Crawling & Ingesting..." : "Track Competitor"}
            </Button>
          </div>

          {job.status === "running" && (
            <div className="p-3 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/50 flex items-center gap-2 text-indigo-900 dark:text-indigo-200">
              <Loader2 className="animate-spin text-indigo-600" size={14} />
              <span>{job.progressMessage || "Extracting catalog schemas and generating baseline price timeline..."}</span>
            </div>
          )}

          {job.status === "done" && job.result && (
            <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/60 flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-900 dark:text-emerald-200 font-semibold">
                <ShieldCheck size={16} className="text-emerald-600" />
                <span>Successfully tracked <b>{job.result.name}</b> ({job.result.products} products cataloged).</span>
              </div>
              <Link href={`/intel/${job.result.id}`}>
                <Button size="sm" variant="primary">
                  View Competitor Profile <ArrowRight size={12} />
                </Button>
              </Link>
            </div>
          )}
        </div>
      </Card>

      {/* Tracked Competitors Directory */}
      <Card
        title="Tracked Competitors & Benchmarks"
        info="Monitored brand catalogs with automated price history and feature gap tracking."
        pad={false}
      >
        <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
          {list.map((c) => (
            <Link
              key={c.id}
              href={`/intel/${c.id}`}
              className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition"
            >
              <div className="space-y-0.5">
                <p className="text-sm font-bold text-slate-900 dark:text-slate-100">{c.name || "Competitor Benchmark"}</p>
                <p className="text-[11px] text-slate-500 font-mono truncate max-w-md">{c.url}</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge tone="info">View Price & Feature Matrix →</Badge>
              </div>
            </Link>
          ))}
          {!list.length && (
            <p className="px-5 py-6 text-center text-slate-500">
              No competitors tracked yet. Add your first competitor above to begin price monitoring.
            </p>
          )}
        </div>
      </Card>
    </main>
  );
}
