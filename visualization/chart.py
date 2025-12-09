"""
Static chart visualization using mplfinance
"""

from typing import List, Optional, Any, Tuple
import pandas as pd
import mplfinance as mpf

from technical_analysis.indicators import Indicator
from .utils import prepare_dataframe, validate_ohlcv_data


class StaticChart:
    """Static chart visualization for trading data with technical indicators"""

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

    def add_indicator(self, indicator: Indicator) -> "StaticChart":
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

    def add_indicators(self, indicators: List[Indicator]) -> "StaticChart":
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

    def _prepare_plot_data(self) -> pd.DataFrame:
        """
        Prepare DataFrame for plotting

        Returns:
            DataFrame with OHLCV columns
        """
        plot_df = self.plot_data[["open", "high", "low", "close"]].copy()
        if "volume" in self.plot_data.columns:
            plot_df["volume"] = self.plot_data["volume"]
        return plot_df

    def _get_plot_style(self, chart_type: str, style: str) -> Any:
        """
        Get plot style for mplfinance

        Args:
            chart_type: Type of chart ('candle', 'line', etc.)
            style: Base style name

        Returns:
            mplfinance style object
        """
        if chart_type == "candle":
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
            return custom_style
        else:
            return style

    def _separate_indicators(
        self,
    ) -> Tuple[List[Tuple[Indicator, dict]], List[Tuple[Indicator, dict]]]:
        """
        Separate indicators into overlay and subplot categories

        Returns:
            Tuple of (overlay_indicators, subplot_indicators)
        """
        overlay_indicators = []
        subplot_indicators = []

        for indicator in self.indicators:
            config = indicator.get_plot_config()
            if config.get("type") in ["rsi", "stochastic", "macd"]:
                subplot_indicators.append((indicator, config))
            else:
                overlay_indicators.append((indicator, config))

        return overlay_indicators, subplot_indicators

    def _add_bollinger_bands(
        self, addplot_list: List[Any], indicator: Indicator, config: dict
    ) -> None:
        """
        Add Bollinger Bands to addplot list

        Args:
            addplot_list: List of mplfinance addplot objects
            indicator: Indicator instance
            config: Indicator configuration
        """
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

    def _add_line_indicator(
        self,
        addplot_list: List[Any],
        indicator: Indicator,
        config: dict,
        plot_df: pd.DataFrame,
    ) -> None:
        """
        Add line indicator (SMA, EMA, etc.) to addplot list

        Args:
            addplot_list: List of mplfinance addplot objects
            indicator: Indicator instance
            config: Indicator configuration
            plot_df: DataFrame with OHLCV data
        """
        for col_name, display_name in indicator.columns.items():
            if col_name in self.plot_data.columns:
                # Get indicator data - ensure it's aligned with plot_df index
                indicator_data = self.plot_data[col_name].copy()

                # Convert None to NaN and handle missing values
                indicator_data = indicator_data.replace([None], pd.NA)
                # Forward fill NaN values (for indicators that need warm-up period)
                indicator_data = indicator_data.ffill()

                # Only add if we have at least some valid data
                if indicator_data.notna().sum() > 0:
                    # Ensure the data uses the same index as plot_df
                    indicator_data_aligned = indicator_data.reindex(plot_df.index)
                    addplot_list.append(
                        mpf.make_addplot(
                            indicator_data_aligned,
                            color=config.get("color", "blue"),
                            linestyle=config.get("style", "-"),
                            width=config.get("width", 1.0),
                            label=display_name,
                        )
                    )

    def _add_overlay_indicators(
        self,
        addplot_list: List[Any],
        overlay_indicators: List[Tuple[Indicator, dict]],
        plot_df: pd.DataFrame,
    ) -> None:
        """
        Add overlay indicators to addplot list

        Args:
            addplot_list: List of mplfinance addplot objects
            overlay_indicators: List of (indicator, config) tuples
            plot_df: DataFrame with OHLCV data
        """
        for indicator, config in overlay_indicators:
            if config["type"] == "bollinger":
                self._add_bollinger_bands(addplot_list, indicator, config)
            else:
                self._add_line_indicator(addplot_list, indicator, config, plot_df)

    def _add_rsi_indicator(
        self,
        addplot_list: List[Any],
        indicator: Indicator,
        config: dict,
        panel_num: int,
    ) -> int:
        """
        Add RSI indicator to addplot list

        Args:
            addplot_list: List of mplfinance addplot objects
            indicator: Indicator instance
            config: Indicator configuration
            panel_num: Current panel number

        Returns:
            Updated panel number
        """
        for col_name in indicator.columns.keys():
            if col_name in self.plot_data.columns:
                addplot_list.append(
                    mpf.make_addplot(
                        self.plot_data[col_name],
                        panel=panel_num,
                        color=config.get("color", "red"),
                        ylabel=indicator.name,
                        ylim=config.get("ylim", (0, 100)),
                    )
                )
        return panel_num + 1

    def _add_macd_indicator(
        self, addplot_list: List[Any], indicator: Indicator, panel_num: int
    ) -> int:
        """
        Add MACD indicator to addplot list

        Args:
            addplot_list: List of mplfinance addplot objects
            indicator: Indicator instance
            panel_num: Current panel number

        Returns:
            Updated panel number
        """
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
        return panel_num + 1

    def _add_stochastic_indicator(
        self,
        addplot_list: List[Any],
        indicator: Indicator,
        config: dict,
        panel_num: int,
    ) -> int:
        """
        Add Stochastic indicator to addplot list

        Args:
            addplot_list: List of mplfinance addplot objects
            indicator: Indicator instance
            config: Indicator configuration
            panel_num: Current panel number

        Returns:
            Updated panel number
        """
        for col_name in indicator.columns.keys():
            if col_name in self.plot_data.columns:
                addplot_list.append(
                    mpf.make_addplot(
                        self.plot_data[col_name],
                        panel=panel_num,
                        color=config.get("color", "blue"),
                        ylabel=indicator.name,
                        ylim=config.get("ylim", (0, 100)),
                    )
                )
        return panel_num + 1

    def _add_subplot_indicators(
        self, addplot_list: List[Any], subplot_indicators: List[Tuple[Indicator, dict]]
    ) -> None:
        """
        Add subplot indicators (RSI, MACD, Stochastic) to addplot list

        Args:
            addplot_list: List of mplfinance addplot objects
            subplot_indicators: List of (indicator, config) tuples
        """
        panel_num = 1
        for indicator, config in subplot_indicators:
            if config["type"] == "rsi":
                panel_num = self._add_rsi_indicator(
                    addplot_list, indicator, config, panel_num
                )
            elif config["type"] == "macd":
                panel_num = self._add_macd_indicator(addplot_list, indicator, panel_num)
            elif config["type"] == "stochastic":
                panel_num = self._add_stochastic_indicator(
                    addplot_list, indicator, config, panel_num
                )

    def _build_mplfinance_kwargs(
        self,
        chart_type: str,
        volume: bool,
        plot_style: Any,
        figsize: tuple,
        addplot_list: List[Any],
        savefig: Optional[str],
        show: bool,
        **kwargs: Any,
    ) -> dict:
        """
        Build mplfinance plot configuration

        Args:
            chart_type: Chart type
            volume: Whether to show volume
            plot_style: Plot style object
            figsize: Figure size
            addplot_list: List of additional plots
            savefig: Optional path to save figure
            show: Whether to display the plot
            **kwargs: Additional arguments

        Returns:
            Dictionary of mplfinance arguments
        """
        mplf_kwargs = {
            "type": chart_type,
            "volume": volume,
            "style": plot_style,
            "figsize": figsize,
            "show_nontrading": False,
            "title": f"{self.symbol} - {self.timeframe}",
        }

        if addplot_list:
            mplf_kwargs["addplot"] = addplot_list

        if savefig:
            mplf_kwargs["savefig"] = savefig

        if not show:
            mplf_kwargs["returnfig"] = True

        # Merge with user kwargs (user kwargs take precedence)
        mplf_kwargs.update(kwargs)

        return mplf_kwargs

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
        # Prepare data for mplfinance
        plot_df = self._prepare_plot_data()

        # Get plot style
        plot_style = self._get_plot_style(type, style)

        # Separate indicators
        overlay_indicators, subplot_indicators = self._separate_indicators()

        # Build addplot list
        addplot_list = []

        # Add overlay indicators
        self._add_overlay_indicators(addplot_list, overlay_indicators, plot_df)

        # Add subplot indicators
        self._add_subplot_indicators(addplot_list, subplot_indicators)

        # Build mplfinance kwargs
        mplf_kwargs = self._build_mplfinance_kwargs(
            type, volume, plot_style, figsize, addplot_list, savefig, show, **kwargs
        )

        # Plot
        mpf.plot(plot_df, **mplf_kwargs)

    def get_data(self) -> pd.DataFrame:
        """
        Get the chart data with all indicators calculated

        Returns:
            DataFrame with OHLCV data and indicator columns
        """
        return self.plot_data.copy()
