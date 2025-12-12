"""
Unified application configuration using Pydantic.

This module provides type-safe configuration management for the trading system.
All configuration is validated at runtime with helpful error messages.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal

from pydantic import BaseModel, Field, field_validator


class LoggingConfig(BaseModel):
    """Configuration for logging system."""

    level: str = Field(default="INFO", description="Log level")
    format: Literal["plain", "json"] = Field(default="plain", description="Log format")
    dest: Literal["stdout", "stderr", "file"] = Field(
        default="stdout", description="Log destination"
    )
    file: Optional[str] = Field(
        default=None, description="Log file path (when dest='file')"
    )

    # Log rotation configuration
    max_file_size: int = Field(default=10*1024*1024, description="Maximum log file size in bytes (10MB default)")
    backup_count: int = Field(default=5, description="Number of backup files to keep")
    rotate_on_startup: bool = Field(default=True, description="Rotate log file on application startup")


class OrchestratorConfig(BaseModel):
    """Configuration for the main orchestrator."""

    symbol: str = Field(default="NDX", description="Default trading symbol")
    timeframe: str = Field(default="1D", description="Default timeframe")
    data_path: str = Field(
        default_factory=lambda: str(Path("data_collection/data/1D/NDX_YFinance.csv")),
        description="Default data file path",
    )
    instrument_type: str = Field(default="INDEX", description="Instrument type")
    source: str = Field(default="YFinance", description="Default data source")
    as_of: Optional[str] = Field(
        default=None, description="As-of date for historical data"
    )


class StrategyConfig(BaseModel):
    """Configuration for individual trading strategies."""

    name: str = Field(..., description="Unique strategy name")
    class_name: str = Field(
        ...,
        description="Full class path (e.g., 'strategies.implementations.golden_death_cross.GoldenDeathCrossStrategy')",
    )
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Strategy-specific parameters"
    )
    window: Optional[int] = Field(
        default=None, description="Data window size for strategy"
    )
    latest_only: bool = Field(
        default=True, description="Only generate signals for latest data"
    )

    @field_validator("class_name")
    @classmethod
    def validate_class_name(cls, v: str) -> str:
        """Ensure class_name is a valid module path."""
        if not v or "." not in v:
            raise ValueError(
                "class_name must be a full module path (e.g., 'module.ClassName')"
            )
        return v


class DispatchConfig(BaseModel):
    """Configuration for signal dispatching."""

    min_strength: Optional[float] = Field(
        default=None, description="Minimum signal strength threshold"
    )
    allowed_instruments: Optional[List[str]] = Field(
        default=None, description="Allowed instrument symbols"
    )
    allowed_strategies: Optional[List[str]] = Field(
        default=None, description="Allowed strategy names"
    )
    dedupe: bool = Field(default=True, description="Remove duplicate signals")
    transports: List[str] = Field(
        default_factory=lambda: ["console"], description="Enabled transport types"
    )


class DataCollectionConfig(BaseModel):
    """Configuration for data collection system."""

    data_sources: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Data source configurations"
    )
    storage: Dict[str, Any] = Field(
        default_factory=lambda: {
            "base_dir": "data",
            "format": "csv",
            "enable_checksums": True,
            "atomic_writes": True,
        },
        description="Storage configuration",
    )
    enable_health_checks: bool = Field(
        default=False, description="Enable health monitoring"
    )


class IGAPIConfig(BaseModel):
    """Configuration for IG API connections."""

    account_type: Literal["demo", "prod"] = Field(
        default="demo", description="IG account type"
    )


class AppConfig(BaseModel):
    """Main application configuration."""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    orchestrator: OrchestratorConfig = Field(default_factory=OrchestratorConfig)
    strategies: List[StrategyConfig] = Field(default_factory=list)
    dispatch: DispatchConfig = Field(default_factory=DispatchConfig)
    data_collection: DataCollectionConfig = Field(default_factory=DataCollectionConfig)
    ig_api: IGAPIConfig = Field(default_factory=IGAPIConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration with environment variable overrides."""
        # Start with defaults
        config = cls()

        # Override with environment variables
        config.logging.level = os.getenv("LOG_LEVEL", config.logging.level)
        config.logging.format = os.getenv("LOG_FORMAT", config.logging.format)  # type: ignore
        config.logging.dest = os.getenv("LOG_DEST", config.logging.dest)  # type: ignore
        config.logging.file = os.getenv("LOG_FILE") or config.logging.file

        config.orchestrator.symbol = os.getenv(
            "DEFAULT_SYMBOL", config.orchestrator.symbol
        )
        config.orchestrator.timeframe = os.getenv(
            "DEFAULT_TIMEFRAME", config.orchestrator.timeframe
        )

        # Set default data path based on symbol/timeframe if not overridden
        if not os.getenv("DATA_PATH"):
            symbol = config.orchestrator.symbol
            timeframe = config.orchestrator.timeframe
            config.orchestrator.data_path = str(
                Path("data_collection") / "data" / timeframe / f"{symbol}_YFinance.csv"
            )

        # Add default strategy if none configured
        if not config.strategies:
            config.strategies = [
                StrategyConfig(
                    name="golden_death_cross_20_50",
                    class_name="strategies.implementations.golden_death_cross.GoldenDeathCrossStrategy",
                    params={
                        "name": "golden_death_cross_20_50",
                        "timeframe": "1D",
                        "short_ma_period": 20,
                        "long_ma_period": 50,
                        "confirmation_periods": 2,
                        "volume_filter": False,
                        "volume_sma_period": 20,
                        "rsi_filter": False,
                        "rsi_period": 14,
                        "rsi_oversold": 30,
                        "rsi_overbought": 70,
                    },
                    window=max(50, 20, 2) + 5,
                    latest_only=True,
                )
            ]

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Create from dictionary for backward compatibility."""
        return cls.model_validate(data)
