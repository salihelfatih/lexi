import { motion } from "framer-motion";

import { Card } from "./ui/card";
import { Button } from "./ui/button";

export function ProcessingPanel({
  documentId,
  isDeleting,
  isPolling,
  jobStatus,
  onDelete,
  progressPercent,
  prettifyStatus
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.24, delay: 0.1 }}>
      <Card className="panel-grid">
        <div>
          <h2>3) Processing Status</h2>
          <p className="status-line">
            <strong>Document:</strong> {documentId || "not uploaded"}
          </p>
          <p className="status-line">
            <strong>Status:</strong> {prettifyStatus(jobStatus || "idle")}
          </p>
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

        <div>
          <h2>4) Cleanup</h2>
          <Button variant="danger" disabled={!documentId || isDeleting} onClick={onDelete}>
            {isDeleting ? "Deleting..." : "Delete document"}
          </Button>
        </div>
      </Card>
    </motion.div>
  );
}
