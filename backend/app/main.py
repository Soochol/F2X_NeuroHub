"""
F2X NeuroHub MES API - FastAPI Application Entry Point.

Manufacturing Execution System (MES) for F2X NeuroHub with:
    - 8 manufacturing processes tracking
    - LOT and serial number management
    - Process data collection with JSONB flexibility
    - Comprehensive audit logging
    - Real-time analytics
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

# Import routers
from app.api.v1 import (
    auth,
    analytics,
    dashboard,
    product_models,
    processes,
    users,
    lots,
    serials,
    process_data,
    audit_logs,
    alerts,
    production_lines,
    equipment,
)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Manufacturing Execution System API for F2X NeuroHub",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "F2X NeuroHub MES API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_PREFIX}/dashboard", tags=["Dashboard"])
app.include_router(product_models.router, prefix=settings.API_V1_PREFIX, tags=["Product Models"])
app.include_router(processes.router, prefix=settings.API_V1_PREFIX, tags=["Processes"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["Users"])
app.include_router(lots.router, prefix=settings.API_V1_PREFIX, tags=["LOTs"])
app.include_router(serials.router, prefix=settings.API_V1_PREFIX, tags=["Serials"])
app.include_router(process_data.router, prefix=settings.API_V1_PREFIX, tags=["Process Data"])
app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX, tags=["Audit Logs"])
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX, tags=["Alerts"])
app.include_router(production_lines.router, prefix=settings.API_V1_PREFIX, tags=["Production Lines"])
app.include_router(equipment.router, prefix=settings.API_V1_PREFIX, tags=["Equipment"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
