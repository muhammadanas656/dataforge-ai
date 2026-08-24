"use client";
import { useState } from "react";
import { Card, Button, Badge } from "./ui";
import { useJob } from "../hooks/useJob";
import { useDataset } from "./DatasetContext";
import { authFetch } from "../api";
import { Globe, ShieldAlert, ShieldCheck, AlertTriangle, Loader2, Sparkles, Database, CheckCircle2 } from "lucide-react";

export default function WebScraperModal({ onClose }) {
  const [url, setUrl] = useState("");
  const [proxy, setProxy] = useState("");
  const [maxPages, setMaxPages] = useState(5);
  const [isStarting, setIsStarting] = useState(false);
  const [startError, setStartError] = useState(null);
  const { refresh, setDatasetId } = useDataset();
  const job = useJob("scrape", { url: "" }, { autoStart: false });

  const handleStart = async () => {
    if (!url.trim() || isStarting) return;
    setIsStarting(true);
    setStartError(null);
    try {
      const res = await authFetch("/api/scrape/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), max_pages: Number(maxPages), proxy: proxy || undefined })
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setStartError(err.detail || `Server error ${res.status}`);
      }
    } catch (e) {
      setStartError("Could not reach backend. Is it running?");
      console.error("Scrape start failed:", e);
    } finally {
      setIsStarting(false);
    }
  };

  const handleDirectScrape = async () => {
    if (!url.trim()) return;
    job.start({ url: url.trim(), max_pages: Number(maxPages), proxy: proxy || undefined });
  };

  const handleApplyDataset = (did) => {
    if (did) {
      setDatasetId(did);
      refresh();
      if (onClose) onClose();
    }
  };

  return (
    <Card 
      title="Agentic Web Scraping Ingest Engine" 
      info="Autonomous crawler with DOM table extraction, microdata parsing, and GDPR/ToS compliance scanning."
      actions={<Badge tone="ai">Agentic Ingestion</Badge>}
    >
      <div className="space-y-4 text-xs">
        <div>
          <label className="block font-bold text-slate-700 dark:text-slate-300 mb-1">Target Web URL to Scrape</label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Globe size={14} className="absolute left-3 top-2.5 text-slate-400" />
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/products or https://en.wikipedia.org/wiki/..."
                className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 text-xs"
              />
            </div>
            <select
              value={maxPages}
              onChange={(e) => setMaxPages(e.target.value)}
              className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 text-xs"
            >
              <option value="1">1 Page</option>
              <option value="3">3 Pages</option>
              <option value="5">5 Pages</option>
              <option value="10">10 Pages</option>
            </select>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Button 
            variant="primary" 
            size="md" 
            onClick={handleDirectScrape} 
            disabled={job.status === "running" || !url.trim()}
          >
            {job.status === "running" ? <Loader2 className="animate-spin" size={14} /> : <Sparkles size={14} />}
            {job.status === "running" ? "Agent is Crawling & Extracting..." : "Launch Agentic Scraper"}
          </Button>

          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>Close</Button>
          )}
        </div>

        {/* Error banner */}
        {startError && (
          <div className="p-2.5 rounded-lg bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 flex items-center gap-2 text-[11px] text-rose-700 dark:text-rose-300">
            <AlertTriangle size={13} className="flex-shrink-0" />
            <span>{startError}</span>
          </div>
        )}

        {/* Live Progress Logs */}
        {job.status === "running" && (
          <div className="p-3.5 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50 space-y-2">
            <div className="flex items-center gap-2 text-indigo-900 dark:text-indigo-200 font-bold text-[11px]">
              <Loader2 className="animate-spin text-indigo-600" size={13} />
              <span>Analyzing DOM elements, structured schemas, and following pagination links...</span>
            </div>
            {job.progressMessage && (
              <p className="text-[10px] font-mono text-slate-600 dark:text-slate-400">{job.progressMessage}</p>
            )}
          </div>
        )}

        {/* Results / Compliance / Action */}
        {job.status === "done" && job.result && (
          <div className="space-y-3 pt-2 border-t border-slate-100 dark:border-slate-800">
            {/* Success Summary */}
            {job.result.status === "success" && (
              <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-emerald-900 dark:text-emerald-200 flex items-center gap-1.5 text-xs">
                    <CheckCircle2 size={14} className="text-emerald-600" /> Scraping Ingest Completed!
                  </span>
                  <Badge tone="good">{job.result.stats?.rows_extracted || 0} rows extracted</Badge>
                </div>
                <p className="text-[11px] text-emerald-800 dark:text-emerald-300">
                  Data automatically converted into canonical schema and saved to <code className="font-mono">{job.result.csv_path}</code>.
                </p>
                {job.result.dataset_id && (
                  <div className="flex flex-wrap gap-2 pt-1">
                    <Button 
                      size="sm" 
                      variant="primary" 
                      onClick={() => handleApplyDataset(job.result.dataset_id)}
                    >
                      <Database size={13} /> Set Active & Profile
                    </Button>
                    <a href="/cleaning">
                      <Button 
                        size="sm" 
                        variant="secondary"
                        onClick={() => handleApplyDataset(job.result.dataset_id)}
                      >
                        Open in Cleaning Studio →
                      </Button>
                    </a>
                  </div>
                )}
              </div>
            )}

            {/* ToS Check */}
            {job.result.tos_check && (
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  {job.result.tos_check.status === "high_risk" ? (
                    <ShieldAlert size={15} className="text-rose-500" />
                  ) : (
                    <ShieldCheck size={15} className="text-emerald-500" />
                  )}
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-200 text-[11px]">Terms of Service Audit</p>
                    <p className="text-[10px] text-slate-500">{job.result.tos_check.reason}</p>
                  </div>
                </div>
                <Badge tone={job.result.tos_check.status === "high_risk" ? "bad" : "good"}>
                  {job.result.tos_check.status}
                </Badge>
              </div>
            )}

            {/* PII Check */}
            {job.result.pii_check?.status === "gdpr_risk" && (
              <div className="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/60">
                <div className="flex items-center gap-1.5 text-amber-800 dark:text-amber-300 font-bold text-[11px]">
                  <AlertTriangle size={14} /> <span>GDPR / PII Privacy Detected</span>
                </div>
                <p className="text-[10px] text-slate-600 dark:text-slate-400 mt-0.5">
                  Scraped columns contain potential personal data: {job.result.pii_check.columns?.map(c => c.column).join(", ")}.
                </p>
              </div>
            )}

            {/* CAPTCHA / Blocked Intervention */}
            {job.result.status === "blocked_captcha" && (
              <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 space-y-2">
                <p className="font-bold text-rose-800 dark:text-rose-300 text-[11px]">🛑 Anti-Bot Challenge Encountered</p>
                <p className="text-[10px] text-slate-600 dark:text-slate-400">
                  Target site presented a CAPTCHA at {job.result.blocked_url}. Provide an unblocked proxy URL to bypass.
                </p>
                <div className="flex gap-2">
                  <input 
                    value={proxy} 
                    onChange={e => setProxy(e.target.value)} 
                    placeholder="http://user:pass@proxy:8080" 
                    className="flex-1 rounded-lg border border-slate-200 dark:border-slate-800 p-1.5 text-[11px] bg-white dark:bg-slate-900"
                  />
                  <Button size="sm" variant="secondary" onClick={handleDirectScrape}>Retry with Proxy</Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
