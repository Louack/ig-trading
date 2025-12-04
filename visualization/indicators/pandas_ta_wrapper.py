"""
Wrapper for pandas-ta technical indicators
"""

from typing import Dict, Any, Optional
import pandas as pd
import pandas_ta as ta

from .base import Indicator


class SMA(Indicator):
    """Simple Moving Average"""

    def __init__(
        self, period: int = 20, column: str = "close", color: Optional[str] = None
    ):
        """
        Initialize SMA indicator

        Args:
            period: Period for moving average
            column: Column to calculate SMA on (default: close)
            color: Optional color for the indicator line (default: auto-assigned based on period)
        """
        super().__init__(name="SMA", period=period, column=column, color=color)
        self.period = period
        self.column = column
        self.color = color
        self.columns = {f"sma_{period}": f"SMA({period})"}

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMA"""
        result = df.copy()
        result[f"sma_{self.period}"] = ta.sma(result[self.column], length=self.period)
        return result

    def get_plot_config(self) -> Dict[str, Any]:
        config = super().get_plot_config()
        # Default colors based on period if not specified
        if self.color is None:
            # Default color scheme for common SMA periods
            default_colors = {
                20: "blue",
                50: "green",
                100: "red",
                200: "purple",
            }
            color = default_colors.get(self.period, "orange")
        else:
            color = self.color
        config.update({"color": color, "label": f"SMA({self.period})"})
        return config


class EMA(Indicator):
    """Exponential Moving Average"""

    def __init__(self, period: int = 20, column: str = "close"):
        """
        Initialize EMA indicator

        Args:
            period: Period for moving average
            column: Column to calculate EMA on (default: close)
        """
        super().__init__(name="EMA", period=period, column=column)
        self.period = period
        self.column = column
        self.columns = {f"ema_{period}": f"EMA({period})"}

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMA"""
        result = df.copy()
        result[f"ema_{self.period}"] = ta.ema(result[self.column], length=self.period)
        return result

    def get_plot_config(self) -> Dict[str, Any]:
        config = super().get_plot_config()
        config.update({"color": "purple", "label": f"EMA({self.period})"})
        return config


class RSI(Indicator):
    """Relative Strength Index"""

    def __init__(self, period: int = 14):
        """
        Initialize RSI indicator

        Args:
            period: Period for RSI calculation
        """
        super().__init__(name="RSI", period=period)
        self.period = period
        self.columns = {f"rsi_{period}": f"RSI({period})"}

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI"""
        result = df.copy()
        result[f"rsi_{self.period}"] = ta.rsi(result["close"], length=self.period)
        return result

    def get_plot_config(self) -> Dict[str, Any]:
        config = super().get_plot_config()
        config.update(
            {
                "type": "line",
                "color": "red",
                "label": f"RSI({self.period})",
                "ylim": (0, 100),
            }
        )
        return config


class MACD(Indicator):
    """Moving Average Convergence Divergence"""

    def __init__(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ):
        """
        Initialize MACD indicator

        Args:
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period
        """
        super().__init__(name="MACD", fast=fast, slow=slow, signal=signal)
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.columns = {
            f"macd_{fast}_{slow}": f"MACD({fast},{slow})",
            f"macd_signal_{signal}": f"MACD Signal({signal})",
            f"macd_hist_{fast}_{slow}_{signal}": f"MACD Histogram",
        }

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD"""
        result = df.copy()
        macd_data = ta.macd(
            result["close"],
            fast=self.fast,
            slow=self.slow,
            signal=self.signal,
        )
        if macd_data is not None:
            for col in macd_data.columns:
                result[col] = macd_data[col]
        return result

    def get_plot_config(self) -> Dict[str, Any]:
        return {
            "type": "macd",
            "label": f"MACD({self.fast},{self.slow},{self.signal})",
        }


class BollingerBands(Indicator):
    """Bollinger Bands"""

    def __init__(self, period: int = 20, std: float = 2.0):
        """
        Initialize Bollinger Bands indicator

        Args:
            period: Period for moving average
            std: Standard deviation multiplier
        """
        super().__init__(name="BB", period=period, std=std)
        self.period = period
        self.std = std
        self.columns = {
            f"bb_upper_{period}": f"BB Upper({period},{std})",
            f"bb_middle_{period}": f"BB Middle({period})",
            f"bb_lower_{period}": f"BB Lower({period},{std})",
        }

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        result = df.copy()
        bb_data = ta.bbands(result["close"], length=self.period, std=self.std)
        if bb_data is not None:
            for col in bb_data.columns:
                result[col] = bb_data[col]
        return result

    def get_plot_config(self) -> Dict[str, Any]:
        return {
            "type": "bollinger",
            "label": f"BB({self.period},{self.std})",
            "color": "gray",
            "alpha": 0.3,
        }


class Stochastic(Indicator):
    """Stochastic Oscillator"""

    def __init__(
        self,
        k_period: int = 14,
        d_period: int = 3,
        smooth_k: int = 3,
    ):
        """
        Initialize Stochastic indicator

        Args:
            k_period: %K period
            d_period: %D period
            smooth_k: Smoothing for %K
        """
        super().__init__(
            name="Stochastic", k_period=k_period, d_period=d_period, smooth_k=smooth_k
        )
        self.k_period = k_period
        self.d_period = d_period
        self.smooth_k = smooth_k
        self.columns = {
            f"stoch_k_{k_period}": f"Stoch %K({k_period})",
            f"stoch_d_{d_period}": f"Stoch %D({d_period})",
        }

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Stochastic"""
        result = df.copy()
        stoch_data = ta.stoch(
            result["high"],
            result["low"],
            result["close"],
            k=self.k_period,
            d=self.d_period,
            smooth_k=self.smooth_k,
        )
        if stoch_data is not None:
            for col in stoch_data.columns:
                result[col] = stoch_data[col]
        return result

    def get_plot_config(self) -> Dict[str, Any]:
        return {
            "type": "line",
            "label": f"Stoch({self.k_period},{self.d_period})",
            "ylim": (0, 100),
        }


class ATR(Indicator):
    """Average True Range"""

    def __init__(self, period: int = 14):
        """
        Initialize ATR indicator

        Args:
            period: Period for ATR calculation
        """
        super().__init__(name="ATR", period=period)
        self.period = period
        self.columns = {f"atr_{period}": f"ATR({period})"}

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ATR"""
        result = df.copy()
        result[f"atr_{self.period}"] = ta.atr(
            result["high"], result["low"], result["close"], length=self.period
        )
        return result

    def get_plot_config(self) -> Dict[str, Any]:
        config = super().get_plot_config()
        config.update({"color": "green", "label": f"ATR({self.period})"})
        return config
