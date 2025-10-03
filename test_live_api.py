import logging

from api_gateway.ig_client.core.logging_config import setup_logging
from api_gateway.ig_client.master_client import IGClient
from api_gateway.ig_client.utils import create_position_and_wait_for_confirmation
from api_gateway.ig_client.utils.deal_helpers import (
    close_position_and_wait_for_confirmation,
)
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS

setup_logging(level="INFO")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    account_type = "demo"
    client = IGClient(
        base_url=BASE_URLS[account_type],
        api_key=API_KEYS[account_type],
        identifier=IDENTIFIERS[account_type],
        password=PASSWORDS[account_type],
    )

    logger.info("IG Client initialized successfully")

    epics = {
        "IX.D.NASDAQ.IFM.IP": {
            "currencyCode": "USD",
            "direction": "BUY",
            "epic": "IX.D.NASDAQ.IFM.IP",
            "expiry": "-",
            "forceOpen": True,
            "guaranteedStop": False,
            "orderType": "MARKET",
            "size": 1,
        },
    }
    markets = client.markets.get_markets(epics=",".join(epics.keys()))
    print(markets)
    for body in epics.values():
        deal_result = create_position_and_wait_for_confirmation(
            dealing_client=client.dealing, body_data=body
        )
        print(deal_result)

    positions = client.dealing.get_positions()
    for position in positions.positions:
        if position.market.epic not in epics.keys():
            continue
        body = {
            "dealId": position.position.dealId,
            "direction": "SELL",
            "orderType": "MARKET",
            "size": 1,
        }
        deal_result = close_position_and_wait_for_confirmation(
            dealing_client=client.dealing, body_data=body
        )
