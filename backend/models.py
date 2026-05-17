"""SQLAlchemy database models."""

from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import (
    Boolean,
    CHAR,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from backend.database import Base


class GUID(TypeDecorator):
    """Platform-independent UUID column.

    PostgreSQL keeps its native UUID type; SQLite stores canonical UUID strings.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, PyUUID):
            uuid_value = value
        else:
            uuid_value = PyUUID(str(value))

        if dialect.name == "postgresql":
            return uuid_value
        return str(uuid_value)

    def process_result_value(self, value, dialect):
        if value is None or isinstance(value, PyUUID):
            return value
        return PyUUID(str(value))


class StorageMode(str, PyEnum):
    """Storage mode for documents."""

    EPHEMERAL = "ephemeral"
    PERSISTENT = "persistent"


class DocumentFormat(str, PyEnum):
    """Supported document formats."""

    PDF = "pdf"
    DOCX = "docx"
    JPEG = "jpeg"
    PNG = "png"


class JobStatusEnum(str, PyEnum):
    """Job processing status."""

    PENDING = "pending"
    UPLOADING = "uploading"
    EXTRACTING_TEXT = "extracting_text"
    CLASSIFYING = "classifying_document"
    EXTRACTING_CLAUSES = "extracting_clauses"
    COMPLETE = "complete"
    FAILED = "failed"


class DocumentType(str, PyEnum):
    """Document classification types."""

    ONTARIO_RESIDENTIAL_LEASE = "ontario_residential_lease"
    UNKNOWN = "unknown"


class ClauseType(str, PyEnum):
    """Clause classification types."""

    TERMINATION = "termination"
    FEES = "fees"
    ACCESS = "access"
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"
    PETS = "pets"
    SUBLETTING = "subletting"
    OTHER = "other"


class RiskSeverity(str, PyEnum):
    """RiskSense severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Document(Base):
    """Document model."""

    __tablename__ = "documents"

    id = Column(GUID(), primary_key=True, default=uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    format = Column(Enum(DocumentFormat), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    storage_mode = Column(Enum(StorageMode), nullable=False)
    s3_key = Column(String(512), nullable=True)

    document_type = Column(Enum(DocumentType), nullable=True)
    classification_confidence = Column(Float, nullable=True)

    extracted_text = Column(Text, nullable=True)
    extraction_confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    consent_record = relationship("ConsentRecord", back_populates="document", uselist=False)
    job_status = relationship("JobStatus", back_populates="document", uselist=False)
    document_metadata = relationship("DocumentMetadata", back_populates="document", uselist=False)
    summary = relationship("DocumentSummary", back_populates="document", uselist=False)
    clauses = relationship("Clause", back_populates="document")
    risk_signals = relationship("RiskSignal", back_populates="document")


class ConsentRecord(Base):
    """Consent record model."""

    __tablename__ = "consent_records"

    id = Column(GUID(), primary_key=True, default=uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id"), nullable=False, unique=True)

    processing_consent = Column(Boolean, nullable=False, default=False)
    processing_consent_at = Column(DateTime, nullable=True)

    storage_consent = Column(Boolean, nullable=False, default=False)
    storage_consent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="consent_record")


class JobStatus(Base):
    """Job status tracking model."""

    __tablename__ = "job_statuses"

    id = Column(GUID(), primary_key=True, default=uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id"), nullable=False, unique=True)

    status = Column(Enum(JobStatusEnum), nullable=False, default=JobStatusEnum.PENDING)
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="job_status")


class DocumentMetadata(Base):
    """Document metadata model."""

    __tablename__ = "document_metadata"

    id = Column(GUID(), primary_key=True, default=uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id"), nullable=False, unique=True)

    lease_start_date = Column(String(50), nullable=True)
    lease_start_date_confidence = Column(Float, nullable=True)

    lease_end_date = Column(String(50), nullable=True)
    lease_end_date_confidence = Column(Float, nullable=True)

    tenant_names = Column(Text, nullable=True)  # JSON array
    landlord_names = Column(Text, nullable=True)  # JSON array

    property_address = Column(Text, nullable=True)

    monthly_rent = Column(String(50), nullable=True)
    monthly_rent_confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="document_metadata")


class DocumentSummary(Base):
    """Grounded LLM summary artifact for a processed document."""

    __tablename__ = "document_summaries"

    id = Column(GUID(), primary_key=True, default=uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id"), nullable=False, unique=True)

    summary_text = Column(Text, nullable=False)
    provider = Column(String(64), nullable=False)
    model = Column(String(128), nullable=False)
    grounded_in = Column(String(64), nullable=False)
    source_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="summary")


class Clause(Base):
    """Clause model."""

    __tablename__ = "clauses"

    id = Column(GUID(), primary_key=True, default=uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id"), nullable=False, index=True)

    clause_number = Column(String(50), nullable=False)
    clause_type = Column(Enum(ClauseType), nullable=False)
    clause_text = Column(Text, nullable=False)

    order_index = Column(Integer, nullable=False)
    indentation_level = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="clauses")
    risk_signals = relationship("RiskSignal", back_populates="source_clause")


class RiskSignal(Base):
    """Source-grounded RiskSense signal for a processed document."""

    __tablename__ = "risk_signals"

    id = Column(GUID(), primary_key=True, default=uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id"), nullable=False, index=True)
    source_clause_id = Column(GUID(), ForeignKey("clauses.id"), nullable=False, index=True)

    rule_id = Column(String(80), nullable=False)
    title = Column(String(160), nullable=False)
    severity = Column(Enum(RiskSeverity), nullable=False)
    confidence = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="risk_signals")
    source_clause = relationship("Clause", back_populates="risk_signals")
