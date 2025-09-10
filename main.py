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
    # Example: Create OTC position
    body_data = {
        "currencyCode": "EUR",
        "direction": "BUY",
        "epic": "IX.D.NASDAQ.IFE.IP",
        "expiry": "-",
        "forceOpen": True,
        "guaranteedStop": True,
        "stopDistance": 400,
        "orderType": "MARKET",
        "size": 1,
    }

    created = client.create_position_otc(body_data=body_data)
    print(created)

    confirmation = client.get_deal_confirmation(deal_reference=created["dealReference"])
    print("Deal confirmation:", confirmation)

    positions = client.get_positions()
    print(positions)
    #
    # markets = client.get_markets(epics="IX.D.NASDAQ.IFE.IP", filter_type="ALL")
    # print("Multiple markets:", markets)
    #
    # # Example: Get single market details
    # single_market = client.get_market(epic="IX.D.NASDAQ.IFE.IP")
    # print("Single market:", single_market)
    #
    # Example: Get historical prices
    # prices = client.get_prices(epic="IX.D.NASDAQ.IFE.IP", query_params={"resolution": "MINUTE", "max": 5})
    # print("Historical prices:", prices)
    #
    # Example: Get historical prices by points
    # prices_by_points = client.get_prices_by_points(epic="IX.D.NASDAQ.IFE.IP", resolution="DAY", num_points=10)
    # print("Historical prices by points:", prices_by_points)
    # for price in prices_by_points["prices"]:
    #     print(price)
    
    # Example: Get historical prices by date range
    # prices_by_date = client.get_prices_by_date_range(
    #     epic="IX.D.NASDAQ.IFE.IP",
    #     resolution="HOUR_4",
    #     start_date="2025-09-01 00:00:00",
    #     end_date="2025-09-09 00:00:00"
    # )
    #
    # num = 0
    # for price in prices_by_date["prices"]:
    #     num += 1
    #     print(price)
    
    # Example: Close OTC position
    close_data = {
        "dealId": "DIAAAAUZTYEFZAH",  # Use actual deal ID from a position
        "direction": "SELL",    # Opposite of the original position direction
        "orderType": "MARKET",
        "size": 1,
    }
    closed = client.close_position_otc(body_data=close_data)
    print("Closed position:", closed)
