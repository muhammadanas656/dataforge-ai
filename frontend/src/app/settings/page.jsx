"use client";
import { useEffect, useState } from "react";
import { Card, Button, Badge, StatTile, PageHeader } from "../components/ui";
import { getApiUrl, setCustomApiUrl } from "../api";
import {
  Settings as SettingsIcon,
  Loader2,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  Sparkles,
  Cpu,
  Key,
  Globe,
  Server,
  Zap,
  Eye,
  EyeOff,
  Copy,
  Check,
  RefreshCw,
} from "lucide-react";

const PROVIDER_PRESETS = {
  groq: [
    { label: "GPT-OSS 20B (Default High-Speed)", value: "openai/gpt-oss-20b" },
    { label: "Llama 3.3 70B Versatile", value: "llama-3.3-70b-versatile" },
    { label: "Llama 3.1 8B Instant", value: "llama-3.1-8b-instant" },
    { label: "Mixtral 8x7B 32k", value: "mixtral-8x7b-32768" },
  ],
  openai: [
    { label: "GPT-4o Mini (Recommended)", value: "gpt-4o-mini" },
    { label: "GPT-4o", value: "gpt-4o" },
    { label: "o3-mini (High Reasoning)", value: "o3-mini" },
  ],
  gemini: [
    { label: "Gemini 2.5 Flash", value: "gemini-2.5-flash" },
    { label: "Gemini 2.5 Pro", value: "gemini-2.5-pro" },
  ],
  anthropic: [
    { label: "Claude 3.5 Sonnet", value: "claude-3-5-sonnet-20241022" },
    { label: "Claude 3.5 Haiku", value: "claude-3-5-haiku-20241022" },
  ],
};

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState("http://localhost:8000");
  const [customUrlInput, setCustomUrlInput] = useState("");
  const [apiConnected, setApiConnected] = useState(null);
  const [pinging, setPinging] = useState(false);

  const [settings, setSettings] = useState({
    provider: "groq",
    model: "openai/gpt-oss-20b",
    api_key: "",
    api_key_masked: "",
    has_key: false,
    fallback: "none",
    auto_l3: true,
    alert_threshold: 65,
  });

  const [showKey, setShowKey] = useState(false);
  const [tier, setTier] = useState(null);
  const [probing, setProbing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const [testingKey, setTestingKey] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [copiedEnv, setCopiedEnv] = useState(false);

  useEffect(() => {
    const currentUrl = getApiUrl();
    setApiUrl(currentUrl);
    setCustomUrlInput(currentUrl);
    checkHealth(currentUrl);
    loadSettings(currentUrl);
    loadTier(currentUrl);
  }, []);

  const checkHealth = async (baseUrl) => {
    setPinging(true);
    try {
      const r = await fetch(`${baseUrl}/health`);
      if (r.ok) {
        setApiConnected(true);
      } else {
        setApiConnected(false);
      }
    } catch {
      setApiConnected(false);
    } finally {
      setPinging(false);
    }
  };

  const loadSettings = async (baseUrl) => {
    try {
      const r = await fetch(`${baseUrl}/api/settings`);
      if (r.ok) {
        const data = await r.json();
        setSettings((prev) => ({ ...prev, ...data }));
      }
    } catch (e) {
      console.warn("Failed to load settings:", e);
    }
  };

  const loadTier = async (baseUrl) => {
    try {
      const r = await fetch(`${baseUrl}/api/model/tier`);
      if (r.ok) {
        const data = await r.json();
        setTier(data);
      }
    } catch (e) {
      console.warn("Failed to load tier:", e);
    }
  };

  const handleUpdateApiUrl = () => {
    const clean = customUrlInput.trim().replace(/\/$/, "");
    setCustomApiUrl(clean);
    setApiUrl(clean || "http://localhost:8000");
    checkHealth(clean || "http://localhost:8000");
    loadSettings(clean || "http://localhost:8000");
  };

  const testKey = async () => {
    setTestingKey(true);
    setTestResult(null);
    try {
      const r = await fetch(`${apiUrl}/api/settings/test-key`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider: settings.provider,
          model: settings.model,
          api_key: settings.api_key || undefined,
        }),
      });
      const res = await r.json();
      setTestResult(res);
    } catch (e) {
      setTestResult({ status: "error", message: e.message || "Failed to reach backend" });
    } finally {
      setTestingKey(false);
    }
  };

  const probe = async () => {
    setProbing(true);
    try {
      const r = await fetch(`${apiUrl}/api/model/probe`);
      const result = await r.json();
      setTier(result);
    } catch (e) {
      console.warn("Probe failed:", e);
    } finally {
      setProbing(false);
    }
  };

  const save = async () => {
    setSaving(true);
    try {
      const r = await fetch(`${apiUrl}/api/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      if (r.ok) {
        const data = await r.json();
        setSettings((prev) => ({ ...prev, ...data.settings }));
        setSaved(true);
        setTimeout(() => setSaved(false), 2500);
      }
    } catch (e) {
      console.warn("Save failed:", e);
    } finally {
      setSaving(false);
    }
  };

  const copyEnvSnippet = () => {
    const snippet = `# DataForge AI Environment Variables
api_provider=${settings.provider}
api_key=${settings.api_key || "<your-key-here>"}
api_model=${settings.model}
NEXT_PUBLIC_API_URL=${apiUrl}`;
    navigator.clipboard.writeText(snippet);
    setCopiedEnv(true);
    setTimeout(() => setCopiedEnv(false), 2000);
  };

  return (
    <main className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto space-y-6 animate-fade-in">
      <PageHeader
        title="System Settings & Connection Hub"
        subtitle="Manage LLM provider credentials, cloud API endpoints, resilience thresholds, and Vercel deployment essentials."
        breadcrumbs={[{ label: "Overview", href: "/" }, { label: "Settings" }]}
        actions={
          <Button
            onClick={save}
            loading={saving}
            icon={saved ? CheckCircle2 : Sparkles}
            variant={saved ? "secondary" : "primary"}
          >
            {saved ? "Saved Successfully" : "Save All Settings"}
          </Button>
        }
      />

      {/* Top Status Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatTile
          label="Backend Status"
          value={apiConnected === null ? "Checking..." : apiConnected ? "Connected" : "Offline"}
          sub={apiUrl}
          tone={apiConnected ? "good" : "bad"}
          icon={Server}
        />
        <StatTile
          label="Active Provider"
          value={settings.provider.toUpperCase()}
          sub={settings.model}
          tone="ai"
          icon={Cpu}
        />
        <StatTile
          label="API Key Guard"
          value={settings.has_key || settings.api_key ? "Configured" : "Unset"}
          sub={settings.api_key_masked || "Using environment default"}
          tone={settings.has_key || settings.api_key ? "good" : "warn"}
          icon={Key}
        />
        <StatTile
          label="Model Tier"
          value={tier?.tier ? tier.tier.toUpperCase() : "MID"}
          sub={tier?.score ? `Score: ${tier.score}/3 (${tier.percentage}%)` : "Resilience Ready"}
          tone="good"
          icon={ShieldCheck}
        />
      </div>

      {/* Section 1: AI Provider & API Key Credentials */}
      <Card
        title="LLM Intelligence & Credentials"
        info="Configure your AI model provider and credentials. Keys are saved locally and used for distillation, semantic typing, and future research engines."
        pad={true}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Provider Selector */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
                Primary LLM Provider
              </label>
              <select
                value={settings.provider}
                onChange={(e) => {
                  const p = e.target.value;
                  const defaultModel = PROVIDER_PRESETS[p]?.[0]?.value || "gpt-4o-mini";
                  setSettings({ ...settings, provider: p, model: defaultModel });
                }}
                className="w-full h-10 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 transition"
              >
                <option value="groq">Groq (Recommended — Ultra Fast LPU)</option>
                <option value="openai">OpenAI (GPT-4o / GPT-4o-mini)</option>
                <option value="gemini">Google Gemini (Gemini 2.5 Flash)</option>
                <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
              </select>
            </div>

            {/* Model Selector */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
                Target Model
              </label>
              <div className="flex gap-2">
                <select
                  value={settings.model}
                  onChange={(e) => setSettings({ ...settings, model: e.target.value })}
                  className="flex-1 h-10 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 transition"
                >
                  {(PROVIDER_PRESETS[settings.provider] || []).map((m) => (
                    <option key={m.value} value={m.value}>
                      {m.label}
                    </option>
                  ))}
                  <option value="custom">Custom Model Name...</option>
                </select>
              </div>
            </div>
          </div>

          {/* API Key Input */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
              API Key ({settings.provider.toUpperCase()})
            </label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                placeholder={settings.api_key_masked || "Enter your API key (e.g. gsk_... or sk-...)"}
                value={settings.api_key || ""}
                onChange={(e) => setSettings({ ...settings, api_key: e.target.value })}
                className="w-full h-10 rounded-xl border border-slate-200 bg-white pl-3.5 pr-20 text-xs font-mono text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 transition"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs font-medium flex items-center gap-1"
              >
                {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
                <span>{showKey ? "Hide" : "Show"}</span>
              </button>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
              Your key is protected locally in <code className="text-indigo-600 dark:text-indigo-400 font-mono">.env</code> and <code className="text-indigo-600 dark:text-indigo-400 font-mono">data/settings.json</code>.
            </p>
          </div>

          {/* Live Test Connection */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={testKey}
                loading={testingKey}
                icon={Zap}
              >
                Test Credentials & Latency
              </Button>
              {testResult && (
                <div className="flex items-center gap-1.5 text-xs font-semibold animate-fade-in">
                  {testResult.status === "success" ? (
                    <Badge tone="good">
                      <CheckCircle2 size={12} />
                      Connected ({testResult.latency_ms}ms)
                    </Badge>
                  ) : (
                    <Badge tone="bad">
                      <XCircle size={12} />
                      {testResult.message || "Failed"}
                    </Badge>
                  )}
                </div>
              )}
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={save}
              loading={saving}
              icon={saved ? CheckCircle2 : Sparkles}
            >
              {saved ? "Saved" : "Save Credentials"}
            </Button>
          </div>
        </div>
      </Card>

      {/* Section 2: Frontend & Backend Cloud Deployment (Vercel / GitHub) */}
      <Card
        title="Deployment & Backend Connection (Vercel / Cloud)"
        info="Connect your Vercel frontend build to your hosted FastAPI backend server (Render, Railway, Fly.io, AWS, etc.)."
        pad={true}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
              Backend API Server URL
            </label>
            <div className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                placeholder="http://localhost:8000 or https://your-backend.onrender.com"
                value={customUrlInput}
                onChange={(e) => setCustomUrlInput(e.target.value)}
                className="flex-1 h-10 rounded-xl border border-slate-200 bg-white px-3 text-xs font-mono text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 transition"
              />
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="md"
                  onClick={handleUpdateApiUrl}
                  loading={pinging}
                  icon={RefreshCw}
                >
                  Ping & Apply URL
                </Button>
                <Button
                  variant="ghost"
                  size="md"
                  onClick={() => {
                    setCustomUrlInput("http://localhost:8000");
                    setCustomApiUrl("");
                    setApiUrl("http://localhost:8000");
                    checkHealth("http://localhost:8000");
                  }}
                >
                  Reset Localhost
                </Button>
              </div>
            </div>
          </div>

          {/* Vercel Environment Variables Box */}
          <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900/50">
            <div className="flex items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 dark:text-slate-300">
                <Globe size={14} className="text-indigo-600 dark:text-indigo-400" />
                <span>Vercel / GitHub Production Environment Variables</span>
              </div>
              <button
                onClick={copyEnvSnippet}
                className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-semibold bg-white ring-1 ring-slate-200 hover:bg-slate-50 dark:bg-slate-800 dark:ring-slate-700 text-slate-700 dark:text-slate-200 transition"
              >
                {copiedEnv ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                <span>{copiedEnv ? "Copied!" : "Copy .env"}</span>
              </button>
            </div>
            <pre className="text-[11px] font-mono text-slate-600 dark:text-slate-400 overflow-x-auto leading-relaxed">
{`# Frontend (Vercel Project Settings -> Environment Variables)
NEXT_PUBLIC_API_URL=${apiUrl}

# Backend (.env or Cloud Platform Config)
api_provider=${settings.provider}
api_key=${settings.api_key_masked ? "<YOUR_SECRET_KEY>" : (settings.api_key || "<YOUR_SECRET_KEY>")}
api_model=${settings.model}`}
            </pre>
          </div>
        </div>
      </Card>

      {/* Section 3: Model Resilience & Autonomous Engine */}
      <Card
        title="Model Resilience & Autonomy Engine"
        info="Control automatic fallback strategies, probe model capabilities, and configure cost alert limits."
        pad={true}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
                Fallback Model Strategy
              </label>
              <select
                value={settings.fallback}
                onChange={(e) => setSettings({ ...settings, fallback: e.target.value })}
                className="w-full h-10 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 transition"
              >
                <option value="none">Deterministic Heuristics (Local RAG & Rules)</option>
                <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                <option value="gpt-4o-mini">OpenAI GPT-4o-mini</option>
                <option value="ollama">Local Ollama</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
                Daily Token Cost Alert Threshold ($)
              </label>
              <input
                type="number"
                value={settings.alert_threshold}
                onChange={(e) =>
                  setSettings({ ...settings, alert_threshold: parseFloat(e.target.value) || 0 })
                }
                className="w-full h-10 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 transition"
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200/80 bg-slate-50 dark:border-slate-800 dark:bg-slate-900/50">
            <div>
              <div className="text-xs font-bold text-slate-800 dark:text-slate-200">
                Autonomous L3 LLM Self-Healing
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">
                Automatically engage multi-pass code synthesis if deterministic transforms fail validation checks.
              </div>
            </div>
            <input
              type="checkbox"
              checked={settings.auto_l3}
              onChange={(e) => setSettings({ ...settings, auto_l3: e.target.checked })}
              className="h-4 w-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300"
            />
          </div>

          <div className="pt-2 flex items-center justify-between border-t border-slate-100 dark:border-slate-800">
            <Button
              variant="secondary"
              size="sm"
              onClick={probe}
              loading={probing}
              icon={Cpu}
            >
              Probe Model Capabilities & Resilience
            </Button>
            {tier && (
              <Badge tone="good">
                Tier: {tier.tier?.toUpperCase()} ({tier.score}/3)
              </Badge>
            )}
          </div>
        </div>
      </Card>
    </main>
  );
}
