"""
Configuration for data collection service
"""

INSTRUMENTS = {
    "forex": [
        "CS.D.EURUSD.CFD.IP",  # EUR/USD
        "CS.D.GBPUSD.CFD.IP",  # GBP/USD
        "CS.D.USDJPY.CFD.IP",  # USD/JPY
        "CS.D.USDCHF.CFD.IP",  # USD/CHF
        "CS.D.AUDUSD.CFD.IP",  # AUD/USD
        "CS.D.USDCAD.CFD.IP",  # USD/CAD
    ],
    "indices": [
        "IX.D.FTSE.IFE.IP",  # FTSE 100
        "IX.D.NASDAQ.IFE.IP",  # NASDAQ
        "IX.D.SP500.IFE.IP",  # S&P 500
        "IX.D.DAX.IFE.IP",  # DAX
        "IX.D.NIKKEI.IFE.IP",  # Nikkei
    ],
    "commodities": [
        "CC.D.CRUDEOIL.CFD.IP",  # Crude Oil
        "CC.D.GOLD.CFD.IP",  # Gold
        "CC.D.SILVER.CFD.IP",  # Silver
        "CC.D.COPPER.CFD.IP",  # Copper
    ],
}

# Timeframe configurations
TIMEFRAMES = {
    "hourly": {"resolution": "HOUR", "points": 168},
    "4hourly": {"resolution": "HOUR_4", "points": 168},
    "daily": {"resolution": "DAY", "points": 365},
}

# Storage configuration
STORAGE_CONFIG = {
    "base_dir": "data",
    "timeframes": ["hourly", "4hourly", "daily"],
    "format": "csv",
    "columns": {
        "metadata": [
            "epic",  # Instrument identifier
            "timeframe",  # Data timeframe
            "timestamp",  # Data timestamp
        ],
        "price_data": {
            "mid": [  # Mid prices (average of bid/ask)
                "openPrice_mid",  # Opening mid price
                "closePrice_mid",  # Closing mid price
                "highPrice_mid",  # Highest mid price
                "lowPrice_mid",  # Lowest mid price
            ],
            "bid": [  # Bid prices (what you get when selling)
                "openPrice_bid",  # Opening bid price
                "closePrice_bid",  # Closing bid price
                "highPrice_bid",  # Highest bid price
                "lowPrice_bid",  # Lowest bid price
            ],
            "ask": [  # Ask prices (what you pay when buying)
                "openPrice_ask",  # Opening ask price
                "closePrice_ask",  # Closing ask price
                "highPrice_ask",  # Highest ask price
                "lowPrice_ask",  # Lowest ask price
            ],
            "spread": [  # Spread (ask - bid)
                "openPrice_spread",  # Opening spread
                "closePrice_spread",  # Closing spread
                "highPrice_spread",  # Highest spread
                "lowPrice_spread",  # Lowest spread
            ],
        },
        "volume_data": [
            "lastTradedVolume",  # Volume for the period
        ],
    },
}
