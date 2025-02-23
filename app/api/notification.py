from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Test-only global variable - NEVER USE IN PRODUCTION
__mock_simulate_exception_never_define_in_prod = False


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class NotificationRequest(StrictBaseModel):
    level: str = Field(examples=["Warning"], description="Level of the notification")
    category: str = Field(
        examples=["stock alerts"], description="Category of the notification"
    )
    title: str = Field(
        examples=["Low stock alert for product 1"],
        description="Title of the notification",
    )
    message: str = Field(
        examples=["Stock level is 15. Consider restocking."],
        description="Detailed notification message",
    )


class NotificationResponse(StrictBaseModel):
    status: str = Field(examples=["success", "error"])
    message: str = Field(
        examples=["Alert sent successfully", "Failed to deliver notification"]
    )
    details: str | None = Field(default=None, examples=["Connection error"])


# Example notification objects for API documentation
example_notification = NotificationResponse(
    status="success", message="Alert sent successfully"
)

example_notification_alt = NotificationResponse(
    status="error", message="Failed to deliver notification", details="Connection error"
)


@router.post(
    "/notifications",
    response_model=NotificationResponse,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Alert sent successfully",
                    }
                }
            }
        },
        500: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Failed to deliver notification",
                        "details": "Connection error",
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
        print(f"Received notification: {notification.model_dump()}")
        # Check test mock flag and throw exception if set
        if __mock_simulate_exception_never_define_in_prod:
            logger.info("Simulating failure due to test mock flag")
            print("Simulating failure due to test mock flag")
            raise Exception("Simulated failure for testing")

        # Return success response with correct content type
        return NotificationResponse(status="success", message="Alert sent successfully")

    except Exception as e:
        # Log and return error response
        logger.error(f"Failed to process notification: {str(e)}")
        print(f"Failed to process notification: {e}")
        return JSONResponse(
            status_code=500,
            content=NotificationResponse(
                status="error", message="Failed to deliver notification", details=str(e)
            ).dict(),
        )
