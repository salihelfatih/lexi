import Link from "next/link";

export const metadata = {
  title: "About Lexi | Legal document understanding",
  description: "Learn how Lexi helps people understand legal documents safely and clearly."
};

const principles = [
  {
    title: "Calm over confident",
    text: "Lexi avoids alarm language. If something may matter, it explains why without pushing you toward a decision."
  },
  {
    title: "Grounded in the document",
    text: "The goal is to show what the uploaded text says, what it means in plain language, and what may be worth clarifying."
  },
  {
    title: "Helpful, not authoritative",
    text: "Lexi provides legal information. It does not determine legality, predict outcomes, or replace a lawyer or legal clinic."
  }
];

const roadmap = [
  "Free document upload, OCR, summaries, key dates, basic clause extraction, and basic risk flags.",
  "Limited document-scoped Q&A that answers from retrieved document text.",
  "RiskSense features for severity, confidence, top risks, comparisons, and organization-level anonymized trends."
];

export default function AboutPage() {
  return (
    <main className="shell content-page">
      <section className="page-hero">
        <p className="kicker">About Lexi</p>
        <h1>A reading companion for legal documents.</h1>
        <p className="subtitle">
          Lexi is built for people who are reading leases, contracts, or official documents without a
          legal team beside them. It helps slow the moment down so the document is easier to understand.
        </p>
      </section>

      <section className="split-section" aria-label="Lexi mission">
        <div>
          <h2>Why Lexi exists</h2>
          <p>
            Legal paperwork often relies on complexity, time pressure, and fatigue. Lexi reduces that
            pressure by turning dense text into clearer explanations and practical questions.
          </p>
          <p>
            The first focus is Ontario residential leases and student housing agreements. Expansion
            comes after the core experience is tested, grounded, and safe.
          </p>
        </div>
        <aside className="soft-callout">
          <strong>Boundary</strong>
          <p>
            Lexi can help you understand what is written. It cannot tell you what legal action to take.
          </p>
        </aside>
      </section>

      <section className="info-grid" aria-label="Product principles">
        {principles.map((principle, index) => (
          <article className="info-card" key={principle.title}>
            <span className="info-index">{String(index + 1).padStart(2, "0")}</span>
            <h2>{principle.title}</h2>
            <p>{principle.text}</p>
          </article>
        ))}
      </section>

      <section className="panel">
        <h2>What Lexi is building toward</h2>
        <ul>
          {roadmap.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <p className="section-note">
          Basic understanding stays free. Premium risk intelligence should add deeper analytics, not
          block people from understanding what they are signing.
        </p>
      </section>

      <section className="cta-band">
        <div>
          <h2>Ready to read a document?</h2>
          <p>Start with the upload flow and keep the final decision with you and qualified support.</p>
        </div>
        <Link className="button" href="/#document-workspace">
          Go to upload
        </Link>
      </section>
    </main>
  );
}
