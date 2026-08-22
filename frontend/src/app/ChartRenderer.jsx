"use client";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, CartesianGrid, Cell
} from "recharts";
import { useTheme } from "./components/theme";

const PALETTE = ["#6366f1", "#8b5cf6", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#14b8a6"];

function useChartTheme() {
  const { dark } = useTheme();
  return {
    tick: { fill: dark ? "#94a3b8" : "#64748b", fontSize: 11 },
    grid: dark ? "#1e293b" : "#eef2f7",
    tooltip: {
      backgroundColor: dark ? "#0f172a" : "#ffffff",
      border: `1px solid ${dark ? "#1e293b" : "#e2e8f0"}`,
      borderRadius: 10,
      fontSize: 12,
      color: dark ? "#e2e8f0" : "#0f172a",
      boxShadow: "0 8px 24px rgba(0,0,0,.12)",
    },
  };
}

export function MplChart({ result }) {
  if (result?.image) {
    return (
      <div className="flex justify-center p-1 bg-white dark:bg-slate-900 rounded-xl">
        <img
          src={`data:image/png;base64,${result.image}`}
          alt={result.title || "Chart"}
          className="w-full max-w-2xl rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm"
        />
      </div>
    );
  }
  return <ChartRenderer result={result} />;
}

export default function ChartRenderer({ result }) {
  const t = useChartTheme();

  if (!result?.data?.length) {
    return <p className="text-sm text-slate-500 italic p-4 text-center">No data available to chart.</p>;
  }

  const { chart_type, x_column: x, y_column: y, data } = result;

  if (chart_type === "scatter") {
    return (
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={t.grid} strokeDasharray="3 3" />
            <XAxis dataKey={x} tick={t.tick} tickLine={false} axisLine={false} />
            <YAxis dataKey={y} tick={t.tick} tickLine={false} axisLine={false} width={60} />
            <Tooltip contentStyle={t.tooltip} cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={data} fill={PALETTE[0]} fillOpacity={0.7} shape="circle" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (chart_type === "histogram" || chart_type === "bar") {
    return (
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={t.grid} vertical={false} />
            <XAxis
              dataKey={x}
              tick={t.tick}
              tickLine={false}
              axisLine={false}
              interval={0}
              angle={data.length > 8 ? -20 : 0}
              textAnchor={data.length > 8 ? "end" : "middle"}
              height={data.length > 8 ? 60 : 30}
            />
            <YAxis tick={t.tick} tickLine={false} axisLine={false} width={50} />
            <Tooltip contentStyle={t.tooltip} cursor={{ fill: "rgba(99,102,241,.06)" }} />
            <Bar dataKey={y} radius={[6, 6, 0, 0]}>
              {data.map((e, i) => (
                <Cell key={i} fill={data.length <= 8 ? PALETTE[i % PALETTE.length] : PALETTE[0]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return <DataTable data={data} />;
}

export function DataTable({ data }) {
  if (!data?.length) return null;
  const cols = Object.keys(data[0]);

  return (
    <div className="max-h-72 overflow-auto rounded-xl border border-slate-100 dark:border-slate-800">
      <table className="w-full text-xs text-left">
        <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800/90 z-10 border-b border-slate-100 dark:border-slate-800">
          <tr>
            {cols.map((c) => (
              <th key={c} className="p-2.5 uppercase tracking-wider font-bold text-slate-500 dark:text-slate-400">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((r, i) => (
            <tr
              key={i}
              className="border-t border-slate-50 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition"
            >
              {cols.map((c) => (
                <td key={c} className="p-2.5 tabular-nums font-mono text-slate-700 dark:text-slate-300">
                  {typeof r[c] === "number" ? Number(r[c]).toLocaleString() : String(r[c])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
