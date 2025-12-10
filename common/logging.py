"""
Shared logging setup with configurable handlers and formats.
"""

from __future__ import annotations

import json
import logging
import sys
from logging import Handler, Formatter
from typing import Optional, List

from settings import LOG_LEVEL, LOG_FORMAT, LOG_DEST, LOG_FILE  # noqa: F401


class JsonFormatter(Formatter):
    """Minimal JSON formatter using stdlib logging."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)
        # Include any extra fields (excluding built-ins)
        for key, value in record.__dict__.items():
            if key in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            ):
                continue
            payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def _build_handlers(
    dest: str, fmt: Formatter, filename: Optional[str]
) -> List[Handler]:
    handlers: List[Handler] = []
    if dest in ("stdout", "both"):
        handlers.append(logging.StreamHandler(sys.stdout))
    if dest in ("file", "both") and filename:
        handlers.append(logging.FileHandler(filename))
    return handlers


def setup_logging(
    level: Optional[str] = None,
    fmt: Optional[str] = None,
    dest: Optional[str] = None,
    filename: Optional[str] = None,
) -> None:
    """
    Configure root logging once.

    Args:
        level: log level name (default from LOG_LEVEL or INFO)
        fmt: "plain" or "json" (default from LOG_FORMAT or plain)
        dest: "stdout", "file", or "both" (default from LOG_DEST or stdout)
        filename: path for file handler when dest includes file (default LOG_FILE)
    """
    level = (level or LOG_LEVEL or "INFO").upper()
    fmt = (fmt or LOG_FORMAT or "plain").lower()
    dest = (dest or LOG_DEST or "stdout").lower()
    filename = filename or LOG_FILE or None

    # Avoid duplicate handlers on repeated calls
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    if fmt == "json":
        formatter: Formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s - %(message)s"
        )

    handlers = _build_handlers(dest, formatter, filename)
    if not handlers:
        handlers = [logging.StreamHandler(sys.stdout)]
    for h in handlers:
        h.setFormatter(formatter)

    logging.basicConfig(level=getattr(logging, level, logging.INFO), handlers=handlers)

    # Tweak noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
