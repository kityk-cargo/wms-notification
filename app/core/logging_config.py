import sys
import logging


def setup_logging():
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers if setup_logging is called multiple times.
    if not root_logger.handlers:
        root_logger.addHandler(handler)
