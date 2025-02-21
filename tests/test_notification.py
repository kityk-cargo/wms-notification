from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_notification():
    """
    When sending a notification request
    Should successfully process the notification and return success status
    """
    notification_data = {
        "alert_type": "LOW_STOCK",
        "message": "Stock level below threshold",
        "severity": "HIGH",
        "inventory_ids": ["INV001", "INV002"],
    }

    response = client.post("/api/v1/notifications/", json=notification_data)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}. Response: {response.text}"

    response_data = response.json()
    assert "id" in response_data
