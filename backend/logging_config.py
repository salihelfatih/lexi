"""Logging configuration with PII protection."""

import logging
import re
from typing import Any

from backend.config import get_settings

settings = get_settings()


class PIIFilter(logging.Filter):
    """Filter to remove PII from log messages."""

    # Patterns for common PII
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    POSTAL_CODE_PATTERN = re.compile(r'\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b')

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize log record to remove PII."""
        if hasattr(record, 'msg'):
            record.msg = self._sanitize(str(record.msg))
        if hasattr(record, 'args') and record.args:
            record.args = self._sanitize_args(record.args)
        return True

    def _sanitize_args(self, args: Any) -> Any:
        """Sanitize logging args without changing placeholder-compatible types."""
        if isinstance(args, dict):
            return {key: self._sanitize_arg(value) for key, value in args.items()}
        if isinstance(args, tuple):
            return tuple(self._sanitize_arg(arg) for arg in args)
        return self._sanitize_arg(args)

    def _sanitize_arg(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._sanitize(value)
        return value

    def _sanitize(self, text: str) -> str:
        """Remove PII patterns from text."""
        text = self.EMAIL_PATTERN.sub('[EMAIL]', text)
        text = self.PHONE_PATTERN.sub('[PHONE]', text)
        text = self.SSN_PATTERN.sub('[SSN]', text)
        text = self.POSTAL_CODE_PATTERN.sub('[POSTAL_CODE]', text)
        return text


def setup_logging() -> None:
    """Configure logging with PII protection."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Add PII filter to all handlers
    pii_filter = PIIFilter()
    for handler in logging.root.handlers:
        handler.addFilter(pii_filter)

    # Set specific log levels for noisy libraries
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('celery').setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with PII protection."""
    return logging.getLogger(name)
