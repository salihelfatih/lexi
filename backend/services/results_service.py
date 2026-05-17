"""Results retrieval service."""

import json
from uuid import UUID

from sqlalchemy.orm import Session

from backend.logging_config import get_logger
from backend.models import (
    Clause,
    Document,
    DocumentMetadata,
    DocumentSummary,
    DocumentType,
    RiskSignal,
)
from backend.schemas import (
    ClauseSchema,
    DocumentMetadataSchema,
    ProcessingResults,
    RiskSensePayload,
    RiskSignalPayload,
    RiskSourceClause,
    SummaryPayload,
)
from backend.services.risk_service import RiskService

logger = get_logger(__name__)
risk_service = RiskService()


class ResultsService:
    """Service for retrieving processing results."""

    async def get_results(self, db: Session, document_id: UUID, user_id: str) -> ProcessingResults:
        """
        Get processing results for a document.

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID

        Returns:
            Processing results
        """
        # Verify document exists and belongs to user
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id,
                Document.deleted_at.is_(None),
            )
            .first()
        )

        if not document:
            raise ValueError("Document not found or access denied")

        if not document.document_type:
            raise ValueError("Document has not been processed yet")

        # Get metadata
        metadata_record = (
            db.query(DocumentMetadata).filter(DocumentMetadata.document_id == document_id).first()
        )

        metadata = DocumentMetadataSchema()
        if metadata_record:
            metadata = DocumentMetadataSchema(
                lease_start_date=metadata_record.lease_start_date or "Not Found",
                lease_start_date_confidence=metadata_record.lease_start_date_confidence,
                lease_end_date=metadata_record.lease_end_date or "Not Found",
                lease_end_date_confidence=metadata_record.lease_end_date_confidence,
                tenant_names=(
                    json.loads(metadata_record.tenant_names) if metadata_record.tenant_names else []
                ),
                landlord_names=(
                    json.loads(metadata_record.landlord_names)
                    if metadata_record.landlord_names
                    else []
                ),
                property_address=metadata_record.property_address or "Not Found",
                monthly_rent=metadata_record.monthly_rent or "Not Found",
                monthly_rent_confidence=metadata_record.monthly_rent_confidence,
            )

        # Get clauses
        clause_records = (
            db.query(Clause)
            .filter(Clause.document_id == document_id)
            .order_by(Clause.order_index)
            .all()
        )

        clauses = [
            ClauseSchema(
                clause_number=c.clause_number,
                clause_type=c.clause_type,
                clause_text=c.clause_text,
                order_index=c.order_index,
                indentation_level=c.indentation_level,
            )
            for c in clause_records
        ]

        summary_record = (
            db.query(DocumentSummary).filter(DocumentSummary.document_id == document_id).first()
        )
        summary = None
        if summary_record:
            summary = SummaryPayload(
                text=summary_record.summary_text,
                provider=summary_record.provider,
                model=summary_record.model,
                grounded_in=summary_record.grounded_in,
                source_count=summary_record.source_count,
            )

        risk_sense = None
        if document.document_type == DocumentType.ONTARIO_RESIDENTIAL_LEASE:
            risk_records = (
                db.query(RiskSignal)
                .filter(RiskSignal.document_id == document_id)
                .order_by(RiskSignal.confidence.desc())
                .all()
            )
            ranked_risk_records = risk_service.rank_signals(risk_records)
            risk_sense = RiskSensePayload(
                top_risks_summary=risk_service.top_risks_summary(ranked_risk_records),
                confidence_rollup=risk_service.confidence_rollup(
                    document=document,
                    metadata=metadata_record,
                    signals=ranked_risk_records,
                ),
                risks=[
                    RiskSignalPayload(
                        risk_id=signal.id,
                        rule_id=signal.rule_id,
                        title=signal.title,
                        severity=signal.severity,
                        confidence=signal.confidence,
                        reason=signal.reason,
                        source_clause=RiskSourceClause(
                            clause_number=signal.source_clause.clause_number,
                            clause_type=signal.source_clause.clause_type,
                            clause_text=signal.source_clause.clause_text,
                            order_index=signal.source_clause.order_index,
                        ),
                    )
                    for signal in ranked_risk_records
                    if signal.source_clause is not None
                ],
            )

        return ProcessingResults(
            document_id=document_id,
            document_type=document.document_type,
            classification_confidence=document.classification_confidence or 0.0,
            metadata=metadata,
            clauses=clauses,
            summary=summary,
            risk_sense=risk_sense,
            extraction_confidence=document.extraction_confidence or 0.0,
            total_clauses=len(clauses),
        )
