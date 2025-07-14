# Comprehensive Logging and Monitoring System

This document describes the comprehensive logging and monitoring system implemented for the SFM (Social Fabric Matrix) service.

## Overview

The monitoring system provides:
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Kubernetes-compatible health endpoints
- **Metrics Collection**: Prometheus metrics for monitoring
- **Request Tracking**: Complete request/response monitoring
- **Error Tracking**: Comprehensive error reporting
- **Observability**: Distributed tracing support

## Components

### 1. Structured Logging (`core/logging_config.py`)

The structured logging system provides:
- JSON-formatted log output
- Correlation ID tracking across requests
- Context-aware logging with operation tracking
- Integration with existing audit logging
- Performance metrics integration

```python
from core.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Operation completed", user_id="123", duration=0.5)
```

### 2. Health Checking (`core/health_checker.py`)

The health checking system provides:
- System resource monitoring
- Database connection health
- Redis cache health
- Service readiness validation
- Kubernetes-compatible probes

Available health checks:
- System resources (CPU, memory, disk)
- Database connectivity
- Redis connectivity
- Service readiness

### 3. Metrics Collection (`core/metrics.py`)

The metrics system provides:
- Prometheus metrics export
- Request/response metrics
- Business logic metrics
- Performance counters
- Custom metric collectors

Key metrics:
- `sfm_requests_total` - Total HTTP requests
- `sfm_request_duration_seconds` - Request duration
- `sfm_entities_created_total` - Entities created
- `sfm_queries_executed_total` - Queries executed
- `sfm_system_errors_total` - System errors

### 4. Monitoring Middleware (`core/monitoring_middleware.py`)

The middleware provides:
- Request/response logging
- Correlation ID propagation
- Performance monitoring
- Error tracking
- Configurable monitoring levels

### 5. Configuration System (`config/monitoring.py`)

The configuration system provides:
- Environment-specific settings
- Alert rules and thresholds
- Comprehensive configuration management
- Environment variable overrides

## API Endpoints

### Health Check Endpoints

- **`GET /health/`** - Overall health check
- **`GET /health/live`** - Liveness probe (for Kubernetes)
- **`GET /health/ready`** - Readiness probe (for Kubernetes)
- **`GET /health/startup`** - Startup probe (for Kubernetes)
- **`GET /health/detailed`** - Detailed health status with metrics

### Metrics Endpoints

- **`GET /metrics/`** - Prometheus metrics (text format)
- **`GET /metrics/performance`** - Performance metrics (JSON format)

## Usage Examples

### Basic Health Check

```bash
curl http://localhost:8000/health/
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": [
    {
      "name": "system_resources",
      "status": "healthy",
      "message": "System resources normal",
      "duration": 0.001
    }
  ]
}
```

### Prometheus Metrics

```bash
curl http://localhost:8000/metrics/
```

Response:
```
# HELP sfm_requests_total Total HTTP requests
# TYPE sfm_requests_total counter
sfm_requests_total{method="GET",endpoint="/health/",status="200"} 5.0

# HELP sfm_request_duration_seconds HTTP request duration
# TYPE sfm_request_duration_seconds histogram
sfm_request_duration_seconds_bucket{method="GET",endpoint="/health/",le="0.005"} 5.0
```

### Correlation ID Tracking

```bash
curl -H "X-Correlation-ID: my-trace-id" http://localhost:8000/health/
```

The correlation ID will be:
- Included in all log entries
- Returned in the response headers
- Used for request tracing

## Configuration

### Environment Variables

- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_FORMAT` - Log format (json, text)
- `METRICS_ENABLED` - Enable metrics collection (true/false)
- `METRICS_PORT` - Metrics export port (default: 9090)
- `HEALTH_CHECK_ENABLED` - Enable health checks (true/false)
- `TRACING_ENABLED` - Enable distributed tracing (true/false)
- `TRACING_SAMPLE_RATE` - Tracing sample rate (0.0-1.0)

### Configuration Files

The system supports environment-specific configurations:

```python
from config.monitoring import get_monitoring_config

# Get configuration for current environment
config = get_monitoring_config()

# Get configuration for specific environment
prod_config = get_monitoring_config("production")
```

## Development vs Production

### Development Configuration
- DEBUG log level
- Text log format
- Higher tracing sample rate
- More detailed logging

### Production Configuration
- INFO log level
- JSON log format
- Lower tracing sample rate
- Optimized for performance

## Kubernetes Integration

The health check endpoints are designed for Kubernetes deployment:

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: sfm-service
    image: sfm-service:latest
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 5
    startupProbe:
      httpGet:
        path: /health/startup
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 30
```

## Monitoring Stack Integration

The system integrates with standard monitoring tools:

### Prometheus
- Scrapes `/metrics/` endpoint
- Collects application and system metrics
- Supports custom metrics

### Grafana
- Visualizes Prometheus metrics
- Pre-configured dashboards available
- Real-time monitoring

### AlertManager
- Processes alerts from Prometheus
- Configurable notification channels
- Escalation policies

### Jaeger (Optional)
- Distributed tracing support
- Request flow visualization
- Performance analysis

## Testing

Run the monitoring system tests:

```bash
python -m pytest tests/test_monitoring_system.py -v
```

Run the demo script:

```bash
python demo_monitoring.py
```

## Performance Impact

The monitoring system is designed for minimal performance impact:
- Asynchronous logging
- Efficient metrics collection
- Configurable monitoring levels
- Optional components

## Security Considerations

- Correlation IDs are generated securely
- No sensitive data in logs
- Configurable log levels
- Health check endpoints are safe to expose

## Future Enhancements

- Distributed tracing integration
- Custom dashboard templates
- Advanced alerting rules
- Log aggregation integration
- Performance profiling

## Troubleshooting

### Common Issues

1. **Health checks returning "unknown"**
   - Check if psutil is installed for system monitoring
   - Verify service dependencies are available

2. **Metrics not appearing**
   - Ensure Prometheus client is installed
   - Check metrics endpoint is accessible
   - Verify configuration settings

3. **Correlation IDs not working**
   - Check middleware is properly configured
   - Verify header names match expectations
   - Ensure logging is configured correctly

### Debugging

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
```

Check health status:
```bash
curl http://localhost:8000/health/detailed
```

View metrics:
```bash
curl http://localhost:8000/metrics/performance
```

## Support

For questions or issues with the monitoring system:
1. Check the logs for error messages
2. Review the configuration settings
3. Run the test suite to verify functionality
4. Use the demo script to test endpoints