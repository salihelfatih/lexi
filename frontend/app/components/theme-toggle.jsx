"use client";

import { useEffect, useState } from "react";

const THEME_KEY = "lexi_theme";

function getPreferredTheme() {
  if (typeof window === "undefined") {
    return "light";
  }

  const storedTheme = window.localStorage.getItem(THEME_KEY);
  if (storedTheme === "light" || storedTheme === "dark") {
    return storedTheme;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  window.localStorage.setItem(THEME_KEY, theme);
}

export function ThemeToggle() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const preferredTheme = getPreferredTheme();
    applyTheme(preferredTheme);
    setTheme(preferredTheme);
  }, []);

  function toggleTheme() {
    const nextTheme = theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    setTheme(nextTheme);
  }

  const isDark = theme === "dark";

  return (
    <button
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-pressed={isDark}
      className={`theme-toggle ${isDark ? "dark" : "light"}`}
      onClick={toggleTheme}
      type="button"
    >
      <span className="theme-icon sun" aria-hidden="true">☀</span>
      <span className="theme-thumb" aria-hidden="true">{isDark ? "🌙" : "☀"}</span>
      <span className="theme-icon moon" aria-hidden="true">🌙</span>
    </button>
  );
}
