"use client";

import { motion } from "framer-motion";
import { Button } from "./ui/button";

function buildSummary(results, prettifyStatus) {
  if (!results) {
    return "No summary available yet.";
  }

  if (results.summary?.text) {
    return results.summary.text;
  }

  const docType = prettifyStatus(results.document_type || "unknown");
  const clauseCount = results.total_clauses || 0;
  const rent = results.metadata?.monthly_rent || "Not Found";
  const startDate = results.metadata?.lease_start_date || "Not Found";
  const endDate = results.metadata?.lease_end_date || "Not Found";

  return `This document was classified as ${docType}. Lexi extracted ${clauseCount} clauses, identified a monthly rent of ${rent}, and found lease dates from ${startDate} to ${endDate}.`;
}

export function UnifiedWorkflowCard({
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
  prettifyStatus,
  progressPercent,
  // Results props
  results,
  onExportPdf
}) {
  const status = activeDocument?.job_status || jobStatus || "idle";
  const type = results?.document_type || activeDocument?.document_type;
  const confidence = results?.classification_confidence ?? activeDocument?.classification_confidence;
  const summary = buildSummary(results, prettifyStatus);
  const sourceClauses = (results?.clauses || []).slice(0, 4);

  const showUpload = !documentId || status === "idle";
  const showConsent = documentId && !processingConsent && status !== "complete" && status !== "failed";
  const showProcessing = documentId && (isPolling || (status !== "idle" && status !== "complete" && status !== "failed"));
  const showResults = results && status === "complete";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.32 }}
      className="unified-workflow-card"
    >
      {/* Document Status Header */}
      {documentId ? (
        <div className="workflow-section">
          <div className="workflow-section-header">
            <h3>
              {activeDocument?.filename || selectedFile?.name || "Document"}
              {status !== "idle" && (
                <span className={`workflow-status-badge ${status === "complete" ? "complete" : "pending"}`}>
                  {prettifyStatus(status)}
                </span>
              )}
            </h3>
            <Button
              variant="danger"
              className="compact-button"
              disabled={!documentId || isDeleting}
              onClick={onDelete}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </Button>
          </div>

          {type ? (
            <p className="muted" style={{ margin: "0.5rem 0 0", fontSize: "0.9rem" }}>
              <strong>Type:</strong> {type}
              {confidence != null ? ` (${Number(confidence).toFixed(1)}% confidence)` : ""}
            </p>
          ) : null}

          {showProcessing ? (
            <div style={{ marginTop: "1rem" }}>
              <div
                aria-label="Processing progress"
                className="progress"
                role="progressbar"
                aria-valuenow={progressPercent}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
              </div>
              <p className="muted progress-label">{progressPercent}% complete</p>
              {isPolling ? <p className="status-pulse">Analyzing your document...</p> : null}
            </div>
          ) : null}
        </div>
      ) : null}

      {/* Upload Section */}
      {showUpload ? (
        <div className="workflow-section">
          <div className="workflow-section-header">
            <h3>📄 Upload Document</h3>
          </div>
          <div
            className={`dropzone ${isDragging ? "dragging" : ""}`}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
          >
            <p>{selectedFile ? selectedFile.name : "Drop your document here"}</p>
            <label className="button secondary" htmlFor="file-upload">
              Choose file
            </label>
            <input
              id="file-upload"
              type="file"
              accept={acceptedTypes}
              onChange={onFileInputChange}
            />
            <small>Accepted: PDF, DOCX, PNG, JPG (max 50MB)</small>
          </div>

          <Button disabled={!canUpload} onClick={onUpload} style={{ width: "100%" }}>
            {isUploading ? "Uploading..." : "Upload document"}
          </Button>
        </div>
      ) : null}

      {/* Consent Section */}
      {showConsent ? (
        <div className="workflow-section">
          <div className="workflow-section-header">
            <h3>✓ Consent Required</h3>
          </div>
          <form className="consent-form" onSubmit={onConsentSubmit}>
            <p className="consent-note">
              You control what happens next. Processing consent is required to analyze this file. Storage
              consent is optional.
            </p>
            <label>
              <input
                checked={processingConsent}
                onChange={(event) => setProcessingConsent(event.target.checked)}
                type="checkbox"
              />
              I consent to processing this document.
            </label>
            <label>
              <input
                checked={storageConsent}
                onChange={(event) => setStorageConsent(event.target.checked)}
                type="checkbox"
              />
              I consent to persistent storage.
            </label>

            <Button type="submit" disabled={!documentId || isSubmittingConsent} style={{ width: "100%" }}>
              {isSubmittingConsent ? "Submitting..." : "Submit consent"}
            </Button>
          </form>
        </div>
      ) : null}

      {/* Results Section */}
      {showResults ? (
        <>
          <div className="workflow-section">
            <div className="workflow-section-header">
              <h3>📊 Summary</h3>
            </div>
            <div className="summary-card">
              <p>{summary}</p>
              {results.summary ? (
                <small className="muted">
                  Grounded in {results.summary.source_count} {results.summary.grounded_in.replaceAll("_", " ")} source
                  {results.summary.source_count === 1 ? "" : "s"}.
                </small>
              ) : null}
            </div>
          </div>

          <div className="workflow-section">
            <div className="workflow-section-header">
              <h3>📋 Key Details</h3>
            </div>
            <div style={{ display: "grid", gap: "0.75rem" }}>
              <div>
                <p style={{ margin: 0 }}>
                  <strong>Lease start:</strong> {results.metadata?.lease_start_date || "Not Found"}
                </p>
              </div>
              <div>
                <p style={{ margin: 0 }}>
                  <strong>Lease end:</strong> {results.metadata?.lease_end_date || "Not Found"}
                </p>
              </div>
              <div>
                <p style={{ margin: 0 }}>
                  <strong>Monthly rent:</strong> {results.metadata?.monthly_rent || "Not Found"}
                </p>
              </div>
            </div>
          </div>

          <div className="workflow-section">
            <div className="workflow-section-header">
              <h3>📝 Clauses ({results.total_clauses || 0})</h3>
            </div>
            <div className="clauses">
              {(results.clauses || []).slice(0, 6).map((clause) => (
                <article className="clause" key={`${clause.order_index}-${clause.clause_number}`}>
                  <p style={{ margin: "0 0 0.35rem" }}>
                    <strong>{clause.clause_number}</strong> <span className="muted">{clause.clause_type}</span>
                  </p>
                  <p style={{ margin: 0, fontSize: "0.92rem" }}>{clause.clause_text}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="workflow-section">
            <div className="workflow-section-header">
              <h3>📖 Source Excerpts</h3>
            </div>
            <div className="source-excerpts">
              {sourceClauses.length ? (
                sourceClauses.map((clause) => (
                  <blockquote key={`source-${clause.order_index}-${clause.clause_number}`}>
                    <strong>
                      {clause.clause_number} - {clause.clause_type}
                    </strong>
                    <span>{clause.clause_text}</span>
                  </blockquote>
                ))
              ) : (
                <p className="muted">No source excerpts are available yet.</p>
              )}
            </div>
          </div>

          <div className="workflow-section">
            <Button variant="secondary" onClick={onExportPdf} style={{ width: "100%" }}>
              Export as PDF
            </Button>
          </div>
        </>
      ) : null}

      {/* Empty State */}
      {!documentId && !selectedFile ? (
        <div className="workflow-section">
          <p className="muted" style={{ textAlign: "center", margin: 0 }}>
            Upload a document to get started
          </p>
        </div>
      ) : null}
    </motion.div>
  );
}
