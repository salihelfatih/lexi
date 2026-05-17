"use client";

import { motion } from "framer-motion";
import { useRef, useEffect } from "react";

const SUGGESTED_QUESTIONS = [
  "What is the monthly rent?",
  "When does the lease end?",
  "What does it say about maintenance?",
  "What does it say about landlord entry?"
];

function activeLabel(activeDocument, documentId) {
  if (activeDocument?.filename) {
    return activeDocument.filename;
  }

  return documentId ? `Document ${documentId}` : "No active document";
}

export function ModernQaPanel({
  activeDocument,
  documentId,
  isAsking,
  messages,
  onAsk,
  question,
  results,
  setQuestion,
  setUserContext,
  userContext
}) {
  const textareaRef = useRef(null);
  const chatEndRef = useRef(null);
  const isReady = Boolean(results && documentId && results.document_type === "ontario_residential_lease");
  const label = activeLabel(activeDocument, documentId);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  function handleSubmit(event) {
    event.preventDefault();
    onAsk();
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (question.trim() && !isAsking) {
        onAsk();
      }
    }
  }

  function autoResize() {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }

  useEffect(() => {
    autoResize();
  }, [question]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32, delay: 0.1 }}
      style={{ marginTop: "1.5rem" }}
    >
      <div className="unified-workflow-card">
        <div className="workflow-section">
          <div className="workflow-section-header">
            <h3>💬 Ask Questions</h3>
          </div>
          <p className="muted" style={{ margin: "0 0 1rem", fontSize: "0.9rem" }}>
            Answering from: <strong>{label}</strong>
          </p>

          {!isReady ? (
            <p className="muted" style={{ textAlign: "center", padding: "2rem 0" }}>
              Q&A appears after Lexi finishes processing a supported Ontario residential lease.
            </p>
          ) : (
            <>
              {/* Chat Thread */}
              <div className="chat-thread" aria-live="polite" style={{ marginBottom: "1.5rem", minHeight: "200px" }}>
                {messages.length === 0 ? (
                  <div style={{ textAlign: "center", padding: "2rem 0" }}>
                    <p className="muted">No questions yet. Try asking something below!</p>
                  </div>
                ) : null}

                {messages.map((message) => (
                  <article className={`chat-message ${message.role}`} key={message.id}>
                    {message.role === "user" ? (
                      <>
                        <p>{message.question}</p>
                        {message.userContext ? (
                          <small>Context: {message.userContext}</small>
                        ) : null}
                      </>
                    ) : (
                      <>
                        <p>{message.answer}</p>
                        {message.userContextNote ? <small>{message.userContextNote}</small> : null}
                        {message.citations?.length ? (
                          <div className="citation-list" style={{ marginTop: "0.75rem" }}>
                            {message.citations.map((citation) => (
                              <blockquote key={`${message.id}-${citation.citation_id}`}>
                                <strong>{citation.citation_id}</strong>
                                <span>{citation.text}</span>
                              </blockquote>
                            ))}
                          </div>
                        ) : null}
                      </>
                    )}
                  </article>
                ))}
                <div ref={chatEndRef} />
              </div>

              {/* Suggested Questions */}
              {messages.length === 0 ? (
                <div className="question-suggestions" style={{ marginBottom: "1rem" }}>
                  <span className="muted" style={{ fontSize: "0.88rem" }}>Suggested:</span>
                  {SUGGESTED_QUESTIONS.map((suggestion) => (
                    <button key={suggestion} type="button" onClick={() => setQuestion(suggestion)}>
                      {suggestion}
                    </button>
                  ))}
                </div>
              ) : null}

              {/* Optional Context Input */}
              {userContext || messages.length > 0 ? (
                <div style={{ marginBottom: "1rem" }}>
                  <label htmlFor="user-context" style={{ display: "block", marginBottom: "0.5rem", fontSize: "0.9rem", fontWeight: 650 }}>
                    Situation context (optional)
                  </label>
                  <textarea
                    id="user-context"
                    className="text-input"
                    onChange={(event) => setUserContext(event.target.value)}
                    placeholder="Example: I was told something different by email."
                    rows={2}
                    value={userContext}
                    style={{ fontSize: "0.92rem" }}
                  />
                  <p className="muted" style={{ margin: "0.35rem 0 0", fontSize: "0.82rem" }}>
                    This stays separate from document evidence and cannot override source text.
                  </p>
                </div>
              ) : null}

              {/* Chat Input */}
              <form onSubmit={handleSubmit}>
                <div className="chat-input-container">
                  <div className="chat-input-wrapper">
                    <textarea
                      ref={textareaRef}
                      className="chat-input"
                      onChange={(event) => setQuestion(event.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask about rent, dates, maintenance, access, or another clause..."
                      value={question}
                      rows={1}
                      style={{ maxHeight: "200px", overflow: "auto" }}
                    />
                    <div className="chat-input-actions">
                      <span className="chat-input-hint">
                        {isAsking ? "Thinking..." : "Press Enter to send, Shift+Enter for new line"}
                      </span>
                      <button
                        type="submit"
                        className="icon-button"
                        disabled={!question.trim() || isAsking}
                      >
                        {isAsking ? "Asking..." : "Send"}
                      </button>
                    </div>
                  </div>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
}
