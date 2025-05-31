import os

from dotenv import load_dotenv
from pathlib import Path

env_path = Path(os.getenv("ENV_PATH", "/etc/dev/ig_trading/.env"))
load_dotenv(dotenv_path=env_path)

IG_API_NAME = os.getenv("IG_API_NAME")
IG_API_KEY = os.getenv("IG_API_KEY")