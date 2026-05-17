"""Document upload and management endpoints."""

import magic
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from uuid import UUID

from backend.config import get_settings
from backend.database import get_db
from backend.logging_config import get_logger
from backend.models import Clause, Document, DocumentFormat, JobStatus, User
from backend.security import get_current_user
from backend.schemas import (
    UploadResponse,
    ConsentRequest,
    ConsentResponse,
    DocumentListItem,
    DocumentListResponse,
    ProcessingResults,
    RagQuestionRequest,
    RagAnswerResponse,
)
from backend.core.document.upload import UploadService
from backend.core.document.consent import ConsentService
from backend.services.results_service import ResultsService
from backend.services.rag_service import QuestionUnavailableError, RagService

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)

upload_service = UploadService()
consent_service = ConsentService()
results_service = ResultsService()
rag_service = RagService()


@router.get("", response_model=DocumentListResponse)
@router.get("/", response_model=DocumentListResponse, include_in_schema=False)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List safe, user-scoped document history metadata for the workspace."""
    documents = (
        db.query(Document)
        .filter(
            Document.user_id == str(current_user.id),
            Document.deleted_at.is_(None),
        )
        .order_by(Document.updated_at.desc(), Document.created_at.desc())
        .all()
    )

    items = []
    for document in documents:
        job_status = db.query(JobStatus).filter(JobStatus.document_id == document.id).first()
        total_clauses = db.query(Clause).filter(Clause.document_id == document.id).count()
        items.append(
            DocumentListItem(
                document_id=document.id,
                filename=document.filename,
                format=document.format,
                size_bytes=document.size_bytes,
                storage_mode=document.storage_mode,
                document_type=document.document_type,
                classification_confidence=document.classification_confidence,
                extraction_confidence=document.extraction_confidence,
                job_status=job_status.status if job_status else None,
                error_message=job_status.error_message if job_status else None,
                has_results=bool(document.document_type),
                total_clauses=total_clauses,
                created_at=document.created_at,
                updated_at=document.updated_at,
                completed_at=job_status.completed_at if job_status else None,
            )
        )

    return DocumentListResponse(documents=items)


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a document for processing.

    Accepts PDF, DOCX, JPEG, and PNG files up to 50MB.
    Returns document ID for consent and processing.
    """
    try:
        file_content = await file.read()
        size_mb = len(file_content) / (1024 * 1024)

        if size_mb > settings.max_file_size_mb:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB",
            )

        mime_type = magic.from_buffer(file_content, mime=True)
        format_map = {
            "application/pdf": DocumentFormat.PDF,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentFormat.DOCX,
            "image/jpeg": DocumentFormat.JPEG,
            "image/png": DocumentFormat.PNG,
        }

        if mime_type not in format_map:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file format. Supported formats: PDF, DOCX, JPEG, PNG",
            )

        document_format = format_map[mime_type]

        document = await upload_service.create_document(
            db=db,
            user_id=str(current_user.id),
            filename=file.filename,
            format=document_format,
            size_bytes=len(file_content),
            file_content=file_content,
        )

        logger.info(f"Document uploaded successfully: {document.id}")

        return UploadResponse(
            document_id=document.id,
            filename=document.filename,
            format=document.format,
            size_bytes=document.size_bytes,
            message="Document uploaded successfully. Please provide consent to proceed.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during upload. Please try again.",
        )


@router.post("/{document_id}/consent", response_model=ConsentResponse)
async def provide_consent(
    document_id: UUID,
    consent: ConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Provide consent for document processing and storage.

    If processing consent is granted, document processing begins.
    If consent is declined, document is deleted immediately.
    """
    try:
        result = await consent_service.process_consent(
            db=db,
            document_id=document_id,
            user_id=str(current_user.id),
            processing_consent=consent.processing_consent,
            storage_consent=consent.storage_consent,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Consent processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing consent.",
        )


@router.get("/{document_id}/results", response_model=ProcessingResults)
async def get_results(
    document_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get processing results for a document.

    Returns classification, metadata, and extracted clauses.
    """
    try:
        results = await results_service.get_results(
            db=db, document_id=document_id, user_id=str(current_user.id)
        )

        return results

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to retrieve results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving results.",
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Delete a document and all associated data.

    Removes document from storage, database, and cache.
    """
    try:
        from backend.core.document.deletion import StorageService

        storage_service = StorageService()

        await storage_service.delete_document(
            db=db, document_id=document_id, user_id=str(current_user.id)
        )

        logger.info(f"Document deleted: {document_id}")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the document.",
        )


@router.post("/{document_id}/ask", response_model=RagAnswerResponse)
async def ask_document(
    document_id: UUID,
    request: RagQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ask a grounded question against a processed document."""
    try:
        return rag_service.ask_document(
            db=db,
            document_id=document_id,
            user_id=str(current_user.id),
            question=request.question,
            user_context=request.user_context,
            top_k=request.top_k,
        )
    except QuestionUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to answer question for document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while answering the question.",
        )
