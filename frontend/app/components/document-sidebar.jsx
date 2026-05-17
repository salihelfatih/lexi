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

export function DocumentSidebar({
  activeDocumentId,
  documents,
  isLoading,
  onSelectDocument,
  onStartNewUpload
}) {
  return (
    <Card className="document-sidebar-panel">
      <div className="sidebar-heading">
        <div>
          <p className="kicker">Workspace</p>
          <h2>Documents</h2>
        </div>
        <Button variant="secondary" className="compact-button" onClick={onStartNewUpload}>
          Upload document
        </Button>
      </div>

      {isLoading ? <p className="muted">Loading your documents...</p> : null}

      {!isLoading && documents.length === 0 ? (
        <p className="muted document-empty-state">No documents yet. Upload a lease to begin.</p>
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
    </Card>
  );
}
