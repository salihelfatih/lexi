"""Consent management service."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.logging_config import get_logger
from backend.models import Document, ConsentRecord, StorageMode, JobStatus, JobStatusEnum
from backend.schemas import ConsentResponse
from backend.services.upload_service import UploadService

logger = get_logger(__name__)


class ConsentService:
    """Service for managing user consent."""

    def __init__(self):
        self.upload_service = UploadService()

    async def process_consent(
        self,
        db: Session,
        document_id: UUID,
        user_id: str,
        processing_consent: bool,
        storage_consent: bool
    ) -> ConsentResponse:
        """
        Process user consent for document processing and storage.

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID
            processing_consent: Whether user consents to processing
            storage_consent: Whether user consents to storage

        Returns:
            Consent response with storage mode
        """
        # Verify document exists and belongs to user
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id,
            Document.deleted_at.is_(None),
        ).first()

        if not document:
            raise ValueError("Document not found or access denied")

        # If consent declined, delete document immediately
        if not processing_consent:
            self._delete_document_immediately(db, document)

            return ConsentResponse(
                document_id=document_id,
                processing_consent=False,
                storage_consent=False,
                storage_mode=StorageMode.EPHEMERAL,
                message="Consent declined. Document has been deleted."
            )

        # Determine storage mode
        storage_mode = StorageMode.PERSISTENT if storage_consent else StorageMode.EPHEMERAL
        document.storage_mode = storage_mode

        # Create consent record
        consent_record = ConsentRecord(
            document_id=document_id,
            processing_consent=processing_consent,
            processing_consent_at=datetime.utcnow() if processing_consent else None,
            storage_consent=storage_consent,
            storage_consent_at=datetime.utcnow() if storage_consent else None
        )

        db.add(consent_record)

        # Update job status to start processing
        job_status = db.query(JobStatus).filter(
            JobStatus.document_id == document_id
        ).first()

        if job_status:
            job_status.status = JobStatusEnum.EXTRACTING_TEXT
            job_status.started_at = datetime.utcnow()

        db.commit()

        # Trigger async processing
        from backend.tasks.processing import process_document
        process_document.delay(str(document_id))

        logger.info(f"Consent granted for document {document_id}, mode: {storage_mode}")

        return ConsentResponse(
            document_id=document_id,
            processing_consent=processing_consent,
            storage_consent=storage_consent,
            storage_mode=storage_mode,
            message=f"Processing started in {storage_mode.value} mode."
        )

    def _delete_document_immediately(self, db: Session, document: Document) -> None:
        """Delete document when consent is declined."""
        # Delete temp file
        self.upload_service.delete_temp_file(document.id)

        # Delete database records
        db.query(JobStatus).filter(JobStatus.document_id == document.id).delete()
        db.delete(document)
        db.commit()

        logger.info(f"Document {document.id} deleted due to declined consent")
