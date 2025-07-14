"""
Tests for the monitoring and health check system.
"""

import pytest
from fastapi.testclient import TestClient
from api.sfm_api import app

client = TestClient(app)


def test_health_check_endpoint():
    """Test the main health check endpoint."""
    response = client.get("/health/")
    assert response.status_code in [200, 503]  # Should return 200 for healthy or 503 for unhealthy
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "checks" in data
    assert data["status"] in ["healthy", "unhealthy", "degraded", "unknown"]


def test_liveness_probe():
    """Test the liveness probe endpoint."""
    response = client.get("/health/live")
    assert response.status_code in [200, 503]
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] in ["healthy", "unhealthy"]


def test_readiness_probe():
    """Test the readiness probe endpoint."""
    response = client.get("/health/ready")
    assert response.status_code in [200, 503]
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] in ["ready", "not_ready"]


def test_startup_probe():
    """Test the startup probe endpoint."""
    response = client.get("/health/startup")
    assert response.status_code in [200, 503]
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] in ["started", "starting"]


def test_detailed_health_status():
    """Test the detailed health status endpoint."""
    response = client.get("/health/detailed")
    assert response.status_code in [200, 503]
    
    data = response.json()
    assert "health" in data
    assert "performance" in data
    assert "timestamp" in data


def test_metrics_endpoint():
    """Test the Prometheus metrics endpoint."""
    response = client.get("/metrics/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    # Check for some expected metrics
    content = response.text
    assert "# HELP" in content or "# No metrics available" in content


def test_performance_metrics_endpoint():
    """Test the performance metrics endpoint."""
    response = client.get("/metrics/performance")
    assert response.status_code == 200
    
    data = response.json()
    assert "performance" in data
    assert "timestamp" in data


def test_correlation_id_header():
    """Test that correlation ID is added to response headers."""
    response = client.get("/health/")
    assert "X-Correlation-ID" in response.headers
    assert len(response.headers["X-Correlation-ID"]) > 0


def test_request_with_correlation_id():
    """Test that existing correlation ID is preserved."""
    correlation_id = "test-correlation-id"
    response = client.get("/health/", headers={"X-Correlation-ID": correlation_id})
    
    # The response should have the same correlation ID
    assert response.headers["X-Correlation-ID"] == correlation_id


def test_error_handling_with_monitoring():
    """Test that error responses include monitoring headers."""
    # Make a request to a non-existent endpoint
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404
    
    # Should still have correlation ID
    assert "X-Correlation-ID" in response.headers


if __name__ == "__main__":
    # Run the tests
    test_health_check_endpoint()
    test_liveness_probe()
    test_readiness_probe()
    test_startup_probe()
    test_detailed_health_status()
    test_metrics_endpoint()
    test_performance_metrics_endpoint()
    test_correlation_id_header()
    test_request_with_correlation_id()
    test_error_handling_with_monitoring()
    print("All monitoring tests passed!")