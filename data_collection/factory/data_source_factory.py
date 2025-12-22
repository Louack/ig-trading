"""
Factory for creating data sources
"""

import logging
from typing import Dict, List, Callable

from settings import secrets
from ..interfaces.data_source import DataSource
from ..sources.ig_data_source import IGDataSource
from ..sources.massive_data_source import MassiveDataSource
from ..sources.yfinance_data_source import YFinanceDataSource

logger = logging.getLogger(__name__)


class DataSourceFactory:
    """Factory for creating data source instances"""

    @classmethod
    def _get_available_configs(cls) -> Dict[str, Callable[[], DataSource]]:
        """
        Get mapping of source names to factory methods.

        Returns:
            Dictionary mapping source names to factory callables
        """
        return {
            "ig_demo": cls.create_ig_demo_data_source,
            "ig_prod": cls.create_ig_prod_data_source,
            "massive": cls.create_massive_data_source,
            "yfinance": cls.create_yfinance_data_source,
        }

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """
        Get list of available data source types

        Returns:
            List of available source types
        """
        return list(cls._get_available_configs().keys())

    @classmethod
    def create_multi_source(cls, source_names: List[str]) -> Dict[str, DataSource]:
        """
        Create multiple data sources from source names.

        Args:
            source_names: List of source names to create

        Returns:
            Dictionary mapping source names to DataSource instances
        """
        sources: Dict[str, DataSource] = {}
        available_configs = cls._get_available_configs()

        for source_name in set(source_names):
            if source_name not in available_configs:
                logger.warning(f"Unknown source name: {source_name}, skipping")
                continue
            try:
                sources[source_name] = available_configs[source_name]()
                logger.info(f"Created {source_name} data source")
            except Exception as e:
                logger.error(f"Failed to create {source_name} data source: {e}")

        return sources

    @classmethod
    def create_ig_demo_data_source(cls) -> IGDataSource:
        """Create IG demo account data source."""
        return IGDataSource(
            name="IG Demo",
            account_type="demo",
            base_url=secrets.ig_base_urls["demo"],
            api_key=secrets.ig_api_keys["demo"],
            identifier=secrets.ig_identifiers["demo"],
            password=secrets.ig_passwords["demo"],
        )

    @classmethod
    def create_ig_prod_data_source(cls) -> IGDataSource:
        """Create IG production account data source."""
        return IGDataSource(
            name="IG Prod",
            account_type="prod",
            base_url=secrets.ig_base_urls["prod"],
            api_key=secrets.ig_api_keys["prod"],
            identifier=secrets.ig_identifiers["prod"],
            password=secrets.ig_passwords["prod"],
        )

    @classmethod
    def create_massive_data_source(cls) -> MassiveDataSource:
        """Create Massive data source."""
        if not secrets.massive_api_key or secrets.massive_api_key == "dummy_key":
            raise ValueError("Massive API key is required and must be valid")
        return MassiveDataSource(
            api_key=secrets.massive_api_key,
            name="Massive",
            tier="free",
        )

    @classmethod
    def create_yfinance_data_source(cls) -> YFinanceDataSource:
        """Create YFinance data source."""
        return YFinanceDataSource(name="YFinance")
