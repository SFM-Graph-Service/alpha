"""
Test suite for security validation enhancements.

This module tests the new security features added to the SFM framework:
- Rate limiting for validation operations
- Enhanced logging for security validation failures
- Advanced input sanitization with bleach
"""

import unittest
import time
from unittest.mock import patch, MagicMock

from infrastructure.security_validators import (
    sanitize_string,
    validate_metadata,
    validate_url,
    validate_node_label,
    SecurityValidationError,
    set_validation_caller_context,
    get_validation_rate_limit_status,
    disable_validation_rate_limiting,
    enable_validation_rate_limiting,
    clear_validation_rate_limit_storage,
    VALIDATION_RATE_LIMIT,
    VALIDATION_RATE_WINDOW,
)


class TestSecurityEnhancements(unittest.TestCase):
    """Test suite for security validation enhancements."""

    def setUp(self):
        """Set up test environment."""
        # Clear rate limiting storage before each test
        clear_validation_rate_limit_storage()
        # Enable rate limiting for testing
        enable_validation_rate_limiting()

    def tearDown(self):
        """Clean up test environment."""
        # Disable rate limiting after each test to not interfere with other tests
        disable_validation_rate_limiting()
        clear_validation_rate_limit_storage()

    def test_rate_limiting_functionality(self):
        """Test that rate limiting works correctly."""
        # Set a caller context
        set_validation_caller_context("test_ip_123")
        
        # First few calls should succeed
        for i in range(5):
            result = sanitize_string(f"test string {i}")
            self.assertEqual(result, f"test string {i}")
        
        # Check rate limit status
        status = get_validation_rate_limit_status()
        self.assertEqual(status["caller_id"], "test_ip_123")
        self.assertEqual(status["current_requests"], 5)
        self.assertEqual(status["limit"], VALIDATION_RATE_LIMIT)
        self.assertEqual(status["remaining_requests"], VALIDATION_RATE_LIMIT - 5)

    def test_rate_limiting_exceeded(self):
        """Test that rate limiting throws error when exceeded."""
        # Set a caller context
        set_validation_caller_context("test_ip_456")
        
        # Make calls up to the limit
        for i in range(VALIDATION_RATE_LIMIT):
            sanitize_string(f"test {i}")
        
        # Next call should raise rate limit error
        with self.assertRaises(SecurityValidationError) as context:
            sanitize_string("one too many")
        
        self.assertIn("rate limit exceeded", str(context.exception).lower())

    def test_rate_limiting_disabled(self):
        """Test that rate limiting can be disabled."""
        disable_validation_rate_limiting()
        
        # Should be able to make many calls without rate limiting
        for i in range(VALIDATION_RATE_LIMIT + 10):
            result = sanitize_string(f"test {i}")
            self.assertEqual(result, f"test {i}")

    def test_enhanced_error_logging(self):
        """Test that enhanced error logging works correctly."""
        with patch('core.security_validators.logger') as mock_logger:
            # Try to validate a string that's too long
            long_string = "a" * 1001
            
            with self.assertRaises(SecurityValidationError) as context:
                sanitize_string(long_string)
            
            # Check that the error was logged
            mock_logger.error.assert_called_once()
            
            # Check that the SecurityValidationError has enhanced context
            error = context.exception
            self.assertIsNotNone(error.context)
            self.assertIn("max_length", error.context)
            self.assertIn("actual_length", error.context)
            self.assertIsNotNone(error.timestamp)

    def test_advanced_html_sanitization(self):
        """Test that advanced HTML sanitization with bleach works."""
        # Test that basic HTML is cleaned
        html_input = "<div>Hello <script>alert('xss')</script> World</div>"
        
        with self.assertRaises(SecurityValidationError):
            sanitize_string(html_input)
        
        # Test that allowed tags are preserved
        safe_input = "<b>Bold text</b>"
        result = sanitize_string(safe_input)
        # Should be HTML escaped since we're being strict
        self.assertIn("&lt;b&gt;", result)

    def test_metadata_validation_with_dangerous_content(self):
        """Test metadata validation with dangerous content."""
        dangerous_metadata = {
            "key": "<script>alert('xss')</script>",
            "safe_key": "safe_value"
        }
        
        with self.assertRaises(SecurityValidationError) as context:
            validate_metadata(dangerous_metadata)
        
        # Should fail on the dangerous content
        self.assertIn("dangerous content", str(context.exception).lower())

    def test_url_validation_with_dangerous_schemes(self):
        """Test URL validation with dangerous schemes."""
        dangerous_urls = [
            "javascript:alert('xss')",
            "vbscript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for url in dangerous_urls:
            with self.assertRaises(SecurityValidationError) as context:
                validate_url(url)
            
            self.assertIn("dangerous", str(context.exception).lower())

    def test_node_label_validation_with_logging(self):
        """Test node label validation with enhanced logging."""
        with patch('core.security_validators.logger') as mock_logger:
            # Test empty label
            with self.assertRaises(SecurityValidationError) as context:
                validate_node_label("")
            
            # Check that error was logged
            mock_logger.error.assert_called_once()
            
            # Check context
            error = context.exception
            self.assertIsNotNone(error.context)
            self.assertIn("empty_label", error.context)

    def test_multiple_caller_contexts(self):
        """Test that rate limiting works with multiple caller contexts."""
        # Set up different callers
        set_validation_caller_context("caller1")
        
        # Make calls for caller1
        for i in range(10):
            sanitize_string(f"caller1 test {i}")
        
        # Switch to caller2
        set_validation_caller_context("caller2")
        
        # Should be able to make calls for caller2
        for i in range(10):
            sanitize_string(f"caller2 test {i}")
        
        # Check statuses
        status1 = get_validation_rate_limit_status("caller1")
        
        # Switch back to caller1 to get its status
        set_validation_caller_context("caller1")
        status_current = get_validation_rate_limit_status()
        
        # Switch to caller2 to get its status
        set_validation_caller_context("caller2")
        status2 = get_validation_rate_limit_status()
        
        self.assertEqual(status1["current_requests"], 10)
        self.assertEqual(status2["current_requests"], 10)
        self.assertEqual(status_current["current_requests"], 10)


if __name__ == '__main__':
    unittest.main()