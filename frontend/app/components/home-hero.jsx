import { motion } from "framer-motion";
import Link from "next/link";

export function HomeHero({ showPublicActions = false, onStartDocument }) {
  return (
    <motion.section
      className="hero"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
    >
      <p className="kicker">Lexi</p>
      <h1>Understand what you are signing.</h1>
      <p className="subtitle">
        Upload a lease or legal document, give explicit consent, and let Lexi help you read it in
        calm, plain language. Lexi highlights what is written, what may deserve attention, and what
        you might want to clarify.
      </p>
      {showPublicActions ? (
        <div className="hero-actions" aria-label="Public home actions">
          <button className="button" onClick={onStartDocument} type="button">
            Start with a Document
          </button>
          <Link className="button secondary" href="/about">
            Learn how Lexi works
          </Link>
        </div>
      ) : null}
    </motion.section>
  );
}
