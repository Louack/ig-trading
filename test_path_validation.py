"""
Test script to demonstrate centralized path parameter validation.
"""

import logging
from api.ig_client import IGClient
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
from core.logging_config import setup_logging
from core.exceptions import IGValidationError

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


def test_path_validation():
    """Test centralized path parameter validation"""

    # Initialize client
    account_type = "demo"
    client = IGClient(
        base_url=BASE_URLS[account_type],
        api_key=API_KEYS[account_type],
        identifier=IDENTIFIERS[account_type],
        password=PASSWORDS[account_type],
    )

    print("🧪 Testing Centralized Path Parameter Validation")
    print("=" * 50)

    # Test 1: Valid date format (should work)
    print("\n1️⃣ Testing valid date format...")
    try:
        activities = client.accounts.get_activities_by_date_range(
            from_date="01-01-2024", to_date="31-12-2024"
        )
        print("✅ Valid date format succeeded")
    except Exception as e:
        print(f"❌ Valid date format failed: {e}")

    # Test 2: Invalid date format (should trigger validation error)
    print("\n2️⃣ Testing invalid date format...")
    try:
        activities = client.accounts.get_activities_by_date_range(
            from_date="2024-01-01",  # Wrong format (should be dd-mm-yyyy)
            to_date="2024-12-31",
        )
        print("❌ Invalid date format test failed - should have raised exception")
    except IGValidationError as e:
        print(f"✅ Date format validation error caught: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 3: Valid deal ID (should work)
    print("\n3️⃣ Testing valid deal ID...")
    try:
        position = client.dealing.get_position(deal_id="DIAAAAUZTYEFZAH")
        print("✅ Valid deal ID succeeded")
    except Exception as e:
        print(f"❌ Valid deal ID failed: {e}")

    # Test 4: Invalid deal ID (should trigger validation error)
    print("\n4️⃣ Testing invalid deal ID...")
    try:
        position = client.dealing.get_position(deal_id="")  # Empty deal ID
        print("❌ Invalid deal ID test failed - should have raised exception")
    except IGValidationError as e:
        print(f"✅ Deal ID validation error caught: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 5: Valid epic (should work)
    print("\n5️⃣ Testing valid epic...")
    try:
        watchlist = client.watchlists.remove_market_from_watchlist(
            watchlist_id="123", epic="IX.D.NASDAQ.IFE.IP"
        )
        print("✅ Valid epic succeeded")
    except Exception as e:
        print(f"❌ Valid epic failed: {e}")

    # Test 6: Invalid epic (should trigger validation error)
    print("\n6️⃣ Testing invalid epic...")
    try:
        watchlist = client.watchlists.remove_market_from_watchlist(
            watchlist_id="123",
            epic="INVALID",  # Too short, invalid format
        )
        print("❌ Invalid epic test failed - should have raised exception")
    except IGValidationError as e:
        print(f"✅ Epic validation error caught: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print("\n🎯 Path validation test completed!")
    print("\n📊 Benefits of centralized validation:")
    print("  • Consistent validation across all clients")
    print("  • Easy to modify validation rules in one place")
    print("  • Clear, descriptive error messages")
    print("  • No repetitive validation code in methods")
    print("  • Type-safe validation with proper error handling")


if __name__ == "__main__":
    test_path_validation()
