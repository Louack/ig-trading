import pandas as pd
import pandas_ta as ta
from datetime import datetime
from typing import List, Dict, Any

from ..base.strategy import BaseStrategy
from ..base.signal import Signal, SignalType, SignalStrength


class GoldenDeathCrossStrategy(BaseStrategy):
    """Golden Cross / Death Cross strategy implementation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Strategy parameters
        self.short_ma_period = config.get("short_ma_period", 50)  # Default 50-day
        self.long_ma_period = config.get("long_ma_period", 200)  # Default 200-day
        self.confirmation_periods = config.get(
            "confirmation_periods", 2
        )  # Wait 2 periods for confirmation
        self.volume_filter = config.get(
            "volume_filter", True
        )  # Use volume confirmation
        self.rsi_filter = config.get("rsi_filter", True)  # Use RSI filter

        # RSI parameters for filtering
        self.rsi_period = config.get("rsi_period", 14)
        self.rsi_oversold = config.get("rsi_oversold", 30)
        self.rsi_overbought = config.get("rsi_overbought", 70)

    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate Golden Cross / Death Cross signals"""
        if not self.validate_data(data):
            return []

        # Add required indicators
        data = self._add_indicators(data)

        # Generate crossover signals
        signals = []

        # Look for crossovers in the last few periods
        for i in range(len(data) - self.confirmation_periods, len(data)):
            if i < 1:  # Need at least 2 periods to detect crossover
                continue

            current_row = data.iloc[i]
            previous_row = data.iloc[i - 1]

            # Check for Golden Cross (bullish crossover)
            if self._is_golden_cross(previous_row, current_row):
                if self._validate_golden_cross_signal(data, i):
                    signal = self._create_signal(
                        epic=data["epic"].iloc[i],
                        signal_type=SignalType.BUY,
                        price=current_row["closePrice_mid"],
                        timestamp=current_row["timestamp"],
                        strength=self._calculate_signal_strength(data, i, "golden"),
                        metadata={
                            "strategy": "golden_cross",
                            "short_ma": current_row[f"sma_{self.short_ma_period}"],
                            "long_ma": current_row[f"sma_{self.long_ma_period}"],
                            "rsi": current_row["rsi_14"],
                            "volume_ratio": self._get_volume_ratio(data, i),
                        },
                    )
                    signals.append(signal)

            # Check for Death Cross (bearish crossover)
            elif self._is_death_cross(previous_row, current_row):
                if self._validate_death_cross_signal(data, i):
                    signal = self._create_signal(
                        epic=data["epic"].iloc[i],
                        signal_type=SignalType.SELL,
                        price=current_row["closePrice_mid"],
                        timestamp=current_row["timestamp"],
                        strength=self._calculate_signal_strength(data, i, "death"),
                        metadata={
                            "strategy": "death_cross",
                            "short_ma": current_row[f"sma_{self.short_ma_period}"],
                            "long_ma": current_row[f"sma_{self.long_ma_period}"],
                            "rsi": current_row["rsi_14"],
                            "volume_ratio": self._get_volume_ratio(data, i),
                        },
                    )
                    signals.append(signal)

        return signals

    def _add_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add required technical indicators"""
        # Moving averages
        data[f"sma_{self.short_ma_period}"] = ta.sma(
            data["closePrice_mid"], length=self.short_ma_period
        )
        data[f"sma_{self.long_ma_period}"] = ta.sma(
            data["closePrice_mid"], length=self.long_ma_period
        )

        # RSI for filtering
        if self.rsi_filter:
            data["rsi_14"] = ta.rsi(data["closePrice_mid"], length=self.rsi_period)

        # Volume moving average for volume filter
        if self.volume_filter:
            data["volume_sma"] = ta.sma(data["lastTradedVolume"], length=20)

        return data

    def _is_golden_cross(self, previous_row: pd.Series, current_row: pd.Series) -> bool:
        """Check if current period shows a Golden Cross"""
        short_ma_prev = previous_row[f"sma_{self.short_ma_period}"]
        long_ma_prev = previous_row[f"sma_{self.long_ma_period}"]
        short_ma_curr = current_row[f"sma_{self.short_ma_period}"]
        long_ma_curr = current_row[f"sma_{self.long_ma_period}"]

        # Golden Cross: short MA was below long MA, now above
        return short_ma_prev <= long_ma_prev and short_ma_curr > long_ma_curr

    def _is_death_cross(self, previous_row: pd.Series, current_row: pd.Series) -> bool:
        """Check if current period shows a Death Cross"""
        short_ma_prev = previous_row[f"sma_{self.short_ma_period}"]
        long_ma_prev = previous_row[f"sma_{self.long_ma_period}"]
        short_ma_curr = current_row[f"sma_{self.short_ma_period}"]
        long_ma_curr = current_row[f"sma_{self.long_ma_period}"]

        # Death Cross: short MA was above long MA, now below
        return short_ma_prev >= long_ma_prev and short_ma_curr < long_ma_curr

    def _validate_golden_cross_signal(self, data: pd.DataFrame, index: int) -> bool:
        """Validate Golden Cross signal with additional filters"""
        current_row = data.iloc[index]

        # RSI filter: Don't buy if overbought
        if self.rsi_filter and current_row["rsi_14"] > self.rsi_overbought:
            return False

        # Volume filter: Require above-average volume
        if self.volume_filter:
            volume_ratio = self._get_volume_ratio(data, index)
            if volume_ratio < 1.2:  # Require 20% above average volume
                return False

        # Trend confirmation: Price should be above long-term MA
        if current_row["closePrice_mid"] < current_row[f"sma_{self.long_ma_period}"]:
            return False

        return True

    def _validate_death_cross_signal(self, data: pd.DataFrame, index: int) -> bool:
        """Validate Death Cross signal with additional filters"""
        current_row = data.iloc[index]

        # RSI filter: Don't sell if oversold
        if self.rsi_filter and current_row["rsi_14"] < self.rsi_oversold:
            return False

        # Volume filter: Require above-average volume
        if self.volume_filter:
            volume_ratio = self._get_volume_ratio(data, index)
            if volume_ratio < 1.2:  # Require 20% above average volume
                return False

        # Trend confirmation: Price should be below long-term MA
        if current_row["closePrice_mid"] > current_row[f"sma_{self.long_ma_period}"]:
            return False

        return True

    def _calculate_signal_strength(
        self, data: pd.DataFrame, index: int, cross_type: str
    ) -> SignalStrength:
        """Calculate signal strength based on multiple factors"""
        current_row = data.iloc[index]

        # Base strength
        strength_score = 1

        # Volume confirmation
        if self.volume_filter:
            volume_ratio = self._get_volume_ratio(data, index)
            if volume_ratio > 1.5:
                strength_score += 1
            elif volume_ratio > 2.0:
                strength_score += 2

        # RSI confirmation
        if self.rsi_filter:
            rsi = current_row["rsi_14"]
            if cross_type == "golden":
                if 30 <= rsi <= 50:  # Good RSI for buying
                    strength_score += 1
            else:  # death cross
                if 50 <= rsi <= 70:  # Good RSI for selling
                    strength_score += 1

        # MA separation
        ma_separation = abs(
            current_row[f"sma_{self.short_ma_period}"]
            - current_row[f"sma_{self.long_ma_period}"]
        )
        ma_separation_pct = (
            ma_separation / current_row[f"sma_{self.long_ma_period}"] * 100
        )

        if ma_separation_pct > 2:  # Strong separation
            strength_score += 1

        # Convert to SignalStrength enum
        if strength_score >= 4:
            return SignalStrength.STRONG
        elif strength_score >= 2:
            return SignalStrength.MEDIUM
        else:
            return SignalStrength.WEAK

    def _get_volume_ratio(self, data: pd.DataFrame, index: int) -> float:
        """Calculate current volume vs average volume"""
        current_volume = data.iloc[index]["lastTradedVolume"]
        avg_volume = data.iloc[index]["volume_sma"]
        return current_volume / avg_volume if avg_volume > 0 else 1.0

    def _create_signal(
        self,
        epic: str,
        signal_type: SignalType,
        price: float,
        timestamp: datetime,
        strength: SignalStrength,
        metadata: Dict[str, Any],
    ) -> Signal:
        """Create a signal object"""
        # Calculate confidence based on strength and filters
        confidence = 0.5  # Base confidence
        if strength == SignalStrength.STRONG:
            confidence = 0.8
        elif strength == SignalStrength.MEDIUM:
            confidence = 0.6

        return Signal(
            epic=epic,
            signal_type=signal_type,
            strength=strength,
            timestamp=timestamp,
            price=price,
            confidence=confidence,
            metadata=metadata,
        )

    def should_enter_position(self, signal: Signal) -> bool:
        """Determine if we should enter a position"""
        # Only enter on strong or medium strength signals
        return signal.strength in [SignalStrength.STRONG, SignalStrength.MEDIUM]

    def should_exit_position(
        self, signal: Signal, current_position: Dict[str, Any]
    ) -> bool:
        """Determine if we should exit a position"""
        # Exit on opposite crossover
        if (
            current_position["direction"] == "BUY"
            and signal.signal_type == SignalType.SELL
        ):
            return True
        elif (
            current_position["direction"] == "SELL"
            and signal.signal_type == SignalType.BUY
        ):
            return True

        return False
