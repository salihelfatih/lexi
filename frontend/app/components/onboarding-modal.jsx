"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence, useAnimate } from "framer-motion";
import { Button } from "./ui/button";

const ONBOARDING_KEY = "lexi_onboarding_completed_v2";

export function OnboardingModal({ disabled = false }) {
  const [isOpen, setIsOpen] = useState(false);
  const [modalScope, animateModal] = useAnimate();

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (disabled) return;

    const completed = window.localStorage.getItem(ONBOARDING_KEY) === "true";
    if (!completed) {
      const timer = window.setTimeout(() => setIsOpen(true), 500);
      return () => window.clearTimeout(timer);
    }
  }, [disabled]);

  useEffect(() => {
    if (disabled && isOpen) {
      setIsOpen(false);
    }
  }, [disabled, isOpen]);

  function handleComplete() {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(ONBOARDING_KEY, "true");
    }
    setIsOpen(false);
  }

  function promptExplicitAcknowledge() {
    if (!modalScope.current) {
      return;
    }

    animateModal(modalScope.current, { x: [0, -7, 7, -4, 4, 0] }, {
      duration: 0.34,
      ease: "easeInOut"
    });
  }

  return (
    <AnimatePresence>
      {isOpen && !disabled && (
        <>
          {/* Backdrop */}
          <motion.div
            className="dialog-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={promptExplicitAcknowledge}
          />

          {/* Modal */}
          <div className="dialog-backdrop" style={{ pointerEvents: "none" }}>
            <motion.div
              ref={modalScope}
              className="onboarding-modal"
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, x: 0, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              onClick={(e) => e.stopPropagation()}
              style={{ pointerEvents: "auto" }}
            >
              {/* Content */}
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.24 }}
                className="onboarding-content"
              >
                <h2>Welcome to Lexi</h2>
                <div className="onboarding-body onboarding-summary">
                  <p>
                    Lexi helps you understand legal documents in calm, plain language. Upload a
                    lease or contract, give explicit consent, and ask questions grounded in the
                    document text.
                  </p>

                  <div className="onboarding-steps-grid" aria-label="How Lexi works">
                    <div className="onboarding-step-card">
                      <span>01</span>
                      <strong>Upload</strong>
                      <p>Choose a lease, contract, or legal document.</p>
                    </div>
                    <div className="onboarding-step-card">
                      <span>02</span>
                      <strong>Consent</strong>
                      <p>You control processing and optional storage.</p>
                    </div>
                    <div className="onboarding-step-card">
                      <span>03</span>
                      <strong>Understand</strong>
                      <p>Read summaries, flags, and document-grounded answers.</p>
                    </div>
                  </div>

                  <section className="onboarding-boundary-card" aria-label="Before you begin">
                    <h3>Before you begin</h3>
                    <ul>
                      <li>Lexi explains legal text in plain language.</li>
                      <li>Lexi can suggest questions worth asking.</li>
                      <li>Lexi provides legal information, not legal advice.</li>
                      <li>Lexi does not replace a lawyer or legal clinic.</li>
                    </ul>
                  </section>

                  <p className="onboarding-privacy-note">
                    Processing starts only after you consent. Storage is optional, and you can delete
                    documents anytime.
                  </p>
                </div>
              </motion.div>

              {/* Actions */}
              <div className="onboarding-actions">
                <div style={{ flex: 1 }} />
                <Button onClick={handleComplete}>I understand, continue</Button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
