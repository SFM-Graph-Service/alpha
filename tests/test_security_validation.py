"""
Test suite for security validation functionality in SFM framework.

This module tests the security validation and input sanitization features
to ensure protection against XSS, injection attacks, and other security vulnerabilities.
"""

import unittest
import uuid
from unittest.mock import patch, MagicMock

from core.security_validators import (
    sanitize_string,
    sanitize_description,
    validate_metadata,
    validate_url,
    validate_node_label,
    validate_node_description,
    validate_and_sanitize_node_data,
    SecurityValidationError,
    disable_validation_rate_limiting,
    clear_validation_rate_limit_storage,
    MAX_STRING_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_METADATA_KEYS,
    MAX_METADATA_VALUE_LENGTH,
)
from core.sfm_service import SFMService, SFMValidationError, SFMError


class TestSecurityValidators(unittest.TestCase):
    """Test suite for security validation functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Disable rate limiting for tests to avoid interference
        disable_validation_rate_limiting()
        clear_validation_rate_limit_storage()

    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        # Test normal string
        result = sanitize_string("Hello World")
        self.assertEqual(result, "Hello World")
        
        # Test HTML escaping for safe content
        result = sanitize_string("Hello <b>World</b>")
        self.assertEqual(result, "Hello &lt;b&gt;World&lt;/b&gt;")
        
        # Test quotes escaping
        result = sanitize_string('Hello "World"')
        self.assertEqual(result, "Hello &quot;World&quot;")

    def test_sanitize_string_dangerous_patterns(self):
        """Test detection of dangerous patterns."""
        # Test script tags
        with self.assertRaises(SecurityValidationError):
            sanitize_string("<script>alert('xss')</script>")
        
        # Test javascript URLs
        with self.assertRaises(SecurityValidationError):
            sanitize_string("javascript:alert('xss')")
        
        # Test event handlers
        with self.assertRaises(SecurityValidationError):
            sanitize_string("onclick=alert('xss')")
        
        # Test eval calls
        with self.assertRaises(SecurityValidationError):
            sanitize_string("eval('malicious code')")

    def test_sanitize_string_length_limits(self):
        """Test string length validation."""
        # Test string within limit
        short_string = "a" * (MAX_STRING_LENGTH - 1)
        result = sanitize_string(short_string)
        self.assertEqual(result, short_string)
        
        # Test string exceeding limit
        long_string = "a" * (MAX_STRING_LENGTH + 1)
        with self.assertRaises(SecurityValidationError):
            sanitize_string(long_string)

    def test_sanitize_description(self):
        """Test description sanitization with longer limits."""
        # Test description within limit
        desc = "a" * (MAX_DESCRIPTION_LENGTH - 1)
        result = sanitize_description(desc)
        self.assertEqual(result, desc)
        
        # Test description exceeding limit
        long_desc = "a" * (MAX_DESCRIPTION_LENGTH + 1)
        with self.assertRaises(SecurityValidationError):
            sanitize_description(long_desc)

    def test_validate_metadata_basic(self):
        """Test basic metadata validation."""
        # Test valid metadata
        metadata = {"key1": "value1", "key2": "value2"}
        result = validate_metadata(metadata)
        self.assertEqual(result, metadata)
        
        # Test empty metadata
        result = validate_metadata({})
        self.assertEqual(result, {})

    def test_validate_metadata_nested(self):
        """Test nested metadata validation."""
        # Test valid nested metadata
        metadata = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        result = validate_metadata(metadata)
        self.assertEqual(result, metadata)
        
        # Test deeply nested metadata (should fail)
        deep_metadata = {
            "l1": {"l2": {"l3": {"l4": "too deep"}}}
        }
        with self.assertRaises(SecurityValidationError):
            validate_metadata(deep_metadata)

    def test_validate_metadata_too_many_keys(self):
        """Test metadata with too many keys."""
        # Create metadata with too many keys
        metadata = {f"key{i}": f"value{i}" for i in range(MAX_METADATA_KEYS + 1)}
        
        with self.assertRaises(SecurityValidationError):
            validate_metadata(metadata)

    def test_validate_metadata_dangerous_values(self):
        """Test metadata with dangerous values."""
        # Test metadata with script tags
        metadata = {"key": "<script>alert('xss')</script>"}
        
        with self.assertRaises(SecurityValidationError):
            validate_metadata(metadata)

    def test_validate_url(self):
        """Test URL validation."""
        # Test valid URLs
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://example.com/path"))
        
        # Test dangerous URLs
        with self.assertRaises(SecurityValidationError):
            validate_url("javascript:alert('xss')")
        
        with self.assertRaises(SecurityValidationError):
            validate_url("vbscript:alert('xss')")
        
        with self.assertRaises(SecurityValidationError):
            validate_url("data:text/html,<script>alert('xss')</script>")

    def test_validate_node_label(self):
        """Test node label validation."""
        # Test valid label
        result = validate_node_label("Valid Label")
        self.assertEqual(result, "Valid Label")
        
        # Test empty label
        with self.assertRaises(SecurityValidationError):
            validate_node_label("")
        
        # Test None label
        with self.assertRaises(SecurityValidationError):
            validate_node_label(None)

    def test_validate_node_description(self):
        """Test node description validation."""
        # Test valid description
        result = validate_node_description("Valid description")
        self.assertEqual(result, "Valid description")
        
        # Test None description
        result = validate_node_description(None)
        self.assertIsNone(result)

    def test_validate_and_sanitize_node_data(self):
        """Test comprehensive node data validation."""
        # Test valid node data
        data = {
            "name": "Test Node",
            "description": "Test description",
            "meta": {"key": "value"}
        }
        result = validate_and_sanitize_node_data(data)
        self.assertEqual(result["name"], "Test Node")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["meta"], {"key": "value"})
        
        # Test node data with dangerous content
        dangerous_data = {
            "name": "Test Node",
            "description": "<script>alert('xss')</script>",
            "meta": {"key": "value"}
        }
        with self.assertRaises(SecurityValidationError):
            validate_and_sanitize_node_data(dangerous_data)


class TestSFMServiceSecurityIntegration(unittest.TestCase):
    """Test security integration with SFM service."""

    def setUp(self):
        """Set up test fixtures."""
        # Disable rate limiting for tests to avoid interference
        disable_validation_rate_limiting()
        clear_validation_rate_limit_storage()
        self.service = SFMService()

    def test_create_actor_with_dangerous_input(self):
        """Test actor creation with dangerous input."""
        dangerous_data = {
            "name": "<script>alert('xss')</script>",
            "description": "Test description",
            "meta": {}
        }
        
        with self.assertRaises((SFMValidationError, SFMError)) as context:
            self.service.create_actor(dangerous_data)
        
        self.assertIn("Input contains potentially dangerous content", str(context.exception))

    def test_create_actor_with_long_input(self):
        """Test actor creation with excessively long input."""
        long_data = {
            "name": "a" * (MAX_STRING_LENGTH + 1),
            "description": "Test description",
            "meta": {}
        }
        
        with self.assertRaises((SFMValidationError, SFMError)) as context:
            self.service.create_actor(long_data)
        
        self.assertIn("String too long", str(context.exception))

    def test_create_actor_with_dangerous_metadata(self):
        """Test actor creation with dangerous metadata."""
        dangerous_data = {
            "name": "Test Actor",
            "description": "Test description",
            "meta": {
                "key": "<script>alert('xss')</script>"
            }
        }
        
        with self.assertRaises((SFMValidationError, SFMError)) as context:
            self.service.create_actor(dangerous_data)
        
        self.assertIn("Input contains potentially dangerous content", str(context.exception))

    def test_create_institution_with_dangerous_input(self):
        """Test institution creation with dangerous input."""
        dangerous_data = {
            "name": "javascript:alert('xss')",
            "description": "Test description",
            "meta": {}
        }
        
        with self.assertRaises((SFMValidationError, SFMError)) as context:
            self.service.create_institution(dangerous_data)
        
        self.assertIn("Input contains potentially dangerous content", str(context.exception))

    def test_create_policy_with_dangerous_input(self):
        """Test policy creation with dangerous input."""
        dangerous_data = {
            "name": "onclick=alert('xss')",
            "description": "Test description",
            "meta": {}
        }
        
        with self.assertRaises((SFMValidationError, SFMError)) as context:
            self.service.create_policy(dangerous_data)
        
        self.assertIn("Input contains potentially dangerous content", str(context.exception))

    def test_create_resource_with_dangerous_input(self):
        """Test resource creation with dangerous input."""
        dangerous_data = {
            "name": "eval('malicious code')",
            "description": "Test description",
            "meta": {}
        }
        
        with self.assertRaises((SFMValidationError, SFMError)) as context:
            self.service.create_resource(dangerous_data)
        
        self.assertIn("Input contains potentially dangerous content", str(context.exception))

    def test_create_actor_with_valid_input(self):
        """Test actor creation with valid input passes security validation."""
        valid_data = {
            "name": "Valid Actor Name",
            "description": "Valid description",
            "meta": {"key": "value"}
        }
        
        # This should not raise an exception
        result = self.service.create_actor(valid_data)
        self.assertIsNotNone(result)
        self.assertEqual(result.label, "Valid Actor Name")

    def test_create_institution_with_valid_input(self):
        """Test institution creation with valid input passes security validation."""
        valid_data = {
            "name": "Valid Institution Name",
            "description": "Valid description",
            "meta": {"key": "value"}
        }
        
        # This should not raise an exception
        result = self.service.create_institution(valid_data)
        self.assertIsNotNone(result)
        self.assertEqual(result.label, "Valid Institution Name")


class TestSecurityValidationEdgeCases(unittest.TestCase):
    """Test edge cases in security validation."""
    
    def setUp(self):
        """Set up test environment."""
        # Disable rate limiting for tests to avoid interference
        disable_validation_rate_limiting()
        clear_validation_rate_limit_storage()

    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        # Empty string should be allowed but sanitized
        result = sanitize_string("")
        self.assertEqual(result, "")

    def test_non_string_input(self):
        """Test handling of non-string inputs."""
        # Non-string inputs should be converted to strings
        result = sanitize_string(123)
        self.assertEqual(result, "123")
        
        result = sanitize_string(None)
        self.assertEqual(result, "None")

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        # Unicode should be preserved
        unicode_string = "Hello 世界 🌍"
        result = sanitize_string(unicode_string)
        self.assertEqual(result, unicode_string)

    def test_whitespace_handling(self):
        """Test handling of whitespace."""
        # Whitespace should be preserved
        whitespace_string = "  Hello  World  "
        result = sanitize_string(whitespace_string)
        self.assertEqual(result, whitespace_string)

    def test_case_insensitive_pattern_matching(self):
        """Test case-insensitive pattern matching."""
        # Test uppercase script tags
        with self.assertRaises(SecurityValidationError):
            sanitize_string("<SCRIPT>alert('xss')</SCRIPT>")
        
        # Test mixed case
        with self.assertRaises(SecurityValidationError):
            sanitize_string("<ScRiPt>alert('xss')</ScRiPt>")


if __name__ == '__main__':
    unittest.main()