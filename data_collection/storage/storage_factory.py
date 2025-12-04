"""
Factory for creating storage instances
"""

from typing import Dict, Any, Optional
from ..interfaces.storage import StorageInterface
from .csv_storage import CSVStorage

# Future imports for other storage types
# from .parquet_storage import ParquetStorage
# from .database_storage import DatabaseStorage


class StorageFactory:
    """Factory for creating storage instances"""

    @staticmethod
    def create_storage(storage_type: str = "csv", **kwargs) -> StorageInterface:
        """
        Create a storage instance

        Args:
            storage_type: Type of storage ('csv', 'parquet', 'database', etc.)
            **kwargs: Storage-specific configuration

        Returns:
            StorageInterface instance

        Raises:
            ValueError: If storage type is unknown
        """
        if storage_type == "csv":
            return CSVStorage(**kwargs)
        # elif storage_type == "parquet":
        #     return ParquetStorage(**kwargs)
        # elif storage_type == "database":
        #     return DatabaseStorage(**kwargs)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")
