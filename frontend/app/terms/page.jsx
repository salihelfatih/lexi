export const metadata = {
  title: "Terms of Service | Lexi",
  description: "Terms of service for using Lexi."
};

export default function TermsPage() {
  return (
    <main className="shell content-page">
      <section className="page-hero">
        <p className="kicker">Terms of Service</p>
        <h1>Using Lexi responsibly</h1>
        <p className="subtitle">
          These terms explain what Lexi does, what it doesn't do, and how to use it safely.
        </p>
      </section>

      <section className="panel">
        <h2>What Lexi provides</h2>
        <p>
          Lexi provides <strong>legal information, not legal advice</strong>. Lexi helps you understand
          what is written in your documents by:
        </p>
        <ul>
          <li>Extracting and structuring text from uploaded documents</li>
          <li>Explaining clauses in plain language</li>
          <li>Highlighting key dates, rent details, and important sections</li>
          <li>Suggesting questions you might want to ask</li>
          <li>Answering questions based on the document text</li>
        </ul>
      </section>

      <section className="panel">
        <h2>What Lexi does not do</h2>
        <p>Lexi has strict boundaries:</p>
        <ul>
          <li>Lexi is not a lawyer</li>
          <li>Lexi does not provide legal advice</li>
          <li>Lexi does not determine whether something is legal or illegal</li>
          <li>Lexi does not predict legal outcomes</li>
          <li>Lexi does not tell you what action to take</li>
        </ul>
        <p>
          <strong>Final decisions remain with you and qualified legal professionals.</strong>
        </p>
      </section>

      <section className="panel">
        <h2>Your responsibilities</h2>
        <p>When using Lexi, you agree to:</p>
        <ul>
          <li>Use Lexi for informational purposes only</li>
          <li>Consult with qualified legal professionals for legal advice</li>
          <li>Not rely solely on Lexi for legal decisions</li>
          <li>Verify important information independently</li>
          <li>Use the service in good faith</li>
        </ul>
      </section>

      <section className="panel">
        <h2>Accuracy and limitations</h2>
        <p>
          Lexi uses AI and machine learning to process documents. While we work to ensure accuracy,
          Lexi may:
        </p>
        <ul>
          <li>Miss information in complex or unclear documents</li>
          <li>Misinterpret ambiguous language</li>
          <li>Have difficulty with poor-quality scans or images</li>
          <li>Not support all document types</li>
        </ul>
        <p>
          When Lexi is unsure, it will say so. Always review the original document and consult with
          legal professionals when making important decisions.
        </p>
      </section>

      <section className="panel">
        <h2>Supported documents</h2>
        <p>
          Lexi currently focuses on Ontario residential leases. Support for other document types may
          be added in the future. Unsupported documents will be identified, and you will be able to
          delete them without processing.
        </p>
      </section>

      <section className="panel">
        <h2>Account and access</h2>
        <p>
          You are responsible for maintaining the security of your account. Do not share your login
          credentials. Notify us immediately if you believe your account has been compromised.
        </p>
      </section>

      <section className="panel">
        <h2>Changes to these terms</h2>
        <p>
          We may update these terms from time to time. Continued use of Lexi after changes means you
          accept the updated terms.
        </p>
      </section>

      <section className="panel">
        <h2>Questions?</h2>
        <p>
          If you have questions about these terms, please contact us through the information provided
          on our Contact page.
        </p>
      </section>
    </main>
  );
}
