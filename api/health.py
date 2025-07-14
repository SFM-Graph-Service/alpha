"""
Health Check API Endpoints for SFM Service

This module provides HTTP endpoints for health checking, including
liveness, readiness, and startup probes for Kubernetes deployment.

Features:
- Health check endpoints
- Dependency monitoring
- Prometheus metrics endpoint
- System status reporting
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Dict, Any
import logging
from datetime import datetime

from core.health_checker import get_health_checker, HealthStatus
from core.metrics import get_metrics_collector
from core.logging_config import get_logger


# Create router for health endpoints
health_router = APIRouter(prefix="/health", tags=["health"])
metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])


@health_router.get("/", summary="Overall health check")
async def health_check():
    """
    Overall health check endpoint.
    
    Returns the health status of the application and all its dependencies.
    This endpoint is suitable for general health monitoring.
    """
    logger = get_logger("api.health")
    logger.info("Health check requested")
    
    try:
        checker = get_health_checker()
        health_summary = checker.check_all()
        
        # Determine HTTP status code
        status_code = 200
        if health_summary.overall_status == HealthStatus.UNHEALTHY:
            status_code = 503
        elif health_summary.overall_status == HealthStatus.DEGRADED:
            status_code = 200  # Still operational but with warnings
        
        response_data = health_summary.to_dict()
        
        logger.info("Health check completed", 
                   status=health_summary.overall_status.value,
                   checks_count=len(health_summary.checks))
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            },
            status_code=503
        )


@health_router.get("/live", summary="Liveness probe")
async def liveness_probe():
    """
    Liveness probe endpoint for Kubernetes.
    
    This endpoint checks if the application is alive and should be restarted
    if it fails. It performs minimal checks to avoid false positives.
    """
    logger = get_logger("api.health.liveness")
    logger.debug("Liveness probe requested")
    
    try:
        checker = get_health_checker()
        health_summary = checker.check_liveness()
        
        # For liveness, we're more lenient - only fail if truly unhealthy
        if health_summary.overall_status == HealthStatus.UNHEALTHY:
            return JSONResponse(
                content={
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Application is not alive"
                },
                status_code=503
            )
        
        return JSONResponse(
            content={
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Application is alive"
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error("Liveness probe failed", error=str(e))
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            },
            status_code=503
        )


@health_router.get("/ready", summary="Readiness probe")
async def readiness_probe():
    """
    Readiness probe endpoint for Kubernetes.
    
    This endpoint checks if the application is ready to serve traffic.
    It performs comprehensive checks including dependency validation.
    """
    logger = get_logger("api.health.readiness")
    logger.debug("Readiness probe requested")
    
    try:
        checker = get_health_checker()
        health_summary = checker.check_readiness()
        
        # For readiness, we're strict - fail if not fully healthy
        if health_summary.overall_status != HealthStatus.HEALTHY:
            return JSONResponse(
                content={
                    "status": "not_ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "checks": [check.to_dict() for check in health_summary.checks]
                },
                status_code=503
            )
        
        return JSONResponse(
            content={
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Application is ready to serve traffic"
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error("Readiness probe failed", error=str(e))
        return JSONResponse(
            content={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            },
            status_code=503
        )


@health_router.get("/startup", summary="Startup probe")
async def startup_probe():
    """
    Startup probe endpoint for Kubernetes.
    
    This endpoint checks if the application has started successfully.
    It's used during application startup to determine when the application
    is ready for liveness and readiness probes.
    """
    logger = get_logger("api.health.startup")
    logger.debug("Startup probe requested")
    
    try:
        checker = get_health_checker()
        health_summary = checker.check_startup()
        
        # For startup, we check if critical components are ready
        if health_summary.overall_status == HealthStatus.UNHEALTHY:
            return JSONResponse(
                content={
                    "status": "starting",
                    "timestamp": datetime.utcnow().isoformat(),
                    "checks": [check.to_dict() for check in health_summary.checks]
                },
                status_code=503
            )
        
        return JSONResponse(
            content={
                "status": "started",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Application has started successfully"
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error("Startup probe failed", error=str(e))
        return JSONResponse(
            content={
                "status": "starting",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            },
            status_code=503
        )


@health_router.get("/detailed", summary="Detailed health status")
async def detailed_health_status():
    """
    Detailed health status endpoint.
    
    Returns comprehensive health information including all check results,
    system metrics, and performance data.
    """
    logger = get_logger("api.health.detailed")
    logger.info("Detailed health status requested")
    
    try:
        checker = get_health_checker()
        health_summary = checker.check_all()
        
        # Get additional metrics
        metrics_collector = get_metrics_collector()
        performance_summary = metrics_collector.get_performance_summary()
        
        # Combine health and performance data
        detailed_status = {
            "health": health_summary.to_dict(),
            "performance": performance_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Determine HTTP status code
        status_code = 200
        if health_summary.overall_status == HealthStatus.UNHEALTHY:
            status_code = 503
        
        logger.info("Detailed health status completed",
                   status=health_summary.overall_status.value)
        
        return JSONResponse(
            content=detailed_status,
            status_code=status_code
        )
        
    except Exception as e:
        logger.error("Detailed health status failed", error=str(e))
        return JSONResponse(
            content={
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            },
            status_code=503
        )


@metrics_router.get("/", summary="Prometheus metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus format for scraping by monitoring systems.
    """
    logger = get_logger("api.metrics")
    logger.debug("Metrics requested")
    
    try:
        metrics_collector = get_metrics_collector()
        metrics_data = metrics_collector.get_prometheus_metrics()
        
        if not metrics_data:
            # If no Prometheus metrics available, return empty response
            metrics_data = "# No metrics available\n"
        
        return PlainTextResponse(
            content=metrics_data,
            media_type="text/plain"
        )
        
    except Exception as e:
        logger.error("Metrics request failed", error=str(e))
        return PlainTextResponse(
            content=f"# Error retrieving metrics: {str(e)}\n",
            media_type="text/plain",
            status_code=500
        )


@metrics_router.get("/performance", summary="Performance metrics")
async def get_performance_metrics():
    """
    Performance metrics endpoint.
    
    Returns performance metrics in JSON format.
    """
    logger = get_logger("api.metrics.performance")
    logger.debug("Performance metrics requested")
    
    try:
        metrics_collector = get_metrics_collector()
        performance_data = metrics_collector.get_performance_summary()
        
        return JSONResponse(
            content={
                "performance": performance_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error("Performance metrics request failed", error=str(e))
        return JSONResponse(
            content={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=500
        )


# Create combined router
def create_health_and_metrics_router() -> APIRouter:
    """Create a combined router with health and metrics endpoints."""
    combined_router = APIRouter()
    combined_router.include_router(health_router)
    combined_router.include_router(metrics_router)
    return combined_router


# Default router instance
router = create_health_and_metrics_router()