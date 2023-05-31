import logging

import settrade_v2.config

from . import config as cfg

logger = logging.getLogger(__name__)


def set_settrade_environment(environment):
    """Set the SETTRADE environment for the current session."""
    settrade_v2.config.config["environment"] = environment


if cfg.SETTRADE_ENVIRONMENT:
    set_settrade_environment(cfg.SETTRADE_ENVIRONMENT)
