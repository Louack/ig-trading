from typing import Dict, Any, Optional


# Default configurations for all strategies
DEFAULT_CONFIGS = {
    'golden_death_cross': {
        'name': 'Golden Cross / Death Cross',
        'timeframe': 'daily',  # Typically used on daily charts
        'short_ma_period': 50,   # 50-day moving average
        'long_ma_period': 200,   # 200-day moving average
        'confirmation_periods': 2,  # Wait 2 periods for confirmation
        'volume_filter': True,      # Use volume confirmation
        'rsi_filter': True,         # Use RSI filter
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70
    }
}


def get_strategy_config(strategy_name: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get strategy configuration with optional overrides
    
    Args:
        strategy_name: Name of the strategy
        overrides: Optional configuration overrides
        
    Returns:
        Strategy configuration dictionary
        
    Raises:
        ValueError: If strategy name is not found
    """
    if strategy_name not in DEFAULT_CONFIGS:
        available_strategies = list(DEFAULT_CONFIGS.keys())
        raise ValueError(f"Strategy '{strategy_name}' not found. Available strategies: {available_strategies}")
    
    config = DEFAULT_CONFIGS[strategy_name].copy()
    
    if overrides:
        config.update(overrides)
    
    return config


def list_available_strategies() -> list:
    """
    List all available strategy names
    
    Returns:
        List of strategy names
    """
    return list(DEFAULT_CONFIGS.keys())


def validate_strategy_config(strategy_name: str, config: Dict[str, Any]) -> bool:
    """
    Validate strategy configuration
    
    Args:
        strategy_name: Name of the strategy
        config: Configuration to validate
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    if strategy_name not in DEFAULT_CONFIGS:
        raise ValueError(f"Strategy '{strategy_name}' not found")
    
    base_config = DEFAULT_CONFIGS[strategy_name]
    
    # Check required fields
    required_fields = ['name', 'timeframe']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Required field '{field}' missing from configuration")
    
    # Strategy-specific validation
    if strategy_name == 'golden_death_cross':
        if 'short_ma_period' in config and 'long_ma_period' in config:
            if config['short_ma_period'] >= config['long_ma_period']:
                raise ValueError("short_ma_period must be less than long_ma_period")
        
        if 'rsi_oversold' in config and 'rsi_overbought' in config:
            if config['rsi_oversold'] >= config['rsi_overbought']:
                raise ValueError("rsi_oversold must be less than rsi_overbought")
    
    return True
