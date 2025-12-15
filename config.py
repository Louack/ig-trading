"""
TOML configuration loading with Pydantic validation.

Loads and validates TOML files containing trading configuration.
"""

import logging
from typing import Dict, Any, List
import tomllib
from pydantic import BaseModel, Field, ValidationError, field_validator
from settings import trading_toml_path

logger = logging.getLogger(__name__)


class InstrumentStrategyConfig(BaseModel):
    """Strategy configuration nested within an instrument."""

    name: str = Field(..., min_length=1, max_length=100)
    timeframes: List[str] = Field(..., min_items=1)
    enabled: bool = Field(default=True)
    parameters: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)

    @field_validator("timeframes")
    def validate_timeframes(cls, v):
        """Validate timeframe format."""
        valid_formats = ["1H", "4H", "1D", "1W"]
        for tf in v:
            if tf not in valid_formats:
                raise ValueError(
                    f"Invalid timeframe: {tf}. Must be one of {valid_formats}"
                )
        return v


class InstrumentConfig(BaseModel):
    """Configuration for a financial instrument."""

    symbol: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    enabled: bool = Field(default=True)
    data_sources: List[str] = Field(..., min_items=1)
    strategies: List[InstrumentStrategyConfig] = Field(default_factory=list)


class TradingConfig(BaseModel):
    """Complete trading configuration."""

    instruments: List[InstrumentConfig] = Field(default_factory=list)


def get_available_strategies() -> Dict[str, str]:
    """
    Get mapping of strategy names to their class names.

    Returns:
        Dictionary mapping strategy str_name to class name
    """
    from strategies.implementations.golden_death_cross import GoldenDeathCrossStrategy

    return {
        GoldenDeathCrossStrategy.str_name: GoldenDeathCrossStrategy.__module__
        + "."
        + GoldenDeathCrossStrategy.__name__
    }


def get_available_data_sources() -> Dict[str, str]:
    """
    Get mapping of data source names to their class names.

    Returns:
        Dictionary mapping data source str_name to class name
    """
    from data_collection.sources.yfinance_data_source import YFinanceDataSource
    from data_collection.sources.ig_data_source import IGDataSource
    from data_collection.sources.massive_data_source import MassiveDataSource

    return {
        YFinanceDataSource.str_name: YFinanceDataSource.__module__
        + "."
        + YFinanceDataSource.__name__,
        IGDataSource.str_name: IGDataSource.__module__ + "." + IGDataSource.__name__,
        MassiveDataSource.str_name: MassiveDataSource.__module__
        + "."
        + MassiveDataSource.__name__,
    }


def load_config() -> TradingConfig:
    """
    Load and validate configuration from TOML file.

    Returns:
        Validated TradingConfig object

    Raises:
        FileNotFoundError: If config file not found
        ValidationError: If config file is invalid
        ValueError: If config file cannot be parsed
    """
    if not trading_toml_path.exists():
        raise FileNotFoundError(f"Config file not found: {trading_toml_path}")

    try:
        with open(trading_toml_path, "rb") as f:
            config_dict = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse TOML file: {e}")

    try:
        config = TradingConfig(**config_dict)
        total_strategies = sum(len(instr.strategies) for instr in config.instruments)
        logger.info(
            f"Successfully loaded config: {len(config.instruments)} instruments, "
            f"{total_strategies} strategy mappings"
        )
        return config
    except ValidationError as e:
        raise ValidationError(f"Configuration validation failed: {e}") from e


if __name__ == "__main__":
    with open("/home/loic/dev/ig-trading/trading.toml.test", "rb") as f:
        config_dict = tomllib.load(f)
        print(config_dict)

    print(get_available_data_sources())
