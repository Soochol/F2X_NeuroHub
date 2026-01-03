"""
Station Service API Routes.

This module exports all FastAPI routers for the Station Service API.
"""

from station_service.api.routes.system import router as system_router
from station_service.api.routes.batches import router as batches_router
from station_service.api.routes.sequences import router as sequences_router
from station_service.api.routes.sequence_upload import router as sequence_upload_router
from station_service.api.routes.deploy import router as deploy_router
from station_service.api.routes.results import router as results_router
from station_service.api.routes.logs import router as logs_router
from station_service.api.routes.manual import router as manual_router
from station_service.api.routes.simulation import router as simulation_router
from station_service.api.routes.manual_sequence import router as manual_sequence_router
from station_service.api.routes.reports import router as reports_router

__all__ = [
    "system_router",
    "batches_router",
    "sequences_router",
    "sequence_upload_router",
    "deploy_router",
    "results_router",
    "logs_router",
    "manual_router",
    "simulation_router",
    "manual_sequence_router",
    "reports_router",
]
