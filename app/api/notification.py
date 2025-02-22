from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class NotificationRequest(StrictBaseModel):
    level: str = Field(
        examples=["Warning"], description="Level of the notification"
    )
    category: str = Field(
        examples=["stock alerts"], description="Category of the notification"
    )
    title: str = Field(
        examples=["Low stock alert for product 1"], 
        description="Title of the notification"
    )
    message: str = Field(
        examples=["Stock level is 15. Consider restocking."],
        description="Detailed notification message",
    )


class NotificationResponse(StrictBaseModel):
    status: str = Field(examples=["success", "error"])
    message: str = Field(examples=["Alert sent successfully", "Failed to deliver notification"])
    details: str | None = Field(default=None, examples=["Connection error"])


# Example notification objects for API documentation
example_notification = NotificationResponse(
    status="success",
    message="Alert sent successfully"
)

example_notification_alt = NotificationResponse(
    status="error",
    message="Failed to deliver notification",
    details="Connection error"
)


@router.post(
    "/notifications",
    response_model=NotificationResponse,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"status": "success", "message": "Alert sent successfully"}
                }
            }
        },
        500: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "error", 
                        "message": "Failed to deliver notification",
                        "details": "Connection error"
                    }
                }
            }
        },
    },
)
async def create_notification(
    notification: NotificationRequest,
    response_model_exclude_none: bool = True,
):
    """
    Create a new notification
    """
    try:
        # Mock implementation - just logging the notification
        logger.info(f"Received notification: {notification.model_dump()}")

        # Return success response with correct content type
        return NotificationResponse(
            status="success",
            message="Alert sent successfully"
        )

    except Exception as e:
        # Log and return error response
        logger.error(f"Failed to process notification: {str(e)}")
        return NotificationResponse(
            status="error",
            message="Failed to deliver notification",
            details="Connection error"
        )
