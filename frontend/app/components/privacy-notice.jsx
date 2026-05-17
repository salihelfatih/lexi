"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const PRIVACY_NOTICE_KEY = "lexi_privacy_notice_dismissed_v1";

export function PrivacyNotice() {
  const [isDismissed, setIsDismissed] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const dismissed = window.localStorage.getItem(PRIVACY_NOTICE_KEY) === "true";
      setIsDismissed(dismissed);
    }
  }, []);

  function handleDismiss() {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(PRIVACY_NOTICE_KEY, "true");
    }
    setIsDismissed(true);
  }

  return (
    <AnimatePresence>
      {!isDismissed ? (
        <motion.aside
          className="privacy-notice"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.3 }}
        >
          <div className="privacy-notice-header">
            <h3>🔒 Privacy First</h3>
            <button
              className="privacy-notice-close"
              onClick={handleDismiss}
              aria-label="Dismiss privacy notice"
            >
              ×
            </button>
          </div>
          <div className="privacy-notice-content">
            <p>Processing starts only after explicit consent, and stored documents stay tied to your account.</p>
            <ul>
              <li>Delete documents anytime with one click</li>
              <li>Encrypted storage for all uploaded files</li>
              <li>No sharing without your permission</li>
              <li>Opt-in only, nothing happens until you consent</li>
            </ul>
          </div>
        </motion.aside>
      ) : null}
    </AnimatePresence>
  );
}
