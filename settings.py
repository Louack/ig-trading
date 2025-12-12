"""
Environment-based secrets management.

This module handles sensitive configuration (API keys, tokens, credentials)
loaded from environment variables. Use app_config.py for application settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env file if present
env_path = Path(os.getenv("ENV_PATH", "/etc/dev/ig_trading/.env"))
load_dotenv(dotenv_path=env_path)


class Secrets:
    """Container for all sensitive configuration values."""

    # IG Markets API credentials
    ig_demo_api_key: str = os.getenv("IG_DEMO_API_KEY", "")
    ig_demo_identifier: str = os.getenv("IG_DEMO_IDENTIFIER", "")
    ig_demo_password: str = os.getenv("IG_DEMO_PASSWORD", "")

    ig_prod_api_key: str = os.getenv("IG_PROD_API_KEY", "")
    ig_prod_identifier: str = os.getenv("IG_PROD_IDENTIFIER", "")
    ig_prod_password: str = os.getenv("IG_PROD_PASSWORD", "")

    # Massive (formerly Polygon.io) API credentials
    massive_api_key: str = os.getenv("MASSIVE_API_KEY", "")

    # Telegram bot configuration
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "test_token_placeholder")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "test_chat_placeholder")

    # Legacy support for POLYGON_API_KEY (will be removed in future)
    @property
    def polygon_api_key(self) -> str:
        """Legacy Polygon API key support."""
        return os.getenv("POLYGON_API_KEY", self.massive_api_key)

    # IG Markets API configuration (derived from secrets)
    @property
    def ig_base_urls(self) -> dict:
        """IG API base URLs."""
        return {
            "demo": "https://demo-api.ig.com/gateway/deal",
            "prod": "https://api.ig.com/gateway/deal",
        }

    @property
    def ig_api_keys(self) -> dict:
        """IG API keys by account type."""
        return {
            "demo": self.ig_demo_api_key,
            "prod": self.ig_prod_api_key,
        }

    @property
    def ig_identifiers(self) -> dict:
        """IG identifiers by account type."""
        return {
            "demo": self.ig_demo_identifier,
            "prod": self.ig_prod_identifier,
        }

    @property
    def ig_passwords(self) -> dict:
        """IG passwords by account type."""
        return {
            "demo": self.ig_demo_password,
            "prod": self.ig_prod_password,
        }


# Global secrets instance
secrets = Secrets()
