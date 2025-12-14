"""
Simple TOML configuration loading.

Loads TOML files containing non-sensitive configuration values.
"""

import logging
from typing import Dict, Any
import tomllib
from settings import trading_toml_path

logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """
    Load configuration from TOML file.

    Returns:
        Dict containing configuration

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config file is invalid
    """
    if not trading_toml_path.exists():
        raise FileNotFoundError(f"Config file not found: {trading_toml_path}")

    with open(trading_toml_path, "rb") as f:
        config = tomllib.load(f)

    return config
