"""
Utility functions for data transformation
"""

import pandas as pd


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for visualization by standardizing column names

    Args:
        df: DataFrame with data collection column names

    Returns:
        DataFrame with standardized column names (open, high, low, close, volume)
    """
    result = df.copy()

    # Map column names to standard format
    column_mapping = {
        "openPrice": "open",
        "highPrice": "high",
        "lowPrice": "low",
        "closePrice": "close",
        "lastTradedVolume": "volume",
    }

    # Rename columns if they exist
    for old_col, new_col in column_mapping.items():
        if old_col in result.columns:
            result.rename(columns={old_col: new_col}, inplace=True)

    # Ensure timestamp is datetime
    if "timestamp" in result.columns:
        result["timestamp"] = pd.to_datetime(result["timestamp"])
        # Set as index for mplfinance compatibility, but keep columns accessible
        if result.index.name != "timestamp":
            result.set_index("timestamp", inplace=True)

    # Ensure required columns exist
    required_cols = ["open", "high", "low", "close"]
    missing_cols = [col for col in required_cols if col not in result.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {missing_cols}. "
            f"Available columns: {list(result.columns)}"
        )

    # Sort by timestamp
    result.sort_index(inplace=True)

    return result


def validate_ohlcv_data(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame has required OHLCV data

    Args:
        df: DataFrame to validate

    Returns:
        True if valid, raises ValueError otherwise
    """
    required_cols = ["open", "high", "low", "close"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Check for null values in required columns
    null_counts = df[required_cols].isnull().sum()
    if null_counts.any():
        raise ValueError(f"Null values found in required columns:\n{null_counts}")

    return True

