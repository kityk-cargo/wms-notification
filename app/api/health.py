from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    components: Optional[Dict[str, Any]] = None


@router.get("/liveness", response_model=HealthResponse)
async def liveness_check():
    """
    Liveness probe endpoint.
    Determines if the application is running.
    """
    return {
        "status": "UP",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/readiness", response_model=HealthResponse)
async def readiness_check():
    """
    Readiness probe endpoint.
    Determines if the service is ready to receive traffic.
    """
    # Here you would check dependencies if needed
    return {
        "status": "UP",
        "timestamp": datetime.now().isoformat(),
        "components": {"application": {"status": "UP"}},
    }


@router.get("/startup", response_model=HealthResponse)
async def startup_check():
    """
    Startup probe endpoint.
    Determines if the application has started correctly.
    """
    return {
        "status": "UP",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Overall health check endpoint.
    Returns comprehensive health status of the service.
    """
    components = {
        "application": {"status": "UP"},
    }

    overall_status = "UP"
    for component, status_info in components.items():
        if status_info["status"] != "UP":
            overall_status = "DOWN"
            break

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "components": components,
    }
