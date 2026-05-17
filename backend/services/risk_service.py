"""Rule-based RiskSense signal generation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from statistics import mean
from uuid import UUID

from sqlalchemy.orm import Session

from backend.logging_config import get_logger
from backend.models import (
    Clause,
    ClauseType,
    Document,
    DocumentMetadata,
    DocumentType,
    RiskSeverity,
    RiskSignal,
)
from backend.schemas import RiskConfidenceRollup

logger = get_logger(__name__)

SEVERITY_RANK = {
    RiskSeverity.HIGH: 3,
    RiskSeverity.MEDIUM: 2,
    RiskSeverity.LOW: 1,
}


@dataclass(frozen=True)
class RiskCandidate:
    """Internal candidate emitted by a RiskSense rule."""

    rule_id: str
    title: str
    severity: RiskSeverity
    confidence: float
    reason: str
    clause: Clause


class RiskService:
    """Generate and shape deterministic, source-grounded RiskSense outputs."""

    max_signals = 6

    def generate_risks(self, db: Session, document_id: UUID) -> list[RiskSignal]:
        """Generate persisted RiskSense signals for a supported processed document."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        db.query(RiskSignal).filter(RiskSignal.document_id == document_id).delete()

        if document.document_type != DocumentType.ONTARIO_RESIDENTIAL_LEASE:
            db.commit()
            logger.info("RiskSense skipped for unsupported document %s", document_id)
            return []

        clauses = (
            db.query(Clause)
            .filter(Clause.document_id == document_id)
            .order_by(Clause.order_index)
            .all()
        )
        candidates = self._collect_candidates(clauses)
        candidates = self._rank_candidates(candidates)[: self.max_signals]

        signals = [
            RiskSignal(
                document_id=document_id,
                source_clause_id=candidate.clause.id,
                rule_id=candidate.rule_id,
                title=candidate.title,
                severity=candidate.severity,
                confidence=self._document_adjusted_confidence(document, candidate.confidence),
                reason=candidate.reason,
            )
            for candidate in candidates
        ]

        db.add_all(signals)
        db.commit()
        for signal in signals:
            db.refresh(signal)

        logger.info("Generated %s RiskSense signals for document %s", len(signals), document_id)
        return signals

    def confidence_rollup(
        self,
        document: Document,
        metadata: DocumentMetadata | None,
        signals: list[RiskSignal],
    ) -> RiskConfidenceRollup:
        """Roll up extraction, classification, metadata, and signal confidence."""
        extraction = self._bounded(document.extraction_confidence)
        classification = self._bounded(document.classification_confidence)
        metadata_confidence, metadata_notes = self._metadata_confidence(metadata)
        risk_confidence = (
            round(mean(signal.confidence for signal in signals), 1) if signals else None
        )

        components = [extraction, classification, metadata_confidence]
        if risk_confidence is not None:
            components.append(risk_confidence)

        notes = list(metadata_notes)
        if risk_confidence is None:
            notes.append("No rule-based risk signals were detected in this first pass.")

        return RiskConfidenceRollup(
            extraction=extraction,
            classification=classification,
            metadata=metadata_confidence,
            risk_signals=risk_confidence,
            overall=round(mean(components), 1) if components else 0.0,
            notes=notes,
        )

    def top_risks_summary(self, signals: list[RiskSignal]) -> str:
        """Build calm summary text for the top RiskSense signals."""
        if not signals:
            return (
                "RiskSense did not find rule-based attention signals in this first pass. "
                "Review the document text directly for anything specific to your situation."
            )

        ranked = self._rank_signals(signals)
        severity_counts = self._severity_counts(ranked)
        top_titles = [signal.title.lower() for signal in ranked[:3]]

        count_text = ", ".join(
            f"{count} {severity.value}" for severity, count in severity_counts if count
        )
        title_text = self._join_plain(top_titles)
        return (
            f"RiskSense found {len(signals)} attention signal"
            f"{'' if len(signals) == 1 else 's'}"
            f"{f' ({count_text})' if count_text else ''}. "
            f"The first item{'s' if len(top_titles) != 1 else ''} to review: {title_text}."
        )

    def rank_signals(self, signals: list[RiskSignal]) -> list[RiskSignal]:
        """Order persisted RiskSense signals by severity, confidence, and document order."""
        return self._rank_signals(signals)

    def _collect_candidates(self, clauses: list[Clause]) -> list[RiskCandidate]:
        candidates = []
        seen_rule_ids = set()
        for clause in clauses:
            for candidate in self._evaluate_clause(clause):
                if candidate.rule_id in seen_rule_ids:
                    continue
                seen_rule_ids.add(candidate.rule_id)
                candidates.append(candidate)
        return candidates

    def _evaluate_clause(self, clause: Clause) -> list[RiskCandidate]:
        text = clause.clause_text.lower()
        candidates = []

        if self._is_rent_payment_clause(clause, text):
            candidates.append(
                RiskCandidate(
                    rule_id="payment_timing",
                    title="Rent payment timing",
                    severity=RiskSeverity.LOW,
                    confidence=78.0,
                    reason=(
                        "This clause describes when rent is due. Payment timing can be "
                        "important, so review the exact date and amount shown in the source text."
                    ),
                    clause=clause,
                )
            )
        elif self._mentions_extra_charges(clause, text):
            candidates.append(
                RiskCandidate(
                    rule_id="extra_charges",
                    title="Extra payment or charge wording",
                    severity=(
                        RiskSeverity.HIGH
                        if self._has_strong_fee_language(text)
                        else RiskSeverity.MEDIUM
                    ),
                    confidence=82.0,
                    reason=(
                        "This clause mentions extra payments, charges, or penalties. "
                        "Review the amount, trigger, and timing in the source text so you know "
                        "what the document says you may be asked to pay."
                    ),
                    clause=clause,
                )
            )

        if self._mentions_access(clause, text):
            broad_access = self._has_broad_access_language(text)
            candidates.append(
                RiskCandidate(
                    rule_id="landlord_access",
                    title="Landlord entry wording",
                    severity=RiskSeverity.HIGH if broad_access else RiskSeverity.LOW,
                    confidence=86.0 if broad_access else 74.0,
                    reason=(
                        "This clause describes landlord entry with broad or no-notice wording. "
                        "The exact notice and timing language may deserve careful review."
                        if broad_access
                        else "This clause sets out landlord entry or inspection language. "
                        "It may be useful to check when entry is allowed and what notice "
                        "the document states."
                    ),
                    clause=clause,
                )
            )

        if self._mentions_tenant_maintenance(clause, text):
            candidates.append(
                RiskCandidate(
                    rule_id="tenant_maintenance",
                    title="Tenant maintenance responsibility",
                    severity=RiskSeverity.MEDIUM,
                    confidence=79.0,
                    reason=(
                        "This clause appears to place maintenance or repair responsibility "
                        "on the tenant. Review the exact wording and the kind of work described."
                    ),
                    clause=clause,
                )
            )

        if self._mentions_utilities(clause, text):
            candidates.append(
                RiskCandidate(
                    rule_id="utilities_responsibility",
                    title="Utility responsibility",
                    severity=RiskSeverity.LOW,
                    confidence=72.0,
                    reason=(
                        "This clause mentions utility responsibilities. It may affect recurring "
                        "costs, so review which services the document assigns to each side."
                    ),
                    clause=clause,
                )
            )

        if self._mentions_termination(clause, text):
            abrupt = self._has_abrupt_termination_language(text)
            candidates.append(
                RiskCandidate(
                    rule_id="termination_notice",
                    title="Ending-the-lease notice",
                    severity=RiskSeverity.HIGH if abrupt else RiskSeverity.LOW,
                    confidence=84.0 if abrupt else 73.0,
                    reason=(
                        "This clause uses abrupt ending-the-lease wording. Review the notice "
                        "steps and timing stated in the source text."
                        if abrupt
                        else "This clause describes ending the lease and notice requirements. "
                        "Dates and notice steps are time-sensitive, so the source wording may "
                        "be worth reviewing."
                    ),
                    clause=clause,
                )
            )

        if self._mentions_subletting(clause, text):
            candidates.append(
                RiskCandidate(
                    rule_id="subletting_assignment",
                    title="Subletting or assignment approval",
                    severity=RiskSeverity.LOW,
                    confidence=72.0,
                    reason=(
                        "This clause describes assignment or subletting approval. Review what "
                        "the document says must be requested or provided."
                    ),
                    clause=clause,
                )
            )

        return candidates

    def _document_adjusted_confidence(self, document: Document, base_confidence: float) -> float:
        document_confidences = [
            value
            for value in [document.extraction_confidence, document.classification_confidence]
            if value is not None
        ]
        document_confidence = mean(document_confidences) if document_confidences else base_confidence
        return self._bounded((base_confidence * 0.62) + (document_confidence * 0.38))

    def _metadata_confidence(self, metadata: DocumentMetadata | None) -> tuple[float, list[str]]:
        if metadata is None:
            return 0.0, ["No lease metadata was available for the confidence rollup."]

        values = []
        notes = []

        for label, value in [
            ("lease start date", metadata.lease_start_date_confidence),
            ("lease end date", metadata.lease_end_date_confidence),
            ("monthly rent", metadata.monthly_rent_confidence),
        ]:
            if value and value > 0:
                values.append(value)
            else:
                notes.append(f"{label.capitalize()} was not found with confidence.")

        if self._json_list_has_values(metadata.tenant_names):
            values.append(75.0)
        else:
            notes.append("Tenant names were not found.")

        if self._json_list_has_values(metadata.landlord_names):
            values.append(75.0)
        else:
            notes.append("Landlord names were not found.")

        if metadata.property_address and metadata.property_address != "Not Found":
            values.append(75.0)
        else:
            notes.append("Rental unit address was not found.")

        return (round(mean(values), 1) if values else 0.0), notes

    def _rank_candidates(self, candidates: list[RiskCandidate]) -> list[RiskCandidate]:
        return sorted(
            candidates,
            key=lambda candidate: (
                SEVERITY_RANK[candidate.severity],
                candidate.confidence,
                -candidate.clause.order_index,
            ),
            reverse=True,
        )

    def _rank_signals(self, signals: list[RiskSignal]) -> list[RiskSignal]:
        return sorted(
            signals,
            key=lambda signal: (
                SEVERITY_RANK[signal.severity],
                signal.confidence,
                -signal.source_clause.order_index if signal.source_clause else 0,
            ),
            reverse=True,
        )

    def _severity_counts(self, signals: list[RiskSignal]) -> list[tuple[RiskSeverity, int]]:
        return [
            (
                RiskSeverity.HIGH,
                sum(1 for signal in signals if signal.severity == RiskSeverity.HIGH),
            ),
            (
                RiskSeverity.MEDIUM,
                sum(1 for signal in signals if signal.severity == RiskSeverity.MEDIUM),
            ),
            (
                RiskSeverity.LOW,
                sum(1 for signal in signals if signal.severity == RiskSeverity.LOW),
            ),
        ]

    def _join_plain(self, values: list[str]) -> str:
        if not values:
            return "none"
        if len(values) == 1:
            return values[0]
        if len(values) == 2:
            return f"{values[0]} and {values[1]}"
        return f"{', '.join(values[:-1])}, and {values[-1]}"

    def _bounded(self, value: float | None) -> float:
        if value is None:
            return 0.0
        return round(max(0.0, min(100.0, float(value))), 1)

    def _json_list_has_values(self, raw_value: str | None) -> bool:
        if not raw_value:
            return False
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            return bool(raw_value.strip())
        return isinstance(value, list) and any(str(item).strip() for item in value)

    def _is_rent_payment_clause(self, clause: Clause, text: str) -> bool:
        return clause.clause_type == ClauseType.FEES and "rent" in text and "month" in text

    def _mentions_extra_charges(self, clause: Clause, text: str) -> bool:
        keywords = ("fee", "charge", "penalty", "deposit", "late", "nsf", "additional payment")
        return clause.clause_type == ClauseType.FEES or any(keyword in text for keyword in keywords)

    def _has_strong_fee_language(self, text: str) -> bool:
        keywords = ("penalty", "late fee", "non-refundable", "forfeit", "additional charge")
        return any(keyword in text for keyword in keywords)

    def _mentions_access(self, clause: Clause, text: str) -> bool:
        keywords = ("entry", "access", "enter", "inspection")
        return clause.clause_type == ClauseType.ACCESS or any(keyword in text for keyword in keywords)

    def _has_broad_access_language(self, text: str) -> bool:
        keywords = ("without notice", "no notice", "at any time", "any time", "whenever")
        return any(keyword in text for keyword in keywords)

    def _mentions_tenant_maintenance(self, clause: Clause, text: str) -> bool:
        if clause.clause_type != ClauseType.MAINTENANCE and not any(
            keyword in text for keyword in ("maintenance", "repair", "repairs")
        ):
            return False
        tenant_patterns = (
            "tenant is responsible for maintenance",
            "tenant responsible for maintenance",
            "tenant is responsible for repairs",
            "tenant responsible for repairs",
            "tenant must repair",
            "tenant shall repair",
            "all repairs",
        )
        landlord_responsible = "landlord is responsible" in text or "landlord shall" in text
        return any(pattern in text for pattern in tenant_patterns) and not landlord_responsible

    def _mentions_utilities(self, clause: Clause, text: str) -> bool:
        keywords = ("utility", "utilities", "hydro", "water", "gas", "electricity")
        return clause.clause_type == ClauseType.UTILITIES or any(keyword in text for keyword in keywords)

    def _mentions_termination(self, clause: Clause, text: str) -> bool:
        keywords = ("terminate", "termination", "notice to end", "end the lease")
        return clause.clause_type == ClauseType.TERMINATION or any(keyword in text for keyword in keywords)

    def _has_abrupt_termination_language(self, text: str) -> bool:
        keywords = ("immediate termination", "without notice", "automatically terminates", "forfeit")
        return any(keyword in text for keyword in keywords)

    def _mentions_subletting(self, clause: Clause, text: str) -> bool:
        keywords = ("sublet", "subletting", "sublease", "assignment", "assign")
        return clause.clause_type == ClauseType.SUBLETTING or any(keyword in text for keyword in keywords)
