import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <p>Lexi provides legal information, not legal advice.</p>
      <div className="footer-links">
        <Link href="/">Home</Link>
        <Link href="/about">About</Link>
        <Link href="/contact">Contact</Link>
        <Link href="/privacy">Privacy</Link>
        <Link href="/terms">Terms</Link>
      </div>
    </footer>
  );
}
