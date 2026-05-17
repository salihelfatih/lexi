import Link from "next/link";

export const metadata = {
  title: "Contact Lexi | Community and support",
  description: "Contact paths for Lexi users, contributors, and community partners."
};

const contactPaths = [
  {
    title: "For renters and students",
    text: "If you are using Lexi through a school, clinic, nonprofit, or tenant group, start with the organization that invited you. They can help connect the document context to local support."
  },
  {
    title: "For legal clinics and nonprofits",
    text: "Lexi is being shaped for privacy-preserving workflows: document education, recurring clause patterns, and anonymized advocacy insights."
  },
  {
    title: "For contributors",
    text: "The strongest help right now is end-to-end testing, accessibility polish, plain-language review, and safe risk-signal design.",
    href: "https://github.com/salihelfatih/lexi",
    linkText: "Explore the code on GitHub"
  }
];

const questions = [
  "What document type are you working with?",
  "What jurisdiction or region does it relate to?",
  "Are you asking as an individual user, organization, or contributor?",
  "Is there any personal information that should be removed before sharing examples?"
];

export default function ContactPage() {
  return (
    <main className="shell content-page">
      <section className="page-hero">
        <p className="kicker">Contact</p>
        <h1>Reach out with context, not pressure.</h1>
        <p className="subtitle">
          Lexi is still moving toward private beta. The best conversations are specific, consent-aware,
          and careful with personal document details.
        </p>
      </section>

      <section className="info-grid" aria-label="Contact paths">
        {contactPaths.map((path, index) => (
          <article className="info-card" key={path.title}>
            <span className="info-index">{String(index + 1).padStart(2, "0")}</span>
            <h2>{path.title}</h2>
            <p>{path.text}</p>
            {path.href ? (
              <a className="text-link" href={path.href} rel="noreferrer" target="_blank">
                {path.linkText}
              </a>
            ) : null}
          </article>
        ))}
      </section>

      <section className="split-section" aria-label="What to include">
        <div>
          <h2>Helpful details to include</h2>
          <ul className="clean-list">
            {questions.map((question) => (
              <li key={question}>{question}</li>
            ))}
          </ul>
        </div>
        <aside className="soft-callout">
          <strong>Privacy first</strong>
          <p>
            Please do not send real leases, names, addresses, signatures, or account details unless a
            secure intake process has been agreed to first.
          </p>
        </aside>
      </section>

      <section className="cta-band">
        <div>
          <h2>Want to try the current flow?</h2>
          <p>Use a synthetic or anonymized document while Lexi is still in technical MVP stage.</p>
        </div>
        <Link className="button" href="/#document-workspace">
          Open Lexi
        </Link>
      </section>
    </main>
  );
}
