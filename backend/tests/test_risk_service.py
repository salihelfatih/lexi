"""RiskSense service behavior tests."""

import json
import os
import tempfile
from pathlib import Path

import pytest

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"lexi_risk_tests_{os.getpid()}.sqlite"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from backend.database import Base, SessionLocal, engine  # noqa: E402
from backend.models import (  # noqa: E402
    Clause,
    ClauseType,
    Document,
    DocumentFormat,
    DocumentMetadata,
    DocumentType,
    RiskSignal,
    StorageMode,
)
from backend.services.results_service import ResultsService  # noqa: E402
from backend.services.risk_service import RiskService  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def database_schema():
    """Create an isolated SQLite schema for RiskSense service tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    TEST_DB_PATH.unlink(missing_ok=True)


@pytest.fixture
def db_session():
    """Provide a database session for each test."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


def _risk_output_text(risk_sense) -> str:
    return " ".join(
        [
            risk_sense["top_risks_summary"],
            *[f"{risk['title']} {risk['reason']}" for risk in risk_sense["risks"]],
        ]
    ).lower()


def _assert_no_legal_or_outcome_claims(text: str) -> None:
    forbidden_phrases = [
        "illegal",
        "unlawful",
        "unenforceable",
        "against the law",
        "legal advice",
        "will win",
        "will lose",
        "will be evicted",
        "guarantee",
        "must sign",
        "do not sign",
        "outcome",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in text


def _create_supported_document(db_session) -> Document:
    document = Document(
        user_id="risk-user",
        filename="risk-lease.pdf",
        format=DocumentFormat.PDF,
        size_bytes=2048,
        storage_mode=StorageMode.EPHEMERAL,
        document_type=DocumentType.ONTARIO_RESIDENTIAL_LEASE,
        classification_confidence=95.0,
        extracted_text="Ontario Standard Lease with rent, access, and maintenance clauses.",
        extraction_confidence=90.0,
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    clauses = [
        Clause(
            document_id=document.id,
            clause_number="1.",
            clause_type=ClauseType.FEES,
            clause_text="1. Rent payment. The tenant must pay monthly rent on the first day.",
            order_index=0,
        ),
        Clause(
            document_id=document.id,
            clause_number="2.",
            clause_type=ClauseType.ACCESS,
            clause_text="2. Entry and access. The landlord may enter at any time without notice.",
            order_index=1,
        ),
        Clause(
            document_id=document.id,
            clause_number="3.",
            clause_type=ClauseType.MAINTENANCE,
            clause_text="3. Maintenance. The tenant is responsible for repairs to appliances.",
            order_index=2,
        ),
    ]
    db_session.add_all(clauses)
    db_session.add(
        DocumentMetadata(
            document_id=document.id,
            lease_start_date="2026-01-01",
            lease_start_date_confidence=85.0,
            lease_end_date="2026-12-31",
            lease_end_date_confidence=85.0,
            tenant_names=json.dumps(["Jane Doe"]),
            landlord_names=json.dumps(["Alex Smith"]),
            property_address="123 King Street, Toronto, ON",
            monthly_rent="$2450",
            monthly_rent_confidence=80.0,
        )
    )
    db_session.commit()
    return document


@pytest.mark.asyncio
async def test_risk_sense_results_are_source_grounded_and_informational(db_session):
    """RiskSense returns source clauses without legal claims or outcome predictions."""
    document = _create_supported_document(db_session)

    signals = RiskService().generate_risks(db_session, document.id)
    assert signals
    assert all(signal.source_clause_id for signal in signals)
    assert any(signal.rule_id == "landlord_access" for signal in signals)
    assert any(signal.severity.value == "high" for signal in signals)

    results = await ResultsService().get_results(db_session, document.id, document.user_id)
    risk_sense = results.model_dump(mode="json")["risk_sense"]

    assert risk_sense["confidence_rollup"]["extraction"] == 90.0
    assert risk_sense["confidence_rollup"]["classification"] == 95.0
    assert risk_sense["confidence_rollup"]["metadata"] > 0
    assert risk_sense["confidence_rollup"]["risk_signals"] > 0
    assert risk_sense["confidence_rollup"]["overall"] > 0
    assert risk_sense["risks"]
    assert {
        risk["source_clause"]["clause_text"]
        for risk in risk_sense["risks"]
    }.issubset({clause.clause_text for clause in document.clauses})
    _assert_no_legal_or_outcome_claims(_risk_output_text(risk_sense))


def test_risk_sense_skips_unsupported_documents(db_session):
    """Unsupported documents do not receive RiskSense signals."""
    document = Document(
        user_id="risk-user",
        filename="unsupported.pdf",
        format=DocumentFormat.PDF,
        size_bytes=1024,
        storage_mode=StorageMode.EPHEMERAL,
        document_type=DocumentType.UNKNOWN,
        classification_confidence=98.0,
        extracted_text="Bakery operations notes.",
        extraction_confidence=96.0,
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    signals = RiskService().generate_risks(db_session, document.id)

    assert signals == []
    assert db_session.query(RiskSignal).filter(RiskSignal.document_id == document.id).count() == 0
