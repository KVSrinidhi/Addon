import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { showToast } from "./Toast";
import "./Summaries.css";

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function Summaries() {
  const { documents } = useOutletContext();

  const [selectedDocId, setSelectedDocId] = useState("");
  const [chapterSection, setChapterSection] = useState("");
  const [loading, setLoading] = useState(false);
  const [summaryResult, setSummaryResult] = useState(null);

  useEffect(() => {
    if (documents && documents.length > 0 && !selectedDocId) {
      const firstId=documents[0]?.id?.toString() || "";
      if(firstId){
        setSelectedDocId(firstId);
      }
    }
  }, [documents, selectedDocId]);

  const handleGenerateSummary = async (e) => {
    if (e) e.preventDefault();
    if (!selectedDocId) {
      showToast("Please select a document first", "error");
      return;
    }

    const selectedDoc = documents.find((doc) => doc.id.toString() === selectedDocId);

    if (selectedDoc?.status === "Processing") {
      showToast("This document is still being analyzed. Wait until it says 'Indexed'.", "info");
      return;
    }
    
    setLoading(true);
    setSummaryResult(null);

    try {
      const response = await fetch(`${API_URL}/summarize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          doc_id: selectedDocId,
          chapter_section: chapterSection || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed generating summary content.");
      }

      const serverData = await response.json(); 
      const rawText = serverData.summary || "";

      // ── Dynamic Highlights Extraction ─────────────────────────────────────
      // Parses the response dynamically to extract markdown bullet points
      const lines = rawText.split("\n").map(l => l.trim());
      const extractedTopics = lines
        .filter(line => line.startsWith("* ") || line.startsWith("- "))
        .map(line => line.substring(2).replace(/\*\*/g, "")); // Strip formatting syntax

      setSummaryResult({
        title: selectedDoc?.name || "Document Overview",
        tag: selectedDoc?.category || "PDF Study Guide",
        content: rawText,
        topics: extractedTopics.length > 0 ? extractedTopics : ["Core highlights successfully analyzed from document vectors."]
      });
      
      showToast("Summary rendered successfully!", "success");
    } catch (error) {
      showToast(`AI Pipeline Error: ${error.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="summaries-page-container">
      <form onSubmit={handleGenerateSummary} className="summary-config-card">
        <div className="config-grid">
          <div className="form-group">
            <label className="config-label">Select Document</label>
            <select
              className="config-select"
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
            >
              {documents.length === 0 ? (
                <option value="">No documents uploaded yet. Go to Documents.</option>
              ) : (
                documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.name} ({doc.status})
                  </option>
                ))
              )}
            </select>
          </div>

          <div className="form-group">
            <label className="config-label">Chapter / Section (optional)</label>
            <input
              type="text"
              className="config-input"
              placeholder="e.g. Chapter 2: System Architectures"
              value={chapterSection}
              onChange={(e) => setChapterSection(e.target.value)}
            />
          </div>
        </div>

        <div className="summary-actions">
          <button 
            type="submit" 
            className="btn-generate" 
            disabled={loading || documents.length === 0}
          >
            {loading ? "Generating..." : "Generate Summary"}
          </button>
          {summaryResult && (
            <button type="button" className="btn-regenerate" onClick={handleGenerateSummary}>
              🔄 Regenerate
            </button>
          )}
        </div>
      </form>

      {loading && (
        <div className="summary-loading-state">
          <div className="loader-spinner"></div>
          <p>Analyzing document syntax and drafting summary contents...</p>
        </div>
      )}

      {summaryResult && !loading && (
        <div className="summary-result-card">
          <div className="result-header">
            <div className="result-title-group">
              <h3>Generated Summary</h3>
              <span className="result-badge">{summaryResult.tag}</span>
            </div>
            <div className="result-actions">
              <button type="button" className="util-btn" onClick={() => { navigator.clipboard.writeText(summaryResult.content); showToast("Copied!", "success"); }}>📋 Copy</button>
              <button type="button" className="util-btn">📄 Export PDF</button>
              <button type="button" className="util-btn save-btn">💾 Save</button>
            </div>
          </div>

          <div className="result-body">
            <h4 className="output-heading">{summaryResult.title}</h4>
            {chapterSection && <p className="output-section-target"><strong>Target Scope:</strong> {chapterSection}</p>}
            
            {/* ── Render Content via our clean Markdown structural parser ── */}
            <FormattedSummary rawText={summaryResult.content} />
            
            <h5 className="section-subheading">Core Highlights & Topics</h5>
            <ul className="output-list">
              {summaryResult.topics.map((topic, i) => (
                <li key={i}>{topic}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}


function FormattedSummary({ rawText }) {
  if (!rawText) return null;

  const lines = rawText.split("\n");

  return (
    <div className="summary-document-render">
      {lines.map((line, idx) => {
        let cleanLine = line.trim();
        if (!cleanLine) return <div key={idx} className="summary-spacer" />;

        if (cleanLine.startsWith("* ") || cleanLine.startsWith("- ")) return null;

        if (cleanLine.startsWith("**") && cleanLine.endsWith("**")) {
          return (
            <h3 key={idx} className="summary-section-title">
              {cleanLine.replace(/\*\*/g, "")}
            </h3>
          );
        }

        return <p key={idx} className="summary-paragraph">{parseInlineBold(cleanLine)}</p>;
      })}
    </div>
  );
}

function parseInlineBold(text) {
  const parts = text.split(/\*\*([^*]+)\*\*/g);
  return parts.map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part));
}

export default Summaries;
