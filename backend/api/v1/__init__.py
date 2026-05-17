"""Backend API v1 package."""

from fastapi import APIRouter

from backend.api.v1 import auth, documents, jobs

router = APIRouter()

router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
