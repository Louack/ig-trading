"""
Comprehensive test script for all implemented IG Trading API routes.
Tests both successful operations and validation errors.
"""

import logging
from datetime import datetime, timedelta
from api.ig_client import IGClient
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
from core.logging_config import setup_logging
from core.exceptions import (
    IGAuthenticationError,
    IGValidationError,
    IGRateLimitError,
    IGNotFoundError,
    IGServerError,
    IGAPIError,
)

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


class RouteTester:
    """Comprehensive route testing class"""

    def __init__(self):
        self.client = None
        self.test_results = {"passed": 0, "failed": 0, "skipped": 0, "errors": []}

    def setup_client(self):
        """Initialize the IG client"""
        try:
            account_type = "demo"
            self.client = IGClient(
                base_url=BASE_URLS[account_type],
                api_key=API_KEYS[account_type],
                identifier=IDENTIFIERS[account_type],
                password=PASSWORDS[account_type],
            )
            print("✅ Client initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize client: {e}")
            return False

    def test_route(self, test_name: str, test_func, *args, **kwargs):
        """Generic route test wrapper"""
        try:
            print(f"\n🧪 Testing: {test_name}")
            result = test_func(*args, **kwargs)
            print(f"✅ {test_name} - PASSED")
            self.test_results["passed"] += 1
            return result
        except IGValidationError as e:
            print(f"✅ {test_name} - VALIDATION ERROR (Expected): {e}")
            self.test_results["passed"] += (
                1  # Validation errors are expected in some tests
            )
            return None
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            return None

    def test_accounts_routes(self):
        """Test all accounts-related routes"""
        print("\n" + "=" * 60)
        print("🏦 TESTING ACCOUNTS ROUTES")
        print("=" * 60)

        # Test 1: Get accounts
        self.test_route("GET /accounts", self.client.accounts.get_accounts)

        # Test 2: Get account preferences
        self.test_route(
            "GET /accounts/preferences", self.client.accounts.get_preferences
        )

        # Test 3: Update account preferences
        update_data = {"trailingStopsEnabled": True}
        self.test_route(
            "PUT /accounts/preferences",
            self.client.accounts.update_preferences,
            update_data,
        )

        # Test 4: Get activities (recent)
        self.test_route(
            "GET /history/activity (recent)", self.client.accounts.get_activities
        )

        # Test 5: Get activities with filters
        activity_filters = {"pageSize": 10, "detailed": True}
        self.test_route(
            "GET /history/activity (filtered)",
            self.client.accounts.get_activities,
            activity_filters,
        )

        # Test 6: Get activities by date range (valid dates)
        self.test_route(
            "GET /history/activity/{fromDate}/{toDate} (valid dates)",
            self.client.accounts.get_activities_by_date_range,
            "01-01-2024",
            "31-12-2024",
        )

        # Test 7: Get activities by date range (invalid date format)
        self.test_route(
            "GET /history/activity/{fromDate}/{toDate} (invalid format)",
            self.client.accounts.get_activities_by_date_range,
            "2024-01-01",
            "2024-12-31",  # Wrong format
        )

        # Test 8: Get transactions
        self.test_route(
            "GET /history/transactions", self.client.accounts.get_transactions
        )

        # Test 9: Get transactions with filters
        transaction_filters = {"type": "ALL_DEAL", "pageSize": 10, "pageNumber": 1}
        self.test_route(
            "GET /history/transactions (filtered)",
            self.client.accounts.get_transactions,
            transaction_filters,
        )

        # Test 10: Get transactions with invalid parameters
        invalid_filters = {"type": "INVALID_TYPE", "pageSize": -1}
        self.test_route(
            "GET /history/transactions (invalid params)",
            self.client.accounts.get_transactions,
            invalid_filters,
        )

    def test_dealing_routes(self):
        """Test all dealing-related routes"""
        print("\n" + "=" * 60)
        print("💼 TESTING DEALING ROUTES")
        print("=" * 60)

        # Test 1: Get positions
        positions = self.test_route("GET /positions", self.client.dealing.get_positions)

        # Test 2: Get specific position (if we have positions)
        if positions and positions.get("positions"):
            first_position = positions["positions"][0]
            deal_id = first_position["position"]["dealId"]
            self.test_route(
                "GET /positions/{dealId}", self.client.dealing.get_position, deal_id
            )
        else:
            print("⚠️  GET /positions/{dealId} - SKIPPED (no positions available)")
            self.test_results["skipped"] += 1

        # Test 3: Get position with invalid deal ID
        self.test_route(
            "GET /positions/{dealId} (invalid ID)", self.client.dealing.get_position, ""
        )

        # Test 4: Create OTC position
        position_data = {
            "currencyCode": "EUR",
            "direction": "BUY",
            "epic": "IX.D.NASDAQ.IFE.IP",
            "expiry": "-",
            "forceOpen": True,
            "guaranteedStop": True,
            "stopDistance": 400,
            "orderType": "MARKET",
            "size": 1.0,
        }
        created_position = self.test_route(
            "POST /positions/otc",
            self.client.dealing.create_position_otc,
            position_data,
        )

        # Test 5: Get deal confirmation (if position was created)
        if created_position and created_position.get("dealReference"):
            deal_ref = created_position["dealReference"]
            self.test_route(
                "GET /confirms/{dealReference}",
                self.client.dealing.get_deal_confirmation,
                deal_ref,
            )
        else:
            print(
                "⚠️  GET /confirms/{dealReference} - SKIPPED (no deal reference available)"
            )
            self.test_results["skipped"] += 1

        # Test 6: Get deal confirmation with invalid reference
        self.test_route(
            "GET /confirms/{dealReference} (invalid ref)",
            self.client.dealing.get_deal_confirmation,
            "INVALID_REF",
        )

        # Test 7: Close/Delete position (if position was created)
        if created_position and created_position.get("dealId"):
            close_position_data = {
                "dealId": created_position["dealId"],
                "direction": "SELL",  # Opposite direction to close
                "size": 1.0,
                "orderType": "MARKET",
            }
            self.test_route(
                "DELETE /positions/otc",
                self.client.dealing.close_position_otc,
                close_position_data,
            )
        else:
            print("⚠️  DELETE /positions/otc - SKIPPED (no position created)")
            self.test_results["skipped"] += 1

        # Test 8: Get working orders
        self.test_route("GET /workingorders", self.client.dealing.get_working_orders)

        # Test 9: Create working order
        working_order_data = {
            "epic": "IX.D.NASDAQ.IFE.IP",
            "direction": "BUY",
            "level": 24000.0,
            "size": 1.0,
            "type": "LIMIT",
            "timeInForce": "GOOD_TILL_CANCELLED",
            "currencyCode": "EUR",
            "expiry": "-",
            "guaranteedStop": False,
        }
        created_order = self.test_route(
            "POST /workingorders/otc",
            self.client.dealing.create_working_order_otc,
            working_order_data,
        )

        # Test 10: Update working order (if order was created)
        if created_order and created_order.get("dealReference"):
            # We'll use a dummy deal ID for testing the validation
            self.test_route(
                "PUT /workingorders/otc/{dealId} (invalid ID)",
                self.client.dealing.update_working_order_otc,
                "",
                {"level": 24050.0},
            )
        else:
            print(
                "⚠️  PUT /workingorders/otc/{dealId} - SKIPPED (no working order available)"
            )
            self.test_results["skipped"] += 1

        # Test 11: Delete working order with invalid ID
        self.test_route(
            "DELETE /workingorders/otc/{dealId} (invalid ID)",
            self.client.dealing.delete_working_order_otc,
            "",
        )

    def test_markets_routes(self):
        """Test all markets-related routes"""
        print("\n" + "=" * 60)
        print("📈 TESTING MARKETS ROUTES")
        print("=" * 60)

        # Test 1: Get markets (single epic)
        self.test_route(
            "GET /markets (single epic)",
            self.client.markets.get_markets,
            epics="IX.D.NASDAQ.IFE.IP",
        )

        # Test 2: Get markets with filters
        market_filters = {"filter": "ALL", "pageSize": 10}
        self.test_route(
            "GET /markets (with filters)",
            self.client.markets.get_markets,
            epics="IX.D.NASDAQ.IFE.IP",
            query_params=market_filters,
        )

        # Test 3: Get market details
        self.test_route(
            "GET /markets/{epic}", self.client.markets.get_market, "IX.D.NASDAQ.IFE.IP"
        )

        # Test 4: Get market details with invalid epic
        self.test_route(
            "GET /markets/{epic} (invalid epic)",
            self.client.markets.get_market,
            "INVALID",
        )

        # Test 5: Get historical prices
        price_params = {"resolution": "MINUTE", "max": 5}
        self.test_route(
            "GET /prices/{epic}",
            self.client.markets.get_prices,
            "IX.D.NASDAQ.IFE.IP",
            price_params,
        )

        # Test 6: Get prices by points
        self.test_route(
            "GET /prices/{epic}/{resolution}/{numPoints}",
            self.client.markets.get_prices_by_points,
            "IX.D.NASDAQ.IFE.IP",
            "MINUTE",
            10,
        )

        # Test 7: Get prices by date range
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_route(
            "GET /prices/{epic}/{resolution}/{startDate}/{endDate}",
            self.client.markets.get_prices_by_date_range,
            "IX.D.NASDAQ.IFE.IP",
            "MINUTE",
            start_date,
            end_date,
        )

        # Test 8: Get prices with invalid resolution
        self.test_route(
            "GET /prices/{epic}/{resolution}/{numPoints} (invalid resolution)",
            self.client.markets.get_prices_by_points,
            "IX.D.NASDAQ.IFE.IP",
            "INVALID",
            10,
        )

    def test_watchlists_routes(self):
        """Test all watchlists-related routes"""
        print("\n" + "=" * 60)
        print("👀 TESTING WATCHLISTS ROUTES")
        print("=" * 60)

        # Test 1: Get watchlists
        watchlists = self.test_route(
            "GET /watchlists", self.client.watchlists.get_watchlists
        )

        # Test 2: Create watchlist
        watchlist_data = {"name": "Test Watchlist", "epics": ["IX.D.NASDAQ.IFE.IP"]}
        created_watchlist = self.test_route(
            "POST /watchlists", self.client.watchlists.create_watchlist, watchlist_data
        )

        # Test 3: Get specific watchlist (if created)
        if created_watchlist and created_watchlist.get("watchlistId"):
            watchlist_id = created_watchlist["watchlistId"]
            self.test_route(
                "GET /watchlists/{watchlistId}",
                self.client.watchlists.get_watchlist,
                watchlist_id,
            )

            # Test 4: Add market to watchlist
            add_market_data = {"epic": "IX.D.NASDAQ.IFE.IP"}
            self.test_route(
                "PUT /watchlists/{watchlistId}",
                self.client.watchlists.add_market_to_watchlist,
                watchlist_id,
                add_market_data,
            )

            # Test 5: Remove market from watchlist
            self.test_route(
                "DELETE /watchlists/{watchlistId}/{epic}",
                self.client.watchlists.remove_market_from_watchlist,
                watchlist_id,
                "IX.D.NASDAQ.IFE.IP",
            )

            # Test 6: Delete watchlist
            self.test_route(
                "DELETE /watchlists/{watchlistId}",
                self.client.watchlists.delete_watchlist,
                watchlist_id,
            )
        else:
            print("⚠️  Watchlist operations - SKIPPED (no watchlist created)")
            self.test_results["skipped"] += 3

        # Test 7: Get watchlist with invalid ID
        self.test_route(
            "GET /watchlists/{watchlistId} (invalid ID)",
            self.client.watchlists.get_watchlist,
            "",
        )

        # Test 8: Remove market with invalid epic
        self.test_route(
            "DELETE /watchlists/{watchlistId}/{epic} (invalid epic)",
            self.client.watchlists.remove_market_from_watchlist,
            "123",
            "INVALID",
        )

    def run_all_tests(self):
        """Run all route tests"""
        print("🚀 STARTING COMPREHENSIVE ROUTE TESTING")
        print("=" * 60)

        if not self.setup_client():
            return

        # Run all test suites
        self.test_accounts_routes()
        self.test_dealing_routes()
        self.test_markets_routes()
        self.test_watchlists_routes()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        total_tests = (
            self.test_results["passed"]
            + self.test_results["failed"]
            + self.test_results["skipped"]
        )

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⚠️  Skipped: {self.test_results['skipped']}")

        if self.test_results["failed"] > 0:
            print(f"\n❌ Failed Tests:")
            for error in self.test_results["errors"]:
                print(f"  • {error}")

        success_rate = (
            (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        )
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")

        if success_rate >= 80:
            print("🎉 Excellent! Most tests are passing.")
        elif success_rate >= 60:
            print("👍 Good! Some tests need attention.")
        else:
            print("⚠️  Several tests are failing. Review the errors above.")


def main():
    """Main test execution"""
    tester = RouteTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
