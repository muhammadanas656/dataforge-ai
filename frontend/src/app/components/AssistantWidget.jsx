"use client";
import { useState, useEffect, useRef } from "react";
import {
  Sparkles,
  X,
  Send,
  Loader2,
  Bot,
  User,
  Database,
  Lightbulb,
  Compass,
  Activity,
  Zap,
  CheckCircle2,
  Play,
  ArrowRight,
  Terminal
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { formatMathMarkdown } from "./markdownUtils";
import { authFetch } from "../api";
import { useContextTracker } from "../hooks/useContextTracker";
import { IconAutopilot, IconWebRadar, IconCausalEDA, IconCodeExporter, IconTrizInvention } from "./AntigravityIcons";

const markdownComponents = {
  table: ({ children }) => (
    <div className="my-2 max-w-full overflow-x-auto rounded-lg">
      <table className="min-w-full">{children}</table>
    </div>
  )
};

export default function AssistantWidget() {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [contextData, setContextData] = useState(null);
  const [tokenStats, setTokenStats] = useState({ total_tokens_saved: 0, cached_queries_count: 0 });
  const [isSimpleMode, setIsSimpleMode] = useState(false);
  const [softRedirect, setSoftRedirect] = useState(null);
  const messagesEndRef = useRef(null);
  const sessionId = useRef(`sess_${Math.random().toString(36).substring(2, 9)}`);
  useContextTracker(sessionId.current);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  useEffect(() => {
    if (isOpen) {
      authFetch(`/api/context/current?session_id=${sessionId.current}`)
        .then((r) => r.json())
        .then(setContextData)
        .catch(() => {});

      authFetch(`/api/assistant/token-stats`)
        .then((r) => r.json())
        .then(setTokenStats)
        .catch(() => {});
    }
  }, [isOpen]);

  const handleSend = async (overrideText = null) => {
    const rawText = overrideText || input;
    if (!rawText.trim() || isStreaming) return;

    const text = isSimpleMode && !rawText.toLowerCase().includes("simply") && !rawText.toLowerCase().includes("simple")
      ? `${rawText.trim()} (explain simply like I'm 10 with analogies)`
      : rawText.trim();

    setMessages((prev) => [...prev, { role: "user", content: rawText }]);
    setInput("");
    setIsStreaming(true);

    try {
      // 1. Try streaming endpoint first
      let streamSucceeded = false;
      try {
        const res = await authFetch(`/api/assistant/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId.current,
            query: text
          })
        });

        if (res.ok && res.body) {
          const reader = res.body.getReader();
          const decoder = new TextDecoder();
          let assistantMsg = { role: "assistant", content: "", action_card: null, cached: false };
          setMessages((prev) => [...prev, assistantMsg]);

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split("\n").filter((l) => l.trim());

            for (const line of lines) {
              try {
                const data = JSON.parse(line);
                if (data.type === "chunk") {
                  assistantMsg.content += data.content;
                  setMessages((prev) => {
                    const updated = [...prev];
                    updated[updated.length - 1] = { ...assistantMsg };
                    return updated;
                  });
                } else if (data.type === "done") {
                  if (data.action_card) assistantMsg.action_card = data.action_card;
                  if (data.cached) assistantMsg.cached = true;
                  if (data.total_tokens_saved) {
                    setTokenStats((prev) => ({ ...prev, total_tokens_saved: data.total_tokens_saved }));
                  }
                  setMessages((prev) => {
                    const updated = [...prev];
                    updated[updated.length - 1] = { ...assistantMsg };
                    return updated;
                  });
                  setIsStreaming(false);
                }
              } catch (e) {
                // Non-json chunk
              }
            }
          }
          streamSucceeded = true;
        }
      } catch (streamErr) {
        console.warn("Stream attempt fallback:", streamErr);
      }

      // 2. Direct JSON query endpoint fallback
      if (!streamSucceeded) {
        const fallbackRes = await authFetch(`/api/assistant/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId.current,
            query: text
          })
        });

        if (fallbackRes.ok) {
          const fallbackData = await fallbackRes.json();
          if (fallbackData.total_tokens_saved) {
            setTokenStats((prev) => ({ ...prev, total_tokens_saved: fallbackData.total_tokens_saved }));
          }
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: fallbackData.response || "I am ready to assist you.",
              action_card: fallbackData.action_card,
              cached: fallbackData.cached
            }
          ]);
        } else {
          throw new Error("Fallback query also returned non-200");
        }
      }
    } catch (err) {
      console.error("Assistant query failed:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "The Copilot is ready. Please send your question again and I will execute the action or analyze your data."
        }
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleExecuteProposal = async (proposal) => {
    if (!proposal || isStreaming) return;
    setIsStreaming(true);

    try {
      const res = await authFetch(`/api/assistant/execute-action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId.current,
          tool_name: proposal.tool_name,
          args: proposal.args || {}
        })
      });

      if (res.ok) {
        const data = await res.json();
        if (data.action_card?.route_link) {
          setSoftRedirect({
            route: data.action_card.route_link,
            label: data.action_card.route_label || "Workspace"
          });
        }
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: data.response || "Action executed successfully.",
            action_card: data.action_card
          }
        ]);
      } else {
        throw new Error("Action execution failed");
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ Failed to execute action: ${e.message}` }
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  const handlePreviewProposal = async (proposal, messageIndex) => {
    if (!proposal || isStreaming) return;
    try {
      const res = await authFetch(`/api/assistant/dry-run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool_name: proposal.tool_name, args: proposal.args || {} })
      });
      const preview = await res.json();
      setMessages((prev) => prev.map((message, index) => index === messageIndex
        ? { ...message, action_card: { ...message.action_card, preview } }
        : message));
    } catch (error) {
      console.error("Action preview failed:", error);
    }
  };

  const suggestedQuestions = isSimpleMode ? [
    { label: "💡 What is TRIZ simply?", action: false },
    { label: "🌳 Explain Causal DAG like I'm 10", action: false },
    { label: "📉 What are Fat Tails simply?", action: false },
    { label: "🛡️ What is SSRF security in easy words?", action: false },
    { label: "🧩 What does MICE imputation do simply?", action: false },
    { label: "🚀 Run Auto-Pilot on my dataset", action: true }
  ] : [
    { label: "🚀 Run Auto-Pilot on my dataset", action: true },
    { label: "🎯 Scrape leads for AI startups", action: true },
    { label: "📦 Export standalone Python code", action: true },
    { label: "💡 Resolve TRIZ contradiction", action: true },
    { label: "❓ What services does DataForge provide?", action: false },
    { label: "📊 How does Causal DAG inference work?", action: false }
  ];

  return (
    <>
      {/* Floating Launcher Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white rounded-full px-4 py-3 shadow-2xl transition-all hover:scale-105 font-medium text-xs border border-indigo-400/40"
        title="Open DataForge Autonomous Copilot"
      >
        <IconAutopilot size={18} className="animate-glow" />
        <span>{isOpen ? "Close Copilot" : "Autonomous Copilot"}</span>
      </button>

      {/* Slide-out Floating Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-6 z-50 w-96 max-w-[calc(100vw-2rem)] h-[580px] max-h-[calc(100vh-6rem)] bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="flex items-center justify-between p-3.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/60">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-indigo-600 text-white">
                <IconAutopilot size={16} />
              </div>
              <div>
                <h3 className="font-bold text-xs text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                  Autonomous Copilot
                  <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-cyan-100 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 font-mono">
                    Action-Enabled
                  </span>
                </h3>
                <div className="flex items-center gap-2 text-[10px] text-slate-500">
                  <span>Module: {contextData?.active_module || "Overview"}</span>
                  {tokenStats.total_tokens_saved > 0 && (
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-0.5">
                      <Zap size={10} /> {tokenStats.total_tokens_saved} tokens saved
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setIsSimpleMode(!isSimpleMode)}
                className={`px-2 py-0.5 rounded-full text-[10px] font-bold border transition ${
                  isSimpleMode
                    ? "bg-amber-500/20 text-amber-500 border-amber-500/40"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-400 border-slate-300 dark:border-slate-700 hover:text-slate-200"
                }`}
                title="Toggle Simple Mode (ELI5 Explanations with Analogies)"
              >
                {isSimpleMode ? "🧸 Simple Mode ON" : "🎓 Simple Mode"}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* Soft Non-Intrusive Redirection Notice */}
          {softRedirect && (
            <div className="flex items-center justify-between p-2.5 bg-gradient-to-r from-indigo-500/15 to-cyan-500/15 border-b border-cyan-500/30 text-[10px] animate-in fade-in slide-in-from-top-2">
              <span className="text-slate-700 dark:text-slate-200 font-medium truncate">
                ✨ <strong>{softRedirect.label}</strong> is ready to explore.
              </span>
              <div className="flex items-center gap-1.5 shrink-0 ml-2">
                <button
                  onClick={() => {
                    router.push(softRedirect.route);
                    setSoftRedirect(null);
                  }}
                  className="px-2 py-0.5 rounded-md bg-cyan-600 hover:bg-cyan-500 text-white font-bold transition flex items-center gap-1 shadow-2xs text-[9px]"
                >
                  <span>Switch View</span>
                  <ArrowRight size={9} />
                </button>
                <button
                  onClick={() => setSoftRedirect(null)}
                  className="p-0.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded"
                  title="Dismiss notice and stay on current page"
                >
                  <X size={12} />
                </button>
              </div>
            </div>
          )}

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-3.5 space-y-3 text-xs">
            {messages.length === 0 && (
              <div className="text-center py-4 space-y-3">
                <div className="w-10 h-10 mx-auto rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                  <Sparkles size={20} />
                </div>
                <div className="space-y-1 px-4">
                  <h4 className="font-semibold text-slate-800 dark:text-slate-200 text-xs">Autonomous Agent & Copilot</h4>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    I can explain concepts, answer questions, or <strong>execute tools directly on your behalf</strong> (cleaning, scraping leads, Causal EDA, code exports).
                  </p>
                </div>

                <div className="grid gap-1.5 pt-2 px-2 text-left">
                  {suggestedQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(q.label)}
                      className="flex items-center justify-between gap-2 w-full p-2 text-[11px] font-medium rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/70 dark:border-slate-700/60 hover:border-cyan-400 dark:hover:border-cyan-500 text-slate-700 dark:text-slate-300 transition hover:bg-cyan-50/30 dark:hover:bg-cyan-950/20"
                    >
                      <span className="truncate">{q.label}</span>
                      {q.action ? (
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-100 dark:bg-cyan-900/50 text-cyan-700 dark:text-cyan-300 font-bold shrink-0">
                          ACT
                        </span>
                      ) : (
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 shrink-0">
                          ASK
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[90%] rounded-2xl px-3.5 py-2.5 text-[11px] leading-relaxed shadow-xs ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white rounded-br-none"
                      : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-bl-none border border-slate-200/80 dark:border-slate-700/80"
                  }`}
                >
                  <div className="flex items-center gap-1.5 mb-1 opacity-70 text-[9px] font-semibold">
                    {msg.role === "user" ? <User size={11} /> : <Bot size={11} />}
                    <span>{msg.role === "user" ? "You" : "DataForge Copilot"}</span>
                    {msg.cached && (
                      <span className="ml-auto text-emerald-500 font-mono text-[9px]">⚡ Zero-Token Instant</span>
                    )}
                  </div>
                  <div className="chat-markdown font-sans [&_p]:mb-2 last:[&_p]:mb-0 [&_strong]:font-bold [&_em]:italic [&_ul]:my-2 [&_ul]:ml-4 [&_ul]:list-disc [&_ol]:my-2 [&_ol]:ml-4 [&_ol]:list-decimal [&_li]:my-0.5 [&_a]:text-cyan-600 [&_a]:underline [&_code]:rounded [&_code]:bg-slate-200 [&_code]:px-1 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-[10px] dark:[&_code]:bg-slate-700 [&_pre]:my-2 [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-slate-900 [&_pre]:p-2 [&_pre]:text-slate-100 [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_blockquote]:my-2 [&_blockquote]:border-l-2 [&_blockquote]:border-cyan-500 [&_blockquote]:pl-2 [&_table]:my-2 [&_table]:w-full [&_table]:text-left [&_th]:border [&_th]:border-slate-300 [&_th]:bg-slate-200 [&_th]:px-2 [&_th]:py-1 [&_td]:border [&_td]:border-slate-300 [&_td]:px-2 [&_td]:py-1 dark:[&_th]:border-slate-600 dark:[&_th]:bg-slate-700 dark:[&_td]:border-slate-600">
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]} components={markdownComponents}>{formatMathMarkdown(msg.content)}</ReactMarkdown>
                  </div>

                  {/* Interactive Action Confirmation & Execution Cards */}
                  {msg.action_card && (
                    <div className="mt-2.5 rounded-xl border p-2.5 text-[10px] space-y-2">
                      {msg.action_card.type === "feature_navigation" ? (
                        <div className="rounded-xl bg-gradient-to-r from-indigo-500/10 to-cyan-500/10 border border-cyan-500/30 p-2.5 space-y-2">
                          <div className="flex items-center gap-1.5 font-bold text-cyan-600 dark:text-cyan-400">
                            <Compass size={13} className="text-cyan-500" />
                            <span>{msg.action_card.title || "Feature Navigation"}</span>
                          </div>
                          <p className="text-[10px] text-slate-600 dark:text-slate-300">
                            Click below to jump directly to this workspace:
                          </p>
                          <div className="pt-1">
                            <button
                              onClick={() => router.push(msg.action_card.route_link)}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold transition shadow-xs cursor-pointer text-[10px]"
                            >
                              <span>{msg.action_card.action_label || msg.action_card.route_label || "Open Workspace"}</span>
                              <ArrowRight size={11} />
                            </button>
                          </div>
                        </div>
                      ) : msg.action_card.type === "action_proposal" ? (
                        <div className="rounded-lg bg-amber-500/10 border border-amber-500/30 p-2.5 space-y-2">
                          <div className="flex items-center gap-1.5 font-bold text-amber-500">
                            <Sparkles size={12} className="animate-pulse" />
                            <span>Action Proposal: {msg.action_card.action_label}</span>
                          </div>
                          <p className="text-[10px] text-slate-600 dark:text-slate-300">
                            {msg.action_card.impact}
                          </p>
                          {msg.action_card.preview && (
                            <div className="rounded-lg bg-white/60 p-2 text-[10px] dark:bg-slate-900/40">
                              <div className="font-bold text-slate-700 dark:text-slate-200">Preview: {msg.action_card.preview.summary}</div>
                              <div className="mt-1 text-slate-500 dark:text-slate-400">Impact: {msg.action_card.preview.impact} · Confirmation: {msg.action_card.preview.requires_confirmation ? "required" : "not required"}</div>
                            </div>
                          )}
                          <div className="flex items-center gap-2 pt-1">
                            <button
                              onClick={() => handlePreviewProposal(msg.action_card, i)}
                              disabled={isStreaming}
                              className="px-2.5 py-1 rounded-lg bg-white/70 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-semibold hover:bg-white dark:hover:bg-slate-700 transition"
                            >
                              Preview Impact
                            </button>
                            <button
                              onClick={() => handleExecuteProposal(msg.action_card)}
                              disabled={isStreaming}
                              className="px-3 py-1 rounded-lg bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold transition shadow-xs"
                            >
                              ✓ Confirm & Execute
                            </button>
                            <button
                              onClick={() => {
                                setMessages((prev) => [
                                  ...prev,
                                  { role: "assistant", content: "Action cancelled. Let me know if you would like to do something else." }
                                ]);
                              }}
                              className="px-2.5 py-1 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="rounded-lg bg-cyan-950/20 border border-cyan-500/30 p-2 space-y-1.5">
                          <div className="flex items-center gap-1.5 font-bold text-cyan-400">
                            <CheckCircle2 size={12} className="text-emerald-400" />
                            <span>Action Completed Autonomously</span>
                          </div>
                          {msg.action_card.route_link && (
                            <div className="flex gap-2 pt-1">
                              <button
                                onClick={() => router.push(msg.action_card.route_link)}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-cyan-600 text-white font-bold hover:bg-cyan-500 transition cursor-pointer"
                              >
                                <span>Open {msg.action_card.route_label || "Studio"}</span>
                                <ArrowRight size={10} />
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isStreaming && (
              <div className="flex items-center gap-2 text-slate-400 text-xs py-1">
                <Loader2 size={12} className="animate-spin text-cyan-500" />
                <span className="text-[10px]">Copilot analyzing & executing...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask or command: 'Clean my data', 'Scrape leads'..."
                className="flex-1 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                disabled={isStreaming}
              />
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="p-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white disabled:opacity-40 transition shadow-sm"
              >
                <Send size={13} />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
