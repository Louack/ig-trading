import os

from dotenv import load_dotenv
from pathlib import Path

env_path = Path(os.getenv("ENV_PATH", "/etc/dev/ig_trading/.env"))
load_dotenv(dotenv_path=env_path)

IG_DEMO_API_KEY = os.getenv("IG_DEMO_API_KEY", default="default")
IG_DEMO_IDENTIFIER = os.getenv("IG_DEMO_IDENTIFIER", default="default")
IG_DEMO_PASSWORD = os.getenv("IG_DEMO_PASSWORD", default="default")

IG_PROD_API_KEY = os.getenv("IG_PROD_API_KEY", default="default")
IG_PROD_IDENTIFIER = os.getenv("IG_PROD_IDENTIFIER", default="default")
IG_PROD_PASSWORD = os.getenv("IG_PROD_PASSWORD", default="default")


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
