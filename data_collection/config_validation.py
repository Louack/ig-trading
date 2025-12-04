"""
Configuration validation using Pydantic
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class DataSourceConfig(BaseModel):
    """Base configuration for data sources"""
    
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal['ig', 'massive'] = Field(...)
    
    # Resilience configuration
    timeout: int = Field(default=30, gt=0, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_base_delay: float = Field(default=1.0, gt=0, le=60)
    retry_max_delay: float = Field(default=30.0, gt=0, le=300)
    
    # Circuit breaker configuration
    circuit_breaker_threshold: int = Field(default=5, ge=1, le=20)
    circuit_breaker_timeout: int = Field(default=60, ge=10, le=600)
    
    # Rate limiting configuration
    rate_limit_calls: int = Field(default=40, ge=1, le=1000)
    rate_limit_period: int = Field(default=60, ge=1, le=3600)
    
    @field_validator('retry_max_delay')
    @classmethod
    def validate_max_delay(cls, v: float, info) -> float:
        """Ensure max_delay >= base_delay"""
        if 'retry_base_delay' in info.data and v < info.data['retry_base_delay']:
            raise ValueError('retry_max_delay must be >= retry_base_delay')
        return v


class IGDataSourceConfig(DataSourceConfig):
    """Configuration specific to IG data source"""
    
    type: Literal['ig'] = Field(default='ig')
    account_type: Literal['demo', 'prod'] = Field(...)
    
    @field_validator('account_type')
    @classmethod
    def validate_account_type(cls, v: str) -> str:
        """Validate account type"""
        if v not in ['demo', 'prod']:
            raise ValueError("account_type must be 'demo' or 'prod'")
        return v


class MassiveDataSourceConfig(DataSourceConfig):
    """Configuration specific to Massive data source"""
    
    type: Literal['massive'] = Field(default='massive')
    api_key: str = Field(..., min_length=1)
    tier: Literal['free', 'starter', 'developer', 'advanced'] = Field(default='free')
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format"""
        if not v or len(v) < 10:
            raise ValueError("Invalid Massive API key")
        return v


class StorageConfig(BaseModel):
    """Configuration for data storage"""
    
    base_dir: str = Field(default='data', min_length=1)
    format: Literal['csv', 'parquet'] = Field(default='csv')
    compression: Optional[str] = Field(default=None)
    enable_checksums: bool = Field(default=True)
    atomic_writes: bool = Field(default=True)


class CollectorConfig(BaseModel):
    """Configuration for data collector"""
    
    data_sources: Dict[str, Dict[str, Any]] = Field(...)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    enable_health_checks: bool = Field(default=True)
    health_check_interval: int = Field(default=300, ge=60, le=3600)
    
    @field_validator('data_sources')
    @classmethod
    def validate_data_sources(cls, v: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Validate data source configurations"""
        if not v:
            raise ValueError('At least one data source must be configured')
        
        # Validate each data source config
        for source_name, source_config in v.items():
            source_type = source_config.get('type')
            
            if source_type == 'ig':
                IGDataSourceConfig(**source_config)
            elif source_type == 'massive':
                MassiveDataSourceConfig(**source_config)
            else:
                raise ValueError(f"Unknown data source type: {source_type}")
        
        return v


def validate_config(config: Dict[str, Any]) -> CollectorConfig:
    """
    Validate collector configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated CollectorConfig object
        
    Raises:
        ValidationError: If configuration is invalid
    """
    return CollectorConfig(**config)


def validate_data_source_config(source_type: str, config: Dict[str, Any]) -> DataSourceConfig:
    """
    Validate data source configuration
    
    Args:
        source_type: Type of data source
        config: Configuration dictionary
        
    Returns:
        Validated DataSourceConfig object
        
    Raises:
        ValidationError: If configuration is invalid
    """
    if source_type == 'ig':
        return IGDataSourceConfig(**config)
    elif source_type == 'massive':
        return MassiveDataSourceConfig(**config)
    else:
        raise ValueError(f"Unknown data source type: {source_type}")

