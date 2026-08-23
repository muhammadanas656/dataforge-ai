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
  Terminal,
  History,
  Plus,
  Trash2,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  Clock
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
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [contextData, setContextData] = useState(null);
  const [tokenStats, setTokenStats] = useState({ total_tokens_saved: 0, cached_queries_count: 0 });
  const [isSimpleMode, setIsSimpleMode] = useState(false);
  const [softRedirect, setSoftRedirect] = useState(null);
  const [sessions, setSessions] = useState([]);
  const messagesEndRef = useRef(null);
  
  // Active session ID state
  const [currentSessionId, setCurrentSessionId] = useState(() => {
    return `sess_${Math.random().toString(36).substring(2, 9)}`;
  });
  const sessionIdRef = useRef(currentSessionId);
  sessionIdRef.current = currentSessionId;

  useContextTracker(currentSessionId);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  // Load saved sessions from localStorage & backend on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem("dataforge_chat_sessions");
      if (stored) {
        setSessions(JSON.parse(stored));
      }
    } catch (e) {
      console.error("Failed to load local chat sessions", e);
    }
  }, []);

  // Sync sessions list with backend
  const fetchBackendSessions = async () => {
    try {
      const res = await authFetch("/api/assistant/sessions");
      if (res.ok) {
        const data = await res.json();
        if (data.sessions && data.sessions.length > 0) {
          setSessions((prev) => {
            const combined = [...data.sessions];
            prev.forEach((p) => {
              if (!combined.some((c) => c.session_id === p.session_id)) {
                combined.push(p);
              }
            });
            localStorage.setItem("dataforge_chat_sessions", JSON.stringify(combined));
            return combined;
          });
        }
      }
    } catch (e) {}
  };

  useEffect(() => {
    if (isOpen) {
      fetchBackendSessions();
      authFetch(`/api/context/current?session_id=${currentSessionId}`)
        .then((r) => r.json())
        .then(setContextData)
        .catch(() => {});

      authFetch(`/api/assistant/token-stats`)
        .then((r) => r.json())
        .then(setTokenStats)
        .catch(() => {});
    }
  }, [isOpen, currentSessionId]);

  // Helper to save current thread into sessions list
  const persistCurrentSession = (updatedMessages, currentSessId) => {
    if (!updatedMessages || updatedMessages.length === 0) return;
    
    const firstUserMsg = updatedMessages.find((m) => m.role === "user");
    let title = firstUserMsg ? firstUserMsg.content.trim().replace(/\n/g, " ") : "New Conversation";
    if (title.length > 36) title = title.substring(0, 33) + "...";

    const sessionObj = {
      session_id: currentSessId,
      title: title || "Conversation",
      message_count: updatedMessages.length,
      last_message: updatedMessages[updatedMessages.length - 1]?.content?.substring(0, 50) || "",
      updated_at: Date.now()
    };

    setSessions((prev) => {
      const filtered = prev.filter((s) => s.session_id !== currentSessId);
      const nextSessions = [sessionObj, ...filtered];
      try {
        localStorage.setItem("dataforge_chat_sessions", JSON.stringify(nextSessions));
        localStorage.setItem(`dataforge_thread_${currentSessId}`, JSON.stringify(updatedMessages));
      } catch (e) {}
      return nextSessions;
    });
  };

  // Start a fresh New Chat
  const handleNewChat = () => {
    if (messages.length > 0) {
      persistCurrentSession(messages, currentSessionId);
    }
    const newSessId = `sess_${Math.random().toString(36).substring(2, 9)}`;
    setCurrentSessionId(newSessId);
    setMessages([]);
    setIsHistoryOpen(false);
  };

  // Switch to a previous chat session
  const handleSelectSession = async (sess) => {
    if (messages.length > 0) {
      persistCurrentSession(messages, currentSessionId);
    }

    setCurrentSessionId(sess.session_id);
    setIsHistoryOpen(false);

    // Try loading thread from local storage first
    try {
      const localThread = localStorage.getItem(`dataforge_thread_${sess.session_id}`);
      if (localThread) {
        setMessages(JSON.parse(localThread));
        return;
      }
    } catch (e) {}

    // Fallback: fetch from backend
    try {
      const res = await authFetch(`/api/assistant/sessions/${sess.session_id}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
      }
    } catch (e) {
      console.error("Failed to load session history", e);
    }
  };

  // Delete a chat session
  const handleDeleteSession = (sessId, e) => {
    e.stopPropagation();
    setSessions((prev) => {
      const nextSessions = prev.filter((s) => s.session_id !== sessId);
      try {
        localStorage.setItem("dataforge_chat_sessions", JSON.stringify(nextSessions));
        localStorage.removeItem(`dataforge_thread_${sessId}`);
      } catch (err) {}
      return nextSessions;
    });

    authFetch(`/api/assistant/sessions/${sessId}`, { method: "DELETE" }).catch(() => {});

    if (currentSessionId === sessId) {
      handleNewChat();
    }
  };

  const handleSend = async (overrideText = null) => {
    const rawText = overrideText || input;
    if (!rawText.trim() || isStreaming) return;

    const text = isSimpleMode && !rawText.toLowerCase().includes("simply") && !rawText.toLowerCase().includes("simple")
      ? `${rawText.trim()} (explain simply like I'm 10 with analogies)`
      : rawText.trim();

    const newMessages = [...messages, { role: "user", content: rawText }];
    setMessages(newMessages);
    setInput("");
    setIsStreaming(true);

    try {
      let streamSucceeded = false;
      try {
        const res = await authFetch(`/api/assistant/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: currentSessionId,
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
            const lines = chunk.split("\n").filter((l) => l.trim().length > 0);
            for (const line of lines) {
              try {
                const parsed = JSON.parse(line);
                if (parsed.type === "chunk") {
                  assistantMsg.content += parsed.content;
                  setMessages((prev) => {
                    const copy = [...prev];
                    copy[copy.length - 1] = { ...assistantMsg };
                    return copy;
                  });
                } else if (parsed.type === "done") {
                  streamSucceeded = true;
                  if (parsed.action_card) {
                    assistantMsg.action_card = parsed.action_card;
                    if (parsed.action_card.route_link) {
                      setSoftRedirect({
                        route: parsed.action_card.route_link,
                        label: parsed.action_card.route_label || "Workspace"
                      });
                    }
                  }
                  if (parsed.cached) assistantMsg.cached = true;
                  setMessages((prev) => {
                    const copy = [...prev];
                    copy[copy.length - 1] = { ...assistantMsg };
                    persistCurrentSession(copy, currentSessionId);
                    return copy;
                  });
                }
              } catch (parseErr) {}
            }
          }
        }
      } catch (streamErr) {
        console.warn("Stream failed, falling back to JSON POST", streamErr);
      }

      if (!streamSucceeded) {
        const res = await authFetch(`/api/assistant/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: currentSessionId, query: text })
        });

        if (res.ok) {
          const data = await res.json();
          if (data.action_card?.route_link) {
            setSoftRedirect({
              route: data.action_card.route_link,
              label: data.action_card.route_label || "Workspace"
            });
          }
          setMessages((prev) => {
            const updated = [
              ...prev,
              {
                role: "assistant",
                content: data.response || "No response.",
                action_card: data.action_card || null,
                cached: data.cached || false
              }
            ];
            persistCurrentSession(updated, currentSessionId);
            return updated;
          });
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
          session_id: currentSessionId,
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
        setMessages((prev) => {
          const updated = [
            ...prev,
            {
              role: "assistant",
              content: data.response || "Action executed successfully.",
              action_card: data.action_card
            }
          ];
          persistCurrentSession(updated, currentSessionId);
          return updated;
        });
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
    { label: "🎨 Generate quantum aerospace vector", action: true },
    { label: "📦 Export standalone Python code", action: true },
    { label: "💡 Resolve TRIZ contradiction", action: true },
    { label: "📊 How does Causal DAG inference work?", action: false }
  ];

  return (
    <>
      {/* Floating Launcher Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white rounded-full px-4 py-3 shadow-2xl transition-all hover:scale-105 font-bold text-xs border border-indigo-400/40 cursor-pointer"
        title="Open DataForge Autonomous Copilot"
      >
        <IconAutopilot size={18} className="animate-pulse text-cyan-300" />
        <span>{isOpen ? "Close Copilot" : "Autonomous Copilot"}</span>
      </button>

      {/* Slide-out Multi-Session Chat Application Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-6 z-50 w-[420px] max-w-[calc(100vw-2rem)] h-[620px] max-h-[calc(100vh-6rem)] bg-white/95 dark:bg-slate-900/95 backdrop-blur-2xl rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          
          {/* HEADER WITH NEW CHAT & HISTORY TOGGLE */}
          <div className="flex items-center justify-between p-3.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-850">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsHistoryOpen(!isHistoryOpen)}
                className={`p-1.5 rounded-xl border transition cursor-pointer ${
                  isHistoryOpen
                    ? "bg-indigo-600 text-white border-indigo-500"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-400 hover:text-white border-slate-300 dark:border-slate-700"
                }`}
                title="View Past Chat Sessions"
              >
                <History size={15} />
              </button>

              <button
                onClick={handleNewChat}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-[11px] font-bold bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 transition cursor-pointer"
                title="Start a New Conversation"
              >
                <Plus size={13} />
                <span>New Chat</span>
              </button>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setIsSimpleMode(!isSimpleMode)}
                className={`px-2 py-1 rounded-xl text-[10px] font-bold border transition cursor-pointer ${
                  isSimpleMode
                    ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-400 border-slate-300 dark:border-slate-700 hover:text-slate-200"
                }`}
                title="Toggle Simple Mode"
              >
                {isSimpleMode ? "🧸 Simple ON" : "🎓 Simple"}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* SESSIONS HISTORY DRAWER (SLIDE OVERLAY) */}
          {isHistoryOpen && (
            <div className="absolute inset-x-0 top-14 bottom-14 z-40 bg-slate-950/95 backdrop-blur-2xl p-4 flex flex-col space-y-3 overflow-y-auto animate-in slide-in-from-left duration-200">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-black uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Clock size={13} className="text-indigo-400" />
                  Past Conversations ({sessions.length})
                </span>
                <button
                  onClick={() => setIsHistoryOpen(false)}
                  className="text-xs text-slate-400 hover:text-white"
                >
                  Close
                </button>
              </div>

              {sessions.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 text-center text-slate-500 space-y-2">
                  <MessageSquare size={28} className="opacity-40" />
                  <p className="text-xs">No saved chat sessions yet.</p>
                  <button
                    onClick={handleNewChat}
                    className="px-3 py-1.5 text-xs font-bold bg-indigo-600 text-white rounded-xl"
                  >
                    Start First Chat
                  </button>
                </div>
              ) : (
                <div className="space-y-1.5">
                  {sessions.map((sess) => {
                    const isActive = sess.session_id === currentSessionId;
                    return (
                      <div
                        key={sess.session_id}
                        onClick={() => handleSelectSession(sess)}
                        className={`group p-3 rounded-2xl border transition-all cursor-pointer flex items-center justify-between gap-2 ${
                          isActive
                            ? "bg-indigo-600/20 border-indigo-500 text-white shadow-md shadow-indigo-600/10"
                            : "bg-slate-900/60 border-slate-800/80 text-slate-300 hover:bg-slate-900 hover:border-slate-700"
                        }`}
                      >
                        <div className="flex items-center gap-2.5 min-w-0">
                          <MessageSquare size={14} className={isActive ? "text-indigo-400 shrink-0" : "text-slate-500 shrink-0"} />
                          <div className="min-w-0">
                            <div className="text-xs font-bold truncate">{sess.title}</div>
                            <div className="text-[10px] text-slate-500 truncate">{sess.message_count || 1} turns • {sess.last_message || "Active chat"}</div>
                          </div>
                        </div>

                        <button
                          onClick={(e) => handleDeleteSession(sess.session_id, e)}
                          className="p-1 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition opacity-0 group-hover:opacity-100"
                          title="Delete Session"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Soft Non-Intrusive Redirection Notice */}
          {softRedirect && (
            <div className="flex items-center justify-between p-2.5 bg-gradient-to-r from-indigo-500/15 to-cyan-500/15 border-b border-cyan-500/30 text-[10px] animate-in fade-in slide-in-from-top-2">
              <span className="text-slate-700 dark:text-slate-200 font-medium truncate">
                ✨ <strong>{softRedirect.label}</strong> is ready to explore.
              </span>
              <button
                onClick={() => {
                  router.push(softRedirect.route);
                  setSoftRedirect(null);
                }}
                className="px-2 py-0.5 rounded-md bg-cyan-600 text-white font-bold hover:bg-cyan-500 transition cursor-pointer"
              >
                Go →
              </button>
            </div>
          )}

          {/* Messages Stream Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4 p-4 text-slate-400">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-cyan-400 flex items-center justify-center text-white shadow-xl shadow-indigo-500/20">
                  <Sparkles size={22} className="animate-pulse" />
                </div>
                <div>
                  <h4 className="font-extrabold text-sm text-slate-900 dark:text-slate-100">
                    How can I assist your workflow today?
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-1 max-w-[240px]">
                    Autonomous agent with real mathematical solvers, live web scraping, and vector synthesis.
                  </p>
                </div>
                <div className="grid grid-cols-1 gap-1.5 w-full pt-1">
                  {suggestedQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(q.label.replace(/^[^a-zA-Z0-9]+/, "").trim())}
                      className="text-left px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 text-slate-700 dark:text-slate-300 text-[11px] font-semibold transition border border-slate-200 dark:border-slate-750 flex items-center justify-between group cursor-pointer"
                    >
                      <span className="truncate">{q.label}</span>
                      <ArrowRight size={11} className="opacity-0 group-hover:opacity-100 text-indigo-400 transition" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-2.5 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-6 h-6 rounded-lg bg-indigo-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                    <Bot size={13} />
                  </div>
                )}
                <div
                  className={`max-w-[85%] rounded-2xl p-3 leading-relaxed ${
                    msg.role === "user"
                      ? "bg-gradient-to-r from-indigo-600 to-cyan-600 text-white shadow-md rounded-tr-xs"
                      : "bg-slate-100 dark:bg-slate-800/90 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-750 rounded-tl-xs"
                  }`}
                >
                  <div className="prose prose-xs dark:prose-invert max-w-none text-[11.5px] leading-relaxed">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex]}
                      components={markdownComponents}
                    >
                      {formatMathMarkdown(msg.content)}
                    </ReactMarkdown>
                  </div>

                  {msg.action_card && (
                    <div className="mt-3 pt-2.5 border-t border-slate-200 dark:border-slate-700/80 space-y-2">
                      <div className="flex items-center justify-between text-[11px] font-bold text-indigo-400">
                        <span>{msg.action_card.title || "Recommended Action"}</span>
                        {msg.action_card.type === "proposal" && (
                          <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono text-[9px]">
                            Approval Required
                          </span>
                        )}
                      </div>

                      {msg.action_card.type === "proposal" ? (
                        <div className="rounded-xl bg-slate-900/60 p-2.5 border border-slate-700/50 space-y-2">
                          <p className="text-[11px] text-slate-300">{msg.action_card.description}</p>
                          {msg.action_card.preview && (
                            <pre className="text-[10px] font-mono bg-slate-950 p-2 rounded-lg overflow-x-auto text-cyan-300">
                              {JSON.stringify(msg.action_card.preview, null, 2)}
                            </pre>
                          )}
                          <div className="flex items-center gap-2 pt-1">
                            <button
                              onClick={() => handlePreviewProposal(msg.action_card, i)}
                              disabled={isStreaming}
                              className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 font-bold hover:bg-slate-700 transition"
                            >
                              Preview
                            </button>
                            <button
                              onClick={() => handleExecuteProposal(msg.action_card)}
                              disabled={isStreaming}
                              className="px-3 py-1 rounded-lg bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold transition"
                            >
                              ✓ Execute
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="rounded-xl bg-cyan-950/20 border border-cyan-500/30 p-2.5 space-y-1.5">
                          <div className="flex items-center gap-1.5 font-bold text-cyan-300">
                            <CheckCircle2 size={13} className="text-emerald-400" />
                            <span>Action Ready</span>
                          </div>
                          {msg.action_card.route_link && (
                            <div className="flex gap-2 pt-1">
                              <button
                                onClick={() => router.push(msg.action_card.route_link)}
                                className="inline-flex items-center gap-1 px-3 py-1 rounded-xl bg-cyan-600 text-white font-bold hover:bg-cyan-500 transition cursor-pointer"
                              >
                                <span>Open {msg.action_card.route_label || "Studio"}</span>
                                <ArrowRight size={11} />
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
                <Loader2 size={13} className="animate-spin text-cyan-400" />
                <span className="text-[11px]">Copilot thinking & solving...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* INPUT BAR */}
          <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask or command: 'Clean my data', 'Scrape leads'..."
                className="flex-1 rounded-2xl border border-slate-200 dark:border-slate-750 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                disabled={isStreaming}
              />
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="p-2.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white disabled:opacity-40 transition shadow-md cursor-pointer"
              >
                <Send size={14} />
              </button>
            </form>
          </div>

        </div>
      )}
    </>
  );
}
