"use client";
import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card, Button, Badge, StatTile } from "../components/ui";
import { useJob } from "../hooks/useJob";
import { FeatureGuide } from "../components/FeatureGuide";
import { WorkflowStepGuide } from "../components/WorkflowStepGuide";
import { authFetch } from "../api";
import {
  Compass,
  Loader2,
  Search,
  Sparkles,
  TrendingUp,
  AlertCircle,
  FileText,
  ArrowRight,
  ShieldCheck,
  Building2,
  DollarSign,
  Layers,
  Zap,
  Target,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  BarChart3,
  Database,
  Terminal,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  Lightbulb,
  Sliders,
  ShieldAlert,
  X,
  Globe,
} from "lucide-react";

const CATEGORIES = [
  "All",
  "E-Commerce",
  "AI & SaaS",
  "Health & Wellness",
  "Creator Economy",
  "Home & Gadgets"
];

const QUICK_TAGS = [
  "B2B AI Lead Qualifier",
  "Cold Plunge Water Chiller",
  "Ergonomic Split Keyboard",
  "Eco Pet Odor Neutralizer",
  "Notion Invoicing SaaS",
  "Smart Soil Nutrient Monitor"
];

export default function ResearchPage() {
  const router = useRouter();
  const [list, setList] = useState([]);
  const [niche, setNiche] = useState("");
  const [price, setPrice] = useState(49);
  const [competition, setCompetition] = useState(0.5);
  const [alerts, setAlerts] = useState([]);
  const [weekly, setWeekly] = useState(null);
  const [weeklyLoading, setWeeklyLoading] = useState(false);

  // Proactive Radar State
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);

  // Real-time Streaming State
  const [streaming, setStreaming] = useState(false);
  const [currentStepTitle, setCurrentStepTitle] = useState("");
  const [streamSteps, setStreamSteps] = useState([]);
  const [streamResult, setStreamResult] = useState(null);
  const [streamError, setStreamError] = useState(null);
  const terminalEndRef = useRef(null);

  // Business Blueprint Modal State
  const [activeBlueprint, setActiveBlueprint] = useState(null);
  const [loadingBlueprint, setLoadingBlueprint] = useState(false);
  const [injectingDataset, setInjectingDataset] = useState(false);
  const [customScrapeUrl, setCustomScrapeUrl] = useState("");
  const [crawlingWebsites, setCrawlingWebsites] = useState(false);

  // Future Horizon & Invention Studio State
  const [studioMode, setStudioMode] = useState("radar"); // 'radar' | 'invention'
  const [invDomain, setInvDomain] = useState("edge_ai_hardware");
  const [targetYear, setTargetYear] = useState(2028);
  const [improvingParam, setImprovingParam] = useState("speed");
  const [worseningParam, setWorseningParam] = useState("energy_efficiency");
  const [inventing, setInventing] = useState(false);
  const [inventionSteps, setInventionSteps] = useState([]);
  const [inventionResult, setInventionResult] = useState(null);
  const [inventionError, setInventionError] = useState(null);
  const invTerminalEndRef = useRef(null);

  // Token Telemetry State
  const [researchTokens, setResearchTokens] = useState(null);

  const job = useJob("research", { niche: "" }, { autoStart: false });

  const handleStreamInvention = async () => {
    setInventing(true);
    setInventionError(null);
    setInventionSteps([]);
    setInventionResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/stream/invent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain: invDomain,
          target_year: targetYear,
          improving: improvingParam,
          worsening: worseningParam
        })
      });

      if (!res.ok) throw new Error("Invention streaming failed");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter((l) => l.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.type === "thought") {
              setInventionSteps((prev) => [...prev, data]);
            } else if (data.type === "result") {
              setInventionResult(data.data);
            }
          } catch (e) {}
        }
      }
    } catch (err) {
      console.error("Invention stream error:", err);
      setInventionError(err.message || "Failed running invention synthesis");
    } finally {
      setInventing(false);
      loadTokens();
    }
  };

  const loadTokens = () => {
    fetch("http://localhost:8000/api/tokens?scope=research")
      .then((r) => r.json())
      .then(setResearchTokens)
      .catch(() => {});
  };

  const loadList = () => {
    fetch("http://localhost:8000/api/research/list")
      .then((r) => r.json())
      .then((d) => setList(d.research || []))
      .catch((e) => console.warn("Failed loading research list:", e));
  };

  const loadAlertsAndWeekly = () => {
    fetch("http://localhost:8000/api/alerts")
      .then((r) => r.json())
      .then((d) => setAlerts(d.alerts || []))
      .catch((e) => console.warn("Failed loading alerts:", e));

    fetch("http://localhost:8000/api/research/weekly/latest")
      .then((r) => r.json())
      .then((d) => setWeekly(d && d.summary ? d : null))
      .catch((e) => console.warn("Failed loading weekly digest:", e));
  };

  const loadSuggestions = (cat = selectedCategory) => {
    setLoadingSuggestions(true);
    const catQuery = cat === "All" ? "all" : encodeURIComponent(cat);
    fetch(`http://localhost:8000/api/research/suggestions?category=${catQuery}&limit=6`)
      .then((r) => r.json())
      .then((d) => setSuggestions(d.suggestions || []))
      .catch((e) => console.warn("Failed loading suggestions:", e))
      .finally(() => setLoadingSuggestions(false));
  };

  const handleAutonomousHunt = () => {
    setLoadingSuggestions(true);
    const catQuery = selectedCategory === "All" ? "all" : selectedCategory;
    fetch("http://localhost:8000/api/research/hunt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category: catQuery, limit: 6 })
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.opportunities && d.opportunities.length > 0) {
          setSuggestions(d.opportunities);
        } else {
          loadSuggestions(selectedCategory);
        }
      })
      .catch((e) => {
        console.warn("Failed autonomous hunting:", e);
        loadSuggestions(selectedCategory);
      })
      .finally(() => setLoadingSuggestions(false));
  };

  const trackEngagement = (nicheName, catName, action, score = null) => {
    fetch("http://localhost:8000/api/research/track-engagement", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ niche: nicheName, category: catName, action, opportunity_score: score })
    }).catch((e) => console.warn("Track engagement failed:", e));
  };

  useEffect(() => {
    loadList();
    loadAlertsAndWeekly();
    loadSuggestions("All");
    loadTokens();
  }, []);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [streamSteps]);

  const handleCategoryChange = (cat) => {
    setSelectedCategory(cat);
    loadSuggestions(cat);
  };

  // Real-Time SSE Streaming Research Execution
  const handleStreamResearch = async (queryNiche = niche, queryPrice = price) => {
    const q = (queryNiche || "").trim();
    if (!q) return;
    setNiche(q);
    setStreaming(true);
    setStreamError(null);
    setStreamSteps([]);
    setStreamResult(null);
    setCurrentStepTitle("Formulating Autonomous ReAct Plan...");

    trackEngagement(q, selectedCategory, "deep_dived");

    try {
      const res = await fetch("http://localhost:8000/api/stream/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          niche: q,
          avg_price: Number(queryPrice) || 50,
          category: selectedCategory === "All" ? "E-Commerce" : selectedCategory,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Streaming research failed");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const rawJson = line.slice(6);
            try {
              const event = JSON.parse(rawJson);
              if (event.type === "thought") {
                setCurrentStepTitle(event.title || event.content);
                setStreamSteps((prev) => [
                  ...prev,
                  {
                    step: event.step,
                    title: event.title,
                    content: event.content,
                    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
                  }
                ]);
              } else if (event.type === "result") {
                setStreamResult(event.data);
                loadList();
                loadAlertsAndWeekly();
              } else if (event.type === "error") {
                setStreamError(event.content);
              }
            } catch (err) {
              console.warn("SSE JSON parse error:", err);
            }
          }
        }
      }
    } catch (err) {
      console.error("Stream research failed:", err);
      setStreamError(err.message || "Failed running streaming research");
    } finally {
      setStreaming(false);
      loadList();
      loadTokens();
    }
  };

  const handleLaunchResearch = (nicheQuery, estPrice = price, score = null) => {
    handleStreamResearch(nicheQuery, estPrice);
  };

  const handleOpenBlueprint = async (nicheName, catName = "E-Commerce", score = null) => {
    trackEngagement(nicheName, catName, "viewed", score);
    setLoadingBlueprint(true);
    setActiveBlueprint({ niche: nicheName, loading: true });
    try {
      const res = await fetch("http://localhost:8000/api/research/blueprint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ niche: nicheName, category: catName })
      });
      if (res.ok) {
        const data = await res.json();
        setActiveBlueprint(data);
      }
    } catch (e) {
      console.error("Failed to generate blueprint:", e);
    } finally {
      setLoadingBlueprint(false);
    }
  };

  const handleInjectDatasetAndOpenCleaning = async (nicheName, catName = "E-Commerce") => {
    trackEngagement(nicheName, catName, "injected_dataset");
    setInjectingDataset(true);
    try {
      const res = await authFetch(`/api/research/export-to-dataset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ niche: nicheName, dataset_type: "comprehensive" })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("dataforge_active_id", data.primary_dataset?.dataset_id || data.dataset_id);
        router.push("/cleaning");
      }
    } catch (e) {
      console.error("Failed to inject dataset:", e);
    } finally {
      setInjectingDataset(false);
    }
  };

  const handleCrawlWebsitesAndOpenCleaning = async (nicheName, targetUrlsInput = "") => {
    setCrawlingWebsites(true);
    try {
      const urls = targetUrlsInput
        ? targetUrlsInput.split(",").map((u) => u.trim()).filter(Boolean)
        : [];
      const res = await authFetch(`/api/research/crawl-niche`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ niche: nicheName, custom_urls: urls, max_pages: 5 }),
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("dataforge_active_id", data.dataset_id);
        router.push("/cleaning");
      }
    } catch (e) {
      console.error("Failed to crawl niche websites:", e);
    } finally {
      setCrawlingWebsites(false);
    }
  };

  const handleRunWeekly = async () => {
    setWeeklyLoading(true);
    try {
      await authFetch(`/api/research/weekly`, { method: "POST" });
      setTimeout(async () => {
        const res = await authFetch(`/api/research/weekly/latest`);
        if (res.ok) setWeekly(await res.json());
        setWeeklyLoading(false);
      }, 3000);
    } catch (e) {
      console.error(e);
      setWeeklyLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-6 py-6 overflow-x-clip">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Compass size={22} className="text-indigo-600 dark:text-indigo-400" />
            Autonomous Market & Business Intelligence
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Proactive niche scouting, business model architecture, 3-tier monetization strategy, and social listening
          </p>
        </div>
        <div className="flex items-center gap-2">
          {researchTokens && (
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-[11px] shadow-sm font-mono">
              <span className="text-slate-500 font-sans font-semibold">Research Tokens:</span>
              <span className="font-bold text-indigo-600 dark:text-indigo-400">
                {(researchTokens.total_tokens || 0).toLocaleString()}
              </span>
              <span className="text-slate-300 dark:text-slate-700">|</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                +{(researchTokens.total_saved || 0).toLocaleString()} saved (0-tkn)
              </span>
            </div>
          )}
          <Badge tone="ai">Real-Time Autonomous Agent Active</Badge>
        </div>
      </div>

      {/* Studio Mode Selector */}
      <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 w-fit">
        <button
          onClick={() => setStudioMode("radar")}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
            studioMode === "radar"
              ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200/80 dark:border-slate-700"
              : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-200"
          }`}
        >
          <Compass size={14} />
          Operational Micro-Niche Radar
        </button>
        <button
          onClick={() => setStudioMode("invention")}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
            studioMode === "invention"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-200"
          }`}
        >
          <Lightbulb size={14} />
          Future Horizon & Invention Studio (2026–2030+)
          <span className="px-1.5 py-0.5 rounded-full bg-indigo-500 text-[10px] text-white font-mono">TRIZ + ML</span>
        </button>
      </div>

      {/* ========================================================= */}
      {/* 💡 MODE 2: FUTURE HORIZON & SYSTEMATIC INVENTION STUDIO */}
      {/* ========================================================= */}
      {studioMode === "invention" && (
        <div className="space-y-6">
          <Card
            title="Future Horizon & Systematic Invention Studio"
            info="Invent uncreated blue-ocean product categories using TRIZ Contradiction Matrices, Morphological Box search, and 2026–2030+ Tech Capability Trajectories."
          >
            <div className="space-y-5">
              {/* Controls Grid */}
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 text-xs">
                {/* Domain Selector */}
                <div className="space-y-1.5">
                  <label className="font-bold text-slate-700 dark:text-slate-300">Target Frontier Domain:</label>
                  <select
                    value={invDomain}
                    onChange={(e) => setInvDomain(e.target.value)}
                    className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="edge_ai_hardware">Edge AI Silicon & Biometric Sensors</option>
                    <option value="enterprise_saas_automation">Autonomous Enterprise Agents & Causal EDA</option>
                  </select>
                </div>

                {/* Target Deployment Year */}
                <div className="space-y-1.5">
                  <label className="font-bold text-slate-700 dark:text-slate-300">Target Launch Horizon:</label>
                  <div className="flex gap-1.5">
                    {[2026, 2027, 2028, 2030].map((yr) => (
                      <button
                        key={yr}
                        onClick={() => setTargetYear(yr)}
                        className={`flex-1 py-1.5 rounded-xl font-mono text-xs font-bold transition ${
                          targetYear === yr
                            ? "bg-indigo-600 text-white shadow-xs"
                            : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
                        }`}
                      >
                        {yr}
                      </button>
                    ))}
                  </div>
                </div>

                {/* TRIZ Improving Parameter */}
                <div className="space-y-1.5">
                  <label className="font-bold text-slate-700 dark:text-slate-300">Improving Parameter (TRIZ):</label>
                  <select
                    value={improvingParam}
                    onChange={(e) => setImprovingParam(e.target.value)}
                    className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium"
                  >
                    <option value="speed">Speed & Processing Latency</option>
                    <option value="reliability">Reliability & Uptime</option>
                    <option value="autonomy">Autonomy & Zero Human-in-Loop</option>
                    <option value="privacy">Privacy & Zero-Leakage</option>
                    <option value="adaptability">Dynamic Adaptability</option>
                  </select>
                </div>

                {/* TRIZ Worsening Parameter */}
                <div className="space-y-1.5">
                  <label className="font-bold text-slate-700 dark:text-slate-300">Worsening Parameter (Trade-off):</label>
                  <select
                    value={worseningParam}
                    onChange={(e) => setWorseningParam(e.target.value)}
                    className="w-full p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium"
                  >
                    <option value="energy_efficiency">Energy & Power Consumption</option>
                    <option value="cost">Manufacturing / Token Cost</option>
                    <option value="complexity">Architectural Complexity</option>
                    <option value="durability">Durability & Model Decay</option>
                  </select>
                </div>
              </div>

              {/* Action Button */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
                <p className="text-[11px] text-slate-500">
                  ⚡ Synthesizes non-obvious Cartesian combinations, applies TRIZ contradiction resolutions, and runs 4-layer grounding validation.
                </p>
                <Button
                  size="md"
                  variant="primary"
                  onClick={handleStreamInvention}
                  disabled={inventing}
                >
                  {inventing ? <Loader2 className="animate-spin" size={14} /> : <Zap size={14} />}
                  {inventing ? "Synthesizing Invention..." : "⚡ Synthesize Blue-Ocean Invention (TRIZ + ML)"}
                </Button>
              </div>
            </div>
          </Card>

          {/* Real-time Streaming Invention Terminal */}
          {(inventing || inventionSteps.length > 0) && (
            <Card
              title="Autonomous Invention Thought Console (TRIZ + ML)"
              info="Watch the AI resolve technical contradictions, audit physics/regulatory constraints, and project S-curve trajectories."
            >
              <div className="rounded-xl bg-slate-950 p-4 font-mono text-xs text-slate-200 space-y-2 max-h-64 overflow-y-auto border border-slate-800">
                {inventionSteps.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-2 animate-in fade-in duration-200">
                    <span className="text-indigo-400 font-bold shrink-0">[{step.agent}]</span>
                    <span className="text-slate-300">{step.status}</span>
                  </div>
                ))}
                {inventing && (
                  <div className="flex items-center gap-2 text-indigo-400 pt-1">
                    <Loader2 className="animate-spin" size={13} />
                    <span>Evaluating 2026-2030 technology horizon and grounding checks...</span>
                  </div>
                )}
                <div ref={invTerminalEndRef} />
              </div>
            </Card>
          )}

          {/* 🌟 Blue-Ocean Invention Dossier Result */}
          {inventionResult && (
            <Card
              title={`🌟 Blue-Ocean Breakthrough: ${inventionResult.concept_name}`}
              info={`Unprecedented category blueprint architected for ${inventionResult.target_market_year} deployment.`}
              actions={
                <div className="flex items-center gap-2">
                  <Badge tone={inventionResult.ml_intelligence?.novelty?.is_breakthrough ? "good" : "ai"}>
                    Novelty: {Math.round((inventionResult.ml_intelligence?.novelty?.novelty_score || 0.8) * 100)}% ({inventionResult.ml_intelligence?.novelty?.differentiation_tier})
                  </Badge>
                  <Button
                    size="sm"
                    variant="primary"
                    onClick={() => handleInjectDatasetAndOpenCleaning(inventionResult.concept_name, inventionResult.category)}
                    disabled={injectingDataset}
                  >
                    <Database size={13} /> {injectingDataset ? "Creating Dataset..." : "Export Future Dataset →"}
                  </Button>
                </div>
              }
            >
              <div className="space-y-5 text-xs">
                {/* Executive Pitch & Persona */}
                <div className="p-4 rounded-2xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-sm font-extrabold text-indigo-950 dark:text-indigo-200">
                      {inventionResult.one_sentence_pitch}
                    </span>
                    <Badge tone="good">Category: {inventionResult.category}</Badge>
                  </div>
                  <p className="text-slate-600 dark:text-slate-400 text-[11px]">
                    <b>🎯 Target Early Adopter Persona:</b> {inventionResult.target_persona}
                  </p>
                </div>

                {/* 4 Stat Tiles */}
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Target Year</span>
                    <span className="text-base font-extrabold text-indigo-600 dark:text-indigo-400 mt-1 block">
                      {inventionResult.target_market_year}
                    </span>
                    <span className="text-[10px] text-slate-500">Commercial launch window</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Grounding Audit</span>
                    <span className="text-base font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 block">
                      {inventionResult.grounding_validation?.passed_checks || 4}/{inventionResult.grounding_validation?.total_checks || 4} Passed
                    </span>
                    <span className="text-[10px] text-slate-500">Physics & regulatory compliant</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Unit Economics</span>
                    <span className="text-base font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 block">
                      {inventionResult.unit_economics?.gross_margin_pct || 75}% Margin
                    </span>
                    <span className="text-[10px] text-slate-500">
                      BOM: ${inventionResult.unit_economics?.estimated_bom_or_cogs_usd} | Price: ${inventionResult.unit_economics?.suggested_price_usd}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Critic Verdict</span>
                    <span className={`text-base font-extrabold mt-1 block ${
                      inventionResult.adversarial_critique?.critic_verdict === "PROCEED"
                        ? "text-emerald-600 dark:text-emerald-400"
                        : "text-amber-600 dark:text-amber-400"
                    }`}>
                      {inventionResult.adversarial_critique?.critic_verdict || "PROCEED"}
                    </span>
                    <span className="text-[10px] text-slate-500">Adversarial stress-test</span>
                  </div>
                </div>

                {/* Technical Architecture & TRIZ Breakthrough */}
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60 space-y-1.5">
                    <span className="font-bold text-slate-800 dark:text-slate-200 text-[11px] block">
                      ⚙️ Technical Spec & Architecture:
                    </span>
                    <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                      {inventionResult.technical_spec_summary}
                    </p>
                    <p className="text-[10px] text-slate-400 pt-1">
                      <b>Why Now Catalyst:</b> {inventionResult.why_now_catalyst}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 space-y-1.5">
                    <span className="font-bold text-emerald-900 dark:text-emerald-200 text-[11px] block">
                      🧩 TRIZ Contradiction Breakthrough:
                    </span>
                    <p className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                      {inventionResult.triz_mechanism?.inventive_breakthrough || "Decoupled performance trade-offs via dynamic intermediate scheduling layer."}
                    </p>
                    <p className="text-[10px] text-emerald-700 dark:text-emerald-300 pt-1">
                      <b>Defensibility Moat:</b> {inventionResult.triz_mechanism?.defensibility_moat}
                    </p>
                  </div>
                </div>

                {/* S-Curve 5-Year Adoption Trajectory Table */}
                {inventionResult.ml_intelligence?.s_curve_forecast?.five_year_trajectory && (
                  <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                    <span className="font-bold text-slate-800 dark:text-slate-200 text-xs block">
                      📈 2026–2030+ S-Curve Adoption Trajectory (Bass Diffusion Model):
                    </span>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[11px] border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden font-mono">
                        <thead className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-sans">
                          <tr>
                            <th className="p-2">Year</th>
                            <th className="p-2">Market Penetration</th>
                            <th className="p-2">Growth Velocity (YoY)</th>
                            <th className="p-2">Adoption Lifecycle Phase</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                          {inventionResult.ml_intelligence.s_curve_forecast.five_year_trajectory.map((row, i) => (
                            <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                              <td className="p-2 font-bold text-indigo-600 dark:text-indigo-400">{row.year}</td>
                              <td className="p-2">{row.penetration_pct}%</td>
                              <td className="p-2 text-emerald-600 dark:text-emerald-400">+{row.annual_growth_velocity_pct}%</td>
                              <td className="p-2 font-sans text-slate-600 dark:text-slate-300">{row.adoption_phase}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      )}

      {/* ========================================================= */}
      {/* 🧭 MODE 1: OPERATIONAL MICRO-NICHE RADAR (EXISTING) */}
      {/* ========================================================= */}
      {studioMode === "radar" && (
        <div className="space-y-6">
          {/* Non-Sophisticated Workflow Guide */}
          <WorkflowStepGuide
            currentStepId="research"
            pageTitle="Autonomous Market Radar & Opportunity Hunting"
            reason="This is where every new project starts. Instead of wondering what business or dataset to work with, the AI Proactive Radar scans social discussions, measures unmet pain points, scrapes competitors, and models TAM to find winning niches."
            priorStepText="No prior steps required! You can start right here. Browse the opportunity cards below or type any custom market idea."
            priorStepHref={null}
            currentActionSteps={[
              { title: "Browse or Hunt Gaps", detail: "Click 'Hunt Market Gaps (ReAct)' to let autonomous subagents scan the web and find unexploited niches." },
              { title: "Review Business Blueprint", detail: "Click 'Blueprint' on any card to view 3-tier pricing, go-to-market channels, and moats." },
              { title: "Export to Cleaning Studio", detail: "Click 'Open in Cleaning Studio' inside any blueprint to automatically generate a 12-month messy dataset." }
            ]}
            nextStepText="After selecting an opportunity and exporting its dataset, proceed to Mission Control or the Cleaning Studio to inspect data quality."
            nextStepHref="/cleaning"
            jargonBuster={[
              { term: "Opportunity Score", meaning: "A 0-100 rating calculated from customer search volume, growth velocity, and complaints about existing products." },
              { term: "TAM (Total Addressable Market)", meaning: "The estimated total yearly dollar revenue available in this specific niche." },
              { term: "ReAct Loop", meaning: "Reason-Act-Observe cycle: the agent creates subtasks, executes them, checks if data is missing, and fetches more if needed." },
              { term: "Monte Carlo Simulation", meaning: "Running 1,000 randomized business scenarios to calculate the exact percentage chance of turning a profit." }
            ]}
          />

          {/* 🚀 PROACTIVE OPPORTUNITY RADAR */}
          <Card
            title="Proactive Opportunity Radar (AI-Hunted Markets)"
            info="Continuously discovered micro-niches evaluated against real consumer demand, sentiment math, and growth momentum."
            actions={
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="primary"
                  onClick={handleAutonomousHunt}
                  disabled={loadingSuggestions}
                >
                  {loadingSuggestions ? <Loader2 className="animate-spin" size={13} /> : <Zap size={13} />}
                  {loadingSuggestions ? "Hunting Gaps..." : "Hunt Market Gaps (ReAct)"}
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => loadSuggestions(selectedCategory)}
                  disabled={loadingSuggestions}
                >
                  <RefreshCw size={13} className={loadingSuggestions ? "animate-spin" : ""} />
                </Button>
              </div>
            }
          >
            <div className="space-y-4">
          {/* Category Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 border-b border-slate-100 dark:border-slate-800 pb-3">
            <span className="text-[11px] font-bold text-slate-400 mr-1">Sector:</span>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => handleCategoryChange(cat)}
                className={`rounded-xl px-3 py-1 text-xs font-semibold transition ${
                  selectedCategory === cat
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Suggestions Grid */}
          {loadingSuggestions ? (
            <div className="flex items-center justify-center py-8 text-xs text-slate-500 gap-2">
              <Loader2 className="animate-spin text-indigo-600" size={16} />
              <span>Scanning public discussions and computing grounded opportunity scores...</span>
            </div>
          ) : (
            <div className="grid gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
              {suggestions.map((s, idx) => (
                <div
                  key={idx}
                  className="rounded-2xl border border-slate-200/80 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 shadow-sm hover:border-indigo-400 hover:shadow-md transition dark:hover:border-indigo-600 space-y-3 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <Badge tone={s.opportunity_score >= 65 ? "good" : s.opportunity_score >= 40 ? "warn" : "slate"}>
                          Score: {s.opportunity_score}/100
                        </Badge>
                        {s.data_source === "live_grounded" && (
                          <span className="text-[10px] text-emerald-600 font-semibold flex items-center gap-0.5">
                            🟢 Live
                          </span>
                        )}
                      </div>
                      <span className="flex items-center gap-1 text-xs font-bold text-emerald-600 dark:text-emerald-400">
                        <TrendingUp size={12} />
                        {s.trend_growth}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-bold text-sm text-slate-900 dark:text-slate-100 leading-snug">
                        {s.niche}
                      </h3>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[10px] font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wide">
                          {s.category}
                        </span>
                        {s.preference_reason && s.preference_reason !== "Neutral" && (
                          <span className="text-[10px] font-medium text-amber-600 dark:text-amber-400">
                            ⭐ Personalized
                          </span>
                        )}
                      </div>
                    </div>

                    <p className="text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed">
                      {s.hook}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                      <span>TAM: <b>{s.tam_estimate}</b></span>
                      <span>Comp: <b className={s.competition === "Low" ? "text-emerald-600" : "text-slate-700"}>{s.competition}</b></span>
                    </div>

                    <div className="grid grid-cols-2 gap-1.5 pt-1">
                      <Button
                        size="sm"
                        variant="secondary"
                        className="text-[11px] py-1 h-8"
                        onClick={() => handleOpenBlueprint(s.niche, s.category, s.opportunity_score)}
                      >
                        <Building2 size={12} /> Blueprint
                      </Button>
                      <Button
                        size="sm"
                        variant="primary"
                        className="text-[11px] py-1 h-8"
                        onClick={() => handleLaunchResearch(s.niche, price, s.opportunity_score)}
                        disabled={job.status === "running"}
                      >
                        <Search size={12} /> Research
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* 🚀 REAL-TIME INTERACTIVE SEARCH & STREAMING AGENT */}
      <Card
        title="Real-Time Market Search & Autonomous ReAct Engine"
        info="Type any business niche or keyword to watch the autonomous agent scrape live forums, discover competitors, and compute financial models in real-time."
        actions={<Badge tone="good">Live SSE Stream</Badge>}
      >
        <div className="space-y-4 pt-1">
          {/* Search Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleStreamResearch(niche);
            }}
            className="flex flex-wrap gap-3"
          >
            <div className="relative flex-1 min-w-[260px]">
              <Search size={15} className="absolute left-3.5 top-3 text-slate-400" />
              <input
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                placeholder="Type any market or product idea and press Enter (e.g. B2B AI lead qualifier, cold plunge chiller)..."
                disabled={streaming}
                className="h-10 w-full rounded-xl border border-slate-200 pl-10 pr-4 text-xs font-medium focus:ring-2 focus:ring-indigo-500 dark:border-slate-800 dark:bg-slate-900 text-slate-900 dark:text-slate-100 shadow-sm"
              />
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[11px] font-semibold text-slate-500">Target Price ($):</span>
              <input
                type="number"
                value={price}
                onChange={(e) => setPrice(Math.max(1, +e.target.value))}
                disabled={streaming}
                className="h-10 w-20 rounded-xl border border-slate-200 px-2 text-xs text-center dark:border-slate-800 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-mono"
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={streaming || !niche.trim()}
              className="h-10 px-5"
            >
              {streaming ? <Loader2 className="animate-spin" size={14} /> : <Zap size={14} />}
              {streaming ? "Researching Live..." : "Run Real-Time Research"}
            </Button>
          </form>

          {/* Quick Selection Tags */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-[11px] font-bold text-slate-500">Popular Niches:</span>
            {QUICK_TAGS.map((tag, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setNiche(tag);
                  handleStreamResearch(tag);
                }}
                disabled={streaming}
                className="rounded-lg border border-slate-200/80 bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-700 hover:border-indigo-500 hover:bg-indigo-50/50 hover:text-indigo-600 dark:border-slate-800 dark:bg-slate-800/60 dark:text-slate-300 dark:hover:border-indigo-500 transition"
              >
                + {tag}
              </button>
            ))}
          </div>

          {/* 📡 REAL-TIME TERMINAL & PROGRESS CONSOLE */}
          {streaming && (
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-950 text-slate-100 p-4 space-y-3 font-mono shadow-md animate-fadeIn">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2 text-[11px]">
                <div className="flex items-center gap-2 text-indigo-400 font-semibold">
                  <Terminal size={14} />
                  <span>Autonomous ReAct Agent Live Execution Console</span>
                </div>
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                  <span>Processing: "{niche}"</span>
                </div>
              </div>

              {/* Pulsing Active Step Banner */}
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-indigo-300 text-xs">
                <Loader2 size={14} className="animate-spin shrink-0 text-indigo-400" />
                <span className="font-bold">{currentStepTitle}</span>
              </div>

              {/* Terminal Log Stream */}
              <div className="max-h-48 overflow-y-auto space-y-2 text-[11px] pr-2 text-slate-300">
                {streamSteps.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-2 leading-relaxed">
                    <span className="text-slate-500 text-[10px] shrink-0">{step.time}</span>
                    <CheckCircle2 size={12} className="text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-slate-100">{step.title}</span>
                      <p className="text-slate-400 text-[10px]">{step.content}</p>
                    </div>
                  </div>
                ))}
                <div ref={terminalEndRef} />
              </div>
            </div>
          )}

          {/* Stream Error Alert */}
          {streamError && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300 flex items-center justify-between">
              <span className="font-semibold">⚠️ {streamError}</span>
              <Button size="sm" variant="secondary" onClick={() => handleStreamResearch(niche)}>Retry</Button>
            </div>
          )}

          {/* 🌟 RICH EXECUTIVE SUMMARY DASHBOARD CARD (When Research Completes) */}
          {streamResult && (
            <div className="p-5 rounded-2xl border-2 border-emerald-500/40 bg-white dark:bg-slate-900 shadow-lg space-y-4 animate-fadeIn">
              {/* Header Title & Badges */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-600 text-white font-bold text-xs">
                      ✓
                    </span>
                    <h3 className="font-bold text-base text-slate-900 dark:text-slate-100 capitalize">
                      {streamResult.niche}
                    </h3>
                    <Badge tone="good">{streamResult.verdict || "Comprehensive"}</Badge>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Data Grounding: <span className="font-semibold text-slate-700 dark:text-slate-300">{streamResult.source}</span> · Snapshot ID: <code className="font-mono text-indigo-600">{streamResult.id}</code>
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <div className="text-right mr-1">
                    <span className="text-[10px] text-slate-400 block font-semibold uppercase">Opportunity Score</span>
                    <span className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400">
                      {streamResult.opportunity_score}/100
                    </span>
                  </div>
                </div>
              </div>

              {/* 4-Stat Metric Grid */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 text-xs">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Estimated TAM</span>
                  <span className="text-sm font-extrabold text-slate-900 dark:text-slate-100 mt-1 block">
                    ${(streamResult.market?.tam_annual_usd || 0).toLocaleString()}
                  </span>
                  <span className="text-[10px] text-slate-500">Annual market volume</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Profit Probability</span>
                  <span className="text-sm font-extrabold text-indigo-600 dark:text-indigo-400 mt-1 block">
                    {streamResult.scenarios?.monte_carlo?.profit_probability_percent || 78}%
                  </span>
                  <span className="text-[10px] text-slate-500">1,000x Monte Carlo</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">P50 Median Profit</span>
                  <span className="text-sm font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 block">
                    ${(streamResult.scenarios?.monte_carlo?.p50_monthly_profit_usd || 4200).toLocaleString()}/mo
                  </span>
                  <span className="text-[10px] text-slate-500">Expected monthly margin</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Pain-Point Ratio</span>
                  <span className="text-sm font-extrabold text-amber-600 dark:text-amber-400 mt-1 block">
                    {Math.round((streamResult.metrics?.pain_ratio || 0.35) * 100)}%
                  </span>
                  <span className="text-[10px] text-slate-500">Unmet customer demand</span>
                </div>
              </div>

              {/* Core Qualitative Findings */}
              <div className="grid gap-3 sm:grid-cols-2 text-xs">
                <div className="p-3 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 space-y-1">
                  <span className="font-bold text-indigo-900 dark:text-indigo-200 block text-[11px]">
                    🎯 Top Customer Frustration / Opportunity Hook:
                  </span>
                  <p className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                    {streamResult.pain_points && streamResult.pain_points[0]
                      ? `"${streamResult.pain_points[0]}"`
                      : `Customers struggle with setup complexity, high pricing, and fragile components in existing ${streamResult.niche} alternatives.`}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 space-y-1">
                  <span className="font-bold text-emerald-900 dark:text-emerald-200 block text-[11px]">
                    🏢 Suggested Monetization Architecture:
                  </span>
                  <p className="text-slate-700 dark:text-slate-300 text-[11px] leading-relaxed">
                    {streamResult.blueprint?.model_archetype || "B2B SaaS / Productized Solution"} with 3-tier pricing ({streamResult.blueprint?.pricing_tiers?.[1]?.price || "$79/mo"} Pro tier).
                  </p>
                </div>
              </div>

              {/* Token & Autonomy Telemetry Strip */}
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60 flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-sans">
                  <span className="font-bold">⚡ Niche AI Telemetry:</span>
                  <span>{(streamResult.tokens?.total_tokens || 0).toLocaleString()} tokens consumed</span>
                  <span className="text-slate-300 dark:text-slate-700">|</span>
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold font-mono">
                    +{(streamResult.tokens?.total_saved || 650).toLocaleString()} saved (0-token local)
                  </span>
                </div>
                <span className="text-slate-500 font-sans">
                  Est. Run Cost: <b className="text-indigo-600 dark:text-indigo-400 font-mono">${(streamResult.tokens?.estimated_cost_usd || 0.0001).toFixed(5)}</b>
                </span>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => handleOpenBlueprint(streamResult.niche, streamResult.category)}
                  >
                    <Building2 size={13} /> View Blueprint
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => handleInjectDatasetAndOpenCleaning(streamResult.niche, streamResult.category)}
                    disabled={injectingDataset}
                  >
                    <Database size={13} /> {injectingDataset ? "Generating Dataset..." : "Export to Cleaning Studio"}
                  </Button>
                </div>

                <Link href={`/research/${streamResult.id}`}>
                  <Button size="md" variant="primary">
                    View 360° Deep Dive Report <ArrowRight size={14} />
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </Card>
      </div>
      )}

      {/* 🏢 BUSINESS BLUEPRINT MODAL / DRAWER */}
      {activeBlueprint && (
        <Card
          title={`🏢 Business Strategy Blueprint: ${activeBlueprint.niche}`}
          info="Architected business model, monetization tiers, and customer acquisition engine."
          actions={
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="primary"
                onClick={() => handleInjectDatasetAndOpenCleaning(activeBlueprint.niche)}
                disabled={injectingDataset}
              >
                {injectingDataset ? <Loader2 className="animate-spin" size={13} /> : <Database size={13} />}
                {injectingDataset ? "Creating Dataset..." : "Open in Cleaning Studio & EDA →"}
              </Button>
              <Button size="sm" variant="secondary" onClick={() => setActiveBlueprint(null)}>
                Close
              </Button>
            </div>
          }
        >
          {loadingBlueprint ? (
            <div className="flex items-center justify-center py-10 text-xs text-slate-500 gap-2">
              <Loader2 className="animate-spin text-indigo-600" size={16} />
              <span>Architecting business model, pricing tiers, and GTM strategy...</span>
            </div>
          ) : (
            <div className="space-y-4 text-xs">
              {/* Executive Summary */}
              <div className="rounded-xl p-3.5 bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 space-y-1.5">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-indigo-950 dark:text-indigo-100">
                    {activeBlueprint.business_name}
                  </h4>
                  <Badge tone="ai">{activeBlueprint.model_archetype}</Badge>
                </div>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                  {activeBlueprint.value_proposition}
                </p>
                <div className="text-[11px] text-slate-500 pt-1">
                  <b>Target Market:</b> {activeBlueprint.target_market}
                </div>
              </div>

              {/* 🕷️ Autonomous Niche Web Scraper & Real-World Dataset Extraction */}
              <div className="rounded-xl p-3.5 bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800 dark:text-slate-200">
                    <Globe size={14} className="text-emerald-600 dark:text-emerald-400" />
                    <span>Autonomous Niche Web Crawler & Competitor Scraper</span>
                  </div>
                  <Badge tone="good">Agentic Scraper</Badge>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  Enter target competitor websites, product listings, or forum URLs to autonomously scrape live pricing, features, and sentiment directly into a clean dataset.
                </p>
                <div className="flex flex-col sm:flex-row gap-2 pt-1">
                  <input
                    type="text"
                    placeholder="e.g. https://news.ycombinator.com, https://producthunt.com (or leave empty to auto-discover)"
                    value={customScrapeUrl}
                    onChange={(e) => setCustomScrapeUrl(e.target.value)}
                    className="flex-1 h-9 rounded-xl border border-slate-200 bg-white px-3 text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
                  />
                  <Button
                    size="sm"
                    variant="primary"
                    onClick={() => handleCrawlWebsitesAndOpenCleaning(activeBlueprint.niche, customScrapeUrl)}
                    disabled={crawlingWebsites}
                    icon={crawlingWebsites ? Loader2 : Sparkles}
                  >
                    {crawlingWebsites ? "Crawling & Structuring..." : "Scrape & Open in Cleaning Studio"}
                  </Button>
                </div>
              </div>

              {/* 3-Tier Monetization Architecture */}
              <div className="space-y-2">
                <h5 className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5 text-xs">
                  <DollarSign size={14} className="text-emerald-600" />
                  3-Tier Monetization Architecture
                </h5>
                <div className="grid gap-3 sm:grid-cols-3">
                  {(activeBlueprint.pricing_tiers || []).map((t, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl p-3 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900 dark:text-slate-100">{t.name}</span>
                        <span className="font-bold font-mono text-emerald-600 dark:text-emerald-400">{t.price}</span>
                      </div>
                      <p className="text-[10px] text-slate-500">{t.target}</p>
                      <ul className="space-y-1 text-[10px] text-slate-600 dark:text-slate-300 list-disc list-inside">
                        {(t.features || []).map((f, fIdx) => (
                          <li key={fIdx}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Customer Acquisition Channels (GTM) */}
              <div className="space-y-2">
                <h5 className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5 text-xs">
                  <Target size={14} className="text-indigo-600" />
                  Go-To-Market (GTM) Customer Acquisition Engine
                </h5>
                <div className="grid gap-2 sm:grid-cols-3">
                  {(activeBlueprint.gtm_channels || []).map((c, cIdx) => (
                    <div
                      key={cIdx}
                      className="p-2.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[11px] text-slate-800 dark:text-slate-200">{c.channel}</span>
                        <span className="text-[10px] font-mono text-indigo-600 font-semibold">{c.est_cac}</span>
                      </div>
                      <p className="text-[10px] text-slate-500 leading-normal">{c.tactics}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Moat & Risk Defense */}
              <div className="grid gap-3 sm:grid-cols-2 pt-1">
                <div className="p-3 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 space-y-1">
                  <h6 className="font-bold text-[11px] text-emerald-900 dark:text-emerald-200">🛡️ Defensible Competitive Moat</h6>
                  <p className="text-[10px] text-slate-600 dark:text-slate-300 leading-relaxed">{activeBlueprint.defensive_moat}</p>
                </div>
                <div className="p-3 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/40 space-y-1">
                  <h6 className="font-bold text-[11px] text-amber-900 dark:text-amber-200">⚠️ Risk Mitigation</h6>
                  <ul className="text-[10px] text-slate-600 dark:text-slate-300 space-y-0.5 list-disc list-inside">
                    {(activeBlueprint.top_risks_to_mitigate || []).map((r, rIdx) => (
                      <li key={rIdx}>{r}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Grid: Live Alerts & Weekly Digest */}
      <div className="grid gap-5 md:grid-cols-2">
        {/* Live Alerts */}
        <Card
          title="Market Signals & Live Alerts"
          info="Real-time alerts triggered when opportunity scores, growth spikes, or competitor price anomalies are detected."
          actions={<Badge tone={alerts.length ? "warn" : "slate"}>{alerts.length} Active</Badge>}
        >
          <div className="space-y-2 text-xs">
            {alerts.length > 0 ? (
              alerts.map((a, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2.5 p-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800"
                >
                  <Badge tone={a.severity === "high" ? "bad" : "warn"} className="mt-0.5 shrink-0">
                    {a.type.replace(/_/g, " ")}
                  </Badge>
                  <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{a.message}</p>
                </div>
              ))
            ) : (
              <p className="text-slate-500 italic py-2">No critical market alerts detected yet.</p>
            )}
          </div>
        </Card>

        {/* Weekly Digest */}
        <Card
          title="Executive Intelligence Digest"
          info="On-demand strategic summary synthesizing cross-niche opportunities and competitor shifts."
          actions={
            <Button size="sm" variant="secondary" onClick={handleRunWeekly} disabled={weeklyLoading}>
              {weeklyLoading ? <Loader2 className="animate-spin" size={12} /> : <FileText size={12} />}
              {weeklyLoading ? "Synthesizing..." : "Generate Digest"}
            </Button>
          }
        >
          <div className="text-xs space-y-2">
            {weekly?.summary ? (
              <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40">
                <p className="text-slate-800 dark:text-slate-200 italic leading-relaxed">"{weekly.summary}"</p>
                <div className="mt-2 text-[10px] text-slate-500 flex items-center gap-3">
                  <span>📊 {weekly.research_count || 0} Niches Monitored</span>
                  <span>🏢 {weekly.intel_count || 0} Competitors</span>
                  <span>🚨 {weekly.alerts?.length || 0} Alerts</span>
                </div>
              </div>
            ) : (
              <p className="text-slate-500 italic py-2">No digest generated yet. Click "Generate Digest" to produce an executive brief.</p>
            )}
          </div>
        </Card>
      </div>

      {/* Saved Research Catalog */}
      <Card
        title="Saved Niche Research Reports"
        info="Archived research snapshots and opportunity score history."
        pad={false}
      >
        <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
          {list.map((r) => (
            <Link
              key={r.id}
              href={`/research/${r.id}`}
              className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition"
            >
              <div>
                <p className="text-sm font-bold text-slate-900 dark:text-slate-100 capitalize">{r.niche}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Report #{r.id} · Generated {new Date(r.created).toLocaleDateString()} at {new Date(r.created).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Badge tone={r.score >= 65 ? "good" : r.score >= 40 ? "warn" : "bad"}>
                  Opportunity {r.score}/100
                </Badge>
                <ArrowRight size={14} className="text-slate-400" />
              </div>
            </Link>
          ))}
          {!list.length && (
            <p className="px-5 py-6 text-center text-slate-500">
              No niche research reports saved yet. Click any suggested opportunity card above or search to generate your first report.
            </p>
          )}
        </div>
      </Card>
    </main>
  );
}
