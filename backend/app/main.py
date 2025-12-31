"""
F2X NeuroHub MES API - FastAPI Application Entry Point.

Manufacturing Execution System (MES) for F2X NeuroHub with:
    - 8 manufacturing processes tracking
    - LOT and serial number management
    - Process data collection with JSONB flexibility
    - Comprehensive audit logging
    - Real-time analytics
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
import os
import uuid
from datetime import datetime

from app.config import settings
from app.core.exceptions import AppException
from app.schemas.error import StandardErrorResponse, ErrorDetail, ErrorCode
from app.core.errors import get_http_status_for_error_code
from app.database import SessionLocal, engine, Base
from app.models import User
from app.schemas import UserRole
from app.core.security import get_password_hash
from contextlib import asynccontextmanager


# Import routers
from app.api.v1 import (
    auth,
    analytics,
    dashboard,
    product_models,
    processes,
    process_operations,
    users,
    lots,
    wip_items,
    serials,
    process_data,
    audit_logs,
    alerts,
    production_lines,
    equipment,
    error_logs,
    printer_monitoring,
    async_operations,
    search,
    stations,
)

# Import middleware
from app.middleware import ErrorLoggingMiddleware, RateLimitMiddleware


# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Application Lifespan (Startup/Shutdown)
# ============================================================================
def init_default_admin():
    """
    Create default admin user if not exists.
    Called on application startup for fresh deployments.

    Environment variables:
        DEFAULT_ADMIN_USERNAME: Admin username (default: 'admin')
        DEFAULT_ADMIN_PASSWORD: Admin password (REQUIRED in production)
        DEFAULT_ADMIN_EMAIL: Admin email (default: 'admin@f2x.com')
    """
    # Read credentials from environment variables
    default_password = "admin123"  # Only used as fallback in DEBUG mode
    admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@f2x.com")

    # Validate password in production mode
    if not settings.DEBUG:
        if not admin_password:
            logger.error(
                "SECURITY ERROR: DEFAULT_ADMIN_PASSWORD environment variable is required in production mode. "
                "Set DEBUG=True for development or provide a secure password."
            )
            return
        if admin_password == default_password:
            logger.error(
                "SECURITY ERROR: Cannot use default password in production mode. "
                "Please set a secure DEFAULT_ADMIN_PASSWORD environment variable."
            )
            return

    # In DEBUG mode, allow fallback to default password with warning
    if not admin_password:
        if settings.DEBUG:
            admin_password = default_password
            logger.warning(
                "Using default admin password in DEBUG mode. "
                "Set DEFAULT_ADMIN_PASSWORD environment variable for production."
            )
        else:
            return  # Should not reach here due to check above, but safety fallback

    db = SessionLocal()
    try:
        # Check if any admin user exists
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_user:
            logger.info("No admin user found. Creating default admin...")
            new_admin = User(
                username=admin_username,
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            # Log creation without exposing actual password
            logger.info(
                f"Default admin created: username='{admin_username}', "
                f"email='{admin_email}', password=***SET_FROM_ENV***"
            )
        else:
            logger.info(f"Admin user exists: {admin_user.username}")
    except Exception as e:
        logger.error(f"Failed to initialize admin user: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info("Starting F2X NeuroHub MES API...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    init_default_admin()
    yield
    # Shutdown
    logger.info("Shutting down F2X NeuroHub MES API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Manufacturing Execution System API for F2X NeuroHub",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,  # POST 요청에서 trailing slash로 인한 307 리다이렉트 방지
)


# Configure CORS (from settings for environment-specific configuration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add Rate Limiting Middleware (before error logging)
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        default_limit=settings.RATE_LIMIT_DEFAULT_REQUESTS,
        default_window=settings.RATE_LIMIT_DEFAULT_WINDOW,
        enabled=settings.RATE_LIMIT_ENABLED,
    )

# Add Error Logging Middleware (after CORS for proper request handling)
app.add_middleware(ErrorLoggingMiddleware)


# ============================================================================
# Global Exception Handlers
# ============================================================================

def create_error_response(
    error_code: ErrorCode,
    message: str,
    request: Request,
    details: list[ErrorDetail] | None = None,
    trace_id: str | None = None,
) -> StandardErrorResponse:
    """
    표준 에러 응답 생성 헬퍼 함수

    Args:
        error_code: 에러 코드
        message: 에러 메시지
        request: FastAPI Request 객체
        details: 필드별 상세 에러
        trace_id: 추적 ID

    Returns:
        표준 에러 응답 객체
    """
    return StandardErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        timestamp=datetime.utcnow().isoformat(),
        path=str(request.url.path),
        trace_id=trace_id or str(uuid.uuid4()),
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    커스텀 애플리케이션 예외 처리

    AppException을 상속한 모든 예외를 표준 포맷으로 변환합니다.
    """
    logger.error(
        f"AppException: {exc.error_code} - {exc.message}",
        extra={"trace_id": exc.trace_id, "path": request.url.path},
    )

    error_response = create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        request=request,
        details=exc.details,
        trace_id=exc.trace_id,
    )

    http_status = get_http_status_for_error_code(exc.error_code)

    return JSONResponse(
        status_code=http_status,
        content=error_response.model_dump(exclude_none=True),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic 검증 에러 처리

    FastAPI의 요청 검증 실패를 표준 포맷으로 변환합니다.
    """
    # Pydantic 에러를 ErrorDetail 리스트로 변환
    details = [
        ErrorDetail(
            field=".".join(str(loc) for loc in err["loc"] if loc not in ("body", "query", "path")),
            message=err["msg"],
            code=err["type"],
        )
        for err in exc.errors()
    ]

    logger.warning(
        f"Validation error: {len(details)} field(s) failed",
        extra={"path": request.url.path, "details": [d.model_dump() for d in details]},
    )

    error_response = create_error_response(
        error_code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed",
        request=request,
        details=details,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(exclude_none=True),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    데이터베이스 무결성 제약 위반 처리

    SQLAlchemy IntegrityError를 분석하여 적절한 에러 코드로 변환합니다.
    """
    error_str = str(exc.orig).lower() if exc.orig else str(exc).lower()

    # 에러 타입 감지
    if "unique constraint" in error_str or "duplicate" in error_str:
        error_code = ErrorCode.DUPLICATE_RESOURCE
        message = "Resource already exists with the same unique identifier"
    elif "foreign key" in error_str or "violates foreign key constraint" in error_str:
        error_code = ErrorCode.CONSTRAINT_VIOLATION
        message = "Referenced resource does not exist"
    elif "not null constraint" in error_str or "violates not-null constraint" in error_str:
        error_code = ErrorCode.MISSING_REQUIRED_FIELD
        message = "Required field cannot be null"
    else:
        error_code = ErrorCode.CONSTRAINT_VIOLATION
        message = "Database constraint violation"

    logger.error(
        f"IntegrityError: {message}",
        extra={"path": request.url.path, "error": error_str},
    )

    error_response = create_error_response(
        error_code=error_code,
        message=message,
        request=request,
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response.model_dump(exclude_none=True),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """
    SQLAlchemy 일반 에러 처리

    데이터베이스 연결 실패, 쿼리 오류 등을 처리합니다.
    """
    trace_id = str(uuid.uuid4())

    logger.error(
        f"SQLAlchemyError: {str(exc)}",
        extra={"trace_id": trace_id, "path": request.url.path},
        exc_info=True,
    )

    error_response = create_error_response(
        error_code=ErrorCode.DATABASE_ERROR,
        message="Database operation failed",
        request=request,
        trace_id=trace_id,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    모든 예상치 못한 예외 처리

    마지막 안전망으로 모든 처리되지 않은 예외를 캐치합니다.
    """
    trace_id = str(uuid.uuid4())

    logger.exception(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={"trace_id": trace_id, "path": request.url.path},
    )

    error_response = create_error_response(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred. Please contact support if the problem persists.",
        request=request,
        trace_id=trace_id,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True),
    )


# Health check endpoint with database ping
@app.get("/health")
async def health_check():
    """
    Health check endpoint for container orchestration and monitoring.

    Performs a lightweight database connectivity check and returns
    service status. Use /health/detailed for comprehensive diagnostics.
    """
    db_status = "healthy"
    db_error = None

    try:
        # Quick database connectivity test
        db = SessionLocal()
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
        logger.error(f"Health check database ping failed: {e}")

    overall_status = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": {
            "database": {
                "status": db_status,
                "error": db_error,
            },
        },
    }


@app.get("/health/detailed")
async def health_check_detailed():
    """
    Detailed health check with comprehensive system diagnostics.

    Returns detailed information about all service components including:
    - Database connectivity and basic stats
    - Cache statistics
    - Rate limiter status
    - Memory usage
    """
    import time
    start_time = time.time()

    # Database check with timing
    db_status = "healthy"
    db_error = None
    db_latency_ms = None

    try:
        db_start = time.time()
        db = SessionLocal()
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db_latency_ms = round((time.time() - db_start) * 1000, 2)
        finally:
            db.close()
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
        logger.error(f"Health check database ping failed: {e}")

    # Cache statistics
    cache_stats = None
    try:
        from app.core.cache import get_cache_stats
        cache_stats = get_cache_stats()
    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")

    overall_status = "healthy" if db_status == "healthy" else "degraded"
    total_latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "latency_ms": total_latency_ms,
        "checks": {
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
                "error": db_error,
            },
            "cache": cache_stats,
        },
        "config": {
            "debug": settings.DEBUG,
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "cache_enabled": settings.CACHE_ENABLED,
        },
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
app.include_router(process_operations.router, prefix=f"{settings.API_V1_PREFIX}/process-operations", tags=["Process Operations"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["Users"])
app.include_router(lots.router, prefix=settings.API_V1_PREFIX, tags=["LOTs"])
app.include_router(wip_items.router, prefix=settings.API_V1_PREFIX, tags=["WIP Items"])
app.include_router(serials.router, prefix=settings.API_V1_PREFIX, tags=["Serials"])
app.include_router(process_data.router, prefix=settings.API_V1_PREFIX, tags=["Process Data"])
app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX, tags=["Audit Logs"])
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX, tags=["Alerts"])
app.include_router(production_lines.router, prefix=settings.API_V1_PREFIX, tags=["Production Lines"])
app.include_router(equipment.router, prefix=settings.API_V1_PREFIX, tags=["Equipment"])
app.include_router(error_logs.router, prefix=settings.API_V1_PREFIX, tags=["Error Logs"])
app.include_router(printer_monitoring.router, prefix=settings.API_V1_PREFIX + "/printer", tags=["Printer Monitoring"])
app.include_router(async_operations.router, prefix=f"{settings.API_V1_PREFIX}/async", tags=["Async Operations"])
app.include_router(search.router, prefix=f"{settings.API_V1_PREFIX}/search", tags=["Search"])
app.include_router(stations.router, prefix=settings.API_V1_PREFIX, tags=["Stations"])


if __name__ == "__main__":
    import uvicorn

    # Uvicorn log config with timestamp
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(client_addr)s - \"%(request_line)s\" %(status_code)s"
    log_config["formatters"]["access"]["datefmt"] = DATE_FORMAT
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["datefmt"] = DATE_FORMAT

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=log_config,
    )
