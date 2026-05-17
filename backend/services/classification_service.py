"""Document classification service using Hugging Face transformers."""

import re
from transformers import pipeline

from backend.config import get_settings
from backend.logging_config import get_logger
from backend.models import DocumentType
from backend.schemas import ClassificationResult

settings = get_settings()
logger = get_logger(__name__)


class ClassificationService:
    """Service for classifying documents."""

    def __init__(self):
        self.classifier = None
        self._load_model()

    def _load_model(self):
        """Load Hugging Face classification model."""
        try:
            # For MVP, we'll use a simple rule-based approach
            # In production, this would load a fine-tuned model
            logger.info("Classification service initialized (rule-based mode)")
        except Exception as e:
            logger.warning(f"Failed to load ML model: {str(e)}, using rule-based fallback")

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify document type.

        Args:
            text: Extracted document text

        Returns:
            Classification result
        """
        # For MVP, use rule-based classification
        return self._rule_based_classify(text)

    def _rule_based_classify(self, text: str) -> ClassificationResult:
        """Rule-based classification for Ontario residential leases."""
        text_lower = text.lower()

        # Ontario lease indicators
        ontario_indicators = [
            "residential tenancies act",
            "landlord and tenant board",
            "ontario",
            "standard lease",
            "tenant",
            "landlord",
            "rental unit",
            "lease term"
        ]

        # Count matches
        matches = sum(1 for indicator in ontario_indicators if indicator in text_lower)

        # Calculate confidence based on matches
        confidence = min((matches / len(ontario_indicators)) * 100, 100)

        # Classify as Ontario lease if confidence >= 70%
        if confidence >= 70:
            document_type = DocumentType.ONTARIO_RESIDENTIAL_LEASE
        else:
            document_type = DocumentType.UNKNOWN
            confidence = 100 - confidence  # Confidence in "unknown" classification

        logger.info(f"Document classified as {document_type.value} with {confidence:.1f}% confidence")

        return ClassificationResult(
            document_type=document_type,
            confidence=confidence
        )
