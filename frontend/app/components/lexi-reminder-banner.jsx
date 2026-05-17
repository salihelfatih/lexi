import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import { Alert } from "./ui/alert";
import { Button } from "./ui/button";

const BANNER_KEY = "lexi_boundaries_banner_dismissed";

export function LexiReminderBanner() {
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    setDismissed(window.localStorage.getItem(BANNER_KEY) === "true");
  }, []);

  function handleDismiss() {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(BANNER_KEY, "true");
    }
    setDismissed(true);
  }

  return (
    <AnimatePresence>
      {!dismissed ? (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
        >
          <Alert variant="info" className="banner-row">
            <div>
              <strong>Lexi boundary:</strong> Lexi helps interpret contract language and suggest
              follow-up questions. It is legal information, not legal advice. Final decisions
              remain with you and qualified legal professionals.
            </div>
            <Button variant="secondary" onClick={handleDismiss}>
              Dismiss
            </Button>
          </Alert>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
