"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { getUserFriendlyError } from "../lib/error-handler";

export function ErrorBanner({ error, onDismiss, autoDismiss = true, autoDismissDelay = 8000 }) {
  const friendlyError = getUserFriendlyError(error);

  useEffect(() => {
    if (!friendlyError || !autoDismiss || !onDismiss) {
      return;
    }

    const timer = setTimeout(() => {
      onDismiss();
    }, autoDismissDelay);

    return () => clearTimeout(timer);
  }, [friendlyError, autoDismiss, autoDismissDelay, onDismiss]);

  if (!friendlyError) {
    return null;
  }

  return (
    <motion.div
      className="error-banner"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      <div className="error-banner-content">
        <div className="error-banner-icon">⚠</div>
        <p className="error-banner-message">{friendlyError}</p>
      </div>
      {onDismiss && (
        <button
          className="error-banner-dismiss"
          onClick={onDismiss}
          aria-label="Dismiss error"
        >
          ×
        </button>
      )}
    </motion.div>
  );
}
