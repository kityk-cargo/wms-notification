import unittest
import os
import logging
import threading
import time
import requests
import uvicorn
from pact import Verifier  # type: ignore
from app.main import app
import io
import contextlib
from fastapi import APIRouter
from app.api import notification as notification_module  # NEW import

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a test-only router for provider states
provider_state_router = APIRouter()


@provider_state_router.post("/_pact/provider_states/")
async def provider_states(request_body: dict):
    """
    Endpoint to handle provider state setup for Pact testing.
    This endpoint should only be available during testing.
    """
    state = request_body.get("state")
    params = request_body.get("params", {})

    print(f"Setting up provider state {request_body}: {state} with params: {params}")

    if state == "Notification service is experiencing a failure":
        print("Setting up provider state FAIL")
        notification_module.__mock_simulate_exception_never_define_in_prod = (
            True  # simulate failure
        )
    elif state == "Notification service is configured for success":
        print("Setting up provider state SUCCESS")
        notification_module.__mock_simulate_exception_never_define_in_prod = (
            None  # type: ignore
        )

    return {"status": "success"}


# Add the provider state router to the test app
app.include_router(provider_state_router)


class ProviderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("Starting uvicorn server in background...")
        cls.host = "127.0.0.1"
        cls.port = 8000
        config = uvicorn.Config(app, host=cls.host, port=cls.port, log_level="info")
        cls.server = uvicorn.Server(config)
        cls.server_thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.server_thread.start()

        # Wait until the server is ready by polling its root endpoint
        timeout = 10  # seconds
        start_time = time.time()
        server_up = False
        while time.time() - start_time < timeout:
            try:
                resp = requests.get(f"http://{cls.host}:{cls.port}/")
                if resp.status_code < 500:
                    server_up = True
                    break
            except Exception:
                pass
            time.sleep(0.2)
        if not server_up:
            raise RuntimeError("Uvicorn server did not start in time")
        logger.info("Uvicorn server is up and running")

    def test_provider(self):
        logger.info("Starting Pact verification test...")

        # Get pact file path
        default_pact_path = (
            "../wms-contracts/pact/rest/wms_notification/wms_inventory_management.json"
        )
        pact_file = os.getenv("PACT_FILE_PATH", default_pact_path)
        logger.info(f"Using Pact file: {pact_file}")

        # Check if pact file exists
        if not os.path.exists(pact_file):
            logger.error(f"Pact file not found at path: {pact_file}")
            raise FileNotFoundError(f"Pact file not found: {pact_file}")

        verifier_output = ""
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            verifier = Verifier(
                provider="WMSNotificationService",
                provider_base_url=f"http://{self.__class__.host}:{self.__class__.port}",
                enable_pending=True,
                publish_verification_results=False,
                provider_verify_options={
                    "follow_redirects": True,
                    "request_customizer": lambda request: {
                        **request,
                        "allow_redirects": True,
                    },
                },
            )
            output = verifier.verify_pacts(
                pact_file,
                provider_states_setup_url=f"http://{self.__class__.host}:{self.__class__.port}/_pact/provider_states/",
            )
            verifier_output = buf.getvalue()
        print(f"output: {output}")
        if output[0] != 0:  # that's pact, that's not me
            logger.error(f"Pact verification failed: {verifier_output}")
            self.fail(f"Pact verification failed: {verifier_output}")
        else:
            logger.info("Pact verification passed successfully")

    @classmethod
    def tearDownClass(cls):
        logger.info("Signaling uvicorn server to shutdown...")
        cls.server.should_exit = True
        cls.server_thread.join()
        logger.info("Uvicorn server shutdown complete")
