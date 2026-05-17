"use client";

import { motion } from "framer-motion";

const features = [
  {
    step: "1",
    title: "Upload your document",
    description: "PDF, DOCX, PNG, or JPG files up to 50MB"
  },
  {
    step: "2",
    title: "Give consent",
    description: "You control processing and storage"
  },
  {
    step: "3",
    title: "Ask questions",
    description: "Get answers grounded in your document"
  }
];

const featureListVariants = {
  visible: {
    transition: {
      staggerChildren: 0.08
    }
  }
};

const featureVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 }
};

export function PublicHomeView({ onStartDocument }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="public-home-container"
    >
      <div className="public-workflow-intro-card">
        <h2>A clearer way to read legal documents</h2>
        <p>Lexi walks you through a simple three-step process to help you understand your document.</p>
      </div>

      <motion.div
        className="public-home-features"
        variants={featureListVariants}
        initial="hidden"
        animate="visible"
      >
        {features.map((feature) => (
          <motion.div
            className="public-feature-item"
            key={feature.step}
            variants={featureVariants}
            transition={{ duration: 0.24, ease: "easeOut" }}
          >
            <div className="public-feature-icon" aria-hidden="true">
              {feature.step}
            </div>
            <div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      <section className="public-start-card" aria-label="Start with Lexi">
        <div>
          <h2>Ready when your document is.</h2>
          <p>Sign in, upload your file, and Lexi will guide you through the next step.</p>
        </div>
        <button className="button" onClick={onStartDocument} type="button">
          Upload a document securely
        </button>
      </section>
    </motion.div>
  );
}
