"""Text extraction service for PDF, DOCX, and images."""

from uuid import UUID
import pypdf
from docx import Document as DocxDocument
from PIL import Image
import pytesseract
from pytesseract.pytesseract import TesseractNotFoundError
from io import BytesIO

from backend.logging_config import get_logger
from backend.models import DocumentFormat
from backend.schemas import ExtractionResult
from backend.services.upload_service import UploadService

logger = get_logger(__name__)


class ExtractionService:
    """Service for extracting text from documents."""

    def __init__(self):
        self.upload_service = UploadService()

    def extract_text(self, document_id: UUID, format: DocumentFormat) -> ExtractionResult:
        """
        Extract text from document based on format.

        Args:
            document_id: Document ID
            format: Document format

        Returns:
            Extraction result with text and confidence
        """
        file_content = self.upload_service.get_temp_file(document_id)

        if format == DocumentFormat.PDF:
            return self._extract_from_pdf(file_content)
        elif format == DocumentFormat.DOCX:
            return self._extract_from_docx(file_content)
        elif format in [DocumentFormat.JPEG, DocumentFormat.PNG]:
            return self._extract_from_image(file_content)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _extract_from_pdf(self, content: bytes) -> ExtractionResult:
        """Extract text from PDF."""
        try:
            pdf_file = BytesIO(content)
            reader = pypdf.PdfReader(pdf_file)

            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            full_text = "\n\n".join(text_parts)
            word_count = len(full_text.split())

            # Check if PDF has selectable text
            if word_count < 50:
                # Likely scanned PDF, try OCR
                logger.info("PDF appears to be scanned, attempting OCR")
                return self._ocr_pdf(content)

            return ExtractionResult(
                text=full_text,
                confidence=95.0,
                word_count=word_count,
                has_structure=True,
                warnings=[]
            )

        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise ValueError("Failed to extract text from PDF")

    def _extract_from_docx(self, content: bytes) -> ExtractionResult:
        """Extract text from DOCX."""
        try:
            docx_file = BytesIO(content)
            doc = DocxDocument(docx_file)

            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            full_text = "\n\n".join(text_parts)
            word_count = len(full_text.split())

            return ExtractionResult(
                text=full_text,
                confidence=98.0,
                word_count=word_count,
                has_structure=True,
                warnings=[]
            )

        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            raise ValueError("Failed to extract text from DOCX. File may be corrupted.")

    def _extract_from_image(self, content: bytes) -> ExtractionResult:
        """Extract text from image using OCR."""
        try:
            image = Image.open(BytesIO(content))

            # Preprocess image
            image = self._preprocess_image(image)

            # Perform OCR
            text = pytesseract.image_to_string(image)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            # Calculate confidence
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            word_count = len(text.split())
            warnings = []

            if avg_confidence < 60:
                warnings.append("Low OCR confidence. Image quality may be poor.")

            return ExtractionResult(
                text=text,
                confidence=avg_confidence,
                word_count=word_count,
                has_structure=False,
                warnings=warnings
            )

        except TesseractNotFoundError:
            logger.error("Image OCR failed: tesseract executable was not found")
            raise
        except Exception as e:
            logger.error(f"Image OCR failed: {str(e)}")
            raise ValueError("Failed to extract text from image. Please upload a clearer image.")

    def _ocr_pdf(self, content: bytes) -> ExtractionResult:
        """Perform OCR on scanned PDF."""
        # Convert PDF pages to images and OCR each
        # This is a simplified implementation
        try:
            from pdf2image import convert_from_bytes

            images = convert_from_bytes(content)
            text_parts = []
            all_confidences = []

            for image in images:
                image = self._preprocess_image(image)
                text = pytesseract.image_to_string(image)
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

                text_parts.append(text)
                confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                all_confidences.extend(confidences)

            full_text = "\n\n".join(text_parts)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            word_count = len(full_text.split())

            warnings = []
            if avg_confidence < 60:
                warnings.append("Low OCR confidence. Scan quality may be poor.")

            return ExtractionResult(
                text=full_text,
                confidence=avg_confidence,
                word_count=word_count,
                has_structure=False,
                warnings=warnings
            )

        except TesseractNotFoundError:
            logger.error("PDF OCR failed: tesseract executable was not found")
            raise
        except ImportError:
            logger.warning("pdf2image not available, falling back to basic extraction")
            raise ValueError("Cannot OCR scanned PDF. Please upload as images instead.")

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        image = image.convert('L')

        # Enhance contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        return image
