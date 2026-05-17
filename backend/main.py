"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1 import router as api_v1_router
from backend.config import get_settings
from backend.logging_config import setup_logging

settings = get_settings()
setup_logging()

app = FastAPI(
    title="Lexi Intelligence System",
    description="Legal understanding engine that turns dense legal documents into clear, plain-English explanations",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lexi"}
