"""
Data storage service for market data
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

from config import STORAGE_CONFIG

logger = logging.getLogger(__name__)


class DataStorage:
    """CSV-based data storage for market data"""

    def __init__(self, data_dir: str = STORAGE_CONFIG["base_dir"]):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        for timeframe in STORAGE_CONFIG["timeframes"]:
            (self.data_dir / timeframe).mkdir(exist_ok=True)

    def _calculate_mid_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate mid prices for OHLC"""
        price_types = ["open", "high", "low", "close"]

        for price_type in price_types:
            bid_col = f"{price_type}Price_bid"
            ask_col = f"{price_type}Price_ask"
            mid_col = f"{price_type}Price_mid"

            if bid_col in df.columns and ask_col in df.columns:
                df[mid_col] = round((df[bid_col] + df[ask_col]) / 2, 1)

        return df

    def _calculate_spreads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate spreads for OHLC"""
        price_types = ["open", "high", "low", "close"]

        for price_type in price_types:
            bid_col = f"{price_type}Price_bid"
            ask_col = f"{price_type}Price_ask"
            spread_col = f"{price_type}Price_spread"

            if bid_col in df.columns and ask_col in df.columns:
                df[spread_col] = round(df[ask_col] - df[bid_col], 1)

        return df

    def _convert_to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Convert market data to DataFrame with flattened price columns"""
        prices = data["data"]["prices"]

        df = pd.DataFrame(prices)

        for price_col in ["openPrice", "closePrice", "highPrice", "lowPrice"]:
            if price_col in df.columns:
                df[f"{price_col}_bid"] = df[price_col].apply(
                    lambda x: round(x.get("bid"), 1)
                    if isinstance(x, dict) and x.get("bid") is not None
                    else None
                )
                df[f"{price_col}_ask"] = df[price_col].apply(
                    lambda x: round(x.get("ask"), 1)
                    if isinstance(x, dict) and x.get("ask") is not None
                    else None
                )
                df.drop(columns=[price_col], inplace=True)

        df = self._calculate_mid_prices(df)
        df = self._calculate_spreads(df)

        df["epic"] = data["epic"]
        df["timeframe"] = data["timeframe"]
        df["timestamp"] = pd.to_datetime(df["snapshotTimeUTC"])

        metadata_cols = ["epic", "timeframe", "timestamp"]

        bid_cols = [col for col in df.columns if col.endswith("_bid")]
        ask_cols = [col for col in df.columns if col.endswith("_ask")]
        mid_cols = [col for col in df.columns if col.endswith("_mid")]
        spread_cols = [col for col in df.columns if col.endswith("_spread")]
        volume_cols = ["lastTradedVolume"]

        other_cols = [
            col
            for col in df.columns
            if col
            not in (
                metadata_cols
                + bid_cols
                + ask_cols
                + mid_cols
                + spread_cols
                + volume_cols
                + ["snapshotTimeUTC"]
            )
        ]

        df = df[
            metadata_cols
            + mid_cols
            + bid_cols
            + ask_cols
            + spread_cols
            + volume_cols
            + other_cols
        ]

        return df

    def store_data(self, data: Dict[str, List[Dict[str, Any]]], timeframe: str):
        """Store collected data to CSV files - one file per instrument"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for category, instruments_data in data.items():
            if not instruments_data:
                continue

            for instrument_data in instruments_data:
                try:
                    df = self._convert_to_dataframe(instrument_data)
                    epic = instrument_data.get("epic", "unknown")

                    filepath = self.data_dir / timeframe / f"{epic}_{timestamp}.csv"
                    df.to_csv(filepath, index=False)

                    logger.info(
                        f"Stored {len(df)} data points for {epic} to {filepath}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to convert data for {instrument_data.get('epic', 'unknown')}: {e}"
                    )

    def append_data(self, new_data: Dict[str, List[Dict[str, Any]]], timeframe: str):
        """Append new data to existing CSV files - one file per instrument"""
        for category, instruments_data in new_data.items():
            if not instruments_data:
                continue

            for instrument_data in instruments_data:
                try:
                    new_df = self._convert_to_dataframe(instrument_data)
                    epic = instrument_data.get("epic", "unknown")

                    existing_df = self.get_latest_data(epic, timeframe)

                    if existing_df is not None:
                        combined_df = pd.concat(
                            [existing_df, new_df], ignore_index=True
                        )
                        combined_df.drop_duplicates(
                            subset=["timestamp"], keep="last", inplace=True
                        )
                    else:
                        combined_df = new_df

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filepath = self.data_dir / timeframe / f"{epic}_{timestamp}.csv"
                    combined_df.to_csv(filepath, index=False)

                    logger.info(f"Appended {len(new_df)} new data points for {epic}")
                except Exception as e:
                    logger.error(
                        f"Failed to append data for {instrument_data.get('epic', 'unknown')}: {e}"
                    )
