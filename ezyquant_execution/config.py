import logging
import os

logger = logging.getLogger(__name__)

SETTRADE_ENVIRONMENT = os.getenv("SETTRADE_ENVIRONMENT")
SETTRADE_COMMISSIION = float(os.getenv("SETTRADE_COMMISSIION", default=0.0025))  # 0.25%


def log_env(name: str):
    v = os.getenv(name)
    if v is not None:
        logger.info(f"Found {name} in environment variable. Setting {name} to {v}")


[log_env(name) for name in ["SETTRADE_ENVIRONMENT", "SETTRADE_COMMISSIION"]]
