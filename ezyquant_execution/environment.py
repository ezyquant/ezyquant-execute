import logging
import os

import settrade_v2.config

logger = logging.getLogger(__name__)


def set_settrade_environment(environment):
    """Set the SETTRADE environment for the current session."""
    settrade_v2.config.config["environment"] = environment
    logger.info("SETTRADE environment set to: %s", environment)


SETTRADE_ENVIRONMENT = os.getenv("SETTRADE_ENVIRONMENT")

if SETTRADE_ENVIRONMENT:
    logger.info(
        "Found SETTRADE_ENVIRONMENT in environment variable: %s", SETTRADE_ENVIRONMENT
    )
    set_settrade_environment(SETTRADE_ENVIRONMENT)
