# Data Collection Module

Unified data collection framework for algorithmic trading system with production-grade resilience and monitoring features.

## Architecture

The module follows a layered architecture with strict separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│            Orchestration Layer                      │
│  UnifiedDataCollector + HealthMonitor              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│             Factory Pattern Layer                   │
│         DataSourceFactory + Validation             │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│           Implementation Layer                      │
│  IGDataSource (+ future: Yahoo, AlphaVantage)      │
│  with Resilience: Circuit Breaker, Rate Limiter    │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│             Storage Layer                           │
│  UnifiedDataStorage (Append-only + Checksums)      │
└─────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Resilience (Rule #4)**

All external API calls include:

- **Exponential Backoff with Jitter**: Prevents thundering herd problem
- **Retries**: Configurable retry attempts with exponential delays
- **Circuit Breaker**: Opens after threshold failures, prevents cascading failures
- **Rate Limiting**: Token bucket algorithm prevents API quota exhaustion
- **Timeouts**: All requests have configurable timeouts

Example configuration:
```python
{
    'timeout': 30,
    'max_retries': 3,
    'retry_base_delay': 1.0,
    'retry_max_delay': 30.0,
    'circuit_breaker_threshold': 5,
    'circuit_breaker_timeout': 60,
    'rate_limit_calls': 40,
    'rate_limit_period': 60
}
```

### 2. **Data Integrity (Rule #5)**

- **Append-Only Storage**: Data files never overwrite, only append
- **Atomic Writes**: Uses temporary files + atomic rename
- **Checksums**: MD5 checksums for each data row
- **Timestamp Validation**: Ensures monotonic, non-future timestamps
- **OHLC Validation**: Validates high >= {open, close, low}
- **Price Validation**: Ensures all prices are positive

### 3. **Error Escalation (Rule #6)**

- **No Silent Failures**: All errors logged with full context
- **Severity Levels**: LOW, MEDIUM, HIGH, CRITICAL
- **Alert Handlers**: Pluggable alert system (ready for Telegram/Slack/PagerDuty)
- **Error Context**: Rich error metadata for debugging

Example:
```python
from data_collection.alerting import alerting_service, AlertSeverity

# Register custom alert handler
def send_to_slack(alert):
    # Implementation to send to Slack
    pass

alerting_service.register_handler(send_to_slack)
```

### 4. **Health Monitoring**

Continuous monitoring of data source health:

- **Connection Status**: Checks if data source is connected
- **Availability Tests**: Verifies symbols and timeframes available
- **Success Rate Tracking**: Monitors consecutive failures
- **Health Status**: Detailed metrics per data source

```python
# Check health
health_status = collector.check_health()

# Get detailed status
detailed = collector.get_health_status()
# Returns:
{
    'ig_demo': {
        'source_name': 'IG Demo Account',
        'connected': True,
        'healthy': True,
        'consecutive_failures': 0,
        'success_rate': 98.5,
        ...
    }
}

# Get unhealthy sources
unhealthy = collector.get_unhealthy_sources()
```

### 5. **Configuration Validation**

Pydantic-based configuration validation:

- Type checking
- Range validation
- Required field validation
- Cross-field validation (e.g., max_delay >= base_delay)

```python
from data_collection.config_validation import validate_config

# Validates at startup - fails fast on invalid config
validated_config = validate_config(config_dict)
```

## Module Structure

```
data_collection/
├── __init__.py
├── config.py                    # Instruments and timeframe configurations
├── main_unified.py              # Entry point with examples
├── unified_data_collector.py    # Main orchestrator
│
├── interfaces/                  # Abstract contracts
│   ├── data_source.py          # DataSource interface
│   └── market_data.py          # Unified data models
│
├── sources/                     # Data source implementations
│   └── ig_data_source.py       # IG Markets implementation
│
├── factory/                     # Factory pattern
│   └── data_source_factory.py # Creates data sources
│
├── storage/                     # Persistence layer
│   └── unified_data_storage.py # Append-only CSV storage
│
├── validation.py               # Data validation utilities
├── resilience.py               # Circuit breaker, rate limiter, retries
├── alerting.py                 # Error escalation system
├── health.py                   # Health monitoring
└── config_validation.py        # Pydantic configuration models
```

## Usage

### Basic Example

```python
from data_collection.unified_data_collector import UnifiedDataCollector
from data_collection.config_validation import validate_config

config = {
    'data_sources': {
        'ig_demo': {
            'type': 'ig',
            'name': 'IG Demo Account',
            'account_type': 'demo',
            'timeout': 30,
            'max_retries': 3
        }
    },
    'enable_health_checks': True
}

# Validate configuration
validated_config = validate_config(config)

# Initialize collector
collector = UnifiedDataCollector(
    validated_config.data_sources,
    enable_health_monitoring=True
)

# Collect and store data
success = collector.collect_and_store(
    symbol="IX.D.FTSE.IFM.IP",
    timeframe="1D"
)

# Load stored data
df = collector.load_data("IX.D.FTSE.IFM.IP", "1D")
```

### Context Manager

```python
with UnifiedDataCollector(config['data_sources']) as collector:
    # Collect data
    data = collector.collect_data_for_symbol("IX.D.FTSE.IFM.IP", "1D")
    
    # Store data
    if data:
        collector.store_data(data)

# Automatically disconnects on exit
```

### Health Monitoring

```python
# Periodic health checks
import time

while True:
    # Check health
    health = collector.check_health()
    
    # Alert if unhealthy
    unhealthy = collector.get_unhealthy_sources()
    if unhealthy:
        logger.warning(f"Unhealthy sources: {unhealthy}")
    
    time.sleep(300)  # Check every 5 minutes
```

## Data Models

### MarketData

Unified representation of market data across all sources:

```python
@dataclass
class MarketData:
    symbol: str              # Instrument identifier
    timeframe: str           # Time interval
    data_points: List[MarketDataPoint]
    source: str              # Data provider
    collected_at: datetime
    metadata: Dict[str, Any]
```

### MarketDataPoint

Single OHLCV candle:

```python
@dataclass
class MarketDataPoint:
    timestamp: datetime
    open_price: PriceData   # bid/ask/mid
    high_price: PriceData
    low_price: PriceData
    close_price: PriceData
    volume: Optional[int]
    metadata: Dict[str, Any]
```

### PriceData

Bid/ask/mid price data with automatic mid calculation:

```python
@dataclass
class PriceData:
    bid: Optional[float]
    ask: Optional[float]
    mid: Optional[float]    # Auto-calculated if not provided
```

## Storage Format

Data stored in append-only CSV files:

**Directory Structure:**
```
data/
├── hourly/
│   ├── IX.D.FTSE.IFM.IP_IG.csv
│   └── CS.D.EURUSD.CFD.IP_IG.csv
├── 4hourly/
│   └── ...
└── daily/
    └── ...
```

**CSV Format:**
```csv
symbol,timeframe,source,timestamp,openPrice,highPrice,lowPrice,closePrice,lastTradedVolume,checksum
IX.D.FTSE.IFM.IP,1D,IG,2025-01-15T00:00:00,7500.0,7520.0,7490.0,7510.0,50000,a3b2c1d4
```

**Checksum**: MD5 hash of (timestamp + OHLC prices) ensures data integrity

## Resilience Features

### Circuit Breaker States

```
CLOSED → (failures ≥ threshold) → OPEN
   ↑                                 ↓
   └──── (recovery timeout) ── HALF_OPEN
```

- **CLOSED**: Normal operation
- **OPEN**: Reject all requests (fail fast)
- **HALF_OPEN**: Test if service recovered

### Rate Limiting

Token bucket algorithm:
- Tracks requests in sliding window
- Blocks when limit reached
- Non-blocking `try_acquire()` available

### Retry Strategy

Exponential backoff with jitter:
```
delay = min(base_delay * 2^attempt, max_delay) * random(0, 1)
```

Example delays with base=1s, max=30s:
- Attempt 1: 0.0-1.0s
- Attempt 2: 0.0-2.0s
- Attempt 3: 0.0-4.0s

## Adding New Data Sources

1. **Create implementation** in `sources/`:

```python
from ..interfaces.data_source import DataSource
from ..resilience import CircuitBreaker, RateLimiter

class YahooDataSource(DataSource):
    def __init__(self, config):
        super().__init__(config)
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter(100, 60)
    
    def connect(self) -> bool:
        # Implementation
        pass
    
    def fetch_historical_data(self, ...) -> MarketData:
        # Implementation with resilience
        self.rate_limiter.acquire()
        return self.circuit_breaker.call(self._fetch, ...)
```

2. **Register in factory**:

```python
from ..sources.yahoo_data_source import YahooDataSource

DataSourceFactory._sources['yahoo'] = YahooDataSource
```

3. **Add config validation**:

```python
class YahooDataSourceConfig(DataSourceConfig):
    type: Literal['yahoo'] = Field(default='yahoo')
    # Add yahoo-specific fields
```

## Testing

Run the unified collector:

```bash
python -m data_collection.main_unified
```

Expected output:
- Configuration validation
- Data source initialization
- Health checks
- Data collection and storage
- Storage verification

## Configuration Reference

### Data Source Config

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Display name |
| `type` | str | Required | 'ig', 'yahoo', etc. |
| `timeout` | int | 30 | Request timeout (seconds) |
| `max_retries` | int | 3 | Maximum retry attempts |
| `retry_base_delay` | float | 1.0 | Base retry delay |
| `retry_max_delay` | float | 30.0 | Maximum retry delay |
| `circuit_breaker_threshold` | int | 5 | Failures before opening |
| `circuit_breaker_timeout` | int | 60 | Recovery wait time |
| `rate_limit_calls` | int | 40 | Max calls per period |
| `rate_limit_period` | int | 60 | Rate limit window |

### Storage Config

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_dir` | str | 'data' | Storage directory |
| `format` | str | 'csv' | File format |
| `enable_checksums` | bool | True | Add checksums |
| `atomic_writes` | bool | True | Use atomic writes |

## Best Practices

1. **Always validate configuration** before initializing collector
2. **Use context manager** for automatic cleanup
3. **Enable health monitoring** in production
4. **Set appropriate rate limits** based on API quotas
5. **Monitor unhealthy sources** and alert
6. **Register alert handlers** for production environments
7. **Use append-only storage** for replayability
8. **Validate data** before trading decisions

## Future Enhancements

- [ ] Parquet storage format for better compression
- [ ] Data deduplication strategies
- [ ] Automatic data gap detection and filling
- [ ] Streaming data support (WebSocket)
- [ ] Multi-source aggregation
- [ ] Data quality metrics
- [ ] Automated failover between sources
- [ ] Distributed storage backends (S3, PostgreSQL)

## Compliance with Project Rules

✅ **Rule #2**: Strict separation between modules  
✅ **Rule #3**: No hardcoded secrets (environment variables)  
✅ **Rule #4**: Timeouts, retries, backoff, circuit breakers  
✅ **Rule #5**: Append-only storage, timestamp validation, checksums  
✅ **Rule #6**: No silent failures, error escalation  
✅ **Rule #7**: Comprehensive docstrings, self-explanatory code  

## License

Part of the IG Trading algorithmic trading system.

