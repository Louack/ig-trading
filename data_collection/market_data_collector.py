"""
Market data collection service
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from api_gateway.ig_client.master_client import IGClient
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
from config import INSTRUMENTS, TIMEFRAMES

logger = logging.getLogger(__name__)


class MarketDataCollector:
    """Collects market data for systematic trading strategies"""

    def __init__(self, account_type: str = "demo"):
        self.client = IGClient(
            base_url=BASE_URLS[account_type],
            api_key=API_KEYS[account_type],
            identifier=IDENTIFIERS[account_type],
            password=PASSWORDS[account_type],
        )

        self.instruments = INSTRUMENTS
        self.timeframes = TIMEFRAMES

    def collect_data_for_instrument(
        self, epic: str, timeframe: str
    ) -> Optional[Dict[str, Any]]:
        """Collect historical data for a specific instrument and timeframe"""
        try:
            config = self.timeframes[timeframe]

            response = self.client.markets.get_prices_by_points(
                epic=epic, resolution=config["resolution"], num_points=config["points"]
            )

            data = response.model_dump()

            logger.info(
                f"Collected {len(data['prices'])} data points for {epic} ({timeframe})"
            )
            return {
                "epic": epic,
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }

        except Exception as e:
            logger.error(f"Failed to collect data for {epic} ({timeframe}): {e}")
            return None

    def collect_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Collect data for all instruments and timeframes"""
        all_data = {}

        for category, epics in self.instruments.items():
            all_data[category] = []

            for epic in epics:
                for timeframe in self.timeframes.keys():
                    data = self.collect_data_for_instrument(epic, timeframe)
                    if data:
                        all_data[category].append(data)

        return all_data

    def collect_data_for_category(
        self, category: str, timeframe: str
    ) -> List[Dict[str, Any]]:
        """Collect data for a specific category and timeframe"""
        if category not in self.instruments:
            logger.error(f"Unknown category: {category}")
            return []

        data_list = []
        for epic in self.instruments[category]:
            data = self.collect_data_for_instrument(epic, timeframe)
            if data:
                data_list.append(data)

        return data_list
