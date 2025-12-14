"""
TOML configuration loading with Pydantic validation.

Loads and validates TOML files containing trading configuration.
"""

import logging
from typing import Dict, Any, List, Literal
import tomllib
from pydantic import BaseModel, Field, validator, ValidationError, field_validator
from settings import trading_toml_path

logger = logging.getLogger(__name__)


class StrategyConfig(BaseModel):
    """Configuration for a trading strategy."""
    name: str = Field(..., min_length=1, max_length=100)
    class_name: str = Field(..., min_length=1)


class DataSourceConfig(BaseModel):
    """Configuration for a data source."""
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal["ig", "massive", "yfinance"] = Field(...)


class StrategyMapping(BaseModel):
    """Mapping between instrument and strategy."""
    strategy: str = Field(..., min_length=1)
    timeframes: List[str] = Field(..., min_items=1)
    enabled: bool = Field(default=True)
    parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    @field_validator('timeframes')
    def validate_timeframes(cls, v):
        """Validate timeframe format."""
        valid_formats = ['1H', '4H', '1D', '1W']
        for tf in v:
            if tf not in valid_formats:
                raise ValueError(f'Invalid timeframe: {tf}. Must be one of {valid_formats}')
        return v


class InstrumentConfig(BaseModel):
    """Configuration for a financial instrument."""
    symbol: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)
    enabled: bool = Field(default=True)
    data_sources: List[str] = Field(..., min_items=1)
    strategy_mappings: List[StrategyMapping] = Field(default_factory=list)


class TradingConfig(BaseModel):
    """Complete trading configuration."""
    strategies: List[StrategyConfig] = Field(default_factory=list)
    data_sources: List[DataSourceConfig] = Field(default_factory=list)
    instruments: List[InstrumentConfig] = Field(default_factory=list)


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
        logger.info(f"Successfully loaded config: {len(config.strategies)} strategies, "
                   f"{len(config.data_sources)} data sources, {len(config.instruments)} instruments")
        return config
    except ValidationError as e:
        raise ValidationError(f"Configuration validation failed: {e}") from e
