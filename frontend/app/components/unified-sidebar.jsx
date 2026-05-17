"use client";

import { motion } from "framer-motion";
import { Card } from "./ui/card";
import { Button } from "./ui/button";

function formatDate(value) {
  if (!value) {
    return "Recently added";
  }

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  }).format(new Date(value));
}

function statusLabel(document) {
  if (!document.job_status) {
    return "Awaiting consent";
  }

  if (document.job_status === "complete") {
    return "Ready";
  }

  return document.job_status.replaceAll("_", " ");
}

function typeLabel(document) {
  if (document.document_type === "unknown") {
    return "unsupported by Lexi";
  }

  return document.document_type ? document.document_type.replaceAll("_", " ") : "";
}

function getInitials(email) {
  if (!email) return "?";
  return email.charAt(0).toUpperCase();
}

export function UnifiedSidebar({
  // Auth props
  currentUser,
  onLogout,
  // Document props
  activeDocumentId,
  documents,
  isLoadingDocuments,
  onSelectDocument,
  onStartNewUpload
}) {
  if (!currentUser) {
    return null;
  }

  return (
    <motion.div
      key="authenticated"
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.28 }}
      className="unified-sidebar-frame"
    >
      <Card className="unified-sidebar-card">
        {/* Account Section */}
        <div className="sidebar-section">
          <h2 style={{ fontSize: "1.1rem", marginBottom: "0.85rem" }}>Account</h2>
          <div className="account-box">
            <div className="compact-account-info">
              <div className="account-avatar">{getInitials(currentUser.email)}</div>
              <div className="account-details">
                <div className="account-email">{currentUser.email}</div>
                <div className="account-status">Signed in</div>
              </div>
            </div>
            <Button variant="secondary" onClick={onLogout} style={{ width: "100%" }}>
              Log out
            </Button>
          </div>
        </div>

        {/* Workspace Section */}
        <div className="sidebar-section workspace-document-section">
          <div className="sidebar-heading">
            <div>
              <p className="kicker" style={{ marginBottom: "0.35rem" }}>Workspace</p>
              <h2 style={{ fontSize: "1.1rem" }}>Documents</h2>
            </div>
            <Button variant="secondary" className="compact-button" onClick={onStartNewUpload}>
              Upload document
            </Button>
          </div>

          {isLoadingDocuments ? <p className="muted">Loading...</p> : null}

          {!isLoadingDocuments && documents.length === 0 ? (
            <p className="muted document-empty-state">
              No documents yet. Upload a lease to begin.
            </p>
          ) : null}

          <div className="document-list" role="list" aria-label="Recent documents">
            {documents.map((document) => {
              const isActive = document.document_id === activeDocumentId;

              return (
                <button
                  aria-current={isActive ? "true" : undefined}
                  className={`document-list-item ${isActive ? "active" : ""}`}
                  key={document.document_id}
                  onClick={() => onSelectDocument(document.document_id)}
                  type="button"
                >
                  <span className="document-list-title">{document.filename}</span>
                  <span className="document-list-meta">
                    {statusLabel(document)}
                    {typeLabel(document) ? ` - ${typeLabel(document)}` : ""}
                  </span>
                  <span className="document-list-date">{formatDate(document.updated_at)}</span>
                </button>
              );
            })}
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
