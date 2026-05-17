"""Grounded summary behavior tests."""

import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

TEST_DB_PATH = Path(tempfile.gettempdir()) / f"lexi_summary_tests_{os.getpid()}.sqlite"
if "TEST_DATABASE_URL" in os.environ:
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
else:
    os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["LLM_PROVIDER"] = "fake"
os.environ["LLM_MODEL_NAME"] = "fake-grounded-summary-v1"

from backend.config import Settings  # noqa: E402
from backend.database import Base, SessionLocal, engine  # noqa: E402
from backend.ml.llm.providers import (  # noqa: E402
    FakeLLMProvider,
    OllamaLLMProvider,
    get_llm_provider,
)
from backend.models import (  # noqa: E402
    Document,
    DocumentFormat,
    DocumentType,
    StorageMode,
)
from backend.services.summary_service import SummaryService  # noqa: E402


@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _create_document(db_session, extracted_text: str, extraction_confidence: float) -> Document:
    document = Document(
        user_id=str(uuid4()),
        filename="summary-test.pdf",
        format=DocumentFormat.PDF,
        size_bytes=len(extracted_text.encode("utf-8")),
        storage_mode=StorageMode.EPHEMERAL,
        document_type=DocumentType.ONTARIO_RESIDENTIAL_LEASE,
        classification_confidence=95.0,
        extracted_text=extracted_text,
        extraction_confidence=extraction_confidence,
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


def test_low_confidence_extraction_gets_conservative_fallback(db_session):
    document = _create_document(
        db_session,
        extracted_text="Ontario Standard Lease OCR text is partially readable.",
        extraction_confidence=35.0,
    )

    summary = SummaryService().generate_summary(db_session, document.id)

    assert summary.provider == "lexi"
    assert summary.model == "low-confidence-summary-fallback-v1"
    assert summary.grounded_in == "low_confidence_extracted_text"
    assert summary.source_count == 1
    assert "low confidence" in summary.summary_text
    assert "unclear or missing" in summary.summary_text
    assert "legal advice" not in summary.summary_text.lower()


def test_summary_does_not_invent_missing_lease_facts(db_session):
    document = _create_document(
        db_session,
        extracted_text=(
            "Ontario Standard Lease\n"
            "2. Maintenance and repair. The landlord is responsible for maintenance "
            "and repair of the rental unit."
        ),
        extraction_confidence=96.0,
    )

    summary = SummaryService().generate_summary(db_session, document.id)

    assert summary.provider == "fake"
    assert "maintenance" in summary.summary_text
    assert "Jane Doe" not in summary.summary_text
    assert "Alex Smith" not in summary.summary_text
    assert "$2450" not in summary.summary_text
    assert "2026-01-01" not in summary.summary_text
    assert "legal advice" not in summary.summary_text.lower()


def test_fake_provider_says_when_context_lacks_readable_lease_details():
    completion = FakeLLMProvider().summarize(
        context="Scanned page noise without named lease parties, rent, dates, or clauses.",
        document_type="ontario_residential_lease",
    )

    assert "does not contain enough readable lease details" in completion.text
    assert "Jane Doe" not in completion.text
    assert "$2450" not in completion.text


def test_ollama_provider_adapter_can_be_selected_without_network():
    provider = get_llm_provider(
        Settings(
            llm_provider="ollama",
            llm_model_name="llama3.1",
            llm_base_url="http://localhost:11434",
        )
    )

    assert provider.name == "ollama"
    assert provider.model == "llama3.1"


def test_ollama_provider_builds_grounded_summary_request_without_network(monkeypatch):
    provider = OllamaLLMProvider(model="llama3.1")
    captured = {}

    def fake_post_json(path, payload):
        captured["path"] = path
        captured["payload"] = payload
        return {"response": "This summary only uses the supplied document context."}

    monkeypatch.setattr(provider, "_post_json", fake_post_json)

    completion = provider.summarize(
        context="Tenant: Jane Doe\nMonthly rent: $2450",
        document_type="ontario_residential_lease",
    )

    assert completion.provider == "ollama"
    assert completion.text == "This summary only uses the supplied document context."
    assert captured["path"] == "/api/generate"
    assert captured["payload"]["stream"] is False
    assert "Tenant: Jane Doe" in captured["payload"]["prompt"]
    assert "Do not add legal advice" in captured["payload"]["prompt"]
