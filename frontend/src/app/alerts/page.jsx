"use client";
import { useEffect, useState } from "react";
import { Card, Badge, Button } from "../components/ui";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { Bell, AlertTriangle, TrendingUp, DollarSign, Package, Loader2, RefreshCw } from "lucide-react";

const ALERT_ICONS = {
  hot_niche: { icon: TrendingUp, color: "text-rose-600 dark:text-rose-400" },
  rising_trend: { icon: TrendingUp, color: "text-amber-600 dark:text-amber-400" },
  price_movement: { icon: DollarSign, color: "text-emerald-600 dark:text-emerald-400" },
  feature_gap: { icon: Package, color: "text-indigo-600 dark:text-indigo-400" },
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const r = await fetch("http://localhost:8000/api/alerts");
      const d = await r.json();
      setAlerts(d.alerts || []);
    } catch (e) {
      console.warn("Failed loading alerts:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <main className="mx-auto max-w-6xl space-y-5 px-6 py-6 overflow-x-clip">
      <Breadcrumbs
        crumbs={[
          { href: "/", label: "Home" },
          { href: "/research", label: "Research & Market" },
          { label: "Market Alerts" },
        ]}
      />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Bell size={20} className="text-indigo-600 dark:text-indigo-400" />
            Consolidated Market & Intelligence Alerts
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Real-time high-conviction signals across niche opportunity scores, growth spikes, and competitor price movements
          </p>
        </div>

        <Button size="sm" variant="secondary" onClick={load} disabled={loading}>
          {loading ? <Loader2 className="animate-spin" size={13} /> : <RefreshCw size={13} />}
          {loading ? "Scanning signals..." : "Refresh Signals"}
        </Button>
      </div>

      <Card
        title="Active Intelligence Signals"
        info="Deduplicated signals filtered within a 24-hour suppression window to prevent alert fatigue."
        pad={false}
      >
        {loading ? (
          <p className="px-5 py-8 text-center text-xs text-slate-500">
            <Loader2 className="animate-spin inline-block mr-2" size={14} /> Scanning signals...
          </p>
        ) : alerts.length === 0 ? (
          <div className="px-5 py-8 text-center">
            <Bell className="mx-auto mb-2 text-slate-300 dark:text-slate-600" size={28} />
            <p className="text-xs text-slate-500">No active alerts detected. All monitored niches and competitor catalogs are stable.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
            {alerts.map((alert, i) => {
              const config = ALERT_ICONS[alert.type] || { icon: AlertTriangle, color: "text-slate-600" };
              const Icon = config.icon;
              return (
                <div key={i} className="flex items-start gap-3 px-5 py-3.5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                  <div className={`mt-0.5 shrink-0 ${config.color}`}>
                    <Icon size={16} />
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge tone={alert.severity === "high" ? "bad" : "warn"}>
                        {alert.type.replace(/_/g, " ")}
                      </Badge>
                      <span className="text-[10px] text-slate-400 uppercase font-semibold">
                        {alert.severity} priority
                      </span>
                    </div>
                    <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                      {alert.message}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {alerts.length > 0 && (
        <Card title="Alert Telemetry Breakdown" info="Distribution of active signals across intelligence categories.">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4 text-center">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700">
              <p className="text-xl font-bold text-rose-600 dark:text-rose-400">
                {alerts.filter((a) => a.severity === "high").length}
              </p>
              <p className="text-[11px] text-slate-500 font-medium mt-0.5">High Priority</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700">
              <p className="text-xl font-bold text-amber-600 dark:text-amber-400">
                {alerts.filter((a) => a.severity === "medium").length}
              </p>
              <p className="text-[11px] text-slate-500 font-medium mt-0.5">Medium Priority</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700">
              <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400">
                {alerts.filter((a) => a.type === "price_movement").length}
              </p>
              <p className="text-[11px] text-slate-500 font-medium mt-0.5">Price Moves</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700">
              <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                {alerts.filter((a) => a.type === "feature_gap").length}
              </p>
              <p className="text-[11px] text-slate-500 font-medium mt-0.5">Feature Gaps</p>
            </div>
          </div>
        </Card>
      )}
    </main>
  );
}
