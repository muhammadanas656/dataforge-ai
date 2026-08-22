"use client";
import { useEffect, useState } from "react";
import { ArrowLeftRight, ChevronLeft, ChevronRight, Loader2, ArrowRight } from "lucide-react";
import { Card, Select, SearchInput, Button, Badge, Tip } from "./components/ui";

export default function DataInspector({ datasetId, defaultStage }) {
  const [stages, setStages] = useState([]);
  const [stage, setStage] = useState(defaultStage || "raw");
  const [view, setView] = useState(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [diff, setDiff] = useState(null);
  const [diffLoading, setDiffLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [meaning, setMeaning] = useState({});

  useEffect(() => {
    if (defaultStage) {
      setStage(defaultStage);
      setPage(1);
    }
  }, [defaultStage]);

  useEffect(() => {
    if (!datasetId) return;
    fetch(`http://localhost:8000/api/data/stages/${datasetId}`)
      .then((r) => r.json())
      .then((d) => {
        setStages(d.stages || ["raw"]);
      })
      .catch((err) => console.error("Failed to fetch stages", err));

    fetch(`http://localhost:8000/api/summary/${datasetId}`)
      .then((r) => r.json())
      .then((s) => {
        const m = {};
        (s.columns || []).forEach((c) => {
          m[c.name] = `${c.semantic_type}: ${c.meaning}`;
        });
        setMeaning(m);
      })
      .catch((err) => console.warn("Failed to load column meanings", err));

    const handleGoto = (e) => {
      if (e.detail) {
        setStage(e.detail);
        setPage(1);
      }
    };
    window.addEventListener("goto-stage", handleGoto);
    return () => window.removeEventListener("goto-stage", handleGoto);
  }, [datasetId]);

  useEffect(() => {
    if (!datasetId) return;
    setLoading(true);
    fetch(`http://localhost:8000/api/data/${datasetId}?stage=${stage}&page=${page}&page_size=50&search=${encodeURIComponent(search)}`)
      .then((r) => r.json())
      .then((d) => {
        setView(d);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch data view", err);
        setLoading(false);
      });
    setDiff(null);
  }, [datasetId, stage, page, search]);

  const showDiff = async () => {
    setDiffLoading(true);
    try {
      const r = await fetch(`http://localhost:8000/api/data/${datasetId}/diff?stage=${stage}`);
      setDiff(await r.json());
    } catch (e) {
      console.error("Failed to fetch diff", e);
    } finally {
      setDiffLoading(false);
    }
  };

  if (!view && loading) {
    return (
      <div className="bg-white p-6 rounded-2xl shadow-sm flex items-center gap-2 text-slate-500 dark:bg-slate-900 dark:text-slate-400">
        <Loader2 className="animate-spin" size={18} />
        Loading Data Inspector…
      </div>
    );
  }

  if (!view) return null;
  const pages = Math.ceil((view.total || 0) / (view.page_size || 50));

  return (
    <div id="data-inspector">
      <Card
        title="Data Inspector"
        info="See the actual records at every stage, and exactly what changed between stages."
        actions={<Badge tone="info">{view.total.toLocaleString()} rows</Badge>}
        pad={false}
      >
        {/* Standardized Control Toolbar */}
        <div className="flex flex-wrap items-center gap-2.5 border-b border-slate-100 px-5 py-3 dark:border-slate-800">
          <Select
            value={stage}
            onChange={(e) => {
              setStage(e.target.value);
              setPage(1);
            }}
          >
            {stages.map((s) => (
              <option key={s} value={s}>
                {s === "raw" ? "Raw Dataset" : s === "cleaned" ? "Cleaned Dataset" : `After ${s.replace("_", " ")}`}
              </option>
            ))}
          </Select>

          <Button
            variant="secondary"
            size="sm"
            onClick={showDiff}
            disabled={diffLoading || stage === "raw"}
          >
            {diffLoading ? <Loader2 className="animate-spin" size={13} /> : <ArrowLeftRight size={13} />}
            Diff vs Previous
            <Tip text="Shows exactly which rows were removed or which cells changed between this stage and the previous snapshot." />
          </Button>

          <SearchInput
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search table rows…"
            className="ml-auto w-64"
          />
        </div>

        {/* Clean Structured Diff Section */}
        {diff && diff.type !== "none" && (
          <div
            className={`m-5 p-4 rounded-xl text-xs border ${
              diff.type === "remove"
                ? "bg-rose-50/70 border-rose-200 text-rose-900 dark:bg-rose-950/30 dark:border-rose-800 dark:text-rose-200"
                : "bg-amber-50/70 border-amber-200 text-amber-900 dark:bg-amber-950/30 dark:border-amber-800 dark:text-amber-200"
            }`}
          >
            {diff.type === "remove" ? (
              <div>
                <p className="font-bold mb-2 flex items-center gap-1.5">
                  <span>❌</span>
                  <span>Removed <b>{diff.removed_rows?.toLocaleString()}</b> rows from previous snapshot:</span>
                </p>
                {diff.removed && diff.removed.length > 0 && (
                  <div className="overflow-x-auto rounded-lg border border-rose-200 dark:border-rose-900/60 bg-white dark:bg-slate-900 max-h-48 overflow-y-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-rose-100/60 dark:bg-rose-950/50 text-[11px] font-bold uppercase text-rose-800 dark:text-rose-300 sticky top-0">
                        <tr>
                          {Object.keys(diff.removed[0]).slice(0, 8).map((c) => (
                            <th key={c} className="p-2">{c}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {diff.removed.slice(0, 10).map((r, i) => (
                          <tr key={i} className="border-t border-rose-100 dark:border-rose-900/40 font-mono text-[11px]">
                            {Object.keys(diff.removed[0]).slice(0, 8).map((c) => (
                              <td key={c} className="p-2 truncate max-w-xs text-rose-700 dark:text-rose-400">
                                {String(r[c])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <p className="font-bold mb-2 flex items-center gap-1.5">
                  <span>✏️</span>
                  <span>Modified <b>{diff.changed_cells?.toLocaleString()}</b> cells:</span>
                </p>
                {diff.changed && diff.changed.length > 0 && (
                  <div className="overflow-x-auto rounded-lg border border-amber-200 dark:border-amber-900/60 bg-white dark:bg-slate-900 max-h-48 overflow-y-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-amber-100/60 dark:bg-amber-950/50 text-[11px] font-bold uppercase text-amber-800 dark:text-amber-300 sticky top-0">
                        <tr>
                          <th className="p-2">Row #</th>
                          <th className="p-2">Column</th>
                          <th className="p-2">Original Value</th>
                          <th className="p-2">Transformed Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {diff.changed.slice(0, 15).map((c, i) => (
                          <tr key={i} className="border-t border-amber-100 dark:border-amber-900/40 font-mono text-[11px]">
                            <td className="p-2 text-slate-500">{c.row_index ?? i + 1}</td>
                            <td className="p-2 font-bold text-indigo-600 dark:text-indigo-400">{c.column}</td>
                            <td className="p-2 text-rose-600 dark:text-rose-400 line-through">{c.before}</td>
                            <td className="p-2 text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
                              <ArrowRight size={11} className="inline text-slate-400" />
                              {c.after}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Paginated Table View with Column Meaning Tooltips */}
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="text-xs w-full text-left">
            <thead className="bg-slate-100/90 dark:bg-slate-800/90 sticky top-0 border-b border-slate-200 dark:border-slate-800 z-10">
              <tr>
                <th className="p-2.5 font-bold text-slate-600 dark:text-slate-400 w-12 text-center">#</th>
                {view.columns.map((c) => (
                  <th key={c} className="p-2.5 font-mono font-bold text-slate-700 dark:text-slate-200 whitespace-nowrap">
                    <span className="inline-flex items-center gap-1.5">
                      {c}
                      {meaning[c] && <Tip text={meaning[c]} />}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {view.rows.length === 0 ? (
                <tr>
                  <td colSpan={view.columns.length + 1} className="p-6 text-center text-slate-500 dark:text-slate-400 italic">
                    No records match your search query.
                  </td>
                </tr>
              ) : (
                view.rows.map((row, i) => (
                  <tr key={i} className="border-b border-slate-100 dark:border-slate-800/70 hover:bg-indigo-50/40 dark:hover:bg-indigo-950/20 transition">
                    <td className="p-2.5 text-center text-slate-400 font-mono">
                      {(page - 1) * view.page_size + i + 1}
                    </td>
                    {view.columns.map((c) => (
                      <td key={c} className="p-2.5 whitespace-nowrap font-mono text-slate-800 dark:text-slate-200 max-w-xs truncate">
                        {String(row[c])}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="flex justify-between items-center px-5 py-3 border-t border-slate-100 dark:border-slate-800 text-xs">
          <span className="text-slate-500 dark:text-slate-400 font-medium">
            Showing {(page - 1) * view.page_size + 1} to {Math.min(page * view.page_size, view.total)} of{" "}
            {view.total.toLocaleString()} records
          </span>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft size={13} /> Prev
            </Button>
            <span className="font-bold text-slate-700 dark:text-slate-300">
              Page {page} of {pages || 1}
            </span>
            <Button
              variant="secondary"
              size="sm"
              disabled={page >= pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next <ChevronRight size={13} />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
