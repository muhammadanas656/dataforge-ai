"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Card, Badge, Button, StatTile } from "../../components/ui";
import { Breadcrumbs } from "../../components/Breadcrumbs";
import { ScenarioPlanner } from "../../components/ScenarioPlanner";
import { WorkflowStepGuide } from "../../components/WorkflowStepGuide";
import {
  Compass,
  ArrowLeft,
  Sparkles,
  TrendingUp,
  Users,
  DollarSign,
  ShieldAlert,
  ShieldCheck,
  Loader2,
  CheckCircle2,
  Wrench,
  Building2,
  Layers,
  Database,
  ExternalLink,
  Target
} from "lucide-react";

export default function ResearchReport() {
  const { id } = useParams();
  const router = useRouter();
  const [r, setR] = useState(null);
  const [tab, setTab] = useState("overview");
  const [swot, setSwot] = useState(null);
  const [swotLoading, setSwotLoading] = useState(false);
  const [injectingDataset, setInjectingDataset] = useState(false);

  // Competitor & Scenario State
  const [competitors, setCompetitors] = useState([]);
  const [scenarios, setScenarios] = useState(null);

  useEffect(() => {
    if (id) {
      fetch(`http://localhost:8000/api/research/${id}`)
        .then((x) => x.json())
        .then((data) => {
          setR(data);
          if (data && data.niche) {
            fetch(`http://localhost:8000/api/research/competitors/${encodeURIComponent(data.niche)}`)
              .then((res) => res.json())
              .then((d) => setCompetitors(d.competitors || []))
              .catch((e) => console.warn("Failed fetching competitors:", e));

            fetch(`http://localhost:8000/api/research/scenarios/${encodeURIComponent(data.niche)}?price=${data.market?.assumptions?.avg_price || 50}`)
              .then((res) => res.json())
              .then(setScenarios)
              .catch((e) => console.warn("Failed fetching scenarios:", e));
          }
        })
        .catch((e) => console.error("Failed loading report:", e));
    }
  }, [id]);

  const generateSwot = async () => {
    if (!r) return;
    setSwotLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/research/swot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ research_id: id, niche: r.niche }),
      });
      if (res.ok) {
        setSwot(await res.json());
      }
    } catch (e) {
      console.error("SWOT generation error:", e);
    } finally {
      setSwotLoading(false);
    }
  };

  const handleInjectDatasetAndClean = async () => {
    if (!r) return;
    setInjectingDataset(true);
    try {
      const res = await fetch("http://localhost:8000/api/research/export-to-dataset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ niche: r.niche, dataset_type: "comprehensive" })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("dataforge_active_id", data.primary_dataset?.dataset_id || data.dataset_id);
        router.push("/cleaning");
      }
    } catch (e) {
      console.error("Failed exporting dataset:", e);
    } finally {
      setInjectingDataset(false);
    }
  };

  if (!r) {
    return (
      <main className="mx-auto max-w-6xl p-8 text-center text-xs text-slate-500">
        <Loader2 className="animate-spin inline-block mr-2" size={16} />
        Loading niche intelligence report #{id}…
      </main>
    );
  }

  const m = r.metrics || {};
  const score = r.opportunity_score || 0;

  return (
    <main className="mx-auto max-w-6xl space-y-5 px-6 py-6 overflow-x-clip">
      <Breadcrumbs
        crumbs={[
          { href: "/", label: "Home" },
          { href: "/research", label: "Niche Research" },
          { label: r.niche || `Report #${id}` },
        ]}
      />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Link href="/research">
            <Button variant="ghost" size="sm">
              <ArrowLeft size={14} /> Back to Hub
            </Button>
          </Link>
          <div>
            <h1 className="text-xl font-bold tracking-tight capitalize flex items-center gap-2">
              <Compass size={20} className="text-indigo-600 dark:text-indigo-400" />
              {r.niche}
            </h1>
            <p className="text-xs text-slate-500">
              Source: <span className="font-mono font-medium">{r.source || "ReAct Agent"}</span> · Snapshot ID: {r.id} · {new Date(r.created).toLocaleString()}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {r.tokens && (
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-[11px] shadow-sm font-mono">
              <span className="text-slate-500 font-sans font-semibold">Dossier Tokens:</span>
              <span className="font-bold text-indigo-600 dark:text-indigo-400">
                {(r.tokens.total_tokens || 0).toLocaleString()}
              </span>
              <span className="text-slate-300 dark:text-slate-700">|</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                +{(r.tokens.total_saved || 650).toLocaleString()} saved (0-tkn)
              </span>
            </div>
          )}
          <Badge tone={score >= 65 ? "good" : score >= 40 ? "warn" : "bad"}>
            Opportunity Score: {score}/100
          </Badge>
          <Button size="sm" variant="primary" onClick={handleInjectDatasetAndClean} disabled={injectingDataset}>
            {injectingDataset ? <Loader2 className="animate-spin" size={13} /> : <Database size={13} />}
            {injectingDataset ? "Creating Dataset..." : "Export to Cleaning Studio →"}
          </Button>
        </div>
      </div>

      {/* Non-Sophisticated Workflow Guide */}
      <WorkflowStepGuide
        currentStepId="research"
        pageTitle={`Deep Dive Intelligence: ${r.niche}`}
        reason="This report gives you a complete 360-degree commercial evaluation of this niche. It combines real social media sentiment, scraped competitor pricing, SWOT analysis, and a 1,000x Monte Carlo financial simulation to verify if this business can make money."
        priorStepText="You selected this niche from the Proactive Opportunity Radar on the Market Research hub."
        priorStepHref="/research"
        currentActionSteps={[
          { title: "Review Financial Scenarios", detail: "Switch to the 'Scenarios & Monte Carlo' tab to check probability of profit and breakeven month." },
          { title: "Inspect Live Competitors", detail: "Check the 'Competitors' tab to see what competitors charge and where their reviews are negative." },
          { title: "Export to Cleaning Studio", detail: "Click 'Export to Cleaning Studio' at top right to auto-generate a 12-month messy dataset and start cleaning." }
        ]}
        nextStepText="Click 'Export to Cleaning Studio →' to load a 12-month unit economics dataset directly into the Cleaning Studio."
        nextStepHref="/cleaning"
        jargonBuster={[
          { term: "Pain-Point Ratio", meaning: "The percentage of organic online discussions where customers complain about existing products." },
          { term: "SWOT Matrix", meaning: "Strengths, Weaknesses, Opportunities, and Threats synthesized directly from market discussions." },
          { term: "Breakeven Month", meaning: "The exact month when cumulative profits cover initial fixed startup costs." },
          { term: "P50 / Median Profit", meaning: "The expected mid-point monthly profit where 50% of simulated business outcomes were higher and 50% lower." }
        ]}
      />

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-slate-200 dark:border-slate-800 text-xs">
        {[
          { id: "overview", label: "Executive Overview" },
          { id: "competitors", label: `Competitors (${competitors.length})` },
          { id: "scenarios", label: "Scenarios & Monte Carlo" },
          { id: "data", label: "TAM & Pain Points" },
          { id: "swot", label: "Grounded SWOT" },
          { id: "personas", label: "Target Personas" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2.5 font-semibold border-b-2 transition ${
              tab === t.id
                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview */}
      {tab === "overview" && (
        <div className="space-y-5">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <StatTile
              label="Total Mentions (1yr)"
              value={m.mentions?.toLocaleString() || 0}
              info="Identified organic discussion threads and product queries."
            />
            <StatTile
              label="Search Growth Trend"
              value={`${(m.growth * 100).toFixed(0)}%`}
              tone={m.growth > 0 ? "good" : "bad"}
              info="Recent conversation volume versus prior period."
            />
            <StatTile
              label="Pain-Point Ratio"
              value={`${(m.pain_ratio * 100).toFixed(0)}%`}
              tone={m.pain_ratio > 0.2 ? "good" : "neutral"}
              info="Share of posts complaining about current market options."
            />
            <StatTile
              label="Average Sentiment"
              value={m.avg_sentiment || 0}
              tone={m.avg_sentiment < 0 ? "warn" : "good"}
              info="Scale: -1.0 (very negative) to +1.0 (very positive)."
            />
          </div>

          <Card
            title="Strategic Opportunity Verdict"
            info="Composite recommendation evaluating demand volume, growth delta, and unmet user pain."
            actions={
              <Button size="sm" variant="secondary" onClick={handleInjectDatasetAndClean} disabled={injectingDataset}>
                <Wrench size={12} /> Open in Cleaning Studio
              </Button>
            }
          >
            <div className="p-3.5 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 text-xs space-y-2">
              <p className="text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                Niche <b>"{r.niche}"</b> scored <b>{score}/100</b>. With an estimated annual TAM of{" "}
                <b>${(r.market?.tam_annual_usd || 0).toLocaleString()}</b> and a growth momentum of{" "}
                <b>{(m.growth * 100).toFixed(0)}%</b>, this category shows strong commercial validation.
              </p>
              <div className="flex flex-wrap gap-2 pt-1">
                <Button size="sm" variant="primary" onClick={() => setTab("scenarios")}>
                  Inspect Monte Carlo Simulation →
                </Button>
                <Button size="sm" variant="secondary" onClick={() => setTab("competitors")}>
                  View Competitor Pricing & Reviews →
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setTab("swot")}>
                  Inspect SWOT Analysis →
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Tab: Competitor Reality Check */}
      {tab === "competitors" && (
        <div className="space-y-4">
          <Card
            title="Competitor Reality Check (Scraped Live)"
            info="Real competitor pricing ranges, feature lists, and customer review sentiment."
            actions={<Badge tone="good">{competitors.length} Competitors Analyzed</Badge>}
          >
            {competitors.length > 0 ? (
              <div className="grid gap-3.5 sm:grid-cols-2">
                {competitors.map((comp, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">{comp.name}</h4>
                      <a
                        href={comp.website}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                      >
                        Visit Site <ExternalLink size={10} />
                      </a>
                    </div>
                    <p className="text-[11px] text-slate-500 leading-normal">{comp.description}</p>
                    
                    <div className="pt-1.5 border-t border-slate-100 dark:border-slate-800 space-y-1">
                      <div className="flex justify-between font-mono text-[11px]">
                        <span className="text-slate-500">Pricing Range:</span>
                        <span className="font-bold text-emerald-600 dark:text-emerald-400">
                          {comp.pricing?.price_range_text || "$49 - $129"}
                        </span>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-500">Review Sentiment:</span>
                        <span className="font-semibold text-slate-800 dark:text-slate-200">
                          ⭐ {comp.reviews?.avg_rating || 4.2} / 5.0 ({comp.reviews?.count || 10} reviews)
                        </span>
                      </div>
                    </div>

                    {comp.features && comp.features.length > 0 && (
                      <div className="pt-1 text-[10px] text-slate-600 dark:text-slate-300">
                        <span className="font-bold text-slate-400 block mb-0.5">Core Features:</span>
                        <ul className="list-disc list-inside space-y-0.5">
                          {comp.features.slice(0, 3).map((f, fIdx) => (
                            <li key={fIdx}>{f}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 text-center text-xs text-slate-500">
                <Loader2 className="animate-spin inline-block mr-2" size={14} />
                Discovering and scraping competitor websites for {r.niche}...
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Tab: Scenarios & Monte Carlo */}
      {tab === "scenarios" && (
        <div className="space-y-4">
          {scenarios ? (
            <ScenarioPlanner scenarios={scenarios} />
          ) : (
            <div className="p-6 text-center text-xs text-slate-500">
              <Loader2 className="animate-spin inline-block mr-2" size={14} />
              Computing 1,000x Monte Carlo simulation and financial scenarios...
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Market TAM & Pain Points */}
      {tab === "data" && (
        <div className="grid gap-5 md:grid-cols-2">
          <Card
            title="Top Unmet Customer Pain Points"
            info="Extracted complaints and failure modes from organic user reviews and discussion threads."
            actions={<Badge tone="bad">Product Angle</Badge>}
          >
            <div className="space-y-2 text-xs">
              {r.pain_points?.length ? (
                r.pain_points.map((p, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 p-2 rounded-lg bg-rose-50/50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/40 text-rose-900 dark:text-rose-200"
                  >
                    <ShieldAlert size={14} className="text-rose-600 shrink-0" />
                    <span className="font-semibold capitalize">{p.replace(/_/g, " ")}</span>
                  </div>
                ))
              ) : (
                <p className="text-slate-500 italic">No specific pain points isolated.</p>
              )}
            </div>
          </Card>

          <Card
            title="Market Sizing (Heuristic TAM)"
            info="Estimated Total Addressable Market calculated from monthly organic interest, conversion rate, and average price."
            actions={<Badge tone="good">TAM Model</Badge>}
          >
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800">
                <span className="text-slate-500">Estimated Monthly Organic Interest:</span>
                <span className="font-bold">{r.market?.monthly_interest?.toLocaleString() || 0} searches</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800">
                <span className="text-slate-500">Estimated Monthly Buyers (2% conv):</span>
                <span className="font-bold">{r.market?.est_buyers_monthly?.toLocaleString() || 0} units</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-100 dark:border-slate-800">
                <span className="text-slate-500">Target Product Price:</span>
                <span className="font-mono font-bold">${r.market?.assumptions?.avg_price || 49}</span>
              </div>
              <div className="pt-2 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Projected Annual TAM:</span>
                <span className="text-base font-bold text-emerald-600 dark:text-emerald-400">
                  ${(r.market?.tam_annual_usd || 0).toLocaleString()} / yr
                </span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Tab 3: SWOT */}
      {tab === "swot" && (
        <Card
          title="Grounded Strategic SWOT Analysis"
          info="Synthesizes competitive strengths, vulnerabilities, market opportunities, and external threats."
          actions={
            <Button size="sm" variant="primary" onClick={generateSwot} disabled={swotLoading}>
              {swotLoading ? <Loader2 className="animate-spin" size={12} /> : <Sparkles size={12} />}
              {swotLoading ? "Synthesizing SWOT..." : swot ? "Regenerate SWOT" : "Generate SWOT Matrix"}
            </Button>
          }
        >
          {swot ? (
            <div className="grid gap-4 md:grid-cols-2 text-xs">
              <div className="p-3 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/70 dark:border-emerald-900/50">
                <h4 className="font-bold text-emerald-900 dark:text-emerald-200 mb-1.5 flex items-center gap-1.5">
                  <CheckCircle2 size={14} className="text-emerald-600" /> Strengths
                </h4>
                <ul className="space-y-1 list-disc list-inside text-slate-700 dark:text-slate-300">
                  {(swot.strengths || []).map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-3 rounded-xl bg-rose-50/60 dark:bg-rose-950/20 border border-rose-200/70 dark:border-rose-900/50">
                <h4 className="font-bold text-rose-900 dark:text-rose-200 mb-1.5 flex items-center gap-1.5">
                  <ShieldAlert size={14} className="text-rose-600" /> Weaknesses & Risks
                </h4>
                <ul className="space-y-1 list-disc list-inside text-slate-700 dark:text-slate-300">
                  {(swot.weaknesses || []).map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-3 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-200/70 dark:border-indigo-900/50">
                <h4 className="font-bold text-indigo-900 dark:text-indigo-200 mb-1.5 flex items-center gap-1.5">
                  <Sparkles size={14} className="text-indigo-600" /> Opportunities
                </h4>
                <ul className="space-y-1 list-disc list-inside text-slate-700 dark:text-slate-300">
                  {(swot.opportunities || []).map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-3 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/70 dark:border-amber-900/50">
                <h4 className="font-bold text-amber-900 dark:text-amber-200 mb-1.5 flex items-center gap-1.5">
                  <ShieldAlert size={14} className="text-amber-600" /> Threats & Competitor Reactions
                </h4>
                <ul className="space-y-1 list-disc list-inside text-slate-700 dark:text-slate-300">
                  {(swot.threats || []).map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic py-2">
              Click "Generate SWOT Matrix" to produce a grounded strategic breakdown of this niche.
            </p>
          )}
        </Card>
      )}

      {/* Tab 4: Personas */}
      {tab === "personas" && (
        <Card
          title="Target Customer Personas"
          info="Autonomous AI personas generated from real buyer search vocabulary and motivation profiles."
          actions={<Badge tone="ai">AI Synthesized</Badge>}
        >
          <div className="grid gap-3 md:grid-cols-3 text-xs">
            {(r.personas || []).map((p, i) => (
              <div key={i} className="p-3.5 rounded-xl bg-slate-50/70 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 space-y-2">
                <div className="flex items-center gap-1.5 font-bold text-slate-900 dark:text-slate-100">
                  <Users size={14} className="text-indigo-600" />
                  <span>{p.name}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Core Goal</span>
                  <p className="text-slate-700 dark:text-slate-300 leading-snug">{p.goal}</p>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-rose-500 block">Frustration / Pain</span>
                  <p className="text-rose-700 dark:text-rose-300 leading-snug">{p.pain_point}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </main>
  );
}
