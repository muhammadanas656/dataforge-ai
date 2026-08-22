"use client";
import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, Loader2, Sparkles, Compass, Database, Activity, Lightbulb } from "lucide-react";
import { useContextTracker } from "../hooks/useContextTracker";
import { getApiUrl, authFetch } from "../api";

export default function AssistantWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [contextData, setContextData] = useState(null);
  const messagesEndRef = useRef(null);
  const sessionId = useRef(`session_${typeof window !== "undefined" ? Math.random().toString(36).substring(7) : "init"}`);

  // Activate context tracking
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
    }
  }, [isOpen]);

  const sendMessage = async (customPrompt) => {
    const text = (customPrompt || input || "").trim();
    if (!text || isStreaming) return;

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsStreaming(true);

    try {
      const res = await authFetch(`/api/assistant/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId.current,
          query: text
        })
      });

      if (!res.ok) throw new Error("Assistant response failed");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = { role: "assistant", content: "" };
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
              setIsStreaming(false);
            }
          } catch (e) {
            // Non-json chunk
          }
        }
      }
    } catch (err) {
      console.error("Assistant query failed:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I encountered a transient connection issue. Please make sure the FastAPI server is running on port 8000."
        }
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  const suggestedQuestions = [
    { label: "Explain TRIZ Invention Studio", icon: Lightbulb },
    { label: "What does this module do?", icon: Compass },
    { label: "How does Causal Inference work?", icon: Activity },
    { label: "Explain Governed Cleaning Studio", icon: Database }
  ];

  return (
    <>
      {/* Floating Launcher Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full px-4 py-3 shadow-xl transition-all hover:scale-105 font-medium text-xs border border-indigo-400/40"
        title="Open DataForge Global Copilot"
      >
        <Sparkles size={16} className="animate-pulse" />
        <span>{isOpen ? "Close Copilot" : "DataForge Copilot"}</span>
      </button>

      {/* Slide-out Floating Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-6 z-50 w-96 max-w-[calc(100vw-2rem)] h-[560px] max-h-[calc(100vh-6rem)] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="flex items-center justify-between p-3.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-indigo-600 text-white">
                <Sparkles size={15} />
              </div>
              <div>
                <h3 className="font-bold text-xs text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                  DataForge Copilot
                  <span className="text-[10px] font-normal px-1.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-mono">
                    Context-Aware
                  </span>
                </h3>
                <p className="text-[10px] text-slate-500 capitalize">
                  Module: {contextData?.active_module || "Active"} · {contextData?.skill_level || "Pro"} Mode
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            >
              <X size={16} />
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-3.5 space-y-3 text-xs">
            {messages.length === 0 && (
              <div className="text-center py-4 space-y-3">
                <div className="w-10 h-10 mx-auto rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                  <Sparkles size={20} />
                </div>
                <div className="space-y-1 px-4">
                  <h4 className="font-semibold text-slate-800 dark:text-slate-200 text-xs">How can I assist you today?</h4>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    I have full cross-module context. Ask me about your data, statistical proofs, TRIZ inventions, or automated workflows.
                  </p>
                </div>

                <div className="grid gap-1.5 pt-2 px-2 text-left">
                  {suggestedQuestions.map((q, i) => {
                    const Icon = q.icon;
                    return (
                      <button
                        key={i}
                        onClick={() => sendMessage(q.label)}
                        className="flex items-center gap-2 w-full p-2 text-[11px] font-medium rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200/70 dark:border-slate-700/60 hover:border-indigo-400 dark:hover:border-indigo-600 text-slate-700 dark:text-slate-300 transition hover:bg-indigo-50/40 dark:hover:bg-indigo-950/20"
                      >
                        <Icon size={13} className="text-indigo-600 dark:text-indigo-400 shrink-0" />
                        <span className="truncate">{q.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-[11px] leading-relaxed shadow-xs ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white rounded-br-xs"
                      : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-xs border border-slate-200/60 dark:border-slate-700/60"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}

            {isStreaming && (
              <div className="flex justify-start">
                <div className="bg-slate-100 dark:bg-slate-800 rounded-2xl rounded-bl-xs px-3.5 py-2 border border-slate-200/60 dark:border-slate-700/60 flex items-center gap-1.5 text-[11px] text-slate-500">
                  <Loader2 className="animate-spin text-indigo-600" size={13} />
                  <span>Thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Footer Input */}
          <div className="p-2.5 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
            <div className="flex items-center gap-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-2.5 py-1.5 shadow-xs focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Ask about data, TRIZ, or workflows..."
                className="flex-1 bg-transparent text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none"
                disabled={isStreaming}
              />
              <button
                onClick={() => sendMessage()}
                disabled={!input.trim() || isStreaming}
                className="p-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white rounded-lg transition shrink-0"
              >
                <Send size={13} />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
