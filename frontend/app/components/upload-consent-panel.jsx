import { motion } from "framer-motion";

import { Card } from "./ui/card";
import { Button } from "./ui/button";

export function UploadConsentPanel({
  acceptedTypes,
  canUpload,
  documentId,
  isDragging,
  isSubmittingConsent,
  isUploading,
  onConsentSubmit,
  onDrop,
  onDragOver,
  onDragLeave,
  onFileInputChange,
  onUpload,
  processingConsent,
  selectedFile,
  setProcessingConsent,
  setStorageConsent,
  storageConsent
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.24, delay: 0.05 }}>
      <Card className="panel-grid">
        <div>
          <h2>Upload</h2>
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

          <Button disabled={!canUpload} onClick={onUpload}>
            {isUploading ? "Uploading..." : "Upload document"}
          </Button>
        </div>

        <div>
          <h2>Consent</h2>
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

            <Button type="submit" disabled={!documentId || isSubmittingConsent}>
              {isSubmittingConsent ? "Submitting..." : "Submit consent"}
            </Button>
          </form>
        </div>
      </Card>
    </motion.div>
  );
}
