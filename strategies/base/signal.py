from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass


class SignalType(Enum):
    """Types of trading signals"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalStrength(Enum):
    """Strength levels for trading signals"""

    WEAK = "WEAK"
    MEDIUM = "MEDIUM"
    STRONG = "STRONG"


@dataclass
class Signal:
    """Represents a trading signal"""

    epic: str
    signal_type: SignalType
    strength: SignalStrength
    timestamp: datetime
    price: float
    confidence: float  # 0.0 to 1.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate signal data after initialization"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )

        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary"""
        return {
            "epic": self.epic,
            "signal_type": self.signal_type.value,
            "strength": self.strength.value,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "confidence": self.confidence,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Signal":
        """Create signal from dictionary"""
        return cls(
            epic=data["epic"],
            signal_type=SignalType(data["signal_type"]),
            strength=SignalStrength(data["strength"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            price=data["price"],
            confidence=data["confidence"],
            metadata=data.get("metadata", {}),
        )
