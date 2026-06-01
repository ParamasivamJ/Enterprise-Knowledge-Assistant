"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send, Loader2, ThumbsUp, ThumbsDown, Sparkles,
  Clock, Zap, FileText, ShieldAlert, Bot, User,
} from "lucide-react";
import AdminDashboard from "./AdminDashboard";

export default function ChatArea({ messages, isLoading, sendMessage, submitFeedback, activeView }) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      sendMessage(input.trim());
      setInput("");
    }
  };

  if (activeView === "admin") {
    return <AdminDashboard />;
  }

  return (
    <main className="flex-1 flex flex-col min-w-0" style={{ background: "var(--bg-primary)" }}>
      {/* Header */}
      <header className="h-14 flex items-center px-6 border-b flex-shrink-0"
        style={{ borderColor: "var(--border)", background: "var(--bg-secondary)" }}>
        <div className="flex items-center gap-2">
          <Sparkles size={16} style={{ color: "var(--accent)" }} />
          <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
            Chat with your Knowledge Base
          </h2>
        </div>
        <div className="ml-auto flex items-center gap-3 text-xs" style={{ color: "var(--text-muted)" }}>
          <span className="flex items-center gap-1">
            <Zap size={12} style={{ color: "var(--success)" }} />
            Groq Llama 3
          </span>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                submitFeedback={submitFeedback}
              />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="px-6 pb-5 pt-2 flex-shrink-0">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div
            className="flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-300"
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={isLoading}
              className="flex-1 bg-transparent outline-none text-sm placeholder-opacity-50"
              style={{ color: "var(--text-primary)" }}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="p-2 rounded-xl transition-all duration-200 disabled:opacity-30"
              style={{
                background: input.trim() ? "var(--accent)" : "var(--bg-hover)",
                color: "#fff",
              }}
            >
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
            </button>
          </div>
          <p className="text-center text-xs mt-2" style={{ color: "var(--text-muted)" }}>
            Answers are grounded in your uploaded documents. Sources are cited.
          </p>
        </form>
      </div>
    </main>
  );
}

/* ── Empty State ── */
function EmptyState() {
  const suggestions = [
    "What are the key findings in my report?",
    "Summarize the main points of the policy document.",
    "What does section 3.2 say about risk mitigation?",
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full animate-fade-in">
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center mb-5 animate-pulse-glow"
        style={{ background: "var(--accent-glow)", border: "1px solid var(--accent)" }}
      >
        <Brain size={30} style={{ color: "var(--accent-light)" }} />
      </div>
      <h2 className="text-xl font-semibold mb-1 gradient-text">Enterprise Knowledge Assistant</h2>
      <p className="text-sm mb-8" style={{ color: "var(--text-secondary)" }}>
        Upload documents and ask questions. Every answer includes citations.
      </p>
      <div className="space-y-2 w-full max-w-md">
        {suggestions.map((s, i) => (
          <button
            key={i}
            className="w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-200 hover:scale-[1.01]"
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              color: "var(--text-secondary)",
            }}
          >
            <span style={{ color: "var(--accent-light)" }}>→ </span>{s}
          </button>
        ))}
      </div>
    </div>
  );
}

/* ── Typing Indicator ── */
function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{ background: "var(--accent-glow)", border: "1px solid var(--accent)" }}>
        <Bot size={16} style={{ color: "var(--accent-light)" }} />
      </div>
      <div className="px-4 py-3 rounded-2xl" style={{ background: "var(--bg-card)" }}>
        <div className="flex gap-1.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full"
              style={{
                background: "var(--accent)",
                animation: `pulse 1.4s ${i * 0.2}s infinite ease-in-out`,
              }}
            />
          ))}
        </div>
      </div>
      <style jsx>{`
        @keyframes pulse {
          0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  );
}

/* ── Brain icon for empty state ── */
function Brain(props) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={props.size} height={props.size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={props.style}>
      <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>
      <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>
      <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/>
      <path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/>
      <path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/>
      <path d="M3.477 10.896a4 4 0 0 1 .585-.396"/>
      <path d="M19.938 10.5a4 4 0 0 1 .585.396"/>
      <path d="M6 18a4 4 0 0 1-1.967-.516"/>
      <path d="M19.967 17.484A4 4 0 0 1 18 18"/>
    </svg>
  );
}

/* ── Message Bubble ── */
function MessageBubble({ message, submitFeedback }) {
  const [feedbackGiven, setFeedbackGiven] = useState(null);
  const isUser = message.role === "user";

  const handleFeedback = (isPositive) => {
    if (message.messageId) {
      submitFeedback(message.messageId, isPositive);
      setFeedbackGiven(isPositive);
    }
  };

  return (
    <div className={`flex gap-3 animate-fade-in ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{
          background: isUser ? "var(--bg-hover)" : "var(--accent-glow)",
          border: `1px solid ${isUser ? "var(--border)" : "var(--accent)"}`,
        }}
      >
        {isUser ? (
          <User size={16} style={{ color: "var(--text-secondary)" }} />
        ) : (
          <Bot size={16} style={{ color: "var(--accent-light)" }} />
        )}
      </div>

      {/* Content */}
      <div className={`max-w-[75%] ${isUser ? "text-right" : ""}`}>
        <div
          className="px-4 py-3 rounded-2xl text-sm leading-relaxed"
          style={{
            background: isUser ? "var(--accent)" : "var(--bg-card)",
            color: isUser ? "#ffffff" : "var(--text-primary)",
            border: isUser ? "none" : "1px solid var(--border)",
            borderTopRightRadius: isUser ? "4px" : "16px",
            borderTopLeftRadius: isUser ? "16px" : "4px",
          }}
        >
          {message.content}
        </div>

        {/* Assistant metadata */}
        {!isUser && !message.isError && (
          <div className="flex items-center gap-3 mt-2 px-1">
            {/* Confidence */}
            {message.confidence !== undefined && (
              <span className="flex items-center gap-1 text-xs" style={{
                color: message.confidence > 0.7 ? "var(--success)" :
                       message.confidence > 0.4 ? "var(--warning)" : "var(--danger)"
              }}>
                <ShieldAlert size={11} />
                {Math.round(message.confidence * 100)}% confidence
              </span>
            )}

            {/* Latency */}
            {message.latency && (
              <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-muted)" }}>
                <Clock size={11} />
                {message.latency.total_ms}ms
              </span>
            )}

            {/* Sources count */}
            {message.sources?.length > 0 && (
              <span className="flex items-center gap-1 text-xs" style={{ color: "var(--accent-light)" }}>
                <FileText size={11} />
                {message.sources.length} sources
              </span>
            )}

            {/* Feedback */}
            <div className="flex gap-1 ml-auto">
              <button
                onClick={() => handleFeedback(true)}
                disabled={feedbackGiven !== null}
                className="p-1 rounded transition-all duration-200"
                style={{
                  color: feedbackGiven === true ? "var(--success)" : "var(--text-muted)",
                  opacity: feedbackGiven !== null && feedbackGiven !== true ? 0.3 : 1,
                }}
              >
                <ThumbsUp size={13} />
              </button>
              <button
                onClick={() => handleFeedback(false)}
                disabled={feedbackGiven !== null}
                className="p-1 rounded transition-all duration-200"
                style={{
                  color: feedbackGiven === false ? "var(--danger)" : "var(--text-muted)",
                  opacity: feedbackGiven !== null && feedbackGiven !== false ? 0.3 : 1,
                }}
              >
                <ThumbsDown size={13} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
