export function Alert({ variant = "default", className = "", children }) {
  const classes = ["alert", variant !== "default" ? `alert-${variant}` : "", className]
    .filter(Boolean)
    .join(" ");

  return <div className={classes}>{children}</div>;
}
