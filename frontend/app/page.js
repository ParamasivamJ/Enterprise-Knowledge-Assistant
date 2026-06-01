"use client";

import { useState } from "react";
import { API_BASE_URL } from "./config";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/ChatArea";
import SourcePanel from "./components/SourcePanel";

export default function Home() {
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [activeSources, setActiveSources] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeView, setActiveView] = useState("chat"); // chat | admin

  // Refresh document list from API
  const refreshDocuments = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/documents`);
      if (res.ok) {
        const docs = await res.json();
        setDocuments(docs);
      }
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    }
  };

  // Send a chat message
  const sendMessage = async (query) => {
    if (!query.trim() || isLoading) return;

    // Add user message
    const userMsg = { role: "user", content: query, id: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setActiveSources([]);

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) throw new Error("Chat request failed");

      const data = await res.json();

      const assistantMsg = {
        role: "assistant",
        content: data.answer,
        confidence: data.confidence,
        sources: data.sources,
        latency: data.latency,
        messageId: data.message_id,
        id: Date.now() + 1,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setActiveSources(data.sources || []);
    } catch (err) {
      const errorMsg = {
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please check that the backend is running.",
        confidence: 0,
        sources: [],
        id: Date.now() + 1,
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // Submit feedback
  const submitFeedback = async (messageId, isPositive) => {
    try {
      await fetch(`${API_BASE_URL}/api/admin/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message_id: messageId, is_positive: isPositive }),
      });
    } catch (err) {
      console.error("Feedback failed:", err);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Sidebar — Documents & Navigation */}
      <Sidebar
        documents={documents}
        refreshDocuments={refreshDocuments}
        activeView={activeView}
        setActiveView={setActiveView}
      />

      {/* Center — Chat Area */}
      <ChatArea
        messages={messages}
        isLoading={isLoading}
        sendMessage={sendMessage}
        submitFeedback={submitFeedback}
        activeView={activeView}
      />

      {/* Right — Source Panel */}
      <SourcePanel sources={activeSources} />
    </div>
  );
}
