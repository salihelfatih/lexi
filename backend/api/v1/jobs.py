"""Job status endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from backend.database import get_db
from backend.logging_config import get_logger
from backend.models import User
from backend.schemas import JobStatusResponse
from backend.security import get_current_user
from backend.services.job_service import JobService

router = APIRouter()
logger = get_logger(__name__)

job_service = JobService()


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current status of a processing job.

    Returns job status, progress, and any error messages.
    """
    try:
        status_info = await job_service.get_status(
            db=db,
            job_id=job_id,
            user_id=str(current_user.id)
        )

        return status_info

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve job status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving job status."
        )
