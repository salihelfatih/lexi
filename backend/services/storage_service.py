"""Storage service for document persistence and encryption."""

import boto3
from cryptography.fernet import Fernet
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.logging_config import get_logger
from backend.models import (
    Clause,
    ConsentRecord,
    Document,
    DocumentMetadata,
    DocumentSummary,
    JobStatus,
    RiskSignal,
)
from backend.services.upload_service import UploadService

settings = get_settings()
logger = get_logger(__name__)


class StorageService:
    """Service for document storage and encryption."""

    def __init__(self):
        self.upload_service = UploadService()
        self.s3_client = self._init_s3_client()
        self.cipher = self._init_cipher()

    def _init_s3_client(self):
        """Initialize S3 client."""
        return boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )

    def _init_cipher(self):
        """Initialize encryption cipher."""
        if settings.master_encryption_key:
            return Fernet(settings.master_encryption_key.encode())
        return None

    def store_document_persistent(self, db: Session, document_id: UUID) -> None:
        """
        Store document persistently in S3 with encryption.

        Args:
            db: Database session
            document_id: Document ID
        """
        try:
            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError(f"Document {document_id} not found")

            # Get file content from temp storage
            file_content = self.upload_service.get_temp_file(document_id)

            # Encrypt if cipher available
            if self.cipher:
                file_content = self.cipher.encrypt(file_content)

            # Upload to S3
            s3_key = f"{document.user_id}/{document_id}/{document.filename}"
            self.s3_client.put_object(Bucket=settings.s3_bucket_name, Key=s3_key, Body=file_content)

            # Update document record
            document.s3_key = s3_key
            db.commit()

            # Clean up temp file
            self.upload_service.delete_temp_file(document_id)

            logger.info(f"Document {document_id} stored persistently at {s3_key}")

        except Exception as e:
            logger.error(f"Failed to store document {document_id}: {str(e)}")
            raise

    async def delete_document(self, db: Session, document_id: UUID, user_id: str) -> None:
        """
        Delete document and all associated data.

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID
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

        # Delete from S3 if stored
        if document.s3_key:
            try:
                self.s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=document.s3_key)
                logger.info(f"Deleted S3 object: {document.s3_key}")
            except Exception as e:
                logger.error(f"Failed to delete S3 object: {str(e)}")

        # Delete temp file if exists
        try:
            self.upload_service.delete_temp_file(document_id)
        except FileNotFoundError:
            logger.info(f"No temporary file found for document {document_id}")

        # Delete database records
        db.query(RiskSignal).filter(RiskSignal.document_id == document_id).delete()
        db.query(Clause).filter(Clause.document_id == document_id).delete()
        db.query(DocumentSummary).filter(DocumentSummary.document_id == document_id).delete()
        db.query(DocumentMetadata).filter(DocumentMetadata.document_id == document_id).delete()
        db.query(JobStatus).filter(JobStatus.document_id == document_id).delete()
        db.query(ConsentRecord).filter(ConsentRecord.document_id == document_id).delete()

        # Soft delete document
        document.deleted_at = datetime.utcnow()

        db.commit()

        logger.info(f"Document {document_id} deleted successfully")
