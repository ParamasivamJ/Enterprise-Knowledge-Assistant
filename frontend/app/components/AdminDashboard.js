"use client";

import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config";
import {
  BarChart3, Clock, Zap, MessageSquare, ThumbsUp,
  ThumbsDown, FileText, RefreshCw, TrendingUp,
  ShieldCheck, DollarSign, Activity,
} from "lucide-react";

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [recentQueries, setRecentQueries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [metricsRes, queriesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/metrics`),
        fetch(`${API_BASE_URL}/api/admin/recent-queries?limit=10`),
      ]);
      if (metricsRes.ok) setMetrics(await metricsRes.json());
      if (queriesRes.ok) setRecentQueries(await queriesRes.json());
    } catch (err) {
      console.error("Failed to fetch metrics:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (isLoading) {
    return (
      <main className="flex-1 flex items-center justify-center" style={{ background: "var(--bg-primary)" }}>
        <RefreshCw size={24} className="animate-spin" style={{ color: "var(--accent)" }} />
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto" style={{ background: "var(--bg-primary)" }}>
      {/* Header */}
      <header className="h-14 flex items-center justify-between px-6 border-b flex-shrink-0"
        style={{ borderColor: "var(--border)", background: "var(--bg-secondary)" }}>
        <div className="flex items-center gap-2">
          <BarChart3 size={16} style={{ color: "var(--accent)" }} />
          <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>Admin Dashboard</h2>
        </div>
        <button onClick={fetchData}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all duration-200"
          style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}>
          <RefreshCw size={12} /> Refresh
        </button>
      </header>

      <div className="p-6 max-w-6xl mx-auto">
        {/* Metric Cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <MetricCard
            icon={MessageSquare} label="Total Queries"
            value={metrics?.queries?.total || 0} color="var(--accent)"
          />
          <MetricCard
            icon={Clock} label="Avg Latency"
            value={`${Math.round(metrics?.queries?.avg_latency_ms || 0)}ms`} color="var(--warning)"
          />
          <MetricCard
            icon={ThumbsUp} label="Satisfaction"
            value={`${metrics?.feedback?.satisfaction_rate || 0}%`} color="var(--success)"
          />
          <MetricCard
            icon={FileText} label="Documents"
            value={metrics?.documents?.total || 0} color="var(--accent-light)"
          />
        </div>

        {/* Two-Column Layout */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {/* Latency Breakdown */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold mb-4 flex items-center gap-2"
              style={{ color: "var(--text-primary)" }}>
              <Activity size={14} style={{ color: "var(--warning)" }} />
              Latency Breakdown
            </h3>
            <div className="space-y-3">
              <BarMetric label="Retrieval" value={metrics?.queries?.avg_retrieval_ms || 0} max={2000} color="var(--accent)" unit="ms" />
              <BarMetric label="Generation" value={metrics?.queries?.avg_generation_ms || 0} max={2000} color="var(--success)" unit="ms" />
              <BarMetric label="Total" value={metrics?.queries?.avg_latency_ms || 0} max={3000} color="var(--warning)" unit="ms" />
            </div>
          </div>

          {/* Quality Scores */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold mb-4 flex items-center gap-2"
              style={{ color: "var(--text-primary)" }}>
              <ShieldCheck size={14} style={{ color: "var(--success)" }} />
              Quality Scores (Evaluation)
            </h3>
            <div className="space-y-3">
              <BarMetric label="Faithfulness" value={(metrics?.evaluation?.avg_faithfulness || 0) * 100} max={100} color="var(--success)" unit="%" />
              <BarMetric label="Answer Relevancy" value={(metrics?.evaluation?.avg_answer_relevancy || 0) * 100} max={100} color="var(--accent)" unit="%" />
              <BarMetric label="Context Precision" value={(metrics?.evaluation?.avg_context_precision || 0) * 100} max={100} color="var(--accent-light)" unit="%" />
            </div>
            {!metrics?.evaluation?.avg_faithfulness && (
              <p className="text-xs mt-3" style={{ color: "var(--text-muted)" }}>
                Run the evaluation script to populate these scores.
              </p>
            )}
          </div>
        </div>

        {/* Feedback Summary */}
        <div className="glass-card p-5 mb-6">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2"
            style={{ color: "var(--text-primary)" }}>
            <TrendingUp size={14} style={{ color: "var(--accent-light)" }} />
            User Feedback
          </h3>
          <div className="flex gap-6">
            <div className="flex items-center gap-2">
              <ThumbsUp size={16} style={{ color: "var(--success)" }} />
              <span className="text-xl font-bold" style={{ color: "var(--success)" }}>
                {metrics?.feedback?.positive || 0}
              </span>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>positive</span>
            </div>
            <div className="flex items-center gap-2">
              <ThumbsDown size={16} style={{ color: "var(--danger)" }} />
              <span className="text-xl font-bold" style={{ color: "var(--danger)" }}>
                {metrics?.feedback?.negative || 0}
              </span>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>negative</span>
            </div>
            <div className="flex items-center gap-2 ml-auto">
              <DollarSign size={14} style={{ color: "var(--text-muted)" }} />
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                Avg tokens/query: {Math.round(metrics?.queries?.avg_input_tokens || 0)} in / {Math.round(metrics?.queries?.avg_output_tokens || 0)} out
              </span>
            </div>
          </div>
        </div>

        {/* Recent Queries Table */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-primary)" }}>
            Recent Queries
          </h3>
          {recentQueries.length === 0 ? (
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>No queries yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr style={{ color: "var(--text-muted)", borderBottom: "1px solid var(--border)" }}>
                    <th className="text-left pb-2 font-medium">Response</th>
                    <th className="text-right pb-2 font-medium">Score</th>
                    <th className="text-right pb-2 font-medium">Latency</th>
                    <th className="text-right pb-2 font-medium">Tokens</th>
                    <th className="text-right pb-2 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {recentQueries.map((q) => (
                    <tr key={q.id} className="border-b" style={{ borderColor: "var(--border)" }}>
                      <td className="py-2.5 pr-4 max-w-xs truncate" style={{ color: "var(--text-secondary)" }}>
                        {q.content}
                      </td>
                      <td className="py-2.5 text-right font-mono" style={{
                        color: (q.top_retrieval_score || 0) > 0.7 ? "var(--success)" :
                               (q.top_retrieval_score || 0) > 0.4 ? "var(--warning)" : "var(--danger)"
                      }}>
                        {q.top_retrieval_score ? `${Math.round(q.top_retrieval_score * 100)}%` : "—"}
                      </td>
                      <td className="py-2.5 text-right font-mono" style={{ color: "var(--text-muted)" }}>
                        {q.latency_ms || "—"}ms
                      </td>
                      <td className="py-2.5 text-right font-mono" style={{ color: "var(--text-muted)" }}>
                        {q.input_tokens || 0}+{q.output_tokens || 0}
                      </td>
                      <td className="py-2.5 text-right" style={{ color: "var(--text-muted)" }}>
                        {q.created_at ? new Date(q.created_at).toLocaleTimeString() : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

/* ── Metric Card ── */
function MetricCard({ icon: Icon, label, value, color }) {
  return (
    <div className="glass-card p-4 animate-fade-in">
      <div className="flex items-center gap-2 mb-2">
        <Icon size={14} style={{ color }} />
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>{label}</span>
      </div>
      <p className="text-2xl font-bold" style={{ color }}>{value}</p>
    </div>
  );
}

/* ── Bar Metric ── */
function BarMetric({ label, value, max, color, unit }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span style={{ color: "var(--text-secondary)" }}>{label}</span>
        <span className="font-mono" style={{ color }}>{Math.round(value)}{unit}</span>
      </div>
      <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--bg-hover)" }}>
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}
