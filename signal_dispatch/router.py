"""
Signal routing with filtering, formatting, and deduplication hooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
import hashlib

from strategies.base.signal import Signal
from signal_dispatch.transports import Transport


@dataclass
class DispatchConfig:
    min_strength: Optional[str] = None  # "WEAK" | "MEDIUM" | "STRONG"
    allowed_strategies: Optional[Set[str]] = None
    allowed_instruments: Optional[Set[str]] = None
    dedupe: bool = True


def _strength_rank(value: str) -> int:
    ranks = {"WEAK": 0, "MEDIUM": 1, "STRONG": 2}
    return ranks.get(value, -1)


def _dedupe_key(signal: Signal) -> str:
    raw = (
        f"{signal.instrument}-{signal.signal_type.value}-{signal.timestamp.isoformat()}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _format_payload(signal: Signal) -> Dict[str, Any]:
    return {
        "instrument": signal.instrument,
        "signal_type": signal.signal_type.value,
        "strength": signal.strength.value,
        "timestamp": signal.timestamp.isoformat(),
        "price": signal.price,
        "confidence": signal.confidence,
        "metadata": signal.metadata or {},
        "source": (signal.metadata or {}).get("source"),
        "instrument_type": (signal.metadata or {}).get("instrument_type"),
    }


def dispatch_signals(
    signals: List[Signal],
    transports: List[Transport],
    config: Optional[DispatchConfig] = None,
) -> None:
    cfg = config or DispatchConfig()
    seen = set()

    for sig in signals:
        if (
            cfg.allowed_strategies
            and sig.metadata
            and sig.metadata.get("strategy") not in cfg.allowed_strategies
        ):
            continue
        if cfg.allowed_instruments and sig.instrument not in cfg.allowed_instruments:
            continue
        if cfg.min_strength and _strength_rank(sig.strength.value) < _strength_rank(
            cfg.min_strength
        ):
            continue

        if cfg.dedupe:
            key = _dedupe_key(sig)
            if key in seen:
                continue
            seen.add(key)

        payload = _format_payload(sig)
        for transport in transports:
            transport.send(payload)
