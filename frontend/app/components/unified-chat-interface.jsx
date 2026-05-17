"use client";

import { motion } from "framer-motion";
import { useRef, useEffect } from "react";
import { Button } from "./ui/button";

const SUGGESTED_QUESTIONS = [
  "What is the monthly rent?",
  "When does the lease end?",
  "What does it say about maintenance?",
  "What does it say about landlord entry?"
];

const RISK_SEVERITY_LABELS = {
  high: "Higher attention",
  medium: "Worth reviewing",
  low: "Helpful to note"
};

function formatConfidence(value) {
  if (value == null) {
    return "Not available";
  }

  return `${Number(value).toFixed(1)}%`;
}

export function UnifiedChatInterface({
  // Upload props
  acceptedTypes,
  canUpload,
  isDragging,
  isUploading,
  onDrop,
  onDragOver,
  onDragLeave,
  onFileInputChange,
  onUpload,
  selectedFile,
  // Consent props
  documentId,
  isSubmittingConsent,
  onConsentSubmit,
  processingConsent,
  setProcessingConsent,
  setStorageConsent,
  storageConsent,
  // Status props
  activeDocument,
  isDeleting,
  isPolling,
  jobStatus,
  onDelete,
  onStartNewUpload,
  prettifyStatus,
  progressPercent,
  // Results props
  results,
  onExportPdf,
  // Q&A props
  isAsking,
  messages,
  onAsk,
  question,
  setQuestion,
  setUserContext,
  userContext
}) {
  const textareaRef = useRef(null);
  const chatEndRef = useRef(null);

  const status = activeDocument?.job_status || jobStatus || "idle";
  const hasDocument = Boolean(documentId);
  const needsConsent = hasDocument && status === "pending";
  const isFailed = status === "failed";
  const isProcessing = hasDocument && !needsConsent && (isPolling || (status !== "idle" && status !== "complete" && status !== "failed"));
  const isComplete = Boolean(status === "complete" && results);
  const isUnsupported = Boolean(isComplete && results?.document_type === "unknown");
  const isReady = Boolean(isComplete && !isUnsupported && documentId && results?.document_type === "ontario_residential_lease");
  const isLowConfidenceResult = Boolean(
    isComplete &&
      !isUnsupported &&
      results?.extraction_confidence != null &&
      Number(results.extraction_confidence) < 60
  );
  const failureMessage = activeDocument?.error_message || "Lexi could not finish processing this document.";
  const unsupportedConfidence = Number(results?.classification_confidence || activeDocument?.classification_confidence || 0);
  const documentType = results?.document_type || activeDocument?.document_type;
  const documentTypeLabel = documentType === "unknown" ? "unsupported by Lexi" : documentType;
  const classificationConfidence = results?.classification_confidence ?? activeDocument?.classification_confidence;
  const riskSense = results?.risk_sense;
  const riskSignals = riskSense?.risks || [];
  const confidenceRollup = riskSense?.confidence_rollup;

  useEffect(() => {
    if (chatEndRef.current && messages.length > 0) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  function handleSubmit(event) {
    event.preventDefault();
    if (!hasDocument && selectedFile && canUpload) {
      onUpload();
    } else if (isReady && question.trim()) {
      onAsk();
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event);
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
      transition={{ duration: 0.32 }}
      className="unified-chat-container"
    >
      {/* Document Status Header (when document exists) */}
      {hasDocument && (
        <div className="chat-document-header">
          <div className="chat-document-info">
            <div className="chat-document-title-block">
              <h3>{activeDocument?.filename || selectedFile?.name || "Document"}</h3>
              <p className="status-line">
                <strong>Document:</strong> {documentId || "not uploaded"}
              </p>
              <p className="status-line">
                <strong>Status:</strong> {prettifyStatus(status)}
              </p>
              {documentType ? (
                <p className="status-line">
                  <strong>Type:</strong> {documentTypeLabel}
                  {classificationConfidence != null ? ` (${Number(classificationConfidence).toFixed(1)}%)` : ""}
                </p>
              ) : null}
            </div>
            {(status === "complete" || isFailed) && (
              <span
                className={`workflow-status-badge ${
                  isFailed ? "failed" : isUnsupported ? "unsupported" : isLowConfidenceResult ? "limited" : "complete"
                }`}
              >
                {isFailed
                  ? "Needs attention"
                  : isUnsupported
                  ? "Unsupported by Lexi"
                  : isLowConfidenceResult
                  ? "Limited summary"
                  : "Ready"}
              </span>
            )}
          </div>
          <Button
            variant="danger"
            className="compact-button"
            disabled={!documentId || isDeleting}
            onClick={onDelete}
          >
            {isDeleting ? "Deleting..." : "Delete document"}
          </Button>
        </div>
      )}

      {/* Processing State */}
      {isProcessing && (
        <div className="chat-processing-state">
          <div className="progress" role="progressbar" aria-valuenow={progressPercent} aria-valuemin={0} aria-valuemax={100}>
            <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
          </div>
          <p className="muted progress-label">{progressPercent}% complete</p>
          {isPolling && <p className="status-pulse">Analyzing your document...</p>}
        </div>
      )}

      {/* Failed State */}
      {isFailed && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.22 }}
          className="chat-failed-state"
          role="alert"
        >
          <div className="failed-state-header">
            <div>
              <p className="kicker">Processing stopped</p>
              <h4>Lexi could not analyze this upload.</h4>
            </div>
          </div>

          <p>{failureMessage}</p>

          <div className="failed-support-note">
            <strong>Next step</strong>
            <span>Start a fresh upload with the original file, or delete this failed document.</span>
          </div>

          <div className="failed-actions">
            <Button variant="secondary" onClick={onStartNewUpload}>
              Upload again
            </Button>
            <Button variant="danger" disabled={!documentId || isDeleting} onClick={onDelete}>
              {isDeleting ? "Deleting..." : "Delete document"}
            </Button>
          </div>
        </motion.div>
      )}

      {/* Consent State */}
      {needsConsent && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.22 }}
          className="chat-consent-state"
        >
          <div className="consent-state-header">
            <div>
              <p className="kicker">Before analysis</p>
              <h4>Choose what Lexi may do with this upload.</h4>
            </div>
          </div>
          <form className="consent-form" onSubmit={onConsentSubmit}>
            <p className="consent-note">
              Uploading only places the file in temporary intake. Processing starts after this step.
            </p>
            <label className="consent-choice">
              <input
                checked={processingConsent}
                onChange={(event) => setProcessingConsent(event.target.checked)}
                type="checkbox"
              />
              <span>
                <strong>I consent to processing this document.</strong>
                <small>Required for Lexi to extract text, summarize, answer questions, and show RiskSense signals.</small>
              </span>
            </label>
            <label className="consent-choice">
              <input
                checked={storageConsent}
                onChange={(event) => setStorageConsent(event.target.checked)}
                type="checkbox"
              />
              <span>
                <strong>I consent to persistent storage.</strong>
                <small>Optional. Leave this off to keep the document in ephemeral processing mode.</small>
              </span>
            </label>
            {!processingConsent ? (
              <p className="consent-decline-note">
                If processing consent stays off, submitting will delete this temporary upload without analysis.
              </p>
            ) : null}
            <Button type="submit" disabled={!documentId || isSubmittingConsent} style={{ width: "100%" }}>
              {isSubmittingConsent ? "Submitting..." : "Submit consent"}
            </Button>
          </form>
        </motion.div>
      )}

      {/* Unsupported State */}
      {isUnsupported && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.22 }}
          className="chat-unsupported-state"
          role="status"
        >
          <div className="unsupported-state-header">
            <div>
              <p className="kicker">Unsupported document</p>
              <h4>Lexi could not identify this as a supported document type yet.</h4>
            </div>
            <span className="unsupported-confidence">
              {unsupportedConfidence.toFixed(1)}% confidence
            </span>
          </div>

          <p>
            Lexi currently supports Ontario residential leases. This file may still be important,
            but it is unsupported by Lexi right now, so summaries and document Q&A are paused for it.
          </p>

          <div className="unsupported-support-note">
            <strong>What you can do next</strong>
            <span>Delete this upload or start again with a supported Ontario residential lease.</span>
          </div>

          <div className="unsupported-actions">
            <Button variant="secondary" onClick={onStartNewUpload}>
              Upload another document
            </Button>
            <Button variant="danger" disabled={!documentId || isDeleting} onClick={onDelete}>
              {isDeleting ? "Deleting..." : "Delete document"}
            </Button>
          </div>
        </motion.div>
      )}

      {/* Results Summary (when complete) */}
      {isComplete && !isUnsupported && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.24 }}
          className="chat-results-summary"
        >
          <div className="summary-section">
            <h4>Summary</h4>
            <p>{results.summary?.text || "Processing complete. You can now ask questions about this document."}</p>
            {results.summary && (
              <small className="muted">
                Grounded in {results.summary.source_count} source{results.summary.source_count === 1 ? "" : "s"}.
              </small>
            )}
          </div>

          <div className="readiness-strip" aria-label="What Lexi checked">
            <div>
              <span>Document type</span>
              <strong>{documentTypeLabel?.replaceAll("_", " ") || "Not found"}</strong>
            </div>
            <div>
              <span>Extraction</span>
              <strong>{formatConfidence(results.extraction_confidence)}</strong>
            </div>
            <div>
              <span>Classification</span>
              <strong>{formatConfidence(results.classification_confidence)}</strong>
            </div>
            <div>
              <span>Source clauses</span>
              <strong>{results.total_clauses || 0}</strong>
            </div>
          </div>

          {results.metadata && (
            <div className="key-details-grid">
              <div>
                <strong>Lease start:</strong> {results.metadata.lease_start_date || "Not Found"}
              </div>
              <div>
                <strong>Lease end:</strong> {results.metadata.lease_end_date || "Not Found"}
              </div>
              <div>
                <strong>Monthly rent:</strong> {results.metadata.monthly_rent || "Not Found"}
              </div>
            </div>
          )}

          {riskSense && (
            <motion.section
              className="risk-sense-section"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.24, delay: 0.05 }}
              aria-labelledby="risk-sense-heading"
            >
              <div className="risk-sense-header">
                <div>
                  <p className="kicker">RiskSense</p>
                  <h4 id="risk-sense-heading">Attention signals</h4>
                </div>
                <span className="risk-confidence-pill">
                  {formatConfidence(confidenceRollup?.overall)} confidence
                </span>
              </div>

              <p className="risk-sense-summary">{riskSense.top_risks_summary}</p>

              {riskSignals.length > 0 ? (
                <div className="risk-signal-list">
                  {riskSignals.slice(0, 3).map((risk) => (
                    <article className={`risk-signal severity-${risk.severity}`} key={risk.risk_id}>
                      <div className="risk-signal-header">
                        <div>
                          <h5>{risk.title}</h5>
                          <span>{formatConfidence(risk.confidence)} signal confidence</span>
                        </div>
                        <span className="risk-severity">{RISK_SEVERITY_LABELS[risk.severity] || risk.severity}</span>
                      </div>
                      <p>{risk.reason}</p>
                      {risk.source_clause ? (
                        <blockquote>
                          <strong>
                            Clause {risk.source_clause.clause_number} - {risk.source_clause.clause_type}
                          </strong>
                          <span>{risk.source_clause.clause_text}</span>
                        </blockquote>
                      ) : null}
                    </article>
                  ))}
                </div>
              ) : (
                <p className="muted">No rule-based attention signals were found in this first pass.</p>
              )}

              {confidenceRollup && (
                <div className="risk-rollup-grid" aria-label="RiskSense confidence rollup">
                  <div>
                    <span>Extraction</span>
                    <strong>{formatConfidence(confidenceRollup.extraction)}</strong>
                  </div>
                  <div>
                    <span>Classification</span>
                    <strong>{formatConfidence(confidenceRollup.classification)}</strong>
                  </div>
                  <div>
                    <span>Metadata</span>
                    <strong>{formatConfidence(confidenceRollup.metadata)}</strong>
                  </div>
                  <div>
                    <span>Risk signals</span>
                    <strong>{formatConfidence(confidenceRollup.risk_signals)}</strong>
                  </div>
                </div>
              )}
            </motion.section>
          )}

          <Button variant="secondary" onClick={onExportPdf} style={{ width: "100%", marginTop: "1rem" }}>
            Export as PDF
          </Button>
        </motion.div>
      )}

      {/* Chat Thread */}
      {isReady && messages.length > 0 && (
        <div className="chat-thread" aria-live="polite">
          {messages.map((message) => (
            <article className={`chat-message ${message.role}`} key={message.id}>
              {message.role === "user" ? (
                <>
                  <p>{message.question}</p>
                  {message.userContext && <small>Context: {message.userContext}</small>}
                </>
              ) : (
                <>
                  <p>{message.answer}</p>
                  {message.userContextNote && <small>{message.userContextNote}</small>}
                  {message.citations?.length > 0 && (
                    <div className="citation-list" style={{ marginTop: "0.75rem" }}>
                      {message.citations.map((citation) => (
                        <blockquote key={`${message.id}-${citation.citation_id}`}>
                          <strong>{citation.citation_id}</strong>
                          <span>{citation.text}</span>
                        </blockquote>
                      ))}
                    </div>
                  )}
                </>
              )}
            </article>
          ))}
          <div ref={chatEndRef} />
        </div>
      )}

      {/* Suggested Questions */}
      {isReady && messages.length === 0 && (
        <div className="question-suggestions">
          <span className="muted">You could ask:</span>
          {SUGGESTED_QUESTIONS.map((suggestion) => (
            <button key={suggestion} type="button" onClick={() => setQuestion(suggestion)}>
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {isReady && (
        <div className="qa-context-inline">
          <label htmlFor="user-context">Situation context (optional)</label>
          <textarea
            id="user-context"
            className="text-input"
            onChange={(event) => setUserContext(event.target.value)}
            placeholder="Example: I was told something different by email."
            rows={2}
            value={userContext}
          />
          <p className="muted context-note">
            This stays separate from document evidence and cannot override source text.
          </p>
        </div>
      )}

      {/* Chat Input */}
      {!isUnsupported && !isFailed && (
      <form onSubmit={handleSubmit} className="chat-input-form">
        {/* Drag & Drop Zone (when no document) */}
        {!hasDocument && (
          <>
            <div
              className={`chat-dropzone ${isDragging ? "dragging" : ""}`}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
            >
              <p>{selectedFile ? selectedFile.name : "Drop your document here or click to upload"}</p>
              <label className="button secondary" htmlFor="file-upload">
                Choose file
              </label>
              <input
                id="file-upload"
                type="file"
                accept={acceptedTypes}
                onChange={onFileInputChange}
                style={{ display: "none" }}
              />
              <small>Accepted: PDF, DOCX, PNG, JPG (max 50MB)</small>
            </div>

            {selectedFile && (
              <p className="upload-intake-note">
                Uploading starts a temporary intake only. Lexi asks for processing and storage consent next.
              </p>
            )}
          </>
        )}

        {/* Text Input */}
        <div className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            className="chat-input"
            aria-label="Question"
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              !hasDocument
                ? selectedFile
                  ? "Ready for consent review..."
                  : "Upload a document to begin..."
                : needsConsent
                ? "Submit consent to analyze this document..."
                : isReady
                ? "Ask about rent, dates, maintenance, access, or another clause..."
                : "Analyzing your document..."
            }
            value={question}
            rows={1}
            disabled={!hasDocument || (!isReady && hasDocument)}
            style={{ maxHeight: "200px", overflow: "auto" }}
          />
          <div className="chat-input-actions">
            <span className="chat-input-hint">
              {!hasDocument && selectedFile
                ? "Use Upload document to continue to consent"
                : needsConsent
                ? "Submit consent above to start analysis"
                : isAsking
                ? "Thinking..."
                : isReady
                ? "Press Enter to ask, Shift+Enter for new line"
                : ""}
            </span>
            <button
              type="submit"
              className="icon-button"
              disabled={(!hasDocument && !canUpload) || needsConsent || (isReady && !question.trim()) || isAsking || isProcessing}
            >
              {!hasDocument
                ? isUploading
                  ? "Uploading..."
                  : "Upload document"
                : isAsking
                ? "Asking..."
                : isReady
                ? "Ask"
                : "Send"}
            </button>
          </div>
        </div>
      </form>
      )}
    </motion.div>
  );
}
