import { motion } from "framer-motion";

import { Card } from "./ui/card";
import { Button } from "./ui/button";

export function AccountPanel({
  authMode,
  currentUser,
  email,
  isAuthLoading,
  isAuthenticating,
  onAuthModeChange,
  onEmailChange,
  onLogout,
  onPasswordChange,
  onSubmit,
  password
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24 }}
      className="panel-grid"
    >
      <Card>
        <h2>Account</h2>
        {isAuthLoading ? (
          <p className="muted">Checking session...</p>
        ) : currentUser ? (
          <div className="account-box">
            <p>
              <strong>Signed in:</strong> {currentUser.email}
            </p>
            <Button variant="secondary" onClick={onLogout}>
              Log out
            </Button>
          </div>
        ) : (
          <form className="consent-form" onSubmit={onSubmit}>
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

            <label>
              <span>Email</span>
              <input
                className="text-input"
                onChange={(event) => onEmailChange(event.target.value)}
                required
                type="email"
                value={email}
              />
            </label>

            <label>
              <span>Password</span>
              <input
                className="text-input"
                minLength={8}
                onChange={(event) => onPasswordChange(event.target.value)}
                required
                type="password"
                value={password}
              />
            </label>

            <Button type="submit" disabled={isAuthenticating}>
              {isAuthenticating ? "Working..." : authMode === "login" ? "Log in" : "Create account"}
            </Button>
          </form>
        )}
      </Card>

      <aside className="soft-callout">
        <strong>Privacy</strong>
        <p>
          Processing only starts after explicit consent, and stored documents stay tied to your account.
        </p>
        <ul className="clean-list">
          <li>Delete your documents anytime with one click</li>
          <li>Encrypted storage for all uploaded files</li>
          <li>No sharing without your permission</li>
          <li>Opt-in only, nothing happens until you consent</li>
        </ul>
      </aside>
    </motion.div>
  );
}
