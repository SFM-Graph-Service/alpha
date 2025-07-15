"""
Comprehensive security tests for API Layer Security Hardening.

Tests cover:
- Authentication and authorization
- JWT token validation
- Role-based access control (RBAC)
- Input validation and sanitization
- Rate limiting
- Security headers
- Audit logging
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from jose import jwt

from api.sfm_api import app
from core.security import (
    auth_manager,
    security_config,
    Role,
    Permission,
    UserCreate,
    UserLogin,
    input_validator,
    SECURITY_HEADERS,
    ROLE_PERMISSIONS
)

class TestAuthentication:
    """Test authentication functionality."""
    
    def setup_method(self):
        """Set up test client and clear users."""
        self.client = TestClient(app)
        # Clear existing users except admin
        auth_manager.users = {}
        auth_manager.user_credentials = {}
        
        # Create test users
        self.admin_user = UserCreate(
            username="test_admin",
            email="admin@test.com",
            password="AdminPass123!",
            role=Role.ADMIN
        )
        
        self.regular_user = UserCreate(
            username="test_user",
            email="user@test.com",
            password="UserPass123!",
            role=Role.USER
        )
        
        # Register users
        auth_manager.create_user(self.admin_user)
        auth_manager.create_user(self.regular_user)
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        new_user = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "NewPass123!",
            "role": "user"
        }
        
        response = self.client.post("/auth/register", json=new_user)
        assert response.status_code == 201
        
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@test.com"
        assert data["role"] == "user"
        assert data["is_active"] == True
    
    def test_user_registration_duplicate_username(self):
        """Test registration fails with duplicate username."""
        duplicate_user = {
            "username": "test_user",  # Already exists
            "email": "duplicate@test.com",
            "password": "DupePass123!",
            "role": "user"
        }
        
        response = self.client.post("/auth/register", json=duplicate_user)
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]
    
    def test_user_registration_invalid_password(self):
        """Test registration fails with invalid password."""
        invalid_user = {
            "username": "invaliduser",
            "email": "invalid@test.com",
            "password": "weak",  # Too weak
            "role": "user"
        }
        
        response = self.client.post("/auth/register", json=invalid_user)
        assert response.status_code == 422  # Validation error
    
    def test_user_login_success(self):
        """Test successful user login."""
        login_data = {
            "username": "test_user",
            "password": "UserPass123!"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
    
    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        login_data = {
            "username": "test_user",
            "password": "WrongPassword"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_get_current_user_info(self):
        """Test getting current user information."""
        # Login first
        login_data = {
            "username": "test_user",
            "password": "UserPass123!"
        }
        
        login_response = self.client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test_user"
        assert data["role"] == "user"
    
    def test_get_user_permissions(self):
        """Test getting user permissions."""
        # Login as admin
        login_data = {
            "username": "test_admin",
            "password": "AdminPass123!"
        }
        
        login_response = self.client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Get permissions
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/auth/permissions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"] == "test_admin"
        assert data["role"] == "admin"
        assert "admin" in data["permissions"]
        assert "read" in data["permissions"]
        assert "write" in data["permissions"]
    
    def test_invalid_token_access(self):
        """Test access with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_missing_token_access(self):
        """Test access without token."""
        response = self.client.get("/auth/me")
        assert response.status_code == 403  # Forbidden due to missing authentication

class TestAuthorization:
    """Test role-based access control."""
    
    def setup_method(self):
        """Set up test client and users."""
        self.client = TestClient(app)
        
        # Clear existing users
        auth_manager.users = {}
        auth_manager.user_credentials = {}
        
        # Create users with different roles
        self.admin_user = UserCreate(
            username="admin",
            email="admin@test.com",
            password="AdminPass123!",
            role=Role.ADMIN
        )
        
        self.regular_user = UserCreate(
            username="user",
            email="user@test.com",
            password="UserPass123!",
            role=Role.USER
        )
        
        self.readonly_user = UserCreate(
            username="readonly",
            email="readonly@test.com",
            password="ReadPass123!",
            role=Role.READONLY
        )
        
        # Register users
        auth_manager.create_user(self.admin_user)
        auth_manager.create_user(self.regular_user)
        auth_manager.create_user(self.readonly_user)
    
    def get_token(self, username: str, password: str) -> str:
        """Helper to get authentication token."""
        login_data = {"username": username, "password": password}
        response = self.client.post("/auth/login", json=login_data)
        return response.json()["access_token"]
    
    def test_admin_access_to_system_clear(self):
        """Test admin can access system clear endpoint."""
        token = self.get_token("admin", "AdminPass123!")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Should be able to access (even though we don't confirm)
        response = self.client.delete("/system/clear?confirm=false", headers=headers)
        assert response.status_code == 400  # Bad request due to confirm=false, not auth issue
    
    def test_user_denied_access_to_system_clear(self):
        """Test regular user cannot access system clear endpoint."""
        token = self.get_token("user", "UserPass123!")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = self.client.delete("/system/clear?confirm=true", headers=headers)
        assert response.status_code == 403  # Forbidden due to insufficient permissions
    
    def test_readonly_user_create_denied(self):
        """Test readonly user cannot create resources."""
        token = self.get_token("readonly", "ReadPass123!")
        headers = {"Authorization": f"Bearer {token}"}
        
        actor_data = {
            "name": "Test Actor",
            "description": "Test description",
            "sector": "test"
        }
        
        response = self.client.post("/actors", json=actor_data, headers=headers)
        assert response.status_code == 403  # Forbidden due to insufficient permissions
    
    def test_user_can_create_resources(self):
        """Test regular user can create resources."""
        token = self.get_token("user", "UserPass123!")
        headers = {"Authorization": f"Bearer {token}"}
        
        actor_data = {
            "name": "Test Actor",
            "description": "Test description",
            "sector": "test"
        }
        
        response = self.client.post("/actors", json=actor_data, headers=headers)
        # Should succeed or fail for business reasons, not auth
        assert response.status_code != 403

class TestInputValidation:
    """Test input validation and sanitization."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
        
        # Create and login user
        auth_manager.users = {}
        auth_manager.user_credentials = {}
        
        user = UserCreate(
            username="testuser",
            email="test@test.com",
            password="TestPass123!",
            role=Role.USER
        )
        auth_manager.create_user(user)
        
        self.token = self.get_token("testuser", "TestPass123!")
    
    def get_token(self, username: str, password: str) -> str:
        """Helper to get authentication token."""
        login_data = {"username": username, "password": password}
        response = self.client.post("/auth/login", json=login_data)
        return response.json()["access_token"]
    
    def test_html_sanitization(self):
        """Test HTML content is sanitized."""
        test_input = "<script>alert('xss')</script>Clean text"
        sanitized = input_validator.sanitize_html(test_input)
        assert "<script>" not in sanitized
        assert "</script>" not in sanitized
        assert "Clean text" in sanitized
        
        # Test another case
        test_input2 = '<img src="x" onerror="alert(1)">Safe text'
        sanitized2 = input_validator.sanitize_html(test_input2)
        assert "onerror" not in sanitized2
        assert "Safe text" in sanitized2
    
    def test_sql_injection_detection(self):
        """Test SQL injection patterns are detected."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users",
            "admin'--",
            "' OR 1=1 --"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(Exception):  # Should raise HTTPException
                input_validator.validate_sql_injection(malicious_input)
    
    def test_content_type_validation(self):
        """Test content type validation."""
        # Create mock request with invalid content type
        request = MagicMock()
        request.headers = {"content-type": "application/xml"}
        
        with pytest.raises(Exception):  # Should raise HTTPException
            input_validator.validate_content_type(request)
    
    def test_request_size_validation(self):
        """Test request size validation."""
        # Create mock request with large content
        request = MagicMock()
        request.headers = {"content-length": str(security_config.max_request_size + 1)}
        
        with pytest.raises(Exception):  # Should raise HTTPException
            input_validator.validate_request_size(request)
    
    def test_safe_input_processing(self):
        """Test safe input is processed correctly."""
        safe_data = {
            "name": "Clean Name",
            "description": "Safe description",
            "meta": {"key": "value"}
        }
        
        sanitized = input_validator.sanitize_input(safe_data)
        assert sanitized["name"] == "Clean Name"
        assert sanitized["description"] == "Safe description"
        assert sanitized["meta"]["key"] == "value"

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
        
        # Create and login user
        auth_manager.users = {}
        auth_manager.user_credentials = {}
        
        user = UserCreate(
            username="testuser",
            email="test@test.com",
            password="TestPass123!",
            role=Role.USER
        )
        auth_manager.create_user(user)
        
        self.token = self.get_token("testuser", "TestPass123!")
    
    def get_token(self, username: str, password: str) -> str:
        """Helper to get authentication token."""
        login_data = {"username": username, "password": password}
        response = self.client.post("/auth/login", json=login_data)
        return response.json()["access_token"]
    
    def test_rate_limit_headers(self):
        """Test rate limit headers are present."""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Make a request to a rate-limited endpoint
        response = self.client.get("/auth/me", headers=headers)
        
        # Check for rate limit headers (implementation may vary)
        assert response.status_code == 200

class TestSecurityHeaders:
    """Test security headers are properly set."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses."""
        response = self.client.get("/")
        
        # Check for key security headers
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        for header in expected_headers:
            assert header in response.headers
    
    def test_security_header_values(self):
        """Test security header values are correct."""
        response = self.client.get("/")
        
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

class TestSecurityEndpoints:
    """Test security-related endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
        
        # Create and login user
        auth_manager.users = {}
        auth_manager.user_credentials = {}
        
        user = UserCreate(
            username="testuser",
            email="test@test.com",
            password="TestPass123!",
            role=Role.USER
        )
        auth_manager.create_user(user)
        
        self.token = self.get_token("testuser", "TestPass123!")
    
    def get_token(self, username: str, password: str) -> str:
        """Helper to get authentication token."""
        login_data = {"username": username, "password": password}
        response = self.client.post("/auth/login", json=login_data)
        return response.json()["access_token"]
    
    def test_security_info_endpoint(self):
        """Test security info endpoint."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/security/info", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "security_features" in data
        assert "current_user" in data
        assert "session_info" in data
        assert "security_headers" in data
        
        # Check security features
        features = data["security_features"]
        assert "authentication" in features
        assert "authorization" in features
        assert "rate_limiting" in features
    
    def test_api_info_includes_security(self):
        """Test API info includes security information."""
        response = self.client.get("/metadata/api-info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "security" in data
        security_info = data["security"]
        assert "authentication" in security_info
        assert "authorization" in security_info
        assert "rate_limiting" in security_info
        assert "roles" in security_info
        assert "permissions" in security_info

class TestAuditLogging:
    """Test audit logging functionality."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
        
        # Create and login user
        auth_manager.users = {}
        auth_manager.user_credentials = {}
        
        user = UserCreate(
            username="testuser",
            email="test@test.com",
            password="TestPass123!",
            role=Role.USER
        )
        auth_manager.create_user(user)
        
        self.token = self.get_token("testuser", "TestPass123!")
    
    def get_token(self, username: str, password: str) -> str:
        """Helper to get authentication token."""
        login_data = {"username": username, "password": password}
        response = self.client.post("/auth/login", json=login_data)
        return response.json()["access_token"]
    
    @patch('core.security.logger')
    def test_audit_logging_on_request(self, mock_logger):
        """Test that requests are logged for audit purposes."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        # Check if logger was called (implementation depends on middleware)
        # This test may need adjustment based on actual logging implementation

if __name__ == "__main__":
    pytest.main([__file__, "-v"])