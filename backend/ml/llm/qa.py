"""Document-scoped Q&A entrypoint."""

import re

from backend.ml.llm.prompts import QA_PROMPT


QUESTION_STOPWORDS = {
    "about",
    "after",
    "also",
    "answer",
    "are",
    "based",
    "can",
    "could",
    "document",
    "does",
    "from",
    "give",
    "has",
    "have",
    "how",
    "into",
    "is",
    "it",
    "lease",
    "legal",
    "lexi",
    "may",
    "me",
    "mention",
    "my",
    "need",
    "say",
    "says",
    "should",
    "show",
    "tell",
    "that",
    "the",
    "this",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
    "would",
    "you",
}

MISSING_ANSWER = (
    "I don't know from this document. I could not find source text that answers " "that question."
)


def answer_document_question(
    question: str,
    context: str,
    chunks: list[dict] | None = None,
    user_context: str | None = None,
) -> dict[str, object]:
    """Build a deterministic, source-quoted answer from retrieved chunks."""
    source_chunks = chunks or _chunks_from_context(context)
    ranked_chunks = _rank_chunks(question=question, chunks=source_chunks)

    user_context_note = None
    if user_context and user_context.strip():
        user_context_note = (
            "Your situation context was kept separate from the document evidence "
            "and was not used as a source of document facts."
        )

    if not ranked_chunks:
        return {
            "prompt": QA_PROMPT,
            "question": question,
            "context": context,
            "answer": MISSING_ANSWER,
            "is_answered": False,
            "citations": [],
            "user_context_note": user_context_note,
        }

    citations = []
    for index, chunk in enumerate(ranked_chunks[:2], start=1):
        citations.append(
            {
                "citation_id": f"Source {index}",
                "chunk_id": str(chunk.get("chunk_id", "")),
                "text": _trim_excerpt(str(chunk.get("text", ""))),
                "score": float(chunk.get("score", 0.0)),
            }
        )

    primary_source = citations[0]["text"]
    answer = f'From this document: "{primary_source}"'

    return {
        "prompt": QA_PROMPT,
        "question": question,
        "context": context,
        "answer": answer,
        "is_answered": True,
        "citations": citations,
        "user_context_note": user_context_note,
    }


def _rank_chunks(question: str, chunks: list[dict]) -> list[dict]:
    question_terms = _meaningful_terms(question)
    if not question_terms:
        return []

    ranked = []
    for chunk in chunks:
        text = str(chunk.get("text", ""))
        chunk_terms = _meaningful_terms(text)
        overlap = question_terms.intersection(chunk_terms)
        if not overlap:
            continue

        lexical_score = len(overlap) / len(question_terms)
        if "rent" in question_terms and "$" in text:
            lexical_score += 1.0
        if {"start", "end", "date"}.intersection(question_terms) and re.search(
            r"\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b",
            text,
        ):
            lexical_score += 0.75

        ranked.append(
            {
                **chunk,
                "score": lexical_score + (float(chunk.get("score", 0.0)) * 0.01),
            }
        )

    return sorted(ranked, key=lambda chunk: chunk["score"], reverse=True)


def _meaningful_terms(text: str) -> set[str]:
    terms = set()
    for token in re.findall(r"[a-z0-9$]+", text.lower()):
        if len(token) < 3 and not token.startswith("$"):
            continue
        if token in QUESTION_STOPWORDS:
            continue
        terms.add(token)
    return terms


def _chunks_from_context(context: str) -> list[dict]:
    return [
        {"chunk_id": str(index), "text": chunk.strip(), "score": 0.0}
        for index, chunk in enumerate(context.split("\n\n"))
        if chunk.strip()
    ]


def _trim_excerpt(text: str, max_length: int = 420) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 1].rstrip() + "..."
