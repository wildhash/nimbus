"""
Structured logging utility for Nimbus Copilot.
"""
import logging
import json
import re
from typing import Any, Dict, Optional
from datetime import datetime


# Patterns for scrubbing sensitive data
SENSITIVE_PATTERNS = [
    (re.compile(r'(token|key|password|secret|credential)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), r'\1: ***REDACTED***'),
    (re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), 'Bearer ***REDACTED***'),
    (re.compile(r'aws_access_key_id\s*=\s*[A-Z0-9]+', re.IGNORECASE), 'aws_access_key_id=***REDACTED***'),
    (re.compile(r'aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]+', re.IGNORECASE), 'aws_secret_access_key=***REDACTED***'),
]


def scrub_secrets(text: str) -> str:
    """
    Scrub sensitive information from log messages.
    
    Args:
        text: Text to scrub
        
    Returns:
        Scrubbed text
    """
    if not text:
        return text
    
    scrubbed = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    
    return scrubbed


class StructuredLogger:
    """Structured logger with automatic secret scrubbing."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (typically module name)
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Add handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(level)
            
            # Use JSON format for structured logs
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log(
        self,
        level: str,
        message: str,
        **kwargs: Any
    ) -> None:
        """
        Log a structured message.
        
        Args:
            level: Log level (info, warning, error, debug)
            message: Log message
            **kwargs: Additional structured data
        """
        # Scrub message
        scrubbed_message = scrub_secrets(message)
        
        # Scrub kwargs
        scrubbed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                scrubbed_kwargs[key] = scrub_secrets(value)
            else:
                scrubbed_kwargs[key] = value
        
        # Build structured log entry
        log_entry = {
            "message": scrubbed_message,
            "timestamp": datetime.utcnow().isoformat(),
            **scrubbed_kwargs
        }
        
        # Log based on level
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(json.dumps(log_entry))
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.log("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.log("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.log("error", message, **kwargs)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.log("debug", message, **kwargs)


def get_logger(name: str, level: int = logging.INFO) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, level)


# Example usage for testing
if __name__ == "__main__":
    logger = get_logger(__name__)
    
    logger.info("Application started")
    logger.info(
        "API request completed",
        provider="friendli",
        latency_ms=150,
        status="success"
    )
    
    # Test secret scrubbing
    logger.info("Testing secret scrubbing: token=abc123xyz secret_key=supersecret")
    logger.warning("Connection failed", error="Authentication failed with key=abc123")
