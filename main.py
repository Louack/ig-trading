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

    # created = client.dealing.create_position_otc(body_data=body_data)
    # print(created)
    #
    # confirmation = client.dealing.get_deal_confirmation(
    #     deal_reference=created["dealReference"]
    # )
    # print("Deal confirmation:", confirmation)
    #
    # Example: Update OTC position (requires an existing position)
    update_data = {
        "limitLevel": 25000.0,
        "stopLevel": 23000.0,
        "guaranteedStop": False,
        "trailingStop": False
    }
    # # Replace 'DEAL_ID_HERE' with an actual deal ID from get_positions()
    # updated = client.dealing.update_position_otc(deal_id="DIAAAAUZTYEFZAH", body_data=update_data)
    # print("Updated position:", updated)
    # confirmation = client.dealing.get_deal_confirmation(
    #          deal_reference="XR3URSULNL2TZEB"
    #     )
    # print(confirmation)
    accounts = client.accounts.get_accounts()
    print(accounts)

    # Example: Get account preferences
    print("\n=== Getting Account Preferences ===")
    preferences = client.accounts.get_preferences()
    print("Account preferences:", preferences)

    # Example: Update account preferences
    print("\n=== Updating Account Preferences ===")
    update_preferences_data = {
        "trailingStopsEnabled": False  # Enable trailing stops
    }
    updated_preferences = client.accounts.update_preferences(body_data=update_preferences_data)
    print("Updated preferences:", updated_preferences)

    # Verify the update
    print("\n=== Verifying Updated Preferences ===")
    updated_prefs = client.accounts.get_preferences()
    print("Updated account preferences:", updated_prefs)

    # Example: Get account activities (recent activity)
    print("\n=== Getting Account Activities (Recent) ===")
    activities = client.accounts.get_activities()
    print("Recent activities:", activities)

    # Example: Get account activities with filters
    print("\n=== Getting Account Activities (Filtered) ===")
    activity_filters = {
        "pageSize": 10,
        "detailed": True
    }
    filtered_activities = client.accounts.get_activities(query_params=activity_filters)
    print("Filtered activities:", filtered_activities)

    # Example: Get account activities by date range (different endpoint)
    print("\n=== Getting Account Activities by Date Range ===")
    activities_by_date = client.accounts.get_activities_by_date_range(
        from_date="01-01-2024",
        to_date="31-12-2024"
    )
    print("Activities by date range:", activities_by_date)

    # Example: Get transaction history
    print("\n=== Getting Transaction History ===")
    transactions = client.accounts.get_transactions()
    print("Recent transactions:", transactions)

    # Example: Get transaction history with filters
    print("\n=== Getting Transaction History (Filtered) ===")
    transaction_filters = {
        "type": "ALL_DEAL",
        "pageSize": 10,
        "pageNumber": 1
    }
    filtered_transactions = client.accounts.get_transactions(query_params=transaction_filters)
    print("Filtered transactions:", filtered_transactions)

    positions = client.dealing.get_positions()
    print(positions)

    position = client.dealing.get_position(deal_id="DIAAAAUZTYEFZAH")
    print(position)

    # Example: Create working order
    # print("\n=== Creating Working Order ===")
    # working_order_data = {
    #     "currencyCode": "EUR",
    #     "direction": "BUY",
    #     "epic": "IX.D.NASDAQ.IFE.IP",
    #     "expiry": "-",
    #     "guaranteedStop": False,
    #     "level": 23500,
    #     "size": 1.0,
    #     "type": "LIMIT",
    #     "timeInForce": "GOOD_TILL_CANCELLED"
    # }
    # created_working_order = client.dealing.create_working_order_otc(body_data=working_order_data)
    # print("Created working order:", created_working_order)
    #
    # confirmation = client.dealing.get_deal_confirmation(
    #     deal_reference=created_working_order["dealReference"]
    # )
    # print("Deal confirmation:", confirmation)
    #
    # # Example: Get working orders
    # print("\n=== Getting Working Orders ===")
    # working_orders = client.dealing.get_working_orders()
    # print("Working orders:", working_orders)
    #
    # # Example: Update working order (if any exist)
    # if working_orders.get("workingOrders"):
    #     deal_id = working_orders["workingOrders"][0]["workingOrderData"]["dealId"]
    #     print(f"\n=== Updating Working Order {deal_id} ===")
    #     update_data = {
    #         "level": 23750.0,
    #         "type": "LIMIT",
    #         "timeInForce": "GOOD_TILL_CANCELLED"
    #     }
    #     updated_order = client.dealing.update_working_order_otc(deal_id=deal_id, body_data=update_data)
    #     print("Updated working order:", updated_order)
    #
    #     confirmation = client.dealing.get_deal_confirmation(
    #              deal_reference=updated_order["dealReference"]
    #         )
    #     print("Deal confirmation:", confirmation)
    #
    #     # Example: Delete working order
    #     print(f"\n=== Deleting Working Order {deal_id} ===")
    #     deleted_order = client.dealing.delete_working_order_otc(deal_id=deal_id)
    #     print("Deleted working order:", deleted_order)
    #     confirmation = client.dealing.get_deal_confirmation(
    #         deal_reference=deleted_order["dealReference"]
    #     )
    #     print("Deal confirmation:", confirmation)
    #
    # markets = client.markets.get_markets(epics="IX.D.NASDAQ.IFE.IP", filter_type="ALL")
    # print("Multiple markets:", markets)
    #
    # # Example: Get single market details
    # single_market = client.markets.get_market(epic="IX.D.NASDAQ.IFE.IP")
    # print("Single market:", single_market)
    #
    # # Example: Get historical prices
    # prices = client.markets.get_prices(
    #     epic="IX.D.NASDAQ.IFE.IP", query_params={"resolution": "MINUTE", "max": 5}
    # )
    # print("Historical prices:", prices)
    #
    # # Example: Get historical prices by points
    # prices_by_points = client.markets.get_prices_by_points(
    #     epic="IX.D.NASDAQ.IFE.IP", resolution="DAY", num_points=10
    # )
    # print("Historical prices by points:", prices_by_points)
    # for price in prices_by_points["prices"]:
    #     print(price)
    #
    # # Example: Get historical prices by date range
    # prices_by_date = client.markets.get_prices_by_date_range(
    #     epic="IX.D.NASDAQ.IFE.IP",
    #     resolution="HOUR_4",
    #     start_date="2025-09-01 00:00:00",
    #     end_date="2025-09-09 00:00:00",
    # )
    #
    # # num = 0
    # # for price in prices_by_date["prices"]:
    # #     num += 1
    # #     print(price)
    #
    # # Example: Close OTC position
    close_data = {
        "dealId": "DIAAAAU2UUSGVBD",
        "direction": "SELL",
        "orderType": "MARKET",
        "size": 1.0,
        "epic": 1,
        "expiry": 1,
        "level": 1,
        "quote_id": 1
    }
    # closed = client.dealing.close_position_otc(body_data=close_data)
    # print("Closed position:", closed)

    # Example: Get watchlists
    # print("\n=== Getting Watchlists ===")
    # watchlists = client.watchlists.get_watchlists()
    # print("Watchlists:", watchlists)
    #
    # # Example: Create watchlist
    # print("\n=== Creating Watchlist ===")
    # create_watchlist_data = {
    #     "name": "My Test Watchlist 1",
    #     "epics": ["IX.D.NASDAQ.IFE.IP", "IX.D.DAX.IFE.IP"]
    # }
    # created_watchlist = client.watchlists.create_watchlist(body_data=create_watchlist_data)
    # print("Created watchlist:", created_watchlist)
    #
    # # Use the created watchlist ID for further examples (if successful)
    # if created_watchlist.get("status") == "SUCCESS" and created_watchlist.get("watchlistId"):
    #     watchlist_id = created_watchlist["watchlistId"]
    #
    #     # Example: Get specific watchlist
    #     print(f"\n=== Getting Watchlist {watchlist_id} ===")
    #     watchlist_details = client.watchlists.get_watchlist(watchlist_id=watchlist_id)
    #     print("Watchlist details:", watchlist_details)
    #
    #     # Example: Add market to watchlist
    #     print(f"\n=== Adding Market to Watchlist {watchlist_id} ===")
    #     add_market_data = {
    #         "epic": "IX.D.FTSE.IFE.IP"
    #     }
    #     add_result = client.watchlists.add_market_to_watchlist(
    #         watchlist_id=watchlist_id,
    #         body_data=add_market_data
    #     )
    #     print("Add market result:", add_result)
    #
    #     # Example: Remove market from watchlist
    #     print(f"\n=== Removing Market from Watchlist {watchlist_id} ===")
    #     remove_result = client.watchlists.remove_market_from_watchlist(
    #         watchlist_id=watchlist_id,
    #         epic="IX.D.FTSE.IFE.IP"
    #     )
    #     print("Remove market result:", remove_result)
    #
    #     # Example: Delete watchlist
    #     print(f"\n=== Deleting Watchlist {watchlist_id} ===")
    #     delete_result = client.watchlists.delete_watchlist(watchlist_id=watchlist_id)
    #     print("Delete result:", delete_result)
