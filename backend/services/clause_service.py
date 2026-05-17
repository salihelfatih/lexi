"""Clause parsing and extraction service."""

import re
from uuid import UUID
from sqlalchemy.orm import Session

from backend.logging_config import get_logger
from backend.models import Clause, ClauseType

logger = get_logger(__name__)


class ClauseService:
    """Service for parsing and extracting clauses."""

    def extract_clauses(self, db: Session, document_id: UUID, text: str) -> None:
        """
        Extract clauses from document text.

        Args:
            db: Database session
            document_id: Document ID
            text: Extracted text
        """
        # Split text into potential clauses
        clauses = self._detect_clause_boundaries(text)

        # Tag each clause with type
        for idx, clause_text in enumerate(clauses):
            clause_number = self._extract_clause_number(clause_text, idx)
            clause_type = self._classify_clause_type(clause_text)
            indentation = self._detect_indentation(clause_text)

            clause = Clause(
                document_id=document_id,
                clause_number=clause_number,
                clause_type=clause_type,
                clause_text=clause_text.strip(),
                order_index=idx,
                indentation_level=indentation
            )

            db.add(clause)

        db.commit()
        logger.info(f"Extracted {len(clauses)} clauses from document {document_id}")

    def _detect_clause_boundaries(self, text: str) -> list:
        """Detect clause boundaries in text."""
        # Patterns for clause numbering
        patterns = [
            r'^\d+\.',  # 1. 2. 3.
            r'^[A-Z]\.',  # A. B. C.
            r'^[a-z]\)',  # a) b) c)
            r'^\d+\.\d+',  # 1.1 1.2 2.1
            r'^[IVX]+\.',  # I. II. III. (Roman numerals)
        ]

        lines = text.split('\n')
        clauses = []
        current_clause = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts a new clause
            is_new_clause = any(re.match(pattern, line) for pattern in patterns)

            if is_new_clause and current_clause:
                clauses.append('\n'.join(current_clause))
                current_clause = [line]
            else:
                current_clause.append(line)

        # Add last clause
        if current_clause:
            clauses.append('\n'.join(current_clause))

        # If no numbered clauses found, split by paragraphs
        if len(clauses) < 2:
            clauses = [p.strip() for p in text.split('\n\n') if p.strip()]

        return clauses

    def _extract_clause_number(self, text: str, index: int) -> str:
        """Extract clause number from text."""
        # Try to find number at start of text
        match = re.match(r'^([\d\.A-Za-z\)]+)', text)
        if match:
            return match.group(1)
        return str(index + 1)

    def _classify_clause_type(self, text: str) -> ClauseType:
        """Classify clause type based on content."""
        text_lower = text.lower()

        # Keyword-based classification
        if any(word in text_lower for word in ['terminate', 'termination', 'end of lease', 'notice to end']):
            return ClauseType.TERMINATION
        elif any(word in text_lower for word in ['fee', 'charge', 'payment', 'cost', 'penalty']):
            return ClauseType.FEES
        elif any(word in text_lower for word in ['entry', 'access', 'enter', 'inspection']):
            return ClauseType.ACCESS
        elif any(word in text_lower for word in ['maintenance', 'repair', 'upkeep', 'fix']):
            return ClauseType.MAINTENANCE
        elif any(word in text_lower for word in ['utility', 'utilities', 'hydro', 'water', 'gas', 'electricity']):
            return ClauseType.UTILITIES
        elif any(word in text_lower for word in ['pet', 'pets', 'animal', 'dog', 'cat']):
            return ClauseType.PETS
        elif any(word in text_lower for word in ['sublet', 'sublease', 'assign', 'assignment']):
            return ClauseType.SUBLETTING
        else:
            return ClauseType.OTHER

    def _detect_indentation(self, text: str) -> int:
        """Detect indentation level of clause."""
        # Count leading spaces/tabs
        match = re.match(r'^(\s+)', text)
        if match:
            spaces = len(match.group(1))
            return spaces // 4  # Assume 4 spaces per indent level
        return 0
