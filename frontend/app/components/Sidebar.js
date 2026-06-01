"use client";

import { useState, useEffect, useRef } from "react";
import { API_BASE_URL } from "../config";
import {
  Upload, FileText, Trash2, CheckCircle, AlertCircle,
  Loader2, MessageSquare, BarChart3, Brain, ChevronRight,
} from "lucide-react";

export default function Sidebar({ documents, refreshDocuments, activeView, setActiveView }) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    refreshDocuments();
  }, []);

  const handleUpload = async (file) => {
    if (!file) return;
    setIsUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/api/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      setUploadStatus({
        type: "success",
        message: `"${data.filename}" processed — ${data.total_chunks} chunks indexed.`,
      });
      refreshDocuments();
    } catch (err) {
      setUploadStatus({ type: "error", message: err.message || "Upload failed" });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!confirm(`Delete "${filename}" and all its vectors?`)) return;
    try {
      await fetch(`${API_BASE_URL}/api/documents/${docId}`, { method: "DELETE" });
      refreshDocuments();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const formatSize = (bytes) => {
    if (!bytes) return "—";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
  };

  return (
    <aside className="w-72 flex-shrink-0 flex flex-col border-r"
      style={{ background: "var(--bg-secondary)", borderColor: "var(--border)" }}
    >
      {/* Logo */}
      <div className="p-5 border-b" style={{ borderColor: "var(--border)" }}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ background: "var(--accent-glow)", border: "1px solid var(--accent)" }}>
            <Brain size={20} style={{ color: "var(--accent-light)" }} />
          </div>
          <div>
            <h1 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>Knowledge</h1>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>Assistant</p>
          </div>
        </div>
      </div>

      {/* Nav Tabs */}
      <div className="flex gap-1 p-3">
        {[
          { id: "chat", icon: MessageSquare, label: "Chat" },
          { id: "admin", icon: BarChart3, label: "Admin" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveView(tab.id)}
            className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-medium transition-all duration-200"
            style={{
              background: activeView === tab.id ? "var(--accent-glow)" : "transparent",
              color: activeView === tab.id ? "var(--accent-light)" : "var(--text-secondary)",
              border: activeView === tab.id ? "1px solid var(--accent)" : "1px solid transparent",
            }}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Upload Zone */}
      <div className="px-3 pb-3">
        <div
          className="relative rounded-xl p-4 text-center cursor-pointer transition-all duration-300"
          style={{
            border: isDragOver ? "2px dashed var(--accent)" : "2px dashed var(--border)",
            background: isDragOver ? "var(--accent-glow)" : "var(--bg-card)",
          }}
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            onChange={(e) => handleUpload(e.target.files[0])}
          />
          {isUploading ? (
            <Loader2 size={24} className="mx-auto mb-2 animate-spin" style={{ color: "var(--accent)" }} />
          ) : (
            <Upload size={24} className="mx-auto mb-2" style={{ color: "var(--text-muted)" }} />
          )}
          <p className="text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
            {isUploading ? "Processing..." : "Drop files or click"}
          </p>
          <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>PDF, DOCX, TXT</p>
        </div>

        {/* Upload Status */}
        {uploadStatus && (
          <div
            className="mt-2 p-2.5 rounded-lg flex items-start gap-2 text-xs animate-fade-in"
            style={{
              background: uploadStatus.type === "success" ? "rgba(0,210,160,0.1)" : "rgba(255,107,107,0.1)",
              border: `1px solid ${uploadStatus.type === "success" ? "var(--success)" : "var(--danger)"}`,
              color: uploadStatus.type === "success" ? "var(--success)" : "var(--danger)",
            }}
          >
            {uploadStatus.type === "success" ? <CheckCircle size={14} className="mt-0.5 flex-shrink-0" /> : <AlertCircle size={14} className="mt-0.5 flex-shrink-0" />}
            <span>{uploadStatus.message}</span>
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        <p className="text-xs font-semibold uppercase tracking-wider mb-2 px-1"
          style={{ color: "var(--text-muted)" }}>
          Documents ({documents.length})
        </p>

        {documents.length === 0 ? (
          <p className="text-xs px-1" style={{ color: "var(--text-muted)" }}>
            No documents uploaded yet.
          </p>
        ) : (
          <div className="space-y-1.5">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="group flex items-center gap-2.5 p-2.5 rounded-lg transition-all duration-200 hover:scale-[1.01]"
                style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
              >
                <FileText size={16} className="flex-shrink-0" style={{ color: "var(--accent-light)" }} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium truncate" style={{ color: "var(--text-primary)" }}>
                    {doc.filename}
                  </p>
                  <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                    {doc.total_chunks} chunks · {formatSize(doc.file_size_bytes)}
                  </p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); handleDelete(doc.id, doc.filename); }}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded transition-all duration-200"
                  style={{ color: "var(--danger)" }}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
