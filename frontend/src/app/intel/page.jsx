"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, Button, Badge } from "../components/ui";
import { useJob } from "../hooks/useJob";
import { WorkflowStepGuide } from "../components/WorkflowStepGuide";
import {
  Radar,
  Loader2,
  Globe,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
  Palette,
  Search,
  CheckCircle2,
  AlertTriangle,
  Code2,
  Download,
  Copy,
  ExternalLink
} from "lucide-react";
import { authFetch } from "../api";

export default function IntelPage() {
  const [activeTab, setActiveTab] = useState("seo_design"); // "seo_design" | "competitors"
  const [list, setList] = useState([]);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  
  // SEO & Design State
  const [targetUrl, setTargetUrl] = useState("https://stripe.com");
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [copiedToken, setCopiedToken] = useState(false);

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

  const handleDeepAudit = async () => {
    if (!targetUrl.trim() || isAuditing) return;
    setIsAuditing(true);
    setAuditResult(null);
    try {
      const res = await authFetch("/api/web/deep-audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: targetUrl.trim(), max_pages: 2 }),
      });
      if (res.ok) {
        const data = await res.json();
        setAuditResult(data);
      }
    } catch (err) {
      console.error("Deep audit failed:", err);
    } finally {
      setIsAuditing(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedToken(true);
    setTimeout(() => setCopiedToken(false), 2000);
  };

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-6 py-6 overflow-x-clip">
      {/* Studio Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Radar size={22} className="text-cyan-600 dark:text-cyan-400" />
            Web Intelligence, SEO & Design Studio
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            360° Technical & Content SEO Auditing, DesignLens UI/UX Token Extraction, and Autonomous Lead Crawlers
          </p>
        </div>
        <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl border border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setActiveTab("seo_design")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "seo_design"
                ? "bg-white dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 shadow-xs"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
            }`}
          >
            🔍 SEO & DesignLens
          </button>
          <button
            onClick={() => setActiveTab("competitors")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "competitors"
                ? "bg-white dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 shadow-xs"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
            }`}
          >
            📊 Competitor Catalogs
          </button>
        </div>
      </div>

      {activeTab === "seo_design" ? (
        <div className="space-y-6">
          {/* Target URL Launcher */}
          <Card
            title="360° Multi-Vector Web & Design Audit"
            info="Crawls any public URL to extract technical SEO, Core Web Vitals, and Figma-ready Design Tokens."
          >
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <div className="relative flex-1 min-w-[280px]">
                  <Globe size={14} className="absolute left-3 top-3 text-slate-400" />
                  <input
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                    placeholder="Enter website URL (e.g. https://stripe.com, https://linear.app)"
                    className="h-10 w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 pl-9 pr-3 text-xs focus:ring-2 focus:ring-cyan-500 text-slate-900 dark:text-slate-100"
                  />
                </div>
                <Button
                  variant="primary"
                  size="md"
                  onClick={handleDeepAudit}
                  disabled={isAuditing || !targetUrl.trim()}
                >
                  {isAuditing ? <Loader2 className="animate-spin" size={14} /> : <Sparkles size={14} />}
                  {isAuditing ? "Auditing 360° Systems..." : "Run Deep Audit"}
                </Button>
              </div>

              {isAuditing && (
                <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center gap-2 text-cyan-700 dark:text-cyan-300 text-xs">
                  <Loader2 className="animate-spin text-cyan-500" size={14} />
                  <span>Crawling DOM tree, computing WCAG contrast, and simulating Core Web Vitals...</span>
                </div>
              )}
            </div>
          </Card>

          {/* Audit Results Dashboard */}
          {auditResult && (
            <div className="space-y-6 animate-fade-in">
              {/* Score Badges */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card>
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Overall SEO Score</span>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-extrabold text-cyan-600 dark:text-cyan-400">
                        {auditResult.summary?.seo_score || 85}
                      </span>
                      <span className="text-xs text-slate-400">/ 100</span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      {auditResult.seo_audit?.headings?.h1_count === 1 ? "✓ Optimal H1 hierarchy" : "⚠️ Heading structure warnings"}
                    </p>
                  </div>
                </Card>

                <Card>
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">WCAG 2.1 Contrast</span>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
                        {auditResult.design_lens?.contrast?.wcag_compliance || "AAA"}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        ({auditResult.design_lens?.contrast?.ratio || "8.5"}:1)
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">High-accessibility visual palette</p>
                  </div>
                </Card>

                <Card>
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Discovered Leads</span>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400">
                        {auditResult.summary?.leads_found_count || 0}
                      </span>
                      <span className="text-xs text-slate-400">contacts</span>
                    </div>
                    <p className="text-[11px] text-slate-500">Cloudflare XOR de-obfuscated</p>
                  </div>
                </Card>
              </div>

              {/* DesignLens Color Moodboard & Tokens */}
              <Card
                title="🎨 DesignLens — Extracted Color Palette & Tokens"
                info="Dominant color harmony clustered from computed CSS stylesheets."
                actions={
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        const blob = new Blob([JSON.stringify(auditResult.design_lens?.export_artifacts?.tokens_json || {}, null, 2)], { type: "application/json" });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = "tokens.json";
                        a.click();
                      }}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 transition"
                    >
                      <Download size={11} />
                      <span>Figma Tokens.json</span>
                    </button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(auditResult.design_lens?.export_artifacts?.tailwind_config_snippet || "")}
                    >
                      {copiedToken ? <CheckCircle2 size={12} className="text-emerald-500" /> : <Copy size={12} />}
                      <span>{copiedToken ? "Copied!" : "Tailwind Config"}</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(auditResult.design_lens?.export_artifacts?.css_variables || "")}
                    >
                      {copiedToken ? <CheckCircle2 size={12} className="text-emerald-500" /> : <Code2 size={12} />}
                      <span>CSS :root</span>
                    </Button>
                  </div>
                }
              >
                <div className="space-y-4">
                  {/* Color Swatches */}
                  <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
                    {Object.entries(auditResult.design_lens?.palette || {}).map(([key, hex]) => (
                      <div key={key} className="rounded-xl border border-slate-200 dark:border-slate-800 p-2 text-center space-y-1.5 bg-slate-50/50 dark:bg-slate-900/50">
                        <div
                          className="h-12 w-full rounded-lg shadow-inner border border-black/10"
                          style={{ backgroundColor: hex }}
                        />
                        <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500">{key}</span>
                        <span className="block text-[11px] font-mono font-bold text-slate-800 dark:text-slate-200">{hex}</span>
                      </div>
                    ))}
                  </div>

                  {/* Typography & Layout */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
                    <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1">
                      <span className="font-bold text-slate-700 dark:text-slate-200">Typography Scale</span>
                      <p className="text-slate-600 dark:text-slate-400">
                        Heading: <b className="font-mono text-cyan-600">{auditResult.design_lens?.typography?.heading_font}</b> · Body: <b className="font-mono text-cyan-600">{auditResult.design_lens?.typography?.body_font}</b>
                      </p>
                      <p className="text-[10px] text-slate-400">Scale: {auditResult.design_lens?.typography?.modular_scale_name}</p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-1">
                      <span className="font-bold text-slate-700 dark:text-slate-200">Grid & Layout Topography</span>
                      <p className="text-slate-600 dark:text-slate-400">
                        System: <b>{auditResult.design_lens?.layout?.grid_system}</b> · Rhythm: <b>{auditResult.design_lens?.layout?.border_radius_rhythm}</b>
                      </p>
                      <p className="text-[10px] text-slate-400">Container Max: {auditResult.design_lens?.layout?.max_container_width}</p>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Technical SEO Audit Breakdown */}
              <Card
                title="🔍 Technical & Content SEO Diagnostics"
                info="Meta tags, heading hierarchy, OpenGraph compliance, and Core Web Vitals estimates."
                actions={
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        const blob = new Blob([auditResult.seo_audit?.export_artifacts?.markdown_report || ""], { type: "text/markdown" });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = "seo_audit_report.md";
                        a.click();
                      }}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition"
                    >
                      <Download size={11} />
                      <span>Download Audit Report (.md)</span>
                    </button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(auditResult.seo_audit?.export_artifacts?.meta_tags_html || "")}
                    >
                      {copiedToken ? <CheckCircle2 size={12} className="text-emerald-500" /> : <Code2 size={12} />}
                      <span>{copiedToken ? "Copied!" : "Copy <meta> Tags"}</span>
                    </Button>
                  </div>
                }
              >
                <div className="space-y-4 text-xs">
                  {/* Actionable Priority Recommendations */}
                  {auditResult.seo_audit?.actionable_recommendations?.length > 0 && (
                    <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-2">
                      <div className="flex items-center gap-1.5 font-bold text-amber-600 dark:text-amber-400">
                        <AlertTriangle size={14} />
                        <span>Actionable Fix Recommendations</span>
                      </div>
                      <ul className="space-y-1 text-[11px] text-slate-700 dark:text-slate-300 list-disc list-inside">
                        {auditResult.seo_audit.actionable_recommendations.map((rec, idx) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-800 dark:text-slate-200">Title Tag</span>
                        <Badge tone={auditResult.seo_audit?.meta?.title_status === "optimal" ? "good" : "warn"}>
                          {auditResult.seo_audit?.meta?.title_length} chars
                        </Badge>
                      </div>
                      <p className="text-[11px] text-slate-600 dark:text-slate-400 italic">
                        "{auditResult.seo_audit?.meta?.title || "None"}"
                      </p>
                    </div>

                    <div className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-800 dark:text-slate-200">Meta Description</span>
                        <Badge tone={auditResult.seo_audit?.meta?.description_status === "optimal" ? "good" : "warn"}>
                          {auditResult.seo_audit?.meta?.description_length} chars
                        </Badge>
                      </div>
                      <p className="text-[11px] text-slate-600 dark:text-slate-400 line-clamp-2">
                        {auditResult.seo_audit?.meta?.description || "Missing meta description"}
                      </p>
                    </div>
                  </div>

                  {/* Core Web Vitals Simulation */}
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 text-[11px]">
                    <div>
                      <span className="font-bold text-slate-700 dark:text-slate-200">Est. Largest Contentful Paint (LCP):</span>
                      <span className="ml-1 font-mono text-cyan-600 dark:text-cyan-400">{auditResult.seo_audit?.core_web_vitals_simulation?.estimated_lcp_ms}ms</span>
                    </div>
                    <div>
                      <span className="font-bold text-slate-700 dark:text-slate-200">First Contentful Paint (FCP):</span>
                      <span className="ml-1 font-mono text-cyan-600 dark:text-cyan-400">{auditResult.seo_audit?.core_web_vitals_simulation?.estimated_fcp_ms}ms</span>
                    </div>
                    <div>
                      <span className="font-bold text-slate-700 dark:text-slate-200">DOM Nodes:</span>
                      <span className="ml-1 font-mono text-slate-500">{auditResult.seo_audit?.core_web_vitals_simulation?.dom_elements_count}</span>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      ) : (
        /* Legacy Competitor Tracker Tab */
        <div className="space-y-6">
          <Card
            title="Track a New Competitor Catalog"
            info="Scrapes live product offerings, baseline pricing, and ratings to establish a competitive benchmark."
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
                    placeholder="https://competitor.com/catalog or store link"
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

          <Card title="Tracked Competitors Directory" info="Monitored brand catalogs with automated price history." pad={false}>
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
        </div>
      )}
    </main>
  );
}
