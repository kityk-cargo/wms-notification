from fastapi import FastAPI
from app.api.notification import router as notification_router

app = FastAPI(
    title="WMS Notification Service",
    description="Service for handling warehouse management system notifications",
    version="1.0.0",
    redirect_slashes=False
)

app.include_router(notification_router, prefix="/api/v1")
