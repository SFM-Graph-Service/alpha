"""
Security validation utilities for SFM input sanitization and validation.

This module provides functions to sanitize and validate user inputs to prevent
security vulnerabilities like XSS attacks, injection attacks, and other
malicious input-based exploits.

Security measures implemented:
- HTML/script tag sanitization
- Length limits for string inputs
- Metadata validation and sanitization
- URL validation
- Input type validation
"""

import re
import html
import logging
import time
from functools import wraps
from collections import defaultdict, deque
from typing import Any, Deque, DefaultDict, Dict, Optional, List, cast, Callable
from urllib.parse import urlparse
import bleach


# Configure logging
logger = logging.getLogger(__name__)

# Rate limiting configuration for validation operations
VALIDATION_RATE_LIMIT = 50  # requests per minute per IP
VALIDATION_RATE_WINDOW = 60  # seconds
VALIDATION_RATE_LIMITING_ENABLED = True  # Can be disabled for testing
validation_rate_storage: DefaultDict[str, Deque[float]] = defaultdict(deque)
_current_caller_context: Optional[str] = None  # Global context for current caller

# Bleach configuration for advanced HTML sanitization
ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'u', 'br', 'p']
ALLOWED_ATTRIBUTES = {}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

# Public API
__all__ = [
    'SecurityValidationError',
    'sanitize_string',
    'sanitize_description',
    'validate_metadata',
    'validate_url',
    'validate_node_label',
    'validate_node_description',
    'validate_and_sanitize_node_data',
    'set_validation_caller_context',
    'get_validation_rate_limit_status',
    'disable_validation_rate_limiting',
    'enable_validation_rate_limiting',
    'clear_validation_rate_limit_storage',
    'MAX_STRING_LENGTH',
    'MAX_DESCRIPTION_LENGTH',
    'VALIDATION_RATE_LIMIT',
    'VALIDATION_RATE_WINDOW',
]

# Security configuration constants
MAX_STRING_LENGTH = 1000
MAX_DESCRIPTION_LENGTH = 2000
MAX_METADATA_KEYS = 50
MAX_METADATA_VALUE_LENGTH = 500
MAX_METADATA_DEPTH = 3

# Dangerous patterns to detect and sanitize
DANGEROUS_PATTERNS = [
    r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # Script tags
    r'javascript:',  # JavaScript URLs
    r'vbscript:',    # VBScript URLs
    r'on\w+\s*=',    # Event handlers (onclick, onload, etc.)
    r'eval\s*\(',    # eval() calls
    r'expression\s*\(',  # CSS expressions
]

# Compile regex patterns for better performance
DANGEROUS_REGEX = re.compile('|'.join(DANGEROUS_PATTERNS), re.IGNORECASE)


def rate_limit_validation(func: Callable) -> Callable:
    """
    Decorator to apply rate limiting to validation functions.
    
    Args:
        func: Function to rate limit
        
    Returns:
        Decorated function with rate limiting
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Skip rate limiting if disabled
        if not VALIDATION_RATE_LIMITING_ENABLED:
            return func(*args, **kwargs)
            
        # Get caller ID from global context or use default
        caller_id = _current_caller_context or 'direct_call'
        
        current_time = time.time()
        
        # Clean old entries
        caller_requests = validation_rate_storage[caller_id]
        while caller_requests and current_time - caller_requests[0] > VALIDATION_RATE_WINDOW:
            caller_requests.popleft()
        
        # Check if limit exceeded
        if len(caller_requests) >= VALIDATION_RATE_LIMIT:
            logger.warning(
                "Validation rate limit exceeded for %s. Function: %s",
                caller_id, func.__name__
            )
            raise SecurityValidationError(
                f"Validation rate limit exceeded. Maximum {VALIDATION_RATE_LIMIT} "
                f"validation requests per minute allowed.",
                field="rate_limit",
                value=len(caller_requests)
            )
        
        # Add current request
        caller_requests.append(current_time)
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper


class SecurityValidationError(Exception):
    """Raised when input fails security validation."""

    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None, context: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.field = field
        self.value = value
        self.context = context or {}
        self.timestamp = time.time()
        super().__init__(message)

    def log_failure(self, logger_instance: logging.Logger) -> None:
        """Log the security validation failure with full context."""
        logger_instance.error(
            "Security validation failed: %s | Field: %s | Value: %s | Context: %s | Timestamp: %s",
            self.message,
            self.field,
            str(self.value)[:100] if self.value else None,
            self.context,
            self.timestamp
        )


@rate_limit_validation
def sanitize_string(value: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """
    Sanitize a string input by removing dangerous content and limiting length.

    Args:
        value: The string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        SecurityValidationError: If string is too long or contains dangerous patterns
    """
    # Ensure the input is treated as a string
    value = str(value)
    original_value = value

    # Check length
    if len(value) > max_length:
        error = SecurityValidationError(
            f"String too long: {len(value)} > {max_length}",
            field="length",
            value=value[:50] + "..." if len(value) > 50 else value,
            context={"max_length": max_length, "actual_length": len(value)}
        )
        error.log_failure(logger)
        raise error

    # Check for dangerous patterns first
    if DANGEROUS_REGEX.search(value):
        error = SecurityValidationError(
            "Input contains potentially dangerous content",
            field="content",
            value=value[:50] + "..." if len(value) > 50 else value,
            context={"patterns_detected": True}
        )
        error.log_failure(logger)
        raise error

    # Use bleach for advanced HTML sanitization
    try:
        # First pass: Clean with bleach
        cleaned = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True
        )
        
        # Second pass: HTML escape any remaining content
        sanitized = html.escape(cleaned, quote=True)
        
        # Log if content was modified during sanitization
        if sanitized != original_value:
            logger.info(
                "Content sanitized: original length=%d, sanitized length=%d",
                len(original_value), len(sanitized)
            )
        
        return sanitized
        
    except Exception as e:
        error = SecurityValidationError(
            f"Sanitization failed: {str(e)}",
            field="sanitization",
            value=value[:50] + "..." if len(value) > 50 else value,
            context={"exception": str(e)}
        )
        error.log_failure(logger)
        raise error


def sanitize_description(value: str) -> str:
    """
    Sanitize a description field with longer length allowance.

    Args:
        value: The description to sanitize

    Returns:
        Sanitized description
    """
    return sanitize_string(value, MAX_DESCRIPTION_LENGTH)


@rate_limit_validation
def validate_metadata(metadata: Dict[str, Any],
                      max_depth: int = MAX_METADATA_DEPTH) -> Dict[str, Any]:
    """
    Validate and sanitize metadata dictionary.

    Args:
        metadata: Dictionary to validate
        max_depth: Maximum nesting depth allowed

    Returns:
        Sanitized metadata dictionary

    Raises:
        SecurityValidationError: If metadata fails validation
    """
    if len(metadata) > MAX_METADATA_KEYS:
        error = SecurityValidationError(
            f"Too many metadata keys: {len(metadata)} > {MAX_METADATA_KEYS}",
            field="keys",
            value=len(metadata),
            context={"max_keys": MAX_METADATA_KEYS, "actual_keys": len(metadata)}
        )
        error.log_failure(logger)
        raise error

    try:
        return _sanitize_dict(metadata, max_depth)
    except Exception as e:
        error = SecurityValidationError(
            f"Metadata validation failed: {str(e)}",
            field="metadata",
            value=str(metadata)[:100],
            context={"exception": str(e)}
        )
        error.log_failure(logger)
        raise error


def _sanitize_dict(data: Dict[Any, Any], depth: int) -> Dict[str, Any]:
    """
    Recursively sanitize dictionary values.

    Args:
        data: Dictionary to sanitize
        depth: Current nesting depth

    Returns:
        Sanitized dictionary
    """
    if depth <= 0:
        error = SecurityValidationError(
            "Metadata nesting too deep",
            field="depth",
            value=depth,
            context={"max_depth": MAX_METADATA_DEPTH}
        )
        error.log_failure(logger)
        raise error

    sanitized: Dict[str, Any] = {}
    for key, value in data.items():
        # Sanitize key
        key_str: str = str(key)
        sanitized_key = sanitize_string(key_str, MAX_METADATA_VALUE_LENGTH)

        # Sanitize value based on type
        if isinstance(value, str):
            sanitized[sanitized_key] = sanitize_string(value, MAX_METADATA_VALUE_LENGTH)
        elif isinstance(value, dict):
            sanitized[sanitized_key] = _sanitize_dict(cast(Dict[Any, Any], value), depth - 1)
        elif isinstance(value, list):
            sanitized[sanitized_key] = _sanitize_list(cast(List[Any], value), depth - 1)
        elif isinstance(value, (int, float, bool)):
            sanitized[sanitized_key] = value
        elif value is None:
            sanitized[sanitized_key] = None
        else:
            # Convert unknown types to sanitized strings
            sanitized[sanitized_key] = sanitize_string(str(value), MAX_METADATA_VALUE_LENGTH)

    return sanitized


def _sanitize_list(data: List[Any], depth: int) -> List[Any]:
    """
    Recursively sanitize list values.

    Args:
        data: List to sanitize
        depth: Current nesting depth

    Returns:
        Sanitized list
    """
    if depth <= 0:
        error = SecurityValidationError(
            "Metadata nesting too deep",
            field="depth",
            value=depth,
            context={"max_depth": MAX_METADATA_DEPTH}
        )
        error.log_failure(logger)
        raise error

    sanitized: List[Any] = []
    for item in data:
        if isinstance(item, str):
            sanitized.append(sanitize_string(item, MAX_METADATA_VALUE_LENGTH))
        elif isinstance(item, dict):
            sanitized.append(_sanitize_dict(cast(Dict[Any, Any], item), depth - 1))
        elif isinstance(item, list):
            sanitized.append(_sanitize_list(cast(List[Any], item), depth - 1))
        elif isinstance(item, (int, float, bool)):
            sanitized.append(item)
        elif item is None:
            sanitized.append(None)
        else:
            sanitized.append(sanitize_string(str(item), MAX_METADATA_VALUE_LENGTH))

    return sanitized


@rate_limit_validation
def validate_url(url: str) -> bool:
    """
    Validate that a URL is safe and properly formatted.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid and safe

    Raises:
        SecurityValidationError: If URL is invalid or unsafe
    """
    if not url:
        error = SecurityValidationError(
            "URL must be a non-empty string",
            field="type",
            value=url,
            context={"url_empty": True}
        )
        error.log_failure(logger)
        raise error

    # Check for dangerous URL schemes
    if url.lower().startswith(('javascript:', 'vbscript:', 'data:')):
        error = SecurityValidationError(
            "Dangerous URL scheme detected",
            field="scheme",
            value=url,
            context={"dangerous_scheme": True}
        )
        error.log_failure(logger)
        raise error

    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            error = SecurityValidationError(
                "Invalid URL format",
                field="format",
                value=url,
                context={"scheme": parsed.scheme, "netloc": parsed.netloc}
            )
            error.log_failure(logger)
            raise error
    except Exception as e:
        error = SecurityValidationError(
            f"URL parsing failed: {str(e)}",
            field="parsing",
            value=url,
            context={"exception": str(e)}
        )
        error.log_failure(logger)
        raise error

    return True


@rate_limit_validation
def validate_node_label(label: str) -> str:
    """
    Validate and sanitize a node label.

    Args:
        label: Label to validate

    Returns:
        Sanitized label
    """
    if not label:
        error = SecurityValidationError(
            "Label must be a non-empty string",
            field="label",
            value=label,
            context={"empty_label": True}
        )
        error.log_failure(logger)
        raise error

    try:
        return sanitize_string(label.strip())
    except Exception as e:
        error = SecurityValidationError(
            f"Label validation failed: {str(e)}",
            field="label",
            value=label,
            context={"exception": str(e)}
        )
        error.log_failure(logger)
        raise error


@rate_limit_validation
def validate_node_description(description: Optional[str]) -> Optional[str]:
    """
    Validate and sanitize a node description.

    Args:
        description: Description to validate

    Returns:
        Sanitized description or None
    """
    if description is None:
        return None

    description = str(description)

    try:
        return sanitize_description(description.strip())
    except Exception as e:
        error = SecurityValidationError(
            f"Description validation failed: {str(e)}",
            field="description",
            value=description,
            context={"exception": str(e)}
        )
        error.log_failure(logger)
        raise error


@rate_limit_validation
def validate_and_sanitize_node_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validation and sanitization of node data.

    Args:
        data: Dictionary containing node data

    Returns:
        Sanitized node data dictionary
    """
    sanitized: Dict[str, Any] = {}

    try:
        # Validate required fields
        if "name" in data:
            sanitized["name"] = validate_node_label(data["name"])

        if "label" in data:
            sanitized["label"] = validate_node_label(data["label"])

        if "description" in data:
            sanitized["description"] = validate_node_description(data["description"])

        # Validate metadata
        if "meta" in data and data["meta"]:
            sanitized["meta"] = validate_metadata(data["meta"])
        elif "meta" in data:
            sanitized["meta"] = {}

        # Copy other fields with basic validation
        for key, value in data.items():
            if key not in ["name", "label", "description", "meta"]:
                if isinstance(value, str):
                    sanitized[key] = sanitize_string(value)
                else:
                    sanitized[key] = value

        logger.info("Node data validated successfully with %d fields", len(sanitized))
        return sanitized
        
    except Exception as e:
        error = SecurityValidationError(
            f"Node data validation failed: {str(e)}",
            field="node_data",
            value=str(data)[:100],
            context={"exception": str(e), "data_keys": list(data.keys())}
        )
        error.log_failure(logger)
        raise error


def set_validation_caller_context(caller_id: str) -> None:
    """
    Set caller context for rate limiting validation operations.
    
    Args:
        caller_id: Identifier for the caller (e.g., IP address)
    """
    global _current_caller_context
    _current_caller_context = caller_id


def get_validation_rate_limit_status(caller_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current rate limit status for a caller.
    
    Args:
        caller_id: Identifier for the caller (uses current context if not provided)
        
    Returns:
        Dictionary with rate limit status information
    """
    # Use provided caller_id or current context
    if caller_id is None:
        caller_id = _current_caller_context or 'direct_call'
    
    current_time = time.time()
    caller_requests = validation_rate_storage[caller_id]
    
    # Clean old entries
    while caller_requests and current_time - caller_requests[0] > VALIDATION_RATE_WINDOW:
        caller_requests.popleft()
    
    return {
        "caller_id": caller_id,
        "current_requests": len(caller_requests),
        "limit": VALIDATION_RATE_LIMIT,
        "window_seconds": VALIDATION_RATE_WINDOW,
        "remaining_requests": max(0, VALIDATION_RATE_LIMIT - len(caller_requests)),
        "window_reset_time": current_time + VALIDATION_RATE_WINDOW if caller_requests else None
    }


def disable_validation_rate_limiting() -> None:
    """
    Disable rate limiting for validation operations.
    Useful for testing environments.
    """
    global VALIDATION_RATE_LIMITING_ENABLED
    VALIDATION_RATE_LIMITING_ENABLED = False


def enable_validation_rate_limiting() -> None:
    """
    Enable rate limiting for validation operations.
    """
    global VALIDATION_RATE_LIMITING_ENABLED
    VALIDATION_RATE_LIMITING_ENABLED = True


def clear_validation_rate_limit_storage() -> None:
    """
    Clear all rate limiting storage.
    Useful for testing environments.
    """
    validation_rate_storage.clear()
    global _current_caller_context
    _current_caller_context = None
