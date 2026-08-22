"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Database,
  Wrench,
  CheckSquare,
  FileText,
  BarChart3,
  Compass,
  Radar,
  Bell,
  HelpCircle,
  Brain,
  Settings,
  Sparkles,
  Menu,
  X,
} from "lucide-react";
import { ThemeToggle } from "./theme";
import { useDataset } from "./DatasetContext";
import TokenTicker from "./TokenTicker";
import { WorkspaceSwitcher } from "./WorkspaceSwitcher";

const NAV_GROUPS = [
  {
    label: "Data Pipeline",
    items: [
      { href: "/", label: "Overview", icon: LayoutDashboard },
      { href: "/data", label: "Raw Data", icon: Database },
      { href: "/cleaning", label: "Cleaning Studio", icon: Wrench },
      { href: "/cleaned", label: "Cleaned Data", icon: CheckSquare },
      { href: "/report", label: "Quality Report", icon: FileText },
    ],
  },
  {
    label: "Analysis",
    items: [
      { href: "/eda", label: "EDA Studio", icon: BarChart3 },
    ],
  },
  {
    label: "Research & Market",
    items: [
      { href: "/research", label: "Niche Research", icon: Compass },
      { href: "/intel", label: "Competitor Intel", icon: Radar },
      { href: "/alerts", label: "Market Alerts", icon: Bell },
    ],
  },
  {
    label: "System & Autonomy",
    items: [
      { href: "/learning", label: "Learning Activity", icon: Brain },
      { href: "/explain", label: "How It Works", icon: HelpCircle },
      { href: "/settings", label: "Settings", icon: Settings },
    ],
  },
];

export default function Sidebar() {
  const path = usePathname();
  const { id, setId, list } = useDataset();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile Top Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-30 flex h-14 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/95 shadow-xs">
        <div className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-violet-700 text-white shadow-sm">
            <Sparkles size={14} />
          </div>
          <span className="text-sm font-bold tracking-tight text-slate-900 dark:text-slate-100">
            DataForge AI
          </span>
        </div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle navigation menu"
          className="p-1.5 rounded-lg text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 transition"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Backdrop for Mobile */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-slate-950/50 backdrop-blur-xs transition-opacity animate-fade-in"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Main Responsive Sidebar Drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-60 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 select-none shadow-medium lg:shadow-none transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-14 items-center justify-between border-b border-slate-100 px-4 dark:border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-700 text-white shadow-soft">
              <Sparkles size={16} />
            </div>
            <div className="leading-tight">
              <span className="text-sm font-bold tracking-tight text-slate-900 dark:text-slate-100">
                DataForge AI
              </span>
              <p className="text-[10px] text-slate-500 font-medium">Enterprise Studio</p>
            </div>
          </div>
          {/* Close button on mobile inside drawer */}
          <button
            onClick={() => setIsOpen(false)}
            className="lg:hidden p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation Groups */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-4">
          {NAV_GROUPS.map((group) => (
            <div key={group.label}>
              <p className="mb-1.5 px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                {group.label}
              </p>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const active = path === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setIsOpen(false)}
                      className={`flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold transition ${
                        active
                          ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300 shadow-xs"
                          : "text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-slate-200"
                      }`}
                    >
                      <item.icon
                        size={15}
                        className={active ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400"}
                      />
                      <span className="truncate">{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer: Token Ticker + Workspace Switcher + Dataset Switcher + Theme */}
        <div className="border-t border-slate-100 p-3 dark:border-slate-800 space-y-2">
          <TokenTicker />
          <WorkspaceSwitcher />
          <div>
            <label className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-slate-400">
              Active Dataset
            </label>
            <select
              value={id || ""}
              onChange={(e) => setId(e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
            >
              {!id && <option value="">— select dataset —</option>}
              {list.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename} ({d.rows || 0} rows)
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-800/60">
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Theme</span>
            <ThemeToggle />
          </div>
        </div>
      </aside>
    </>
  );
}
