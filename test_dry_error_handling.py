"""
Test script to demonstrate the DRY error handling approach.
"""

import logging
from api.ig_client import IGClient
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
from core.logging_config import setup_logging
from core.exceptions import IGValidationError

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


def test_dry_error_handling():
    """Test the DRY error handling approach"""

    # Initialize client
    account_type = "demo"
    client = IGClient(
        base_url=BASE_URLS[account_type],
        api_key=API_KEYS[account_type],
        identifier=IDENTIFIERS[account_type],
        password=PASSWORDS[account_type],
    )

    print("🧪 Testing DRY Error Handling")
    print("=" * 40)

    # Test 1: Valid request (should work)
    print("\n1️⃣ Testing valid request...")
    try:
        accounts = client.accounts.get_accounts()
        print("✅ Valid request succeeded")
    except Exception as e:
        print(f"❌ Valid request failed: {e}")

    # Test 2: Validation error (should be caught by decorator)
    print("\n2️⃣ Testing validation error...")
    try:
        invalid_transactions = client.accounts.get_transactions(
            query_params={
                "type": "INVALID_TYPE",  # Invalid transaction type
                "pageSize": -1,  # Invalid page size
            }
        )
        print("❌ Validation error test failed - should have raised exception")
    except IGValidationError as e:
        print(f"✅ Validation error caught by decorator: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 3: Test dealing client with same pattern
    print("\n3️⃣ Testing dealing client...")
    try:
        positions = client.dealing.get_positions()
        print("✅ Dealing client request succeeded")
    except Exception as e:
        print(f"❌ Dealing client request failed: {e}")

    # Test 4: Test watchlists client with same pattern
    print("\n4️⃣ Testing watchlists client...")
    try:
        watchlists = client.watchlists.get_watchlists()
        print("✅ Watchlists client request succeeded")
    except Exception as e:
        print(f"❌ Watchlists client request failed: {e}")

    print("\n🎯 DRY error handling test completed!")
    print("\n📊 Benefits of DRY approach:")
    print("  • No repetitive try/catch blocks")
    print("  • Consistent error handling across all methods")
    print("  • Easy to modify error handling behavior")
    print("  • Clean, readable method implementations")
    print("  • Automatic logging for all operations")


if __name__ == "__main__":
    test_dry_error_handling()
