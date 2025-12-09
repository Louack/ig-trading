"""
Settings and environment variable configuration.

This module serves as the single source of truth for all environment variables
used across the application. All environment variable access should go through
this module rather than using os.getenv() directly.
"""

import os

from dotenv import load_dotenv
from pathlib import Path

env_path = Path(os.getenv("ENV_PATH", "/etc/dev/ig_trading/.env"))
load_dotenv(dotenv_path=env_path)

# IG Markets API credentials
IG_DEMO_API_KEY = os.getenv("IG_DEMO_API_KEY", default="default")
IG_DEMO_IDENTIFIER = os.getenv("IG_DEMO_IDENTIFIER", default="default")
IG_DEMO_PASSWORD = os.getenv("IG_DEMO_PASSWORD", default="default")

IG_PROD_API_KEY = os.getenv("IG_PROD_API_KEY", default="default")
IG_PROD_IDENTIFIER = os.getenv("IG_PROD_IDENTIFIER", default="default")
IG_PROD_PASSWORD = os.getenv("IG_PROD_PASSWORD", default="default")

# Massive (formerly Polygon.io) API credentials
MASSIVE_API_KEY = os.getenv(
    "MASSIVE_API_KEY", default=os.getenv("POLYGON_API_KEY", default="")
)
# Legacy support for POLYGON_API_KEY (will be removed in future)
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", default=MASSIVE_API_KEY)

# IG Markets API configuration
BASE_URLS = {
    "demo": "https://demo-api.ig.com/gateway/deal",
    "prod": "https://api.ig.com/gateway/deal",
}

API_KEYS = {
    "demo": IG_DEMO_API_KEY,
    "prod": IG_PROD_API_KEY,
}

IDENTIFIERS = {
    "demo": IG_DEMO_IDENTIFIER,
    "prod": IG_PROD_IDENTIFIER,
}

PASSWORDS = {
    "demo": IG_DEMO_PASSWORD,
    "prod": IG_PROD_PASSWORD,
}

# Telegram bot configuration (alert transport)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", default="")
