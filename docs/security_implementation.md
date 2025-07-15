# API Layer Security Hardening Implementation

## Overview
This document summarizes the comprehensive security hardening implemented for the SFM Graph Service API layer.

## Security Features Implemented

### 1. Authentication & Authorization
- **JWT-based Authentication**: Implemented using `python-jose` with access and refresh tokens
- **Role-Based Access Control (RBAC)**: Four roles with hierarchical permissions
  - `ADMIN`: Full access to all operations
  - `ANALYST`: Read and analytics operations
  - `USER`: Read and write operations
  - `READONLY`: Read-only access
- **Password Security**: BCrypt hashing with salt for password storage
- **Token Management**: Configurable token expiration (30 min access, 7 days refresh)

### 2. Input Validation & Sanitization
- **HTML Sanitization**: Using `bleach` library to prevent XSS attacks
- **SQL Injection Protection**: Pattern detection and prevention
- **Content-Type Validation**: Whitelist of allowed content types
- **Request Size Limits**: Configurable maximum request size (10MB default)
- **Input Validation Decorators**: Comprehensive input validation middleware

### 3. Rate Limiting & DoS Protection
- **Per-Endpoint Rate Limiting**: Using `SlowAPI` library
  - Authentication: 10 requests/minute
  - Read operations: 60 requests/minute
  - Write operations: 20 requests/minute
  - Analytics: 10 requests/minute
- **Rate Limit Headers**: Proper HTTP headers for rate limit status
- **Graceful Error Handling**: Informative error messages with retry-after headers

### 4. Security Headers & CORS
- **Comprehensive Security Headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- **CORS Configuration**: Configurable CORS origins and methods

### 5. Audit Logging
- **Comprehensive Request Logging**: All requests/responses logged with correlation IDs
- **Security Event Logging**: Authentication, authorization, and security events
- **User Action Tracking**: All user actions logged with user context
- **Structured Logging**: JSON-formatted logs with metadata

## API Endpoints

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login with JWT token response
- `GET /auth/me` - Current user information
- `GET /auth/permissions` - User permissions based on role

### Security Information
- `GET /security/info` - Comprehensive security configuration and user context
- `GET /metadata/api-info` - API information including security details

### Protected Endpoints
All existing endpoints now require authentication and appropriate permissions:
- Entity operations (actors, institutions, policies, resources) require `WRITE` permission
- Read operations require `READ` permission
- Analytics operations require `ANALYTICS` permission
- System operations require `ADMIN` permission

## Security Configuration

### Dependencies Added
- `python-jose[cryptography]` - JWT token handling
- `python-multipart` - Form data parsing
- `passlib[bcrypt]` - Password hashing
- `slowapi` - Rate limiting
- `cryptography` - Cryptographic operations

### Configuration Options
- Token expiration times
- Rate limit settings
- Input validation rules
- Security headers configuration
- Audit logging settings

## Testing

### Comprehensive Test Suite
- **Authentication Tests**: Registration, login, token validation
- **Authorization Tests**: Role-based access control validation
- **Input Validation Tests**: XSS prevention, SQL injection protection
- **Rate Limiting Tests**: Rate limit enforcement
- **Security Headers Tests**: Proper header configuration
- **Audit Logging Tests**: Security event logging validation

### Test Coverage
- User registration and login flows
- Permission-based access control
- Input sanitization and validation
- Rate limiting functionality
- Security header presence and values
- Security endpoint functionality

## Security Best Practices Implemented

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Role-based permissions with minimal required access
3. **Input Validation**: Comprehensive sanitization and validation
4. **Secure Defaults**: Security-first configuration defaults
5. **Audit Trail**: Comprehensive logging for security monitoring
6. **Error Handling**: Secure error messages without information disclosure

## Usage Examples

### User Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "role": "user"
  }'
```

### User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "SecurePass123!"
  }'
```

### Authenticated Request
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Monitoring

### Key Metrics to Monitor
- Authentication failure rates
- Rate limit violations
- Input validation failures
- Unauthorized access attempts
- Security header compliance

### Audit Events
- User registration and login
- Permission denied events
- Rate limit exceeded events
- Input validation failures
- Security configuration changes

## Production Considerations

### Environment Variables
- `SECRET_KEY`: JWT signing key (should be environment-specific)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `RATE_LIMIT_*`: Rate limiting configuration
- `SECURITY_HEADERS_*`: Security header configuration

### Deployment Recommendations
1. Use strong, environment-specific JWT signing keys
2. Configure appropriate rate limits based on expected load
3. Set up security monitoring and alerting
4. Regularly review audit logs for security events
5. Consider implementing API key authentication for service-to-service communication

## Future Enhancements

### Phase 2 Recommendations
1. **Advanced RBAC**: Fine-grained permission system
2. **API Key Management**: Service-to-service authentication
3. **OAuth2 Integration**: Third-party authentication providers
4. **Advanced Threat Detection**: Machine learning-based security monitoring
5. **Security Scanning**: Automated vulnerability scanning
6. **Multi-Factor Authentication**: Enhanced user authentication

## Compliance

This implementation addresses common security frameworks and standards:
- **OWASP Top 10**: Protection against common web vulnerabilities
- **NIST Cybersecurity Framework**: Security controls and monitoring
- **ISO 27001**: Information security management practices
- **SOC 2**: Security and availability controls

The security hardening provides a solid foundation for production deployment while maintaining the flexibility to extend and customize security controls as needed.