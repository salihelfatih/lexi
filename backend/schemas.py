"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DocumentFormat(str, Enum):
    """Supported document formats."""

    PDF = "pdf"
    DOCX = "docx"
    JPEG = "jpeg"
    PNG = "png"


class StorageMode(str, Enum):
    """Storage mode."""

    EPHEMERAL = "ephemeral"
    PERSISTENT = "persistent"


class JobStatusEnum(str, Enum):
    """Job status."""

    PENDING = "pending"
    UPLOADING = "uploading"
    EXTRACTING_TEXT = "extracting_text"
    CLASSIFYING = "classifying_document"
    EXTRACTING_CLAUSES = "extracting_clauses"
    COMPLETE = "complete"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Document types."""

    ONTARIO_RESIDENTIAL_LEASE = "ontario_residential_lease"
    UNKNOWN = "unknown"


class ClauseType(str, Enum):
    """Clause types."""

    TERMINATION = "termination"
    FEES = "fees"
    ACCESS = "access"
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    PETS = "pets"
    SUBLETTING = "subletting"
    OTHER = "other"


class RiskSeverity(str, Enum):
    """RiskSense severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Upload schemas
class UploadResponse(BaseModel):
    """Response after document upload."""

    document_id: UUID
    filename: str
    format: DocumentFormat
    size_bytes: int
    message: str = "Document uploaded successfully. Please provide consent to proceed."


# Consent schemas
class ConsentRequest(BaseModel):
    """Consent request."""

    processing_consent: bool
    storage_consent: bool = False


class ConsentResponse(BaseModel):
    """Consent response."""

    document_id: UUID
    processing_consent: bool
    storage_consent: bool
    storage_mode: StorageMode
    message: str


# Job status schemas
class JobStatusResponse(BaseModel):
    """Job status response."""

    job_id: UUID
    document_id: UUID
    status: JobStatusEnum
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime


# Extraction schemas
class ExtractionResult(BaseModel):
    """Text extraction result."""

    text: str
    confidence: float = Field(ge=0.0, le=100.0)
    word_count: int
    has_structure: bool
    warnings: List[str] = []


# Classification schemas
class ClassificationResult(BaseModel):
    """Document classification result."""

    document_type: DocumentType
    confidence: float = Field(ge=0.0, le=100.0)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate confidence is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError("Confidence must be between 0 and 100")
        return v


# Clause schemas
class ClauseSchema(BaseModel):
    """Clause schema."""

    clause_number: str
    clause_type: ClauseType
    clause_text: str
    order_index: int
    indentation_level: int = 0


# Metadata schemas
class DocumentMetadataSchema(BaseModel):
    """Document metadata schema."""

    lease_start_date: Optional[str] = "Not Found"
    lease_start_date_confidence: Optional[float] = None

    lease_end_date: Optional[str] = "Not Found"
    lease_end_date_confidence: Optional[float] = None

    tenant_names: List[str] = []
    landlord_names: List[str] = []

    property_address: Optional[str] = "Not Found"

    monthly_rent: Optional[str] = "Not Found"
    monthly_rent_confidence: Optional[float] = None


class SummaryPayload(BaseModel):
    """Grounded summary returned with processing results."""

    text: str
    provider: str
    model: str
    grounded_in: str
    source_count: int


class RiskSourceClause(BaseModel):
    """Source clause attached to a RiskSense signal."""

    clause_number: str
    clause_type: ClauseType
    clause_text: str
    order_index: int


class RiskSignalPayload(BaseModel):
    """Source-grounded RiskSense signal returned with processing results."""

    risk_id: UUID
    rule_id: str
    title: str
    severity: RiskSeverity
    confidence: float = Field(ge=0.0, le=100.0)
    reason: str
    source_clause: RiskSourceClause


class RiskConfidenceRollup(BaseModel):
    """Confidence rollup across processing and RiskSense stages."""

    extraction: float = Field(ge=0.0, le=100.0)
    classification: float = Field(ge=0.0, le=100.0)
    metadata: float = Field(ge=0.0, le=100.0)
    risk_signals: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    overall: float = Field(ge=0.0, le=100.0)
    notes: List[str] = Field(default_factory=list)


class RiskSensePayload(BaseModel):
    """RiskSense summary returned with processing results."""

    top_risks_summary: str
    confidence_rollup: RiskConfidenceRollup
    risks: List[RiskSignalPayload] = Field(default_factory=list)


class DocumentListItem(BaseModel):
    """Safe document metadata for the workspace history/sidebar."""

    document_id: UUID
    filename: str
    format: DocumentFormat
    size_bytes: int
    storage_mode: StorageMode
    document_type: Optional[DocumentType] = None
    classification_confidence: Optional[float] = None
    extraction_confidence: Optional[float] = None
    job_status: Optional[JobStatusEnum] = None
    error_message: Optional[str] = None
    has_results: bool = False
    total_clauses: int = 0
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class DocumentListResponse(BaseModel):
    """User-scoped document history response."""

    documents: List[DocumentListItem]


# Results schemas
class ProcessingResults(BaseModel):
    """Complete processing results."""

    document_id: UUID
    document_type: DocumentType
    classification_confidence: float

    metadata: DocumentMetadataSchema
    clauses: List[ClauseSchema]
    summary: Optional[SummaryPayload] = None
    risk_sense: Optional[RiskSensePayload] = None

    extraction_confidence: float
    total_clauses: int


# Error schemas
class ErrorResponse(BaseModel):
    """Error response."""

    error_code: str
    message: str
    details: Optional[str] = None


class UserCreate(BaseModel):
    """User registration payload."""

    email: str
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    """Public user payload."""

    id: UUID
    email: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class RagQuestionRequest(BaseModel):
    """Request payload for document-scoped Q&A."""

    question: str = Field(min_length=3, max_length=1000)
    user_context: Optional[str] = Field(default=None, max_length=1500)
    top_k: int = Field(default=5, ge=1, le=20)


class RagChunkMatch(BaseModel):
    """Single retrieved chunk with similarity score."""

    chunk_id: str
    text: str
    score: float


class RagCitation(BaseModel):
    """Source text shown with a grounded answer."""

    citation_id: str
    chunk_id: str
    text: str
    score: float


class RagAnswerResponse(BaseModel):
    """Response payload for document-scoped Q&A retrieval."""

    document_id: UUID
    question: str
    top_k: int
    answer: str
    is_answered: bool
    citations: List[RagCitation]
    user_context_note: Optional[str] = None
    retrieved_chunks: List[RagChunkMatch]
    context: str
    answer_payload: dict[str, object]
