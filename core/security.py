"""
Security module for API Layer Security Hardening.

This module provides comprehensive security features including:
- JWT authentication and authorization
- Role-based access control (RBAC)
- Input validation and sanitization
- Security headers
- Rate limiting enhancement
- Audit logging
"""

import logging
import secrets
from typing import Optional, Dict, Any, List, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import hashlib
import bleach
import re
from pathlib import Path

from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# User roles and permissions
class Role(str, Enum):
    """User roles for RBAC system."""
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"
    READONLY = "readonly"

class Permission(str, Enum):
    """Permissions for different operations."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    ANALYTICS = "analytics"

# Role-permission mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN, Permission.ANALYTICS},
    Role.ANALYST: {Permission.READ, Permission.ANALYTICS},
    Role.USER: {Permission.READ, Permission.WRITE},
    Role.READONLY: {Permission.READ}
}

@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = SECRET_KEY
    algorithm: str = ALGORITHM
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire_days: int = REFRESH_TOKEN_EXPIRE_DAYS
    enable_rate_limiting: bool = True
    enable_audit_logging: bool = True
    enable_input_validation: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    allowed_content_types: List[str] = None
    
    def __post_init__(self):
        if self.allowed_content_types is None:
            self.allowed_content_types = [
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data"
            ]

# Pydantic models for authentication
class UserCreate(BaseModel):
    """User creation model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    role: Role = Role.USER
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Username can only contain alphanumeric characters, dots, hyphens, and underscores')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str

class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    role: Optional[Role] = None
    permissions: List[Permission] = []

class User(BaseModel):
    """User model."""
    username: str
    email: str
    role: Role
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class SecurityMiddleware:
    """Security middleware for FastAPI."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.security = HTTPBearer()
        
    async def __call__(self, request: Request, call_next):
        """Process request through security middleware."""
        # Add security headers
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add audit logging
        if self.config.enable_audit_logging:
            await self._log_request(request, response)
        
        return response
    
    async def _log_request(self, request: Request, response):
        """Log request for audit purposes."""
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "status_code": response.status_code,
            "response_size": response.headers.get("content-length", 0)
        }
        
        # Add user information if available
        if hasattr(request.state, 'user'):
            audit_data["user"] = request.state.user.username
            audit_data["role"] = request.state.user.role.value
        
        logger.info("Security audit", extra=audit_data)

class AuthenticationManager:
    """Handles authentication and authorization."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.users: Dict[str, User] = {}  # In-memory user store (replace with database)
        self.user_credentials: Dict[str, str] = {}  # username -> hashed_password
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        if user_data.username in self.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Hash password
        hashed_password = self.get_password_hash(user_data.password)
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            role=user_data.role
        )
        
        # Store user and credentials
        self.users[user_data.username] = user
        self.user_credentials[user_data.username] = hashed_password
        
        logger.info(f"User created: {user_data.username}")
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        if username not in self.users:
            return None
        
        user = self.users[username]
        if not user.is_active:
            return None
        
        if not self.verify_password(password, self.user_credentials[username]):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        logger.info(f"User authenticated: {username}")
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Get user to check permissions
            user = self.users.get(username)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            permissions = list(ROLE_PERMISSIONS.get(user.role, set()))
            token_data = TokenData(username=username, role=user.role, permissions=permissions)
            return token_data
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
        """Get current authenticated user."""
        token_data = self.verify_token(credentials.credentials)
        user = self.users.get(token_data.username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission."""
        def permission_checker(user: User = Depends(self.get_current_user)):
            user_permissions = ROLE_PERMISSIONS.get(user.role, set())
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission.value}' required"
                )
            return user
        return permission_checker
    
    def require_role(self, role: Role):
        """Decorator to require specific role."""
        def role_checker(user: User = Depends(self.get_current_user)):
            if user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role.value}' required"
                )
            return user
        return role_checker

class InputValidator:
    """Input validation and sanitization."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def sanitize_html(self, text: str) -> str:
        """Sanitize HTML content."""
        if not isinstance(text, str):
            return text
        
        # Remove potentially harmful HTML tags and attributes
        # Allow no tags at all and strip everything
        cleaned = bleach.clean(text, tags=[], attributes={}, strip=True)
        
        # Additional cleaning for script content using bleach
        cleaned = bleach.clean(cleaned, tags=[], attributes={}, strip=True)
        
        return cleaned
        
        return cleaned
    
    def validate_content_type(self, request: Request):
        """Validate request content type."""
        if not self.config.enable_input_validation:
            return
        
        content_type = request.headers.get("content-type", "").split(";")[0].strip()
        if content_type and content_type not in self.config.allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported content type: {content_type}"
            )
    
    def validate_request_size(self, request: Request):
        """Validate request size."""
        if not self.config.enable_input_validation:
            return
        
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.config.max_request_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request size too large: {size} bytes (max: {self.config.max_request_size})"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid content-length header"
                )
    
    def validate_sql_injection(self, text: str) -> str:
        """Basic SQL injection protection."""
        if not isinstance(text, str):
            return text
        
        # Common SQL injection patterns
        sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bupdate\b.*\bset\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\bexec\b.*\b\()",
            r"(\bscript\b.*\>)",
            r"(\';.*--)",
            r"(\bor\b.*\b=\b.*\bor\b)",
            r"(\band\b.*\b=\b.*\band\b)",
            # Additional patterns to catch more injection attempts
            r"(\bor\b.*\b=\b.*\b=\b)",  # OR 1=1
            r"(\bor\b.*\b'.*'.*\b=\b.*\b'.*')",  # OR '1'='1'
            r"(\bor\b.*\b1\b.*\b=\b.*\b1\b)",  # OR 1=1
            r"(.*'.*--)",  # admin'--
            r"(\bor\b.*\b=\b.*--)",  # OR 1=1 --
            r"('.*\bor\b.*'.*=.*')",  # 1' OR '1'='1' pattern
        ]
        
        text_lower = text.lower()
        for pattern in sql_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
        
        return text
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data recursively."""
        if isinstance(data, str):
            # Sanitize HTML and check for SQL injection
            sanitized = self.sanitize_html(data)
            return self.validate_sql_injection(sanitized)
        elif isinstance(data, dict):
            return {key: self.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        else:
            return data

# Global security manager instances
security_config = SecurityConfig()
auth_manager = AuthenticationManager(security_config)
input_validator = InputValidator(security_config)
security_middleware = SecurityMiddleware(security_config)

# Dependency functions for FastAPI
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """FastAPI dependency to get current user."""
    return auth_manager.get_current_user(credentials)

def require_permission(permission: Permission):
    """FastAPI dependency to require permission."""
    return auth_manager.require_permission(permission)

def require_role(role: Role):
    """FastAPI dependency to require role."""
    return auth_manager.require_role(role)

def validate_input(request: Request):
    """FastAPI dependency to validate input."""
    input_validator.validate_content_type(request)
    input_validator.validate_request_size(request)
    return True

# Rate limiting decorators
def rate_limit(calls: int, period: str = "minute"):
    """Rate limiting decorator."""
    if period == "minute":
        limit_string = f"{calls}/minute"
    elif period == "hour":
        limit_string = f"{calls}/hour"
    elif period == "day":
        limit_string = f"{calls}/day"
    else:
        limit_string = f"{calls}/{period}"
    
    return limiter.limit(limit_string)

# Create default admin user
def create_default_admin():
    """Create default admin user if none exists."""
    admin_username = "admin"
    if admin_username not in auth_manager.users:
        admin_data = UserCreate(
            username=admin_username,
            email="admin@example.com",
            password="AdminPass123!",
            role=Role.ADMIN
        )
        auth_manager.create_user(admin_data)
        logger.info("Default admin user created")

# Initialize security system
create_default_admin()