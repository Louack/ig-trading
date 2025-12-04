"""
Chart visualization using mplfinance
"""

from typing import List, Optional, Any
import pandas as pd
import mplfinance as mpf

from .indicators.base import Indicator
from .utils import prepare_dataframe, validate_ohlcv_data


class Chart:
    """Chart visualization for trading data with technical indicators"""

    def __init__(
        self,
        df: pd.DataFrame,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
    ):
        """
        Initialize chart

        Args:
            df: DataFrame with OHLCV data (from data_collection module)
            symbol: Symbol name (optional, for display)
            timeframe: Timeframe (optional, for display)
        """
        # Prepare and validate data
        self.df = prepare_dataframe(df)
        validate_ohlcv_data(self.df)

        # Extract symbol and timeframe from DataFrame if not provided
        # Note: symbol/timeframe columns are preserved even when timestamp is index
        if symbol is None:
            if "symbol" in self.df.columns and len(self.df) > 0:
                self.symbol = self.df["symbol"].iloc[0]
            else:
                self.symbol = "Unknown"
        else:
            self.symbol = symbol

        if timeframe is None:
            if "timeframe" in self.df.columns and len(self.df) > 0:
                self.timeframe = self.df["timeframe"].iloc[0]
            else:
                self.timeframe = "Unknown"
        else:
            self.timeframe = timeframe

        self.indicators: List[Indicator] = []
        self.plot_data = self.df.copy()

    def add_indicator(self, indicator: Indicator) -> "Chart":
        """
        Add a technical indicator to the chart

        Args:
            indicator: Indicator instance

        Returns:
            Self for method chaining
        """
        self.indicators.append(indicator)
        self.plot_data = indicator.calculate(self.plot_data)
        return self

    def add_indicators(self, indicators: List[Indicator]) -> "Chart":
        """
        Add multiple indicators to the chart

        Args:
            indicators: List of Indicator instances

        Returns:
            Self for method chaining
        """
        for indicator in indicators:
            self.add_indicator(indicator)
        return self

    def plot(
        self,
        type: str = "candle",
        volume: bool = True,
        style: str = "yahoo",
        figsize: tuple = (12, 8),
        savefig: Optional[str] = None,
        show: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Plot the chart with indicators

        Args:
            type: Chart type ('candle', 'line', 'ohlc', 'renko', 'pnf')
            volume: Show volume subplot
            style: mplfinance style ('yahoo', 'classic', 'charles', etc.)
            figsize: Figure size (width, height)
            savefig: Optional path to save figure
            show: Whether to display the plot
            **kwargs: Additional arguments passed to mplfinance.plot()
        """
        # Prepare data for mplfinance (needs lowercase column names)
        plot_df = self.plot_data[["open", "high", "low", "close"]].copy()
        if "volume" in self.plot_data.columns:
            plot_df["volume"] = self.plot_data["volume"]

        # Configure candlestick colors: green for bullish (close > open), red for bearish (close < open)
        if type == "candle":
            # Create custom market colors: green for up (close > open), red for down (close < open)
            marketcolors = mpf.make_marketcolors(
                up="g",  # Green for bullish candles
                down="r",  # Red for bearish candles
                edge="inherit",
                wick="inherit",
                volume="inherit",
            )
            # Create custom style with our color scheme
            custom_style = mpf.make_mpf_style(
                marketcolors=marketcolors,
                gridstyle="",
                y_on_right=False,
            )
            plot_style = custom_style
        else:
            plot_style = style

        # Build mplfinance plot configuration
        mplf_kwargs = {
            "type": type,
            "volume": volume,
            "style": plot_style,
            "figsize": figsize,
            "show_nontrading": False,
        }

        # Add title
        title = f"{self.symbol} - {self.timeframe}"
        mplf_kwargs["title"] = title

        # Prepare additional plots for indicators
        addplot_list = []
        panel_config = []

        # Separate indicators by type
        overlay_indicators = []  # Indicators on main price chart
        subplot_indicators = []  # Indicators in separate panels

        for indicator in self.indicators:
            config = indicator.get_plot_config()
            if config.get("type") in ["rsi", "stochastic", "macd"]:
                subplot_indicators.append((indicator, config))
            else:
                overlay_indicators.append((indicator, config))

        # Add overlay indicators (moving averages, bollinger bands, etc.)
        for indicator, config in overlay_indicators:
            if config["type"] == "bollinger":
                # Bollinger Bands
                bb_upper = None
                bb_middle = None
                bb_lower = None
                for col in self.plot_data.columns:
                    if "bb_upper" in col.lower() or "bbu" in col.lower():
                        bb_upper = self.plot_data[col]
                    elif "bb_middle" in col.lower() or "bbm" in col.lower():
                        bb_middle = self.plot_data[col]
                    elif "bb_lower" in col.lower() or "bbl" in col.lower():
                        bb_lower = self.plot_data[col]

                if bb_upper is not None and bb_lower is not None:
                    addplot_list.append(
                        mpf.make_addplot(
                            bb_upper,
                            color=config.get("color", "gray"),
                            linestyle="--",
                            alpha=0.5,
                        )
                    )
                    addplot_list.append(
                        mpf.make_addplot(
                            bb_lower,
                            color=config.get("color", "gray"),
                            linestyle="--",
                            alpha=0.5,
                        )
                    )
                if bb_middle is not None:
                    addplot_list.append(
                        mpf.make_addplot(
                            bb_middle,
                            color=config.get("color", "gray"),
                            linestyle="-",
                            alpha=0.3,
                        )
                    )
            else:
                # Line indicators (SMA, EMA, etc.)
                for col_name, display_name in indicator.columns.items():
                    if col_name in self.plot_data.columns:
                        # Get indicator data - ensure it's aligned with plot_df index
                        indicator_data = self.plot_data[col_name].copy()

                        # Convert None to NaN and handle missing values
                        indicator_data = indicator_data.replace([None], pd.NA)
                        # Forward fill NaN values (for indicators that need warm-up period like SMA 200)
                        indicator_data = indicator_data.ffill()

                        # Only add if we have at least some valid data
                        if indicator_data.notna().sum() > 0:
                            # Ensure the data uses the same index as plot_df
                            indicator_data_aligned = indicator_data.reindex(
                                plot_df.index
                            )
                            addplot_list.append(
                                mpf.make_addplot(
                                    indicator_data_aligned,
                                    color=config.get("color", "blue"),
                                    linestyle=config.get("style", "-"),
                                    width=config.get("width", 1.0),
                                    label=display_name,
                                )
                            )

        # Add subplot indicators (RSI, MACD, Stochastic)
        for indicator, config in subplot_indicators:
            if config["type"] == "rsi":
                for col_name in indicator.columns.keys():
                    if col_name in self.plot_data.columns:
                        addplot_list.append(
                            mpf.make_addplot(
                                self.plot_data[col_name],
                                panel=len(panel_config) + 1,
                                color=config.get("color", "red"),
                                ylabel=indicator.name,
                                ylim=config.get("ylim", (0, 100)),
                            )
                        )
                        panel_config.append(
                            {
                                "ylabel": indicator.name,
                                "ylim": config.get("ylim", (0, 100)),
                            }
                        )
            elif config["type"] == "macd":
                # MACD requires multiple lines
                macd_line = None
                signal_line = None
                histogram = None

                for col in self.plot_data.columns:
                    if (
                        "macd" in col.lower()
                        and "signal" not in col.lower()
                        and "hist" not in col.lower()
                    ):
                        macd_line = self.plot_data[col]
                    elif "macd_signal" in col.lower() or "macds" in col.lower():
                        signal_line = self.plot_data[col]
                    elif "macd_hist" in col.lower() or "macdh" in col.lower():
                        histogram = self.plot_data[col]

                panel_num = len(panel_config) + 1
                if macd_line is not None:
                    addplot_list.append(
                        mpf.make_addplot(
                            macd_line,
                            panel=panel_num,
                            color="blue",
                            ylabel="MACD",
                        )
                    )
                if signal_line is not None:
                    addplot_list.append(
                        mpf.make_addplot(
                            signal_line,
                            panel=panel_num,
                            color="red",
                        )
                    )
                if histogram is not None:
                    addplot_list.append(
                        mpf.make_addplot(
                            histogram,
                            panel=panel_num,
                            type="bar",
                            color="gray",
                            alpha=0.3,
                        )
                    )
                panel_config.append({"ylabel": "MACD"})
            elif config["type"] == "stochastic":
                for col_name in indicator.columns.keys():
                    if col_name in self.plot_data.columns:
                        addplot_list.append(
                            mpf.make_addplot(
                                self.plot_data[col_name],
                                panel=len(panel_config) + 1,
                                color=config.get("color", "blue"),
                                ylabel=indicator.name,
                                ylim=config.get("ylim", (0, 100)),
                            )
                        )
                        panel_config.append(
                            {
                                "ylabel": indicator.name,
                                "ylim": config.get("ylim", (0, 100)),
                            }
                        )

        # Add additional plots if specified
        if addplot_list:
            mplf_kwargs["addplot"] = addplot_list

        # Merge with user kwargs (user kwargs take precedence)
        mplf_kwargs.update(kwargs)

        # Plot
        if savefig:
            mplf_kwargs["savefig"] = savefig

        if not show:
            mplf_kwargs["returnfig"] = True

        mpf.plot(plot_df, **mplf_kwargs)

    def get_data(self) -> pd.DataFrame:
        """
        Get the chart data with all indicators calculated

        Returns:
            DataFrame with OHLCV data and indicator columns
        """
        return self.plot_data.copy()
