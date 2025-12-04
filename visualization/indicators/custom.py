"""
Custom technical indicators
"""

from typing import Dict, Any
import pandas as pd

from .base import Indicator


# Example custom indicator - add your own here
class CustomIndicator(Indicator):
    """Template for custom indicators"""

    def __init__(self, **params: Any):
        """
        Initialize custom indicator

        Args:
            **params: Indicator-specific parameters
        """
        super().__init__(name="Custom", **params)

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate custom indicator

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with indicator columns added
        """
        result = df.copy()
        # Add your custom calculation here
        # result['custom_indicator'] = ...
        return result

    def get_plot_config(self) -> Dict[str, Any]:
        config = super().get_plot_config()
        config.update({"color": "blue", "label": "Custom Indicator"})
        return config

