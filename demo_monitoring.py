#!/usr/bin/env python3
"""
Monitoring System Demo for SFM Service

This script demonstrates the comprehensive logging and monitoring system
implemented for the SFM service, including health checks, metrics,
and structured logging.
"""

import requests
import time
import json
from datetime import datetime


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def demo_health_endpoints():
    """Demonstrate health check endpoints."""
    print_section("HEALTH CHECK ENDPOINTS")
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        ("/health/", "Overall Health Check"),
        ("/health/live", "Liveness Probe"),
        ("/health/ready", "Readiness Probe"),
        ("/health/startup", "Startup Probe"),
        ("/health/detailed", "Detailed Health Status")
    ]
    
    for endpoint, description in endpoints:
        print(f"\n{description} ({endpoint}):")
        print("-" * 40)
        
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")


def demo_metrics_endpoints():
    """Demonstrate metrics endpoints."""
    print_section("METRICS ENDPOINTS")
    
    base_url = "http://localhost:8000"
    
    # Prometheus metrics
    print("\nPrometheus Metrics (/metrics/):")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/metrics/")
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print("Sample metrics:")
        lines = response.text.split('\n')[:20]
        for line in lines:
            if line.strip():
                print(f"  {line}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Performance metrics
    print("\nPerformance Metrics (/metrics/performance):")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/metrics/performance")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


def demo_correlation_id_tracking():
    """Demonstrate correlation ID tracking."""
    print_section("CORRELATION ID TRACKING")
    
    base_url = "http://localhost:8000"
    
    # Test with custom correlation ID
    correlation_id = f"demo-{int(time.time())}"
    headers = {"X-Correlation-ID": correlation_id}
    
    print(f"\nSending request with correlation ID: {correlation_id}")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/health/", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Correlation ID: {response.headers.get('X-Correlation-ID')}")
        print(f"Correlation ID preserved: {response.headers.get('X-Correlation-ID') == correlation_id}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with auto-generated correlation ID
    print(f"\nSending request without correlation ID:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/health/")
        print(f"Status Code: {response.status_code}")
        print(f"Generated Correlation ID: {response.headers.get('X-Correlation-ID')}")
    except Exception as e:
        print(f"Error: {e}")


def demo_error_tracking():
    """Demonstrate error tracking."""
    print_section("ERROR TRACKING")
    
    base_url = "http://localhost:8000"
    
    print("\nTesting error handling with monitoring:")
    print("-" * 40)
    
    # Test 404 error
    try:
        response = requests.get(f"{base_url}/non-existent-endpoint")
        print(f"Status Code: {response.status_code}")
        print(f"Correlation ID in error response: {response.headers.get('X-Correlation-ID')}")
    except Exception as e:
        print(f"Error: {e}")


def demo_request_monitoring():
    """Demonstrate request monitoring."""
    print_section("REQUEST MONITORING")
    
    base_url = "http://localhost:8000"
    
    print("\nMaking multiple requests to generate metrics:")
    print("-" * 40)
    
    # Make several requests
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/health/")
            print(f"Request {i+1}: Status {response.status_code}, Correlation ID: {response.headers.get('X-Correlation-ID')}")
        except Exception as e:
            print(f"Request {i+1}: Error - {e}")
    
    # Check updated metrics
    print("\nUpdated metrics after requests:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/metrics/")
        lines = response.text.split('\n')
        for line in lines:
            if 'sfm_requests_total' in line and 'health' in line:
                print(f"  {line}")
    except Exception as e:
        print(f"Error: {e}")


def demo_monitoring_configuration():
    """Demonstrate monitoring configuration."""
    print_section("MONITORING CONFIGURATION")
    
    print("\nDefault monitoring configuration:")
    print("-" * 40)
    
    # Show configuration structure
    config_info = {
        "logging": {
            "level": "INFO",
            "format": "json",
            "correlation_tracking": True
        },
        "metrics": {
            "enabled": True,
            "export_port": 9090,
            "prometheus_enabled": True
        },
        "health_check": {
            "enabled": True,
            "check_interval": 30,
            "timeout": 5
        },
        "middleware": {
            "correlation_id_enabled": True,
            "error_tracking_enabled": True,
            "metrics_enabled": True
        }
    }
    
    print(json.dumps(config_info, indent=2))


def main():
    """Main demo function."""
    print("SFM Service Monitoring System Demo")
    print(f"Started at: {datetime.now()}")
    print("\nThis demo shows the comprehensive monitoring system implemented for the SFM service.")
    print("Make sure the SFM service is running on localhost:8000 before running this demo.")
    
    # Check if service is running
    try:
        response = requests.get("http://localhost:8000/health/", timeout=5)
        print(f"\n✓ Service is running (Status: {response.status_code})")
    except Exception as e:
        print(f"\n✗ Service is not running: {e}")
        print("Please start the service with:")
        print("  python -c \"from api.sfm_api import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)\"")
        return
    
    # Run demonstrations
    demo_health_endpoints()
    demo_metrics_endpoints()
    demo_correlation_id_tracking()
    demo_error_tracking()
    demo_request_monitoring()
    demo_monitoring_configuration()
    
    print_section("DEMO COMPLETED")
    print("The monitoring system provides:")
    print("• Structured logging with correlation IDs")
    print("• Health check endpoints for Kubernetes")
    print("• Prometheus metrics for monitoring")
    print("• Request/response tracking")
    print("• Error tracking and reporting")
    print("• Configurable monitoring settings")
    print(f"\nDemo completed at: {datetime.now()}")


if __name__ == "__main__":
    main()