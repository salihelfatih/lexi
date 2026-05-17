import { motion } from "framer-motion";

import { Card } from "./ui/card";
import { Button } from "./ui/button";

function buildSummary(results, prettifyStatus) {
  if (!results) {
    return "No summary available yet.";
  }

  if (results.document_type === "unknown") {
    return "Lexi could not identify this as a supported document type yet.";
  }

  if (results.summary?.text) {
    return results.summary.text;
  }

  const docType = prettifyStatus(results.document_type || "unknown");
  const clauseCount = results.total_clauses || 0;
  const rent = results.metadata?.monthly_rent || "Not Found";
  const startDate = results.metadata?.lease_start_date || "Not Found";
  const endDate = results.metadata?.lease_end_date || "Not Found";

  return `This document was classified as ${docType}. Lexi extracted ${clauseCount} clauses, identified a monthly rent of ${rent}, and found lease dates from ${startDate} to ${endDate}.`;
}

function formatConfidence(value) {
  if (value == null) {
    return "Not available";
  }

  return `${Number(value).toFixed(1)}%`;
}

export function ResultsPanel({ onExportPdf, prettifyStatus, results }) {
  const summary = buildSummary(results, prettifyStatus);
  const sourceClauses = (results?.clauses || []).slice(0, 4);
  const isUnsupported = results?.document_type === "unknown";
  const riskSense = results?.risk_sense;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.24, delay: 0.15 }}>
      <Card>
        <div className="section-heading">
          <p className="kicker">Understanding</p>
          <h2>Summary and source excerpts</h2>
        </div>
        {isUnsupported ? (
          <div className="chat-unsupported-state">
            <div className="unsupported-state-header">
              <div>
                <p className="kicker">Unsupported document</p>
                <h4>{summary}</h4>
              </div>
              <span className="unsupported-confidence">
                {Number(results.classification_confidence || 0).toFixed(1)}% confidence
              </span>
            </div>
            <p>
              Lexi currently supports Ontario residential leases. This file is unsupported by
              Lexi right now, so summaries and document Q&A are paused for it.
            </p>
          </div>
        ) : results ? (
          <div className="results-grid">
            <div className="summary-card" id="print-report">
              <h3>Summary</h3>
              <p>{summary}</p>
              {results.summary ? (
                <small className="muted">
                  Grounded in {results.summary.source_count} {results.summary.grounded_in.replaceAll("_", " ")} source
                  {results.summary.source_count === 1 ? "" : "s"}.
                </small>
              ) : null}
            </div>

            <div>
              <h3>Classification</h3>
              <p>
                <strong>Type:</strong> {results.document_type}
              </p>
              <p>
                <strong>Confidence:</strong> {Number(results.classification_confidence).toFixed(1)}%
              </p>
            </div>

            <div>
              <h3>Metadata</h3>
              <p>
                <strong>Lease start:</strong> {results.metadata?.lease_start_date || "Not Found"}
              </p>
              <p>
                <strong>Lease end:</strong> {results.metadata?.lease_end_date || "Not Found"}
              </p>
              <p>
                <strong>Monthly rent:</strong> {results.metadata?.monthly_rent || "Not Found"}
              </p>
            </div>

            <div className="clauses">
              <h3>Clauses ({results.total_clauses || 0})</h3>
              {(results.clauses || []).slice(0, 8).map((clause) => (
                <article className="clause" key={`${clause.order_index}-${clause.clause_number}`}>
                  <p>
                    <strong>{clause.clause_number}</strong> <span>{clause.clause_type}</span>
                  </p>
                  <p>{clause.clause_text}</p>
                </article>
              ))}
            </div>

            <div className="source-excerpts">
              <h3>Source excerpts</h3>
              {sourceClauses.length ? (
                sourceClauses.map((clause) => (
                  <blockquote key={`source-${clause.order_index}-${clause.clause_number}`}>
                    <strong>
                      {clause.clause_number} - {clause.clause_type}
                    </strong>
                    <span>{clause.clause_text}</span>
                  </blockquote>
                ))
              ) : (
                <p className="muted">No source excerpts are available yet.</p>
              )}
            </div>

            {riskSense ? (
              <div className="risk-sense-section">
                <div className="risk-sense-header">
                  <div>
                    <p className="kicker">RiskSense</p>
                    <h3>Attention signals</h3>
                  </div>
                  <span className="risk-confidence-pill">
                    {formatConfidence(riskSense.confidence_rollup?.overall)} confidence
                  </span>
                </div>
                <p className="risk-sense-summary">{riskSense.top_risks_summary}</p>
                <div className="risk-signal-list">
                  {(riskSense.risks || []).slice(0, 3).map((risk) => (
                    <article className={`risk-signal severity-${risk.severity}`} key={risk.risk_id}>
                      <div className="risk-signal-header">
                        <div>
                          <h5>{risk.title}</h5>
                          <span>{formatConfidence(risk.confidence)} signal confidence</span>
                        </div>
                      </div>
                      <p>{risk.reason}</p>
                    </article>
                  ))}
                </div>
              </div>
            ) : null}

            <div>
              <Button variant="secondary" onClick={onExportPdf}>
                Export as PDF
              </Button>
            </div>
          </div>
        ) : (
          <p className="muted">No results yet. Upload, consent, and wait for completion.</p>
        )}
      </Card>
    </motion.div>
  );
}
