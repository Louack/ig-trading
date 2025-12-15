# Trading Orchestrator

The Trading Orchestrator automates the complete trading pipeline based on the TOML configuration.

## Overview

The orchestrator performs the following steps for each configured instrument:

1. **Data Collection**: Fetches market data from configured sources for specified timeframes
2. **Strategy Execution**: Runs trading strategies on the collected data
3. **Signal Generation**: Analyzes data for trading signals
4. **Alert Notifications**: Sends alerts via Telegram when signals are generated

## Usage

### Basic Execution

```bash
# Run the complete orchestration pipeline
python -m orchestrator.trading_orchestrator
```

### With Environment Variables

```bash
# Set required environment variables
export MASSIVE_API_KEY="your_api_key"
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Run orchestrator
python -m orchestrator.trading_orchestrator
```

## Configuration

The orchestrator reads configuration from `trading.toml` as defined by the `TRADING_TOML_PATH` environment variable (defaults to `/etc/dev/ig_trading/trading.toml`).

### Example Configuration

```toml
[[strategies]]
name = "strategy_1"
class_name = "strategies.implementations.golden_death_cross.GoldenDeathCrossStrategy"

[[data_sources]]
name = "yfinance"
type = "yfinance"

[[instruments]]
symbol = "NDX"
name = "NASDAQ 100"
enabled = true
data_sources = ["yfinance"]
strategy_mappings = [
    {strategy = "strategy_1", timeframes = ["1D"], enabled = true}
]
```

## Features

- **TOML-Driven**: All configuration read from TOML files
- **Multi-Source**: Supports multiple data sources (YFinance, IG, Massive)
- **Multi-Strategy**: Runs multiple strategies per instrument
- **Multi-Timeframe**: Supports different timeframes per strategy
- **Telegram Alerts**: Sends real-time notifications for signals
- **Error Handling**: Robust error handling and logging
- **Date Simulation**: Can simulate running on specific dates (currently set to 2025-05-13)

## Data Flow

```
TOML Config → Data Collection → Strategy Execution → Signal Generation → Telegram Alerts
     ↓              ↓              ↓              ↓              ↓
 Instruments → Market Data → Trading Signals → Notifications → User
```

## Output

The orchestrator provides detailed logging and summary statistics:

```
=== Orchestration Summary ===
Data collection: X success, Y failed
Strategy executions: Z
Signals generated: A
Alerts sent: B
```
