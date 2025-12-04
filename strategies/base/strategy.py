from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd
import logging

from .signal import Signal, SignalType, SignalStrength


class BaseStrategy(ABC):
    """Base class for all trading strategies"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration

        Args:
            config: Strategy configuration dictionary
        """
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.timeframe = config.get("timeframe", "daily")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Validate configuration
        self._validate_config()

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals based on market data

        Args:
            data: Market data DataFrame with OHLCV data

        Returns:
            List of trading signals
        """
        pass

    @abstractmethod
    def should_enter_position(self, signal: Signal) -> bool:
        """
        Determine if a signal should trigger a position entry

        Args:
            signal: The trading signal to evaluate

        Returns:
            True if position should be entered
        """
        pass

    @abstractmethod
    def should_exit_position(
        self, signal: Signal, current_position: Dict[str, Any]
    ) -> bool:
        """
        Determine if a signal should trigger a position exit

        Args:
            signal: The trading signal to evaluate
            current_position: Current position information

        Returns:
            True if position should be exited
        """
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that the input data has required columns

        Args:
            data: Market data DataFrame

        Returns:
            True if data is valid
        """
        required_columns = [
            "epic",
            "timestamp",
            "openPrice_mid",
            "highPrice_mid",
            "lowPrice_mid",
            "closePrice_mid",
            "lastTradedVolume",
        ]

        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False

        if data.empty:
            self.logger.error("Data is empty")
            return False

        return True

    def _validate_config(self) -> None:
        """
        Validate strategy configuration

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(self.config, dict):
            raise ValueError("Config must be a dictionary")

        if not self.name:
            raise ValueError("Strategy name is required")

        if not self.timeframe:
            raise ValueError("Timeframe is required")

    def get_config(self) -> Dict[str, Any]:
        """Get strategy configuration"""
        return self.config.copy()

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update strategy configuration

        Args:
            updates: Dictionary of configuration updates
        """
        self.config.update(updates)
        self._validate_config()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', timeframe='{self.timeframe}')"

    def __repr__(self) -> str:
        return self.__str__()
