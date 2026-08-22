"use client";
import { useState } from "react";
import { Sparkles, Send, Loader2, BarChart2, Table as TableIcon, HelpCircle } from "lucide-react";
import { Card, Badge, Button } from "./ui";

export default function DatasetChatBox({ datasetId }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [errorMsg, setErrorMsg] = useState(null);

  const quickPrompts = [
    "Show me top 10 highest value records",
    "Breakdown metrics grouped by category",
    "Give me an overview of all columns",
    "What are the main outliers in this data?"
  ];

  const handleSend = async (textToSend) => {
    const q = textToSend || query;
    if (!q.trim() || !datasetId) return;

    setLoading(true);
    setErrorMsg(null);
    const userMsg = { role: "user", text: q };
    setChatHistory((prev) => [...prev, userMsg]);
    setQuery("");

    try {
      const res = await fetch("http://localhost:8000/api/eda/query-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: datasetId, query: q })
      });

      if (!res.ok) {
        throw new Error("Failed to process dataset query");
      }

      const data = await res.json();
      const botMsg = {
        role: "assistant",
        text: data.answer_text,
        summary: data.summary_metric,
        records: data.records,
        chartSpec: data.chart_spec
      };
      setChatHistory((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Query failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-5 border-cyan-500/30 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="text-cyan-400" size={18} />
          <h3 className="text-sm font-bold text-slate-100">Conversational Data Analyst (Ask Your Dataset)</h3>
        </div>
        <Badge variant="cyan" size="xs">Sandboxed Interpreter</Badge>
      </div>

      {/* Suggested Quick Prompts */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {quickPrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            className="rounded-full border border-slate-700 bg-slate-800/80 px-2.5 py-1 text-[11px] text-slate-300 hover:border-cyan-500 hover:text-cyan-300 transition"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="space-y-3 max-h-72 overflow-y-auto pr-1 mb-4">
        {chatHistory.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center text-xs text-slate-500">
            <HelpCircle size={20} className="mb-1.5 opacity-50" />
            <span>Ask any natural language question about distributions, top records, or segment breakdowns.</span>
          </div>
        ) : (
          chatHistory.map((msg, i) => (
            <div
              key={i}
              className={`rounded-xl p-3 text-xs leading-relaxed ${
                msg.role === "user"
                  ? "ml-8 bg-cyan-950/40 border border-cyan-800/50 text-cyan-200"
                  : "mr-8 bg-slate-850 border border-slate-750 text-slate-200"
              }`}
            >
              <div className="font-semibold mb-1 text-[11px] opacity-80">
                {msg.role === "user" ? "You" : "DataForge Analyst"}
              </div>
              <div>{msg.text}</div>
              {msg.summary && (
                <div className="mt-2 rounded bg-slate-900/80 p-2 font-mono text-[11px] text-cyan-300 border border-slate-800">
                  {msg.summary}
                </div>
              )}
              {msg.records && msg.records.length > 0 && (
                <div className="mt-2.5 overflow-x-auto rounded border border-slate-800">
                  <table className="min-w-full divide-y divide-slate-800 text-[10px]">
                    <thead className="bg-slate-900 text-slate-400">
                      <tr>
                        {Object.keys(msg.records[0]).slice(0, 5).map((k) => (
                          <th key={k} className="px-2 py-1 text-left font-medium">{k}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-950/60 text-slate-300">
                      {msg.records.slice(0, 5).map((row, rIdx) => (
                        <tr key={rIdx}>
                          {Object.keys(msg.records[0]).slice(0, 5).map((k) => (
                            <td key={k} className="px-2 py-1 truncate max-w-[120px]">{String(row[k])}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Input Box */}
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a question about this cleaned dataset..."
          className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
        />
        <Button size="sm" variant="primary" onClick={() => handleSend()} disabled={loading || !query.trim()}>
          {loading ? <Loader2 size={13} className="animate-spin" /> : <Send size={13} />}
          <span>Ask</span>
        </Button>
      </div>
      {errorMsg && <p className="mt-2 text-[11px] text-rose-400">{errorMsg}</p>}
    </Card>
  );
}
