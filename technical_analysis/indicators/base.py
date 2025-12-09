"""
Base indicator interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class Indicator(ABC):
    """Base class for technical indicators"""

    def __init__(self, name: str, **params: Any):
        """
        Initialize indicator

        Args:
            name: Indicator name
            **params: Indicator-specific parameters
        """
        self.name = name
        self.params = params
        self.columns: Dict[str, str] = {}

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate indicator values

        Args:
            df: DataFrame with OHLCV data (columns: open, high, low, close, volume)

        Returns:
            DataFrame with indicator columns added
        """
        raise NotImplementedError

    def get_plot_config(self) -> Dict[str, Any]:
        """
        Get configuration for plotting this indicator

        Returns:
            Dictionary with plot configuration (type, color, style, etc.)
        """
        return {
            "type": "line",
            "color": "blue",
            "style": "-",
            "width": 1.0,
        }

    def __repr__(self) -> str:
        params_str = ", ".join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.__class__.__name__}({params_str})"
