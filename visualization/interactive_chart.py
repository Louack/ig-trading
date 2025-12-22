"""
Interactive chart visualization using Plotly
"""

from typing import List, Optional, Any
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from technical_analysis.indicators import Indicator
from .utils import prepare_dataframe, validate_ohlcv_data


class InteractiveChart:
    """Interactive chart visualization for trading data with technical indicators using Plotly"""

    def __init__(
        self,
        df: pd.DataFrame,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
    ):
        """
        Initialize interactive chart

        Args:
            df: DataFrame with OHLCV data (from data_collection module)
            symbol: Symbol name (optional, for display)
            timeframe: Timeframe (optional, for display)
        """
        self.df = prepare_dataframe(df)
        validate_ohlcv_data(self.df)

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

    def add_indicator(self, indicator: Indicator) -> "InteractiveChart":
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

    def add_indicators(self, indicators: List[Indicator]) -> "InteractiveChart":
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

    def _create_subplots(self, volume: bool) -> go.Figure:
        """
        Create Plotly subplots

        Args:
            volume: Whether to include volume subplot

        Returns:
            Plotly Figure with subplots
        """
        rows = 1
        row_heights = [1.0]
        if volume:
            rows += 1
            row_heights = [0.7, 0.3]  # Price chart larger, volume smaller

        fig = make_subplots(
            rows=rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=(
                [f"{self.symbol} - {self.timeframe}"] + (["Volume"] if volume else [])
            ),
        )
        return fig

    def _generate_hover_texts(self, plot_df: pd.DataFrame, volume: bool) -> List[str]:
        """
        Generate hover text for each data point

        Args:
            plot_df: DataFrame with OHLCV data
            volume: Whether to include volume in hover text

        Returns:
            List of hover text strings
        """
        hover_texts = []
        for i, idx in enumerate(plot_df.index):
            # Format date/time for display
            if isinstance(idx, pd.Timestamp):
                date_str = idx.strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = str(idx)

            hover_parts = [
                f"<b>{date_str}</b>",
                f"Open: {plot_df.iloc[i]['open']:.2f}",
                f"High: {plot_df.iloc[i]['high']:.2f}",
                f"Low: {plot_df.iloc[i]['low']:.2f}",
                f"Close: {plot_df.iloc[i]['close']:.2f}",
            ]

            for indicator in self.indicators:
                config = indicator.get_plot_config()
                if config.get("type") not in ["rsi", "stochastic", "macd"]:
                    for col_name, display_name in indicator.columns.items():
                        if col_name in self.plot_data.columns:
                            value = self.plot_data.loc[idx, col_name]
                            if pd.notna(value):
                                hover_parts.append(f"{display_name}: {value:.2f}")

            if volume and "volume" in plot_df.columns:
                hover_parts.append(f"Volume: {plot_df.iloc[i]['volume']:,.0f}")

            hover_texts.append("<br>".join(hover_parts))

        return hover_texts

    def _add_price_chart(
        self,
        fig: go.Figure,
        plot_df: pd.DataFrame,
        chart_type: str,
        hover_texts: List[str],
    ) -> None:
        """
        Add price chart (candlestick, line, or OHLC) to figure

        Args:
            fig: Plotly Figure
            plot_df: DataFrame with OHLCV data
            chart_type: Type of chart ('candle', 'line', 'ohlc')
            hover_texts: List of hover text strings
        """
        if chart_type == "candle":
            trace = go.Candlestick(
                x=plot_df.index,
                open=plot_df["open"],
                high=plot_df["high"],
                low=plot_df["low"],
                close=plot_df["close"],
                increasing_line_color="green",
                decreasing_line_color="red",
                increasing_fillcolor="green",
                decreasing_fillcolor="red",
                name="Price",
                hovertemplate="%{text}<extra></extra>",
                text=hover_texts,
            )
        elif chart_type == "line":
            trace = go.Scatter(
                x=plot_df.index,
                y=plot_df["close"],
                mode="lines",
                name="Close",
                line=dict(color="blue", width=1),
                hovertemplate="%{text}<extra></extra>",
                text=hover_texts,
            )
        elif chart_type == "ohlc":
            trace = go.Ohlc(
                x=plot_df.index,
                open=plot_df["open"],
                high=plot_df["high"],
                low=plot_df["low"],
                close=plot_df["close"],
                increasing_line_color="green",
                decreasing_line_color="red",
                name="Price",
                hovertemplate="%{text}<extra></extra>",
                text=hover_texts,
            )
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        fig.add_trace(trace, row=1, col=1)

    def _add_overlay_indicators(self, fig: go.Figure, plot_df: pd.DataFrame) -> None:
        """
        Add overlay indicators (moving averages, etc.) to the figure

        Args:
            fig: Plotly Figure
            plot_df: DataFrame with OHLCV data
        """
        for indicator in self.indicators:
            config = indicator.get_plot_config()
            if config.get("type") not in ["rsi", "stochastic", "macd"]:
                for col_name, display_name in indicator.columns.items():
                    if col_name in self.plot_data.columns:
                        indicator_data = self.plot_data[col_name].copy()
                        indicator_data = indicator_data.replace([None], pd.NA)
                        indicator_data = indicator_data.ffill()

                        if indicator_data.notna().sum() > 0:
                            indicator_data = indicator_data.reindex(plot_df.index)
                            fig.add_trace(
                                go.Scatter(
                                    x=plot_df.index,
                                    y=indicator_data,
                                    mode="lines",
                                    name=display_name,
                                    line=dict(
                                        color=config.get("color", "blue"),
                                        width=config.get("width", 1.0),
                                        dash=self._convert_linestyle(
                                            config.get("style", "-")
                                        ),
                                    ),
                                    hovertemplate=f"<b>{display_name}</b><br>"
                                    f"Value: %{{y:.2f}}<br>"
                                    f"Date: %{{x}}<extra></extra>",
                                ),
                                row=1,
                                col=1,
                            )

    def _add_volume_subplot(
        self, fig: go.Figure, plot_df: pd.DataFrame, volume: bool
    ) -> None:
        """
        Add volume subplot to figure

        Args:
            fig: Plotly Figure
            plot_df: DataFrame with OHLCV data
            volume: Whether to show volume
        """
        if volume and "volume" in plot_df.columns:
            colors = [
                (
                    "green"
                    if plot_df.iloc[i]["close"] >= plot_df.iloc[i]["open"]
                    else "red"
                )
                for i in range(len(plot_df))
            ]

            fig.add_trace(
                go.Bar(
                    x=plot_df.index,
                    y=plot_df["volume"],
                    name="Volume",
                    marker_color=colors,
                    hovertemplate="<b>Volume</b><br>"
                    "Value: %{y:,.0f}<br>"
                    "Date: %{x}<extra></extra>",
                ),
                row=2,
                col=1,
            )

    def _update_layout(
        self, fig: go.Figure, figsize: tuple, volume: bool, **kwargs: Any
    ) -> None:
        """
        Update figure layout

        Args:
            fig: Plotly Figure
            figsize: Figure size (width, height) in pixels
            volume: Whether volume subplot is shown
            **kwargs: Additional layout arguments
        """
        fig.update_layout(
            title=f"{self.symbol} - {self.timeframe}",
            xaxis_title="Date",
            yaxis_title="Price",
            height=figsize[1],
            width=figsize[0],
            hovermode="x unified",
            template="plotly_white",
            xaxis_rangeslider_visible=False,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        if volume:
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)

        fig.update_layout(**kwargs)

    def plot(
        self,
        type: str = "candle",
        volume: bool = True,
        figsize: tuple = (1400, 800),
        savefig: Optional[str] = None,
        show: bool = True,
        **kwargs: Any,
    ) -> Optional[go.Figure]:
        """
        Plot the interactive chart with indicators

        Args:
            type: Chart type ('candle', 'line', 'ohlc')
            volume: Show volume subplot
            figsize: Figure size (width, height) in pixels
            savefig: Optional path to save figure (HTML format)
            show: Whether to display the plot
            **kwargs: Additional arguments passed to Plotly

        Returns:
            Plotly Figure object (if show=False) or None
        """
        plot_df = self._prepare_plot_data()

        fig = self._create_subplots(volume)

        hover_texts = self._generate_hover_texts(plot_df, volume)

        self._add_price_chart(fig, plot_df, type, hover_texts)

        self._add_overlay_indicators(fig, plot_df)

        self._add_volume_subplot(fig, plot_df, volume)

        self._update_layout(fig, figsize, volume, **kwargs)

        if savefig:
            fig.write_html(savefig)

        if show:
            fig.show()
            return None
        else:
            return fig

    def _convert_linestyle(self, style: str) -> str:
        """
        Convert matplotlib linestyle to Plotly dash style

        Args:
            style: Matplotlib linestyle ('-', '--', '-.', ':')

        Returns:
            Plotly dash style
        """
        style_map = {
            "-": "solid",
            "--": "dash",
            "-.": "dashdot",
            ":": "dot",
        }
        return style_map.get(style, "solid")

    def get_data(self) -> pd.DataFrame:
        """
        Get the chart data with all indicators calculated

        Returns:
            DataFrame with OHLCV data and indicator columns
        """
        return self.plot_data.copy()
