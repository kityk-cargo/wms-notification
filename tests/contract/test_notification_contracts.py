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
import glob
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
    Handle provider state setup for Pact testing.
    """
    state = request_body.get("state")
    params = request_body.get("params", {})
    logger.info("Setting up provider state: %s with params: %s", state, params)
    if state == "Notification service is experiencing a failure":
        logger.info("Provider state FAIL: simulating failure")
        notification_module.__mock_simulate_exception_never_define_in_prod = True
    elif state == "Notification service is configured for success":
        logger.info("Provider state SUCCESS: simulating success")
        notification_module.__mock_simulate_exception_never_define_in_prod = None  # type: ignore
    return {"status": "success"}


# Add the provider state router to the test app
app.include_router(provider_state_router)


class NotificationContractsTest(unittest.TestCase):
    """
    Tests all Pact contracts for the WMS Notification Service.

    This test verifies that the notification service fulfills all contracts
    expected by consumer services by checking all pact files in the specified
    directory. This includes contracts from Inventory Management, Order Processing,
    User Management, and any other service that relies on notifications.
    """

    @classmethod
    def wait_for_server(cls, host: str, port: int, timeout: int = 10) -> None:
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                resp = requests.get(f"http://{host}:{port}/")
                if resp.status_code < 500:
                    return
            except Exception:
                pass
            time.sleep(0.2)
        raise RuntimeError("Uvicorn server did not start in time")

    @classmethod
    def setUpClass(cls):
        logger.info("Starting uvicorn server in background...")
        cls.host = "127.0.0.1"
        cls.port = 8000
        config = uvicorn.Config(app, host=cls.host, port=cls.port, log_level="info")
        cls.server = uvicorn.Server(config)
        cls.server_thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.server_thread.start()
        cls.wait_for_server(cls.host, cls.port)
        logger.info("Uvicorn server is up and running")

    def test_provider(self):
        """Pact verification test for all Notification service contracts."""
        logger.info("Starting Pact verification test...")

        # Set up the default directory path
        default_pact_dir = "../wms-contracts/pact/rest/wms_notification"
        pact_dir = os.getenv("PACT_DIR_PATH", default_pact_dir)

        # Check if the directory exists
        if not os.path.exists(pact_dir):
            logger.error("Pact directory not found at path: %s", pact_dir)
            raise FileNotFoundError(f"Pact directory not found: {pact_dir}")

        # Find all pact files in the directory
        pact_files = glob.glob(os.path.join(pact_dir, "*.json"))

        if not pact_files:
            logger.error("No Pact files found in directory: %s", pact_dir)
            raise FileNotFoundError(f"No Pact files found in: {pact_dir}")

        logger.info("Found %d Pact files to verify: %s", len(pact_files), pact_files)

        # Initialize success flag
        verification_successful = True
        all_outputs = []

        # Verify each pact file
        for pact_file in pact_files:
            logger.info("Verifying Pact file: %s", pact_file)

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
                all_outputs.append(
                    f"File: {os.path.basename(pact_file)}\n{verifier_output}"
                )

            logger.info(
                "Pact verification for %s: %s",
                pact_file,
                "SUCCESS" if output[0] == 0 else "FAILED",
            )

            if output[0] != 0:
                verification_successful = False
                logger.error("Pact verification failed for: %s", pact_file)

        # Log all outputs at the end
        logger.info("All Pact verification outputs:\n%s", "\n".join(all_outputs))

        # Fail the test if any verification failed
        if not verification_successful:
            self.fail("One or more Pact verifications failed. See logs for details.")
        else:
            logger.info("All Pact verifications passed successfully")

    @classmethod
    def tearDownClass(cls):
        logger.info("Signaling uvicorn server to shutdown...")
        cls.server.should_exit = True
        cls.server_thread.join()
        logger.info("Uvicorn server shutdown complete")
