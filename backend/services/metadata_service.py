"""Metadata extraction service."""

import json
import re
from datetime import datetime
from uuid import UUID

from dateutil import parser as date_parser
from sqlalchemy.orm import Session

from backend.logging_config import get_logger
from backend.models import DocumentMetadata

logger = get_logger(__name__)


class MetadataService:
    """Service for extracting metadata from documents."""

    def extract_metadata(self, db: Session, document_id: UUID, text: str) -> None:
        """
        Extract metadata from document text.

        Args:
            db: Database session
            document_id: Document ID
            text: Extracted text
        """
        metadata = DocumentMetadata(document_id=document_id)

        # Extract dates
        start_date, start_confidence = self._extract_start_date(text)
        metadata.lease_start_date = start_date
        metadata.lease_start_date_confidence = start_confidence

        end_date, end_confidence = self._extract_end_date(text)
        metadata.lease_end_date = end_date
        metadata.lease_end_date_confidence = end_confidence

        # Extract names
        tenant_names = self._extract_tenant_names(text)
        metadata.tenant_names = json.dumps(tenant_names)

        landlord_names = self._extract_landlord_names(text)
        metadata.landlord_names = json.dumps(landlord_names)

        # Extract address
        address = self._extract_address(text)
        metadata.property_address = address

        # Extract rent
        rent, rent_confidence = self._extract_rent(text)
        metadata.monthly_rent = rent
        metadata.monthly_rent_confidence = rent_confidence

        db.add(metadata)
        db.commit()

        logger.info(f"Extracted metadata for document {document_id}")

    def _extract_start_date(self, text: str) -> tuple:
        """Extract lease start date."""
        patterns = [
            r'start date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'commencement date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'beginning[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    parsed_date = date_parser.parse(date_str)
                    return parsed_date.strftime('%Y-%m-%d'), 85.0
                except:
                    continue

        return "Not Found", 0.0

    def _extract_end_date(self, text: str) -> tuple:
        """Extract lease end date."""
        patterns = [
            r'end date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'termination date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'expiry[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    parsed_date = date_parser.parse(date_str)
                    return parsed_date.strftime('%Y-%m-%d'), 85.0
                except:
                    continue

        return "Not Found", 0.0

    def _extract_tenant_names(self, text: str) -> list:
        """Extract tenant names."""
        # Simple pattern matching for tenant names
        patterns = [
            r'^\s*[Tt]enant[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)\s*$',
            r'^\s*[Ll]essee[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)\s*$',
        ]

        names = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            names.extend(matches)

        return list(set(names))  # Remove duplicates

    def _extract_landlord_names(self, text: str) -> list:
        """Extract landlord names."""
        patterns = [
            r'^\s*[Ll]andlord[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)\s*$',
            r'^\s*[Ll]essor[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)\s*$',
        ]

        names = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            names.extend(matches)

        return list(set(names))

    def _extract_address(self, text: str) -> str:
        """Extract property address."""
        # Ontario address pattern
        pattern = r'\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd)[,\s]+[A-Z][a-z]+[,\s]+(?:ON|Ontario)'

        match = re.search(pattern, text)
        if match:
            return match.group(0)

        return "Not Found"

    def _extract_rent(self, text: str) -> tuple:
        """Extract monthly rent amount."""
        patterns = [
            r'monthly rent[:\s]+\$?([\d,]+\.?\d*)',
            r'rent[:\s]+\$?([\d,]+\.?\d*)\s*per month',
            r'\$?([\d,]+\.?\d*)\s*per month',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                return f"${amount}", 80.0

        return "Not Found", 0.0
