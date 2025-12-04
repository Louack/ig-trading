"""
Data storage for market data from any source
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import hashlib

from ..interfaces.market_data import MarketData
from data_collection.config import STORAGE_CONFIG
from ..validation import DataValidator

logger = logging.getLogger(__name__)


class DataStorage:
    """Data storage for market data from any source"""

    def __init__(
        self,
        data_dir: Optional[str] = None,
        timeframes: Optional[List[str]] = None,
        validator: Optional[DataValidator] = None,
    ):
        """
        Initialize data storage

        Args:
            data_dir: Base directory for data storage (defaults to STORAGE_CONFIG["base_dir"])
            timeframes: List of timeframes to create subdirectories for (defaults to STORAGE_CONFIG["timeframes"])
            validator: Optional DataValidator instance (uses static methods if not provided)
        """
        self.data_dir = Path(data_dir or STORAGE_CONFIG["base_dir"])
        self.data_dir.mkdir(exist_ok=True)

        self.validator = validator
        timeframes_list = timeframes or STORAGE_CONFIG["timeframes"]

        # Create subdirectories for timeframes
        for timeframe in timeframes_list:
            (self.data_dir / timeframe).mkdir(exist_ok=True)

    def store_market_data(self, market_data: MarketData) -> bool:
        """
        Store market data to CSV file in append-only fashion

        Args:
            market_data: MarketData object to store

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate data before storing
            if self.validator:
                is_valid = self.validator.validate_market_data(market_data)
            else:
                is_valid = DataValidator.validate_market_data(market_data)

            if not is_valid:
                logger.error(f"Data validation failed for {market_data.symbol}")
                return False

            # Convert to DataFrame
            new_df = market_data.to_dataframe()

            if new_df.empty:
                logger.warning(f"No data to store for {market_data.symbol}")
                return False

            # Use canonical filename (no timestamp)
            filename = f"{market_data.symbol}_{market_data.source}.csv"
            timeframe_dir = self.data_dir / market_data.timeframe
            timeframe_dir.mkdir(parents=True, exist_ok=True)
            filepath = timeframe_dir / filename

            # Load existing data if file exists
            if filepath.exists():
                existing_df = pd.read_csv(filepath)
                existing_df["timestamp"] = pd.to_datetime(existing_df["timestamp"])
                # Normalize to timezone-naive (UTC) for consistency
                if existing_df["timestamp"].dt.tz is not None:
                    existing_df["timestamp"] = existing_df["timestamp"].dt.tz_localize(None)

                # Normalize new data timestamps to timezone-naive
                if new_df["timestamp"].dt.tz is not None:
                    new_df["timestamp"] = new_df["timestamp"].dt.tz_localize(None)

                # Append new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)

                # Remove duplicates based on timestamp (keep last)
                combined_df = combined_df.drop_duplicates(
                    subset=["timestamp"], keep="last"
                )

                # Sort by timestamp
                combined_df = combined_df.sort_values("timestamp")

                logger.info(
                    f"Appending {len(new_df)} new points to existing {len(existing_df)} points"
                )
            else:
                # Normalize timestamps to timezone-naive for new files
                if new_df["timestamp"].dt.tz is not None:
                    new_df["timestamp"] = new_df["timestamp"].dt.tz_localize(None)
                combined_df = new_df
                logger.info(f"Creating new file with {len(new_df)} data points")

            # Add data integrity checksum
            combined_df["checksum"] = combined_df.apply(
                self._calculate_row_checksum, axis=1
            )

            # Write atomically using temporary file
            temp_filepath = filepath.with_suffix(".tmp")
            combined_df.to_csv(temp_filepath, index=False)

            # Atomic rename (POSIX guarantees atomicity)
            temp_filepath.replace(filepath)

            logger.info(
                f"Stored {len(new_df)} data points for {market_data.symbol} to {filepath}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to store market data for {market_data.symbol}: {e}")
            return False

    @staticmethod
    def _calculate_row_checksum(row: pd.Series) -> str:
        """Calculate checksum for a data row"""
        # Create string from key columns
        data_string = f"{row['timestamp']}{row.get('openPrice', '')}{row.get('closePrice', '')}{row.get('highPrice', '')}{row.get('lowPrice', '')}"
        return hashlib.md5(data_string.encode()).hexdigest()[:8]

    def store_multiple_market_data(
        self, market_data_list: List[MarketData]
    ) -> Dict[str, bool]:
        """
        Store multiple market data objects

        Args:
            market_data_list: List of MarketData objects

        Returns:
            Dictionary mapping instrument names to success status
        """
        results = {}

        for market_data in market_data_list:
            success = self.store_market_data(market_data)
            results[market_data.symbol] = success

        return results

    def load_latest_data(
        self, symbol: str, timeframe: str, source: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load the most recent data for a symbol

        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            source: Optional source filter

        Returns:
            DataFrame with latest data or None if not found
        """
        try:
            timeframe_dir = self.data_dir / timeframe

            if not timeframe_dir.exists():
                logger.warning(f"Timeframe directory {timeframe_dir} does not exist")
                return None

            # Look for canonical filename first
            if source:
                filename = f"{symbol}_{source}.csv"
                filepath = timeframe_dir / filename

                if filepath.exists():
                    df = pd.read_csv(filepath)
                    df["timestamp"] = pd.to_datetime(df["timestamp"])

                    # Validate checksums if present
                    if "checksum" in df.columns:
                        self._validate_checksums(df, symbol)

                    logger.info(
                        f"Loaded {len(df)} data points for {symbol} from {filepath}"
                    )
                    return df

            # Fallback: Find files with pattern (for backward compatibility)
            pattern = f"{symbol}_*.csv"
            if source:
                pattern = f"{symbol}_{source}*.csv"

            files = list(timeframe_dir.glob(pattern))

            if not files:
                logger.warning(f"No data files found for {symbol} ({timeframe})")
                return None

            # Get the most recent file
            latest_file = max(files, key=lambda x: x.stat().st_mtime)

            # Load data
            df = pd.read_csv(latest_file)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Validate checksums if present
            if "checksum" in df.columns:
                self._validate_checksums(df, symbol)

            # Ensure source column exists (for backward compatibility)
            if "source" not in df.columns:
                # Extract source from filename if not in data
                filename_parts = latest_file.stem.split("_")
                if len(filename_parts) >= 2:
                    df["source"] = filename_parts[1]
                else:
                    df["source"] = "unknown"

            logger.info(f"Loaded {len(df)} data points for {symbol} from {latest_file}")
            return df

        except Exception as e:
            logger.error(f"Failed to load latest data for {symbol}: {e}")
            return None

    def _validate_checksums(self, df: pd.DataFrame, symbol: str) -> None:
        """Validate row checksums"""
        invalid_count = 0
        for idx, row in df.iterrows():
            expected_checksum = self._calculate_row_checksum(row)
            if row.get("checksum") != expected_checksum:
                invalid_count += 1

        if invalid_count > 0:
            logger.warning(
                f"Found {invalid_count} rows with invalid checksums in {symbol}"
            )

    def load_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Load historical data for a symbol

        Args:
            symbol: Symbol identifier
            timeframe: Timeframe
            start_date: Start date filter
            end_date: End date filter
            source: Optional source filter

        Returns:
            DataFrame with historical data or None if not found
        """
        try:
            # Load latest data first
            df = self.load_latest_data(symbol, timeframe, source)

            if df is None or df.empty:
                return None

            # Apply date filters
            if start_date:
                df = df[df["timestamp"] >= start_date]

            if end_date:
                df = df[df["timestamp"] <= end_date]

            # Sort by timestamp
            df = df.sort_values("timestamp")

            logger.info(f"Loaded {len(df)} historical data points for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to load historical data for {symbol}: {e}")
            return None

    def append_market_data(self, market_data: MarketData) -> bool:
        """
        Append new market data to existing file (delegates to store_market_data)

        Args:
            market_data: MarketData object to append

        Returns:
            True if successful, False otherwise
        """
        # The store_market_data method now handles appending automatically
        return self.store_market_data(market_data)

    def list_available_symbols(
        self, timeframe: str, source: Optional[str] = None
    ) -> List[str]:
        """
        List available symbols for a timeframe

        Args:
            timeframe: Timeframe
            source: Optional source filter

        Returns:
            List of symbol identifiers
        """
        try:
            timeframe_dir = self.data_dir / timeframe

            if not timeframe_dir.exists():
                return []

            # Get all CSV files
            files = list(timeframe_dir.glob("*.csv"))

            symbols = set()
            for file in files:
                # Extract symbol from filename
                # Format: {symbol}_{source}_{timestamp}.csv
                parts = file.stem.split("_")
                if len(parts) >= 2:
                    symbol = parts[0]
                    file_source = parts[1] if len(parts) > 2 else None

                    if source is None or file_source == source:
                        symbols.add(symbol)

            return sorted(list(symbols))

        except Exception as e:
            logger.error(f"Failed to list available symbols: {e}")
            return []

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about stored data

        Returns:
            Dictionary with storage information
        """
        info = {
            "data_directory": str(self.data_dir),
            "timeframes": {},
            "total_files": 0,
            "total_size_mb": 0,
        }

        try:
            timeframes_list = STORAGE_CONFIG["timeframes"]
            for timeframe in timeframes_list:
                timeframe_dir = self.data_dir / timeframe

                if timeframe_dir.exists():
                    files = list(timeframe_dir.glob("*.csv"))
                    total_size = sum(f.stat().st_size for f in files)

                    info["timeframes"][timeframe] = {
                        "files": len(files),
                        "size_mb": round(total_size / (1024 * 1024), 2),
                        "symbols": self.list_available_symbols(timeframe),
                    }

                    info["total_files"] += len(files)
                    info["total_size_mb"] += total_size / (1024 * 1024)

            info["total_size_mb"] = round(info["total_size_mb"], 2)

        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")

        return info

    def get_source_for_symbol(self, symbol: str, timeframe: str) -> Optional[str]:
        """
        Get the data source for a specific symbol and timeframe

        Args:
            symbol: Symbol identifier
            timeframe: Timeframe

        Returns:
            Source name or None if not found
        """
        try:
            df = self.load_latest_data(symbol, timeframe)
            if df is not None and not df.empty and "source" in df.columns:
                return df["source"].iloc[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get source for {symbol}: {e}")
            return None

    def get_sources_for_timeframe(self, timeframe: str) -> Dict[str, str]:
        """
        Get all symbols and their sources for a timeframe

        Args:
            timeframe: Timeframe

        Returns:
            Dictionary mapping symbols to their sources
        """
        try:
            symbols = self.list_available_symbols(timeframe)
            symbol_sources = {}

            for symbol in symbols:
                source = self.get_source_for_symbol(symbol, timeframe)
                if source:
                    symbol_sources[symbol] = source

            return symbol_sources
        except Exception as e:
            logger.error(f"Failed to get sources for timeframe {timeframe}: {e}")
            return {}
