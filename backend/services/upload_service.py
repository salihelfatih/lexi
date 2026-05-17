"""Upload service for handling document uploads."""

import tempfile
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.logging_config import get_logger
from backend.models import Document, DocumentFormat, StorageMode, JobStatus, JobStatusEnum

logger = get_logger(__name__)


class UploadService:
    """Service for handling document uploads."""

    async def create_document(
        self,
        db: Session,
        user_id: str,
        filename: str,
        format: DocumentFormat,
        size_bytes: int,
        file_content: bytes
    ) -> Document:
        """
        Create a document record and store file temporarily.

        Args:
            db: Database session
            user_id: User ID
            filename: Original filename
            format: Document format
            size_bytes: File size in bytes
            file_content: File content as bytes

        Returns:
            Created document record
        """
        # Create document record
        document = Document(
            user_id=user_id,
            filename=filename,
            format=format,
            size_bytes=size_bytes,
            storage_mode=StorageMode.EPHEMERAL  # Default to ephemeral until consent
        )

        db.add(document)
        db.flush()

        # Create job status record
        job_status = JobStatus(
            document_id=document.id,
            status=JobStatusEnum.PENDING
        )

        db.add(job_status)

        # Store file temporarily in Redis or temp directory
        temp_path = self._store_temp_file(document.id, file_content)
        logger.info(f"Stored temporary file at: {temp_path}")

        db.commit()
        db.refresh(document)

        return document

    def _store_temp_file(self, document_id: UUID, content: bytes) -> str:
        """Store file temporarily before consent."""
        temp_dir = self._temp_dir()
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_path = temp_dir / str(document_id)
        temp_path.write_bytes(content)

        return str(temp_path)

    def get_temp_file(self, document_id: UUID) -> bytes:
        """Retrieve temporarily stored file."""
        temp_path = self._temp_dir() / str(document_id)

        if not temp_path.exists():
            raise FileNotFoundError(f"Temporary file not found for document {document_id}")

        return temp_path.read_bytes()

    def delete_temp_file(self, document_id: UUID) -> None:
        """Delete temporarily stored file."""
        temp_path = self._temp_dir() / str(document_id)

        if temp_path.exists():
            temp_path.unlink()
            logger.info(f"Deleted temporary file: {temp_path}")

    def _temp_dir(self) -> Path:
        settings = get_settings()
        if settings.upload_temp_dir:
            return Path(settings.upload_temp_dir)
        return Path(tempfile.gettempdir()) / "lexi_uploads"
