from fastapi import FastAPI
from app.api.notification import router as notification_router
from app.api.health import router as health_router  # Import the health router
from app.core.logging_config import setup_logging  # NEW import

setup_logging()  # Initialize logging for the whole project

app = FastAPI(
    title="WMS Notification Service",
    description="Service for handling warehouse management system notifications",
    version="1.0.0",
    redirect_slashes=False,
)

app.include_router(notification_router, prefix="/api/v1")
app.include_router(health_router, prefix="/health")  # Add health router
