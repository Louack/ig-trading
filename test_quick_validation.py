"""
Quick validation test script for IG Trading API routes.
Tests basic functionality without creating/modifying data.
"""

import logging
from api_gateway.ig_client.master_client import IGClient
from settings import secrets
from api_gateway.ig_client.core.logging_config import setup_logging

# Setup logging
setup_logging(level="WARNING")  # Less verbose for quick tests
logger = logging.getLogger(__name__)


def quick_validation_test():
    """Quick validation of all read-only routes"""

    print("⚡ QUICK VALIDATION TEST - READ-ONLY ROUTES")
    print("=" * 50)

    # Initialize client
    try:
        account_type = "demo"
        client = IGClient(
            base_url=secrets.ig_base_urls[account_type],
            api_key=secrets.ig_api_keys[account_type],
            identifier=secrets.ig_identifiers[account_type],
            password=secrets.ig_passwords[account_type],
        )
        print("✅ Client initialized")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return

    tests = [
        # Accounts routes
        ("GET /accounts", lambda: client.accounts.get_accounts()),
        ("GET /accounts/preferences", lambda: client.accounts.get_preferences()),
        ("GET /history/activity", lambda: client.accounts.get_activities()),
        ("GET /history/transactions", lambda: client.accounts.get_transactions()),
        # Dealing routes
        ("GET /positions", lambda: client.dealing.get_positions()),
        ("GET /workingorders", lambda: client.dealing.get_working_orders()),
        # Markets routes
        (
            "GET /markets",
            lambda: client.markets.get_markets(epics="IX.D.NASDAQ.IFE.IP"),
        ),
        (
            "GET /markets/{epic}",
            lambda: client.markets.get_market("IX.D.NASDAQ.IFE.IP"),
        ),
        (
            "GET /prices/{epic}",
            lambda: client.markets.get_prices(
                "IX.D.NASDAQ.IFE.IP", {"resolution": "MINUTE", "max": 5}
            ),
        ),
        # Watchlists routes
        ("GET /watchlists", lambda: client.watchlists.get_watchlists()),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {str(e)[:100]}...")
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All read-only routes are working!")
    else:
        print("⚠️  Some routes need attention.")


def validation_error_test():
    """Test validation error handling"""

    print("\n🔍 VALIDATION ERROR TEST")
    print("=" * 30)

    try:
        account_type = "demo"
        client = IGClient(
            base_url=secrets.ig_base_urls[account_type],
            api_key=secrets.ig_api_keys[account_type],
            identifier=secrets.ig_identifiers[account_type],
            password=secrets.ig_passwords[account_type],
        )

        # Test validation errors
        validation_tests = [
            (
                "Invalid date format",
                lambda: client.accounts.get_activities_by_date_range(
                    "2024-01-01", "2024-12-31"
                ),
            ),
            ("Invalid deal ID", lambda: client.dealing.get_position("")),
            ("Invalid epic", lambda: client.markets.get_market("INVALID")),
            (
                "Invalid transaction type",
                lambda: client.accounts.get_transactions({"type": "INVALID_TYPE"}),
            ),
        ]

        for test_name, test_func in validation_tests:
            try:
                test_func()
                print(f"❌ {test_name}: Should have failed but didn't")
            except Exception as e:
                if "validation" in str(e).lower() or "invalid" in str(e).lower():
                    print(f"✅ {test_name}: Validation error caught")
                else:
                    print(f"⚠️  {test_name}: Unexpected error: {str(e)[:50]}...")

    except Exception as e:
        print(f"❌ Validation test setup failed: {e}")


def main():
    """Run quick validation tests"""
    quick_validation_test()
    validation_error_test()


if __name__ == "__main__":
    main()
