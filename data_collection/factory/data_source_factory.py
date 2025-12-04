"""
Factory for creating data sources
"""

import logging
from typing import Dict, Any, Type, List
from ..interfaces.data_source import DataSource
from ..sources.ig_data_source import IGDataSource
from ..sources.massive_data_source import MassiveDataSource

logger = logging.getLogger(__name__)


class DataSourceFactory:
    """Factory for creating data source instances"""

    _sources: Dict[str, Type[DataSource]] = {
        "ig": IGDataSource,
        "massive": MassiveDataSource,
    }

    @classmethod
    def create_data_source(
        cls, source_type: str, config: Dict[str, Any], **dependencies: Any
    ) -> DataSource:
        """
        Create a data source instance

        Args:
            source_type: Type of data source ('ig', 'massive', etc.)
            config: Configuration for the data source
            **dependencies: Optional dependencies to inject (client, circuit_breaker, etc.)

        Returns:
            DataSource instance

        Raises:
            ValueError: If source type is not supported
        """
        if source_type not in cls._sources:
            available_sources = list(cls._sources.keys())
            raise ValueError(
                f"Unsupported data source type: {source_type}. Available: {available_sources}"
            )

        source_class = cls._sources[source_type]

        try:
            # Add source type to config
            config["source_type"] = source_type

            # Pass dependencies if provided, otherwise use config defaults
            source_instance = source_class(config, **dependencies)

            logger.info(f"Created {source_type} data source")
            return source_instance

        except Exception as e:
            logger.error(f"Failed to create {source_type} data source: {e}")
            raise

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """
        Get list of available data source types

        Returns:
            List of available source types
        """
        return list(cls._sources.keys())

    @classmethod
    def register_data_source(
        cls, source_type: str, source_class: Type[DataSource]
    ) -> None:
        """
        Register a new data source type

        Args:
            source_type: Type identifier for the data source
            source_class: DataSource class to register
        """
        if not issubclass(source_class, DataSource):
            raise ValueError(f"Source class must inherit from DataSource")

        cls._sources[source_type] = source_class
        logger.info(f"Registered data source: {source_type}")

    @classmethod
    def unregister_data_source(cls, source_type: str) -> None:
        """
        Unregister a data source type

        Args:
            source_type: Type identifier to unregister
        """
        if source_type in cls._sources:
            del cls._sources[source_type]
            logger.info(f"Unregistered data source: {source_type}")
        else:
            logger.warning(f"Data source {source_type} was not registered")

    @classmethod
    def create_multi_source(
        cls, configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, DataSource]:
        """
        Create multiple data sources from configurations

        Args:
            configs: Dictionary mapping source types to their configurations

        Returns:
            Dictionary mapping source types to DataSource instances
        """
        sources = {}

        for source_type, config in configs.items():
            try:
                sources[source_type] = cls.create_data_source(source_type, config)
            except Exception as e:
                logger.error(f"Failed to create {source_type} source: {e}")
                # Continue with other sources

        return sources
