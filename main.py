from api.ig_client import IGClient
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS

if __name__ == "__main__":
    account_type = "demo"
    client = IGClient(
        base_url=BASE_URLS[account_type],
        api_key=API_KEYS[account_type],
        identifier=IDENTIFIERS[account_type],
        password=PASSWORDS[account_type],
    )
    body_data = {
        "currencyCode": "GBP",
        "direction": "BUY",
        "epic": "CS.D.EURUSD.CFD.IP",
        "expiry": "DFB",
        "forceOpen": True,
        "guaranteedStop": False,
        "orderType": "MARKET",
        "size": 1,
    }
    created = client.create_position_otc(body_data)
    print(created)
