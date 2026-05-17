"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Button } from "./ui/button";

export function AuthModal({
  isOpen,
  onClose,
  authMode,
  onAuthModeChange,
  authNotice = "",
  authProvider = "custom",
  email,
  onEmailChange,
  password,
  onPasswordChange,
  onPasswordReset,
  onSubmit,
  isAuthenticating
}) {
  const isSupabase = authProvider === "supabase";
  const authKicker = isSupabase ? "Public beta access" : "Private beta access";
  const authModeLabel = authMode === "login"
    ? "Log back in"
    : isSupabase
    ? "Create public beta account"
    : "Create private beta account";
  const contextText = isSupabase
    ? "Use your email and password for the Supabase-backed public beta."
    : "Use this private preview to keep your document workspace tied to your account. Public beta sign-in is moving to Supabase-backed sessions.";

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit(event);
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="dialog-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            onClick={onClose}
          />

          {/* Modal */}
          <div className="dialog-backdrop" style={{ pointerEvents: "none" }}>
            <motion.div
              className="auth-modal"
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{
                duration: 0.25,
                ease: [0.4, 0, 0.2, 1]
              }}
              onClick={(e) => e.stopPropagation()}
              style={{ pointerEvents: "auto" }}
            >
              <div className="auth-modal-header">
                <div>
                  <p className="auth-modal-kicker">{authKicker}</p>
                  <h2>Welcome to Lexi</h2>
                </div>
                <button
                  className="auth-modal-close"
                  onClick={onClose}
                  aria-label="Close"
                >
                  ×
                </button>
              </div>

              <div className="auth-switch">
                <button
                  className={`chip ${authMode === "login" ? "active" : ""}`}
                  onClick={() => onAuthModeChange("login")}
                  type="button"
                >
                  Log in
                </button>
                <button
                  className={`chip ${authMode === "register" ? "active" : ""}`}
                  onClick={() => onAuthModeChange("register")}
                  type="button"
                >
                  Register
                </button>
              </div>

              <motion.div
                key={authMode}
                className="auth-context-note"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.18, ease: "easeOut" }}
              >
                <span className="auth-context-badge">{authModeLabel}</span>
                <p>{contextText}</p>
              </motion.div>

              {authNotice ? (
                <motion.p
                  className="auth-notice"
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.18, ease: "easeOut" }}
                  role="status"
                >
                  {authNotice}
                </motion.p>
              ) : null}

              <form className="auth-form" onSubmit={handleSubmit}>
                <label>
                  <span className="auth-label">Email</span>
                  <input
                    className="text-input"
                    onChange={(event) => onEmailChange(event.target.value)}
                    required
                    type="email"
                    value={email}
                    placeholder="your@email.com"
                  />
                </label>

                <label>
                  <span className="auth-label">Password</span>
                  <input
                    className="text-input"
                    minLength={8}
                    onChange={(event) => onPasswordChange(event.target.value)}
                    required
                    type="password"
                    value={password}
                    placeholder="At least 8 characters"
                  />
                </label>

                {isSupabase && authMode === "login" ? (
                  <button
                    className="auth-link-button"
                    disabled={isAuthenticating}
                    onClick={onPasswordReset}
                    type="button"
                  >
                    Reset password
                  </button>
                ) : null}

                <Button type="submit" disabled={isAuthenticating} style={{ width: "100%" }}>
                  {isAuthenticating ? "Working..." : authMode === "login" ? "Log in" : "Create account"}
                </Button>
              </form>

              <p className="auth-modal-note">
                By signing in, you agree to our <a href="/terms">Terms</a> and <a href="/privacy">Privacy Policy</a>.
              </p>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
