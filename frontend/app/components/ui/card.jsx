export function Card({ as: Tag = "section", className = "", children, ...props }) {
  const classes = ["panel", className].filter(Boolean).join(" ");
  return (
    <Tag className={classes} {...props}>
      {children}
    </Tag>
  );
}
