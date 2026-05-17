export function Button({ variant = "primary", className = "", type = "button", ...props }) {
  const variantClass = variant === "secondary" ? "secondary" : variant === "danger" ? "danger" : "";
  const classes = ["button", variantClass, className].filter(Boolean).join(" ");

  return <button type={type} className={classes} {...props} />;
}
