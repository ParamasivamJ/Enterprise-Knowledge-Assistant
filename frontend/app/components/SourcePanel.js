"use client";

import { FileText, ExternalLink, Hash } from "lucide-react";

export default function SourcePanel({ sources }) {
  if (!sources || sources.length === 0) {
    return (
      <aside className="w-72 flex-shrink-0 border-l flex flex-col"
        style={{ background: "var(--bg-secondary)", borderColor: "var(--border)" }}>
        <div className="p-5 border-b" style={{ borderColor: "var(--border)" }}>
          <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>Sources</h3>
          <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
            Retrieved passages will appear here
          </p>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center">
            <div className="w-12 h-12 rounded-xl mx-auto mb-3 flex items-center justify-center"
              style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}>
              <FileText size={20} style={{ color: "var(--text-muted)" }} />
            </div>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              Ask a question to see relevant source passages with page references.
            </p>
          </div>
        </div>
      </aside>
    );
  }

  return (
    <aside className="w-72 flex-shrink-0 border-l flex flex-col"
      style={{ background: "var(--bg-secondary)", borderColor: "var(--border)" }}>
      <div className="p-5 border-b" style={{ borderColor: "var(--border)" }}>
        <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
          Sources
          <span className="ml-2 px-1.5 py-0.5 rounded text-xs"
            style={{ background: "var(--accent-glow)", color: "var(--accent-light)" }}>
            {sources.length}
          </span>
        </h3>
        <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
          Retrieved passages for this answer
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {sources.map((source, i) => (
          <div
            key={i}
            className="rounded-xl p-3.5 transition-all duration-200 animate-fade-in hover:scale-[1.01]"
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              animationDelay: `${i * 80}ms`,
              animationFillMode: "backwards",
            }}
          >
            {/* Source header */}
            <div className="flex items-center gap-2 mb-2">
              <FileText size={13} style={{ color: "var(--accent-light)" }} />
              <span className="text-xs font-medium truncate" style={{ color: "var(--accent-light)" }}>
                {source.filename}
              </span>
              <span className="ml-auto text-xs px-1.5 py-0.5 rounded"
                style={{ background: "var(--bg-hover)", color: "var(--text-muted)" }}>
                p.{source.page}
              </span>
            </div>

            {/* Preview text */}
            <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
              {source.preview}
            </p>

            {/* Score bar */}
            <div className="mt-2.5 flex items-center gap-2">
              <div className="flex-1 h-1 rounded-full overflow-hidden"
                style={{ background: "var(--bg-hover)" }}>
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.round(source.score * 100)}%`,
                    background: source.score > 0.7
                      ? "var(--success)"
                      : source.score > 0.4
                        ? "var(--warning)"
                        : "var(--danger)",
                  }}
                />
              </div>
              <span className="text-xs font-mono" style={{
                color: source.score > 0.7 ? "var(--success)" :
                       source.score > 0.4 ? "var(--warning)" : "var(--danger)"
              }}>
                {Math.round(source.score * 100)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
