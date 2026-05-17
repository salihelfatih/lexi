"""LLM provider interface and deterministic test provider."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Protocol
from urllib import error, request

from backend.config import Settings, get_settings


@dataclass(frozen=True)
class SummaryCompletion:
    """Provider-produced summary output."""

    text: str
    provider: str
    model: str


class LLMProvider(Protocol):
    """Interface for grounded LLM providers."""

    name: str
    model: str

    def summarize(self, context: str, document_type: str) -> SummaryCompletion:
        """Summarize a document using only the supplied context."""


class FakeLLMProvider:
    """Deterministic provider for gates and local development."""

    name = "fake"

    def __init__(self, model: str = "fake-grounded-summary-v1"):
        self.model = model

    def summarize(self, context: str, document_type: str) -> SummaryCompletion:
        normalized = _normalize_context(context)
        tenant = _first_match(r"\bTenant:\s*([^\n]+)", normalized)
        landlord = _first_match(r"\bLandlord:\s*([^\n]+)", normalized)
        address = _first_match(r"\bRental unit:\s*([^\n]+)", normalized)
        rent = _first_match(r"\bMonthly rent:\s*(\$?[\d,]+(?:\.\d+)?)", normalized)
        start_date = _first_match(r"\bLease term start date:\s*([^\n]+)", normalized)
        end_date = _first_match(r"\bLease term end date:\s*([^\n]+)", normalized)

        facts = []
        if tenant and landlord:
            facts.append(f"names {tenant} as tenant and {landlord} as landlord")
        elif tenant:
            facts.append(f"names {tenant} as tenant")
        elif landlord:
            facts.append(f"names {landlord} as landlord")

        if address:
            facts.append(f"identifies the rental unit as {address}")
        if rent:
            facts.append(f"lists monthly rent of {rent}")
        if start_date and end_date:
            facts.append(f"sets a lease term from {start_date} to {end_date}")

        clause_topics = _clause_topics(normalized)
        if clause_topics:
            facts.append(
                f"includes clauses about {', '.join(clause_topics[:-1])}, and {clause_topics[-1]}"
                if len(clause_topics) > 1
                else f"includes a clause about {clause_topics[0]}"
            )

        doc_label = document_type.replace("_", " ") if document_type else "processed document"
        if facts:
            text = f"This {doc_label} " + "; ".join(facts) + "."
        else:
            text = (
                f"This {doc_label} does not contain enough readable lease details "
                "for a specific summary from the provided context."
            )

        return SummaryCompletion(text=text, provider=self.name, model=self.model)


class OllamaLLMProvider:
    """Ollama-compatible local provider for real grounded summaries."""

    name = "ollama"

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout_seconds: int = 30,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def summarize(self, context: str, document_type: str) -> SummaryCompletion:
        prompt = _summary_prompt(context=context, document_type=document_type)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        }
        response_payload = self._post_json("/api/generate", payload)
        text = str(response_payload.get("response", "")).strip()
        if not text:
            raise ValueError("Ollama summary response was empty")

        return SummaryCompletion(text=text, provider=self.name, model=self.model)

    def _post_json(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(f"Ollama provider request failed: {exc}") from exc


def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    """Resolve the configured LLM provider."""

    resolved_settings = settings or get_settings()
    provider_name = resolved_settings.llm_provider.strip().lower()

    if provider_name in {"fake", "test"}:
        return FakeLLMProvider(model=resolved_settings.llm_model_name)

    if provider_name == "ollama":
        return OllamaLLMProvider(
            model=resolved_settings.llm_model_name,
            base_url=resolved_settings.llm_base_url or "http://localhost:11434",
            timeout_seconds=resolved_settings.llm_request_timeout_seconds,
        )

    raise ValueError(f"Unsupported LLM provider: {resolved_settings.llm_provider}")


def _normalize_context(context: str) -> str:
    return "\n".join(line.strip() for line in context.splitlines() if line.strip())


def _first_match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _clause_topics(text: str) -> list[str]:
    topics = [
        ("rent payment", ("rent payment", "pay monthly rent")),
        ("maintenance", ("maintenance", "repair")),
        ("entry and access", ("entry", "access", "inspection")),
        ("utilities", ("utilities", "hydro", "water", "gas", "electricity")),
        ("ending the lease", ("notice to end", "terminate", "termination")),
        ("subletting", ("subletting", "sublet", "assignment")),
    ]
    text_lower = text.lower()
    return [label for label, needles in topics if any(needle in text_lower for needle in needles)]


def _summary_prompt(context: str, document_type: str) -> str:
    doc_label = document_type.replace("_", " ") if document_type else "processed document"
    return (
        f"Summarize this {doc_label} in plain language using only the supplied "
        "document context. Do not add legal advice, recommendations, external "
        "rules, or facts that are not present. If a detail is not present, say "
        "it is not stated in the document context.\n\n"
        f"Document context:\n{context}"
    )
