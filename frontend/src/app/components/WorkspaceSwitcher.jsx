"use client";
import { useEffect, useState } from "react";
import { Layers, Plus } from "lucide-react";

export function WorkspaceSwitcher() {
  const [workspaces, setWorkspaces] = useState(["default"]);
  const [active, setActive] = useState("default");
  const [newWs, setNewWs] = useState("");

  const load = async () => {
    try {
      const r = await fetch("http://localhost:8000/api/workspaces");
      if (r.ok) {
        const d = await r.json();
        setWorkspaces(d.workspaces || ["default"]);
        const saved = localStorage.getItem("dataforge_workspace") || "default";
        if (d.workspaces && d.workspaces.includes(saved)) {
          setActive(saved);
        }
      }
    } catch (e) {
      console.warn("Failed to load workspaces:", e);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const switchTo = async (wid) => {
    if (!wid) return;
    try {
      await fetch(`http://localhost:8000/api/workspaces/${wid}`, { method: "POST" });
      localStorage.setItem("dataforge_workspace", wid);
      setActive(wid);
      window.location.reload();
    } catch (e) {
      console.error("Failed to switch workspace:", e);
    }
  };

  return (
    <div className="p-2 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/60 dark:border-slate-700/60 space-y-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Layers size={12} className="text-indigo-600 dark:text-indigo-400" />
          <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Workspace
          </label>
        </div>
        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 font-semibold">
          {active}
        </span>
      </div>

      {/* Select Dropdown */}
      <select
        value={active}
        onChange={(e) => switchTo(e.target.value)}
        className="w-full rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-medium text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
      >
        {workspaces.map((w) => (
          <option key={w} value={w}>
            📁 {w}
          </option>
        ))}
      </select>

      {/* Create New Workspace Row */}
      <div className="flex items-center gap-1 pt-0.5">
        <input
          value={newWs}
          onChange={(e) => setNewWs(e.target.value)}
          placeholder="New workspace..."
          onKeyDown={(e) => {
            if (e.key === "Enter" && newWs.trim()) {
              switchTo(newWs.trim());
              setNewWs("");
            }
          }}
          className="flex-1 min-w-0 rounded-lg border border-slate-200 bg-white px-2 py-1 text-[11px] text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
        />
        <button
          onClick={() => {
            const v = newWs.trim();
            if (v) {
              switchTo(v);
              setNewWs("");
            }
          }}
          title="Create Workspace"
          className="flex items-center justify-center h-6 w-6 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition shrink-0"
        >
          <Plus size={12} />
        </button>
      </div>
    </div>
  );
}
