import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

from technical_analysis.indicators import SMA, RSI
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
        self.rsi_column = f"rsi_{self.rsi_period}"

        # Volume filter parameters
        self.volume_sma_period = config.get("volume_sma_period", 20)

        # Indicator instances
        self.short_sma_indicator = SMA(period=self.short_ma_period, column="close")
        self.long_sma_indicator = SMA(period=self.long_ma_period, column="close")
        self.rsi_indicator = RSI(period=self.rsi_period)
        self.volume_sma_indicator = SMA(period=self.volume_sma_period, column="volume")

    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate signals across the provided dataset (caller controls window)."""
        if not self.validate_data(data):
            return []

        data = self._add_indicators(data)
        warmup = max(
            self.short_ma_period,
            self.long_ma_period,
            self.confirmation_periods,
            1,
        )
        signals: List[Signal] = []

        for i in range(warmup, len(data)):
            current_row = data.iloc[i]
            previous_row = data.iloc[i - 1]

            if self._is_golden_cross(previous_row, current_row):
                signal = self._build_golden_cross_signal(data, i, current_row)
                if signal:
                    signals.append(signal)
            elif self._is_death_cross(previous_row, current_row):
                signal = self._build_death_cross_signal(data, i, current_row)
                if signal:
                    signals.append(signal)

        return signals

    def _build_golden_cross_signal(
        self, data: pd.DataFrame, index: int, current_row: pd.Series
    ) -> Optional[Signal]:
        if not self._validate_golden_cross_signal(data, index):
            return None
        return self._create_signal(
            epic=self._get_epic(data, index),
            signal_type=SignalType.BUY,
            price=current_row["closePrice"],
            timestamp=current_row["timestamp"],
            strength=self._calculate_signal_strength(data, index, "golden"),
            metadata={
                "strategy": "golden_cross",
                "short_ma": current_row[f"sma_{self.short_ma_period}"],
                "long_ma": current_row[f"sma_{self.long_ma_period}"],
                "rsi": self._get_rsi_value(current_row),
                "volume_ratio": self._get_volume_ratio(data, index),
            },
        )

    def _build_death_cross_signal(
        self, data: pd.DataFrame, index: int, current_row: pd.Series
    ) -> Optional[Signal]:
        if not self._validate_death_cross_signal(data, index):
            return None
        return self._create_signal(
            epic=self._get_epic(data, index),
            signal_type=SignalType.SELL,
            price=current_row["closePrice"],
            timestamp=current_row["timestamp"],
            strength=self._calculate_signal_strength(data, index, "death"),
            metadata={
                "strategy": "death_cross",
                "short_ma": current_row[f"sma_{self.short_ma_period}"],
                "long_ma": current_row[f"sma_{self.long_ma_period}"],
                "rsi": self._get_rsi_value(current_row),
                "volume_ratio": self._get_volume_ratio(data, index),
            },
        )

    def _add_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add required technical indicators using the shared TA module."""
        df = self._prepare_indicator_inputs(data)

        df = self.short_sma_indicator.calculate(df)
        df = self.long_sma_indicator.calculate(df)

        if self.rsi_filter:
            df = self.rsi_indicator.calculate(df)

        if self.volume_filter:
            df = self.volume_sma_indicator.calculate(df)
            volume_col = f"sma_{self.volume_sma_period}"
            if volume_col in df.columns:
                df = df.rename(columns={volume_col: "volume_sma"})

        return df

    def _prepare_indicator_inputs(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create canonical OHLCV columns expected by indicators."""
        df = data.copy()
        column_map = {
            "openPrice": "open",
            "highPrice": "high",
            "lowPrice": "low",
            "closePrice": "close",
            "lastTradedVolume": "volume",
        }
        for source, target in column_map.items():
            if source in df.columns:
                df[target] = df[source]
        return df

    def _get_epic(self, data: pd.DataFrame, index: int) -> str:
        """Return instrument identifier with backward compatibility."""
        if "symbol" in data.columns:
            return data["symbol"].iloc[index]
        if "epic" in data.columns:
            return data["epic"].iloc[index]
        return "unknown"

    def _get_rsi_value(self, row: pd.Series) -> Any:
        """Safely retrieve RSI value if present."""
        return row[self.rsi_column] if self.rsi_column in row else None

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
        if self.rsi_filter:
            rsi_value = self._get_rsi_value(current_row)
            if rsi_value is None:
                self.logger.warning("RSI value missing; skipping RSI filter for row.")
            elif rsi_value > self.rsi_overbought:
                return False

        # Volume filter: Require above-average volume
        if self.volume_filter:
            volume_ratio = self._get_volume_ratio(data, index)
            if volume_ratio < 1.2:  # Require 20% above average volume
                return False

        # Trend confirmation: Price should be above long-term MA
        if current_row["closePrice"] < current_row[f"sma_{self.long_ma_period}"]:
            return False

        return True

    def _validate_death_cross_signal(self, data: pd.DataFrame, index: int) -> bool:
        """Validate Death Cross signal with additional filters"""
        current_row = data.iloc[index]

        # RSI filter: Don't sell if oversold
        if self.rsi_filter:
            rsi_value = self._get_rsi_value(current_row)
            if rsi_value is None:
                self.logger.warning("RSI value missing; skipping RSI filter for row.")
            elif rsi_value < self.rsi_oversold:
                return False

        # Volume filter: Require above-average volume
        if self.volume_filter:
            volume_ratio = self._get_volume_ratio(data, index)
            if volume_ratio < 1.2:  # Require 20% above average volume
                return False

        # Trend confirmation: Price should be below long-term MA
        if current_row["closePrice"] > current_row[f"sma_{self.long_ma_period}"]:
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
            rsi = self._get_rsi_value(current_row)
            if rsi is not None:
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
        if "volume_sma" not in data.columns:
            return 1.0
        current_row = data.iloc[index]
        current_volume = current_row.get("lastTradedVolume", 0) or 0
        avg_volume = current_row.get("volume_sma", 0) or 0
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
