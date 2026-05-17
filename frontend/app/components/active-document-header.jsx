import { motion } from "framer-motion";

import { Card } from "./ui/card";
import { Button } from "./ui/button";

function documentTitle(activeDocument, selectedFile, documentId) {
  if (activeDocument?.filename) {
    return activeDocument.filename;
  }

  if (selectedFile?.name) {
    return selectedFile.name;
  }

  return documentId ? "Uploaded document" : "No active document";
}

export function ActiveDocumentHeader({
  activeDocument,
  documentId,
  isDeleting,
  isPolling,
  jobStatus,
  onDelete,
  prettifyStatus,
  progressPercent,
  results,
  selectedFile
}) {
  const title = documentTitle(activeDocument, selectedFile, documentId);
  const status = activeDocument?.job_status || jobStatus || "idle";
  const type = results?.document_type || activeDocument?.document_type;
  const typeLabel = type === "unknown" ? "unsupported by Lexi" : type;
  const confidence = results?.classification_confidence ?? activeDocument?.classification_confidence;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22 }}>
      <Card className="active-document-card">
        <div className="active-document-main">
          <p className="kicker">Active document</p>
          <h2>{title}</h2>
          <p className="status-line">
            <strong>Document:</strong> {documentId || "not uploaded"}
          </p>
          <p className="status-line">
            <strong>Status:</strong> {prettifyStatus(status)}
          </p>
          {type ? (
            <p className="status-line">
              <strong>Type:</strong> {typeLabel}
              {confidence != null ? ` (${Number(confidence).toFixed(1)}%)` : ""}
            </p>
          ) : null}
        </div>

        <div className="active-document-actions">
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
          <Button variant="danger" disabled={!documentId || isDeleting} onClick={onDelete}>
            {isDeleting ? "Deleting..." : "Delete document"}
          </Button>
        </div>
      </Card>
    </motion.div>
  );
}
