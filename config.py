"""
Simple configuration factory.

This replaces the complex config/loader.py with a clean factory
that uses the unified AppConfig system.
"""

from typing import Tuple
from app_config import AppConfig
from settings import secrets, Secrets


def load_config() -> AppConfig:
    """
    Load application configuration from environment variables.

    Returns:
        AppConfig: Validated application configuration
    """
    return AppConfig.from_env()


def load_config_with_secrets() -> Tuple[AppConfig, Secrets]:
    """
    Load both application configuration and secrets.

    Returns:
        Tuple of (AppConfig, Secrets): Configuration and secrets
    """
    return load_config(), secrets


# Backward compatibility aliases
def load_config_from_env() -> AppConfig:
    """Legacy alias for load_config."""
    return load_config()
