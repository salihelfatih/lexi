"""Clause-level chunking utilities for RAG."""

import re
from typing import Any


def chunk_document(document_text: str) -> list[dict[str, Any]]:
    """Chunk a document into retrieval-ready clause-like blocks.

    The MVP keeps chunks short enough to quote back to users. It recognizes
    numbered clauses and common lease metadata labels while still falling back
    to paragraph chunks for less structured text.
    """
    lines = [line.strip() for line in document_text.replace("\r\n", "\n").split("\n")]
    parts = []
    current = []

    for line in lines:
        if not line:
            if current:
                parts.append(" ".join(current).strip())
                current = []
            continue

        starts_new_chunk = bool(
            re.match(r"^(\d+\.|[A-Z]\.|[a-z]\)|[IVX]+\.)\s+", line)
            or re.match(
                r"^(landlord|tenant|rental unit|lease term|monthly rent)\s*:",
                line,
                re.IGNORECASE,
            )
        )

        if starts_new_chunk and current:
            parts.append(" ".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        parts.append(" ".join(current).strip())

    if len(parts) < 2:
        parts = [part.strip() for part in document_text.split("\n\n") if part.strip()]

    return [
        {
            "chunk_id": index,
            "text": part,
        }
        for index, part in enumerate(parts)
    ]
