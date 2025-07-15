"""
Monitoring Middleware for SFM Service

This module provides middleware for request monitoring, correlation ID tracking,
and performance metrics collection for FastAPI applications.

Features:
- Request/response logging with correlation IDs
- Performance metrics collection
- Error tracking and reporting
- Request tracing
- Health check integration
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
import json

from core.logging_config import get_logger, LoggingManager
from core.metrics import get_metrics_collector


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request monitoring and logging.

    This middleware:
    - Generates correlation IDs for each request
    - Logs request/response details
    - Collects performance metrics
    - Tracks errors and exceptions
    - Integrates with health checking
    """

    def __init__(self, app: ASGIApp, config: Dict[str, Any] = None):
        super().__init__(app)
        self.config = config or {}
        self.logger = get_logger("middleware.monitoring")
        self.metrics_collector = get_metrics_collector()
        self.logging_manager = LoggingManager(self.config.get('logging', {}))

        # Configuration options
        self.log_requests = self.config.get('log_requests', True)
        self.log_responses = self.config.get('log_responses', True)
        self.log_headers = self.config.get('log_headers', False)
        self.log_body = self.config.get('log_body', False)
        self.excluded_paths = set(
            self.config.get(
                'excluded_paths', [
                    '/health', '/metrics']))

        self.logger.info("Monitoring middleware initialized",
                         config=self.config)

    async def dispatch(
            self,
            request: Request,
            call_next: Callable) -> Response:
        """Process request and response with monitoring."""
        # Check for existing correlation ID in headers
        correlation_id = request.headers.get('x-correlation-id')
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Add correlation ID to request state
        request.state.correlation_id = correlation_id

        # Skip monitoring for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Create request logger with correlation ID
        request_logger = self.logger.with_context(
            correlation_id=correlation_id,
            request_id=correlation_id,
            operation="http_request"
        )

        # Record request start
        start_time = time.time()

        # Log request details
        if self.log_requests:
            await self._log_request(request, request_logger)

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response details
            if self.log_responses:
                await self._log_response(request, response, duration, request_logger)

            # Record metrics
            self._record_metrics(request, response, duration)

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            request_logger.error(f"Request processing failed: {str(e)}",
                                 error=str(e),
                                 error_type=type(e).__name__,
                                 duration=duration,
                                 method=request.method,
                                 url=str(request.url))

            # Record error metrics
            self.metrics_collector.record_error(type(e).__name__, str(e))
            self.metrics_collector.record_request(
                request.method,
                request.url.path,
                500,
                duration
            )

            # Re-raise the exception
            raise

    async def _log_request(self, request: Request, logger):
        """Log request details."""
        # Prepare request data
        request_data = {
            'method': request.method,
            'url': str(request.url),
            'path': request.url.path,
            'query_params': dict(request.query_params),
            'client_host': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent'),
        }

        # Add headers if configured
        if self.log_headers:
            request_data['headers'] = dict(request.headers)

        # Add body if configured (for non-GET requests)
        if self.log_body and request.method != 'GET':
            try:
                body = await request.body()
                if body:
                    # Try to decode as JSON, fallback to string
                    try:
                        request_data['body'] = json.loads(body.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_data['body'] = body.decode(
                            'utf-8', errors='replace')
            except Exception as e:
                request_data['body_error'] = str(e)

        logger.info("Request received", **request_data)

    async def _log_response(
            self,
            request: Request,
            response: Response,
            duration: float,
            logger):
        """Log response details."""
        # Prepare response data
        response_data = {
            'status_code': response.status_code,
            'duration': duration,
            'content_length': response.headers.get('content-length'),
            'content_type': response.headers.get('content-type'),
        }

        # Add headers if configured
        if self.log_headers:
            response_data['headers'] = dict(response.headers)

        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = 'error'
        elif response.status_code >= 400:
            log_level = 'warning'
        else:
            log_level = 'info'

        getattr(logger, log_level)(
            f"Request completed - {response.status_code}",
            **response_data
        )

    def _record_metrics(
            self,
            request: Request,
            response: Response,
            duration: float):
        """Record request metrics."""
        self.metrics_collector.record_request(
            request.method,
            request.url.path,
            response.status_code,
            duration
        )


class CorrelationIdMiddleware:
    """
    Lightweight middleware for correlation ID handling.

    This middleware ensures that all requests have a correlation ID
    that can be used for tracing across services.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope, receive, send):
        """ASGI application."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Generate or extract correlation ID
        correlation_id = None

        # Check for existing correlation ID in headers
        for header_name, header_value in scope.get("headers", []):
            if header_name.lower() == b"x-correlation-id":
                correlation_id = header_value.decode("utf-8")
                break

        # Generate new correlation ID if not found
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Add correlation ID to scope
        scope["correlation_id"] = correlation_id

        # Continue with the request
        await self.app(scope, receive, send)


class MetricsMiddleware:
    """
    Lightweight middleware for metrics collection only.

    This middleware focuses solely on collecting metrics without
    extensive logging, useful for high-performance scenarios.
    """

    def __init__(self, app: ASGIApp):
        self.app = app
        self.metrics_collector = get_metrics_collector()

    async def __call__(self, scope, receive, send):
        """ASGI application."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request information
        method = scope["method"]
        path = scope["path"]

        # Record start time
        start_time = time.time()

        # Create a custom send function to capture response
        status_code = 500  # Default to error

        async def send_with_metrics(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            # Process request
            await self.app(scope, receive, send_with_metrics)

        except Exception as e:
            # Record error
            self.metrics_collector.record_error(type(e).__name__, str(e))
            raise

        finally:
            # Record metrics
            duration = time.time() - start_time
            self.metrics_collector.record_request(
                method, path, status_code, duration)


class ErrorTrackingMiddleware:
    """
    Middleware for error tracking and reporting.

    This middleware captures and reports errors with context
    for better debugging and monitoring.
    """

    def __init__(self, app: ASGIApp, config: Dict[str, Any] = None):
        self.app = app
        self.config = config or {}
        self.logger = get_logger("middleware.error_tracking")
        self.metrics_collector = get_metrics_collector()

        # Configuration
        self.capture_stack_traces = self.config.get(
            'capture_stack_traces', True)
        self.log_error_details = self.config.get('log_error_details', True)

    async def __call__(self, scope, receive, send):
        """ASGI application."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as e:
            # Extract request information
            method = scope.get("method", "UNKNOWN")
            path = scope.get("path", "UNKNOWN")
            correlation_id = scope.get("correlation_id", "UNKNOWN")

            # Log error with context
            if self.log_error_details:
                error_context = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'method': method,
                    'path': path,
                    'correlation_id': correlation_id,
                }

                if self.capture_stack_traces:
                    import traceback
                    error_context['stack_trace'] = traceback.format_exc()

                self.logger.error("Unhandled exception in request processing",
                                  **error_context)

            # Record error metrics
            self.metrics_collector.record_error(type(e).__name__, str(e))

            # Re-raise the exception
            raise


def create_monitoring_middleware(
        app: ASGIApp, config: Dict[str, Any] = None) -> ASGIApp:
    """
    Create and configure monitoring middleware for the application.

    Args:
        app: ASGI application
        config: Monitoring configuration

    Returns:
        Configured application with monitoring middleware
    """
    config = config or {}

    # Add correlation ID middleware
    if config.get('correlation_id_enabled', True):
        app = CorrelationIdMiddleware(app)

    # Add error tracking middleware
    if config.get('error_tracking_enabled', True):
        app = ErrorTrackingMiddleware(app, config.get('error_tracking', {}))

    # Add metrics middleware
    if config.get('metrics_enabled', True):
        if config.get('lightweight_metrics', False):
            app = MetricsMiddleware(app)
        else:
            app = MonitoringMiddleware(app, config.get('monitoring', {}))

    return app
