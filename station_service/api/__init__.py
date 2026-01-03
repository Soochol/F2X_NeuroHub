"""
Station Service API Package.

This module provides the FastAPI application factory and router registration
for the Station Service REST API.

Usage:
    from station_service.api import create_app

    app = create_app()
"""

from fastapi import FastAPI

from station_service.api.routes import (
    batches_router,
    deploy_router,
    logs_router,
    manual_router,
    manual_sequence_router,
    reports_router,
    results_router,
    sequences_router,
    sequence_upload_router,
    simulation_router,
    system_router,
)


def create_app(
    title: str = "Station Service API",
    description: str = "REST API for Station Service - Test Sequence Execution and Management",
    version: str = "1.0.0",
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    This factory function creates a FastAPI application with all routers
    registered and configured.

    Args:
        title: API title for OpenAPI documentation
        description: API description for OpenAPI documentation
        version: API version string

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Register routers
    # NOTE: sequence_upload_router MUST come before sequences_router
    # because both use prefix "/api/sequences" and sequence_upload_router
    # has more specific routes like /{name}/download that would otherwise
    # be matched by sequences_router's /{sequence_name} pattern
    app.include_router(system_router)
    app.include_router(batches_router)
    app.include_router(sequence_upload_router)  # Must come before sequences_router
    app.include_router(sequences_router)
    app.include_router(deploy_router)
    app.include_router(results_router)
    app.include_router(logs_router)
    app.include_router(manual_router)
    app.include_router(simulation_router)
    app.include_router(manual_sequence_router)
    app.include_router(reports_router)

    return app


__all__ = [
    "create_app",
    "batches_router",
    "deploy_router",
    "logs_router",
    "manual_router",
    "manual_sequence_router",
    "reports_router",
    "results_router",
    "sequences_router",
    "sequence_upload_router",
    "simulation_router",
    "system_router",
]
