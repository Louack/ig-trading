"""
Transports for delivering trading signals (e.g., webhook, console).
"""

from __future__ import annotations

from typing import Dict, Any, Protocol
import json
import logging
import httpx
from settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class Transport(Protocol):
    def send(self, payload: Dict[str, Any]) -> None: ...


class ConsoleTransport:
    """Simple console transport for testing."""

    def send(self, payload: Dict[str, Any]) -> None:
        logger.info("Signal dispatched", extra={"payload": payload})
        print(json.dumps(payload, default=str))  # keep for quick visibility


class TelegramTransport:
    """Telegram Bot API transport for sending text messages."""

    def __init__(
        self,
        token: str = TELEGRAM_BOT_TOKEN,
        chat_id: str = TELEGRAM_CHAT_ID,
        timeout: float = 5.0,
    ):
        if not token or not chat_id:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be configured"
            )
        self.token = token
        self.chat_id = chat_id
        self.timeout = timeout

    def send(self, payload: Dict[str, Any]) -> None:
        metadata = payload.get("metadata") or {}
        source = payload.get("source") or metadata.get("source")
        instrument_type = payload.get("instrument_type") or metadata.get(
            "instrument_type"
        )
        metadata_text = json.dumps(metadata, default=str, ensure_ascii=False)
        text = (
            f"Signal Alert\n"
            f"Instrument: {payload.get('instrument')}\n"
            f"Type: {payload.get('signal_type')}\n"
            f"Strength: {payload.get('strength')}\n"
            f"Price: {payload.get('price')}\n"
            f"Confidence: {payload.get('confidence')}\n"
            f"Timestamp: {payload.get('timestamp')}\n"
            f"Source: {source}\n"
            f"Instrument Type: {instrument_type}\n"
            f"Metadata: {metadata_text}"
        )
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": text}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, data=data)
                resp.raise_for_status()
        except Exception as exc:
            logger.error(
                "Telegram transport failed",
                extra={"error": str(exc), "chat_id": self.chat_id},
            )
