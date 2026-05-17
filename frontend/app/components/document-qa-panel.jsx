import { motion } from "framer-motion";

import { Card } from "./ui/card";
import { Button } from "./ui/button";

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

export function DocumentQaPanel({
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
  const isReady = Boolean(results && documentId && results.document_type === "ontario_residential_lease");
  const label = activeLabel(activeDocument, documentId);

  function handleSubmit(event) {
    event.preventDefault();
    onAsk();
  }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22, delay: 0.1 }}>
      <Card className="qa-panel">
        <div className="section-heading">
          <p className="kicker">Document Q&A</p>
          <h2>Ask about this document</h2>
          <p className="muted answer-source-line">Answering from: {label}</p>
        </div>

        {!isReady ? (
          <p className="muted">
            Q&A appears after Lexi finishes processing a supported Ontario residential lease.
          </p>
        ) : (
          <>
            <div className="question-suggestions" aria-label="Suggested questions">
              <span className="muted">You could ask:</span>
              {SUGGESTED_QUESTIONS.map((suggestion) => (
                <button key={suggestion} type="button" onClick={() => setQuestion(suggestion)}>
                  {suggestion}
                </button>
              ))}
            </div>

            <form className="qa-form" onSubmit={handleSubmit}>
              <label htmlFor="user-context">Situation context (optional)</label>
              <textarea
                id="user-context"
                className="text-input"
                onChange={(event) => setUserContext(event.target.value)}
                placeholder="Example: I was told something different by email."
                rows={3}
                value={userContext}
              />
              <p className="muted context-note">
                This stays separate from document evidence and cannot override source text.
              </p>

              <label htmlFor="document-question">Question</label>
              <div className="qa-input-row">
                <input
                  id="document-question"
                  className="text-input"
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Ask about rent, dates, maintenance, access, or another clause"
                  value={question}
                />
                <Button type="submit" disabled={!question.trim() || isAsking}>
                  {isAsking ? "Asking..." : "Ask"}
                </Button>
              </div>
            </form>

            <div className="chat-thread" aria-live="polite">
              {messages.length === 0 ? (
                <p className="muted">No questions yet for this document.</p>
              ) : null}

              {messages.map((message) => (
                <article className={`chat-message ${message.role}`} key={message.id}>
                  {message.role === "user" ? (
                    <>
                      <p>{message.question}</p>
                      {message.userContext ? (
                        <small>Situation context: {message.userContext}</small>
                      ) : null}
                    </>
                  ) : (
                    <>
                      <p>{message.answer}</p>
                      {message.userContextNote ? <small>{message.userContextNote}</small> : null}
                      {message.citations?.length ? (
                        <div className="citation-list">
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
            </div>
          </>
        )}
      </Card>
    </motion.div>
  );
}
