"""Job status tracking service."""

from uuid import UUID

from sqlalchemy.orm import Session

from backend.logging_config import get_logger
from backend.models import JobStatus, Document
from backend.schemas import JobStatusResponse

logger = get_logger(__name__)


class JobService:
    """Service for tracking job status."""

    async def get_status(
        self,
        db: Session,
        job_id: UUID,
        user_id: str
    ) -> JobStatusResponse:
        """
        Get job status for a document.

        Args:
            db: Database session
            job_id: Job ID (same as document ID)
            user_id: User ID

        Returns:
            Job status response
        """
        # Verify document exists and belongs to user
        document = db.query(Document).filter(
            Document.id == job_id,
            Document.user_id == user_id,
            Document.deleted_at.is_(None),
        ).first()

        if not document:
            raise ValueError("Job not found or access denied")

        # Get job status
        job_status = db.query(JobStatus).filter(
            JobStatus.document_id == job_id
        ).first()

        if not job_status:
            raise ValueError("Job status not found")

        return JobStatusResponse(
            job_id=job_status.id,
            document_id=job_status.document_id,
            status=job_status.status,
            error_message=job_status.error_message,
            started_at=job_status.started_at,
            completed_at=job_status.completed_at,
            updated_at=job_status.updated_at
        )
