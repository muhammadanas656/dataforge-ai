"use client";
import { Card, Badge } from "./ui";
import { TrendingDown, Minus, TrendingUp, DollarSign, Activity } from "lucide-react";

export function ScenarioPlanner({ scenarios }) {
  if (!scenarios || !scenarios.scenarios) return null;
  
  const { conservative, base, aggressive } = scenarios.scenarios;
  const monte_carlo = scenarios.monte_carlo;
  const recommendations = scenarios.recommendations || [];
  
  const scenarioCards = [
    {
      key: 'conservative',
      data: conservative,
      icon: TrendingDown,
      tone: 'warn',
      borderColor: 'border-amber-400',
      description: 'Slow growth & high CAC'
    },
    {
      key: 'base',
      data: base,
      icon: Minus,
      tone: 'good',
      borderColor: 'border-indigo-500',
      description: 'Expected operating performance'
    },
    {
      key: 'aggressive',
      data: aggressive,
      icon: TrendingUp,
      tone: 'ai',
      borderColor: 'border-emerald-500',
      description: 'High volume & viral scale'
    }
  ];
  
  return (
    <div className="space-y-4">
      {/* 3 Scenario Cards */}
      <div className="grid gap-3.5 sm:grid-cols-3">
        {scenarioCards.map(({ key, data, icon: Icon, tone, borderColor, description }) => (
          <div
            key={key}
            className={`rounded-2xl border-2 ${borderColor} bg-white dark:bg-slate-900 p-4 shadow-sm space-y-2.5`}
          >
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">{data.name}</h4>
                <p className="text-[10px] text-slate-500">{description}</p>
              </div>
              <Badge tone={tone}>
                <Icon size={12} className="inline mr-0.5" />
                {key}
              </Badge>
            </div>
            
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Units/mo:</span>
                <span className="font-mono font-semibold text-slate-900 dark:text-slate-100">{data.units_per_month}</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Selling Price:</span>
                <span className="font-mono font-semibold text-slate-900 dark:text-slate-100">${data.price_usd}</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Est. CAC:</span>
                <span className="font-mono font-semibold text-slate-900 dark:text-slate-100">${data.cac_usd}</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Growth / mo:</span>
                <span className="font-mono font-semibold text-slate-900 dark:text-slate-100">{(data.growth_rate_monthly * 100).toFixed(0)}%</span>
              </div>
              
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center text-xs">
                <span className="font-medium text-slate-500">Breakeven:</span>
                {data.breakeven_months ? (
                  <span className="font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                    Month {data.breakeven_months}
                  </span>
                ) : (
                  <Badge tone="bad">Long Runway</Badge>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Monte Carlo 1,000x Simulation Card */}
      {monte_carlo && !monte_carlo.error && (
        <div className="rounded-2xl border border-slate-200 bg-white dark:bg-slate-900 dark:border-slate-800 p-4 space-y-4 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <div>
              <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                <Activity size={16} className="text-indigo-600" />
                Monte Carlo Simulation Analysis ({monte_carlo.n_simulations || 1000} Iterations)
              </h4>
              <p className="text-[11px] text-slate-500">
                Models stochastic variance across monthly customer volume, conversion rates, and acquisition cost.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge tone={monte_carlo.risk_level === 'low' ? 'good' : monte_carlo.risk_level === 'medium' ? 'warn' : 'bad'}>
                Risk Profile: {monte_carlo.risk_level?.toUpperCase()}
              </Badge>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
              <span className="text-[10px] text-slate-500 block">Probability of Profit</span>
              <span className="text-xl font-extrabold text-emerald-600 font-mono">
                {(monte_carlo.probability_of_profit * 100).toFixed(0)}%
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
              <span className="text-[10px] text-slate-500 block">Expected Profit (P50)</span>
              <span className="text-xl font-extrabold text-slate-900 dark:text-slate-100 font-mono">
                ${monte_carlo.monthly_profit?.p50?.toLocaleString()}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
              <span className="text-[10px] text-slate-500 block">Worst-Case (P10)</span>
              <span className="text-xl font-extrabold text-rose-600 font-mono">
                ${monte_carlo.monthly_profit?.p10?.toLocaleString()}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
              <span className="text-[10px] text-slate-500 block">Best-Case Upside (P90)</span>
              <span className="text-xl font-extrabold text-indigo-600 font-mono">
                ${monte_carlo.monthly_profit?.p90?.toLocaleString()}
              </span>
            </div>
          </div>

          {/* Histogram Bar Chart */}
          {monte_carlo.histogram && (
            <div className="space-y-1.5 pt-2">
              <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300">
                Simulated Monthly Profit Distribution:
              </span>
              <div className="flex items-end gap-1 h-24 bg-slate-50 dark:bg-slate-800/30 p-2 rounded-xl border border-slate-100 dark:border-slate-800">
                {monte_carlo.histogram.map((bin, idx) => (
                  <div
                    key={idx}
                    className="flex-1 bg-indigo-500 hover:bg-indigo-600 rounded-t transition cursor-pointer"
                    style={{
                      height: `${Math.max(8, (bin.percentage / Math.max(...monte_carlo.histogram.map((b) => b.percentage || 1))) * 100)}%`
                    }}
                    title={`$${bin.bin_start} to $${bin.bin_end}: ${bin.count} iterations (${bin.percentage}%)`}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Strategic Recommendations */}
          {recommendations.length > 0 && (
            <div className="p-3 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 text-xs space-y-1 text-slate-700 dark:text-slate-300">
              <span className="font-bold text-indigo-900 dark:text-indigo-200">💡 Strategic Recommendations:</span>
              <ul className="list-disc list-inside space-y-0.5">
                {recommendations.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
