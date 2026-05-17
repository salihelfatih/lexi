export const metadata = {
  title: "Privacy | Lexi",
  description: "How Lexi handles your documents and data."
};

export default function PrivacyPage() {
  return (
    <main className="shell content-page">
      <section className="page-hero">
        <p className="kicker">Privacy</p>
        <h1>Your documents, your control</h1>
        <p className="subtitle">
          Lexi is built with privacy as a core principle. You control what happens to your documents.
        </p>
      </section>

      <section className="panel">
        <h2>How Lexi handles your documents</h2>
        <ul>
          <li>Processing only starts after you explicitly consent</li>
          <li>Storage consent is optional and separate from processing consent</li>
          <li>You can delete your documents anytime with one click</li>
          <li>All uploaded files are encrypted at rest</li>
          <li>No sharing without your permission</li>
          <li>Opt-in only, nothing happens until you consent</li>
        </ul>
      </section>

      <section className="split-section">
        <div>
          <h2>What we collect</h2>
          <p>When you use Lexi, we collect:</p>
          <ul className="clean-list">
            <li>Your email address (for account access)</li>
            <li>Documents you upload (only with your consent)</li>
            <li>Processing results (summaries, extracted clauses, metadata)</li>
            <li>Questions you ask about your documents</li>
          </ul>
        </div>

        <div>
          <h2>What we don't do</h2>
          <ul className="clean-list">
            <li>We don't sell your data</li>
            <li>We don't share your documents with third parties</li>
            <li>We don't use your documents to train AI models</li>
            <li>We don't keep documents you choose not to store</li>
          </ul>
        </div>
      </section>

      <section className="panel">
        <h2>Data retention</h2>
        <p>
          If you consent to storage, your documents and processing results are kept in your account
          until you delete them. If you do not consent to storage, documents are processed and then
          removed from our systems.
        </p>
        <p>
          You can delete individual documents or your entire account at any time.
        </p>
      </section>

      <section className="panel">
        <h2>Security</h2>
        <p>
          All documents are encrypted at rest using industry-standard encryption. Access to your
          documents is protected by secure authentication. We follow security best practices to
          protect your data.
        </p>
      </section>

      <section className="panel">
        <h2>Questions?</h2>
        <p>
          If you have questions about how Lexi handles your data, please contact us through the
          information provided on our Contact page.
        </p>
      </section>
    </main>
  );
}
