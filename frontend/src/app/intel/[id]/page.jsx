"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Card, Badge, Button, StatTile } from "../../components/ui";
import { Breadcrumbs } from "../../components/Breadcrumbs";
import { Radar, ArrowLeft, RefreshCw, Loader2, DollarSign, Layers, MessageSquare, AlertTriangle, CheckCircle2, TrendingUp, Sparkles } from "lucide-react";

export default function IntelReport() {
  const { id } = useParams();
  const [r, setR] = useState(null);
  const [tab, setTab] = useState("overview");
  const [reviews, setReviews] = useState("");
  const [sent, setSent] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const loadData = () => {
    fetch(`http://localhost:8000/api/intel/${id}`)
      .then((x) => x.json())
      .then(setR)
      .catch((e) => console.error("Failed loading intel report:", e));
  };

  useEffect(() => {
    if (id) loadData();
  }, [id]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch(`http://localhost:8000/api/intel/${id}/refresh`, { method: "POST" });
      setTimeout(() => {
        loadData();
        setRefreshing(false);
      }, 3500);
    } catch (e) {
      console.error(e);
      setRefreshing(false);
    }
  };

  const handleAnalyzeReviews = async () => {
    if (!reviews.trim()) return;
    setAnalyzing(true);
    try {
      const res = await fetch("http://localhost:8000/api/intel/reviews", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reviews: reviews.split("\n").filter((l) => l.trim().length > 0) }),
      });
      if (res.ok) {
        setSent(await res.json());
      }
    } catch (e) {
      console.error("Sentiment analysis error:", e);
    } finally {
      setAnalyzing(false);
    }
  };

  if (!r) {
    return (
      <main className="mx-auto max-w-6xl p-8 text-center text-xs text-slate-500">
        <Loader2 className="animate-spin inline-block mr-2" size={16} />
        Loading competitor intelligence #{id}…
      </main>
    );
  }

  const reg = r.registry || {};
  const products = r.latest?.products || [];
  const changes = r.changes || [];
  const gaps = r.gaps || [];

  return (
    <main className="mx-auto max-w-6xl space-y-5 px-6 py-6 overflow-x-clip">
      <Breadcrumbs
        crumbs={[
          { href: "/", label: "Home" },
          { href: "/intel", label: "Competitor Intel" },
          { label: reg.name || `Competitor #${id}` },
        ]}
      />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Link href="/intel">
            <Button variant="ghost" size="sm">
              <ArrowLeft size={14} /> Back to Intel Hub
            </Button>
          </Link>
          <div>
            <h1 className="text-xl font-bold tracking-tight capitalize flex items-center gap-2">
              <Radar size={20} className="text-indigo-600 dark:text-indigo-400" />
              {reg.name || "Competitor Benchmark"}
            </h1>
            <p className="text-xs text-slate-500 font-mono">{reg.url}</p>
          </div>
        </div>

        <Button size="sm" variant="secondary" onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? <Loader2 className="animate-spin" size={13} /> : <RefreshCw size={13} />}
          {refreshing ? "Re-scraping catalog..." : "Capture New Snapshot"}
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-slate-200 dark:border-slate-800 text-xs">
        {[
          { id: "overview", label: "Catalog Overview" },
          { id: "trends", label: "Price Trends & Changes" },
          { id: "gaps", label: "Feature Gaps" },
          { id: "reviews", label: "Review Aspect NLP" },
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

      {/* Stats Tile Grid */}
      <div className="grid grid-cols-3 gap-3">
        <StatTile label="Tracked Products" value={products.length} info="Identified catalog items and offerings." />
        <StatTile
          label="Snapshot History"
          value={r.snapshots || 1}
          info="Chronological scrape points. Re-scrape over time to monitor competitor price moves."
        />
        <StatTile
          label="Price Fluctuations"
          value={changes.length}
          tone={changes.length ? "warn" : "good"}
          info="Detected price increases or discounts across snapshots."
        />
      </div>

      {/* Tab 1: Catalog Overview */}
      {tab === "overview" && (
        <Card title="Current Scraped Product Catalog" info="Latest snapshot of product titles, prices, and star ratings." pad={false}>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 text-[10px] uppercase font-bold text-slate-500">
                  <th className="p-3">Product Name</th>
                  <th className="p-3">Price</th>
                  <th className="p-3">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {products.map((p, i) => (
                  <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                    <td className="p-3 font-medium text-slate-800 dark:text-slate-200">{p.title}</td>
                    <td className="p-3 font-mono font-bold text-slate-900 dark:text-slate-100">${p.price}</td>
                    <td className="p-3 font-mono text-amber-600 dark:text-amber-400">★ {p.rating || "4.5"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Tab 2: Price Trends */}
      {tab === "trends" && (
        <div className="space-y-5">
          {r.chart && (
            <Card title="Price Trends & Fluctuation Timeline" info="Visualized price points across catalog offerings over historical snapshots.">
              <img
                src={`data:image/png;base64,${r.chart}`}
                alt="Price History"
                className="w-full rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm"
              />
            </Card>
          )}

          {changes.length > 0 ? (
            <Card title="Recent Competitor Price Moves" info="Historical price deltas computed across successive snapshot captures." pad={false}>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 text-[10px] uppercase font-bold text-slate-500">
                      <th className="p-3">Product Name</th>
                      <th className="p-3">Previous Price</th>
                      <th className="p-3">Current Price</th>
                      <th className="p-3">Net Delta</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {changes.map((c, i) => (
                      <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                        <td className="p-3 font-medium text-slate-800 dark:text-slate-200">{c.title}</td>
                        <td className="p-3 font-mono text-slate-500">${c.before}</td>
                        <td className="p-3 font-mono font-bold text-slate-800 dark:text-slate-200">${c.after}</td>
                        <td className="p-3 font-mono font-bold">
                          <span className={c.delta > 0 ? "text-rose-600 dark:text-rose-400" : "text-emerald-600 dark:text-emerald-400"}>
                            {c.delta > 0 ? `+${c.delta}` : c.delta}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          ) : (
            <Card title="Recent Competitor Price Moves">
              <p className="text-xs text-slate-500 italic py-3">
                No price changes detected yet. Click "Capture New Snapshot" over time to record pricing moves.
              </p>
            </Card>
          )}
        </div>
      )}

      {/* Tab 3: Feature Gaps */}
      {tab === "gaps" && (
        <Card
          title="Cross-Competitor Feature Gap Analysis"
          info="Reveals features competitors market vs. features they lack — directly exposing your product differentiation angles."
          actions={<Badge tone="good">Differentiation Angle</Badge>}
        >
          <div className="space-y-2 text-xs">
            {gaps.length > 0 ? (
              gaps.map((g, i) => (
                <div key={i} className="p-2.5 rounded-lg bg-slate-50/80 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-indigo-600 dark:text-indigo-400 capitalize">✦ {g.feature}</span>
                    <Badge tone="slate">Feature Gap</Badge>
                  </div>
                  <div className="text-[11px] text-slate-600 dark:text-slate-300">
                    <span>Offered by: <b>{g.offered_by.join(", ")}</b></span>
                    <span className="mx-2">·</span>
                    <span className="text-rose-600 dark:text-rose-400 font-semibold">
                      Missing from: {g.missing_from.join(", ")}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 italic py-2">
                Track 2 or more competitors to generate an automatic cross-brand feature comparison matrix.
              </p>
            )}
          </div>
        </Card>
      )}

      {/* Tab 4: Aspect NLP */}
      {tab === "reviews" && (
        <Card
          title="Aspect-Level Customer Review Sentiment NLP"
          info="Paste raw customer feedback or product reviews (one per line) to evaluate granular sentiment across price, quality, shipping, support, and features."
          actions={<Badge tone="ai">Aspect NLP</Badge>}
        >
          <div className="space-y-3 text-xs">
            <textarea
              value={reviews}
              onChange={(e) => setReviews(e.target.value)}
              rows={4}
              placeholder={"Paste customer reviews here (one per line):\nGreat build quality and very durable, but customer service was slow to respond.\nSuper fast shipping, love the materials!\nToo expensive for what it offers, broke after two weeks."}
              className="w-full rounded-xl border border-slate-200 p-3 text-xs dark:border-slate-800 dark:bg-slate-900 focus:ring-2 focus:ring-indigo-500 text-slate-900 dark:text-slate-100"
            />

            <Button size="sm" variant="primary" onClick={handleAnalyzeReviews} disabled={analyzing || !reviews.trim()}>
              {analyzing ? <Loader2 className="animate-spin" size={12} /> : <MessageSquare size={12} />}
              {analyzing ? "Classifying Aspects..." : "Analyze Review Aspects"}
            </Button>

            {sent && (
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/70 border border-slate-200/80 dark:border-slate-700 space-y-2.5 animate-fadeIn">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800 dark:text-slate-200">Overall Sentiment Score</span>
                  <Badge tone={sent.overall < 0 ? "bad" : "good"}>Overall: {sent.overall}</Badge>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-1">
                  {Object.entries(sent.aspects || {}).map(([aspect, sc]) => (
                    <div key={aspect} className="p-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 text-center">
                      <span className="text-[10px] text-slate-400 capitalize block">{aspect}</span>
                      <span
                        className={`font-bold font-mono text-xs ${
                          sc > 0 ? "text-emerald-600 dark:text-emerald-400" : sc < 0 ? "text-rose-600 dark:text-rose-400" : "text-slate-600"
                        }`}
                      >
                        {sc > 0 ? `+${sc}` : sc}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </main>
  );
}
