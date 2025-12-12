"""
Test script to verify error handling implementation.
"""

import logging
from api_gateway.ig_client.master_client import IGClient
from settings import secrets
from api_gateway.ig_client.core.logging_config import setup_logging
from api_gateway.ig_client.core import (
    IGValidationError,
)

# Setup logging
setup_logging(level="DEBUG")
logger = logging.getLogger(__name__)


def test_error_handling():
    """Test various error scenarios"""

    # Initialize client
    account_type = "demo"
    client = IGClient(
        base_url=secrets.ig_base_urls[account_type],
        api_key=secrets.ig_api_keys[account_type],
        identifier=secrets.ig_identifiers[account_type],
        password=secrets.ig_passwords[account_type],
    )

    print("🧪 Testing Error Handling Implementation")
    print("=" * 50)

    # Test 1: Valid request (should work)
    print("\n1️⃣ Testing valid request...")
    try:
        accounts = client.accounts.get_accounts()
        print("✅ Valid request succeeded")
    except Exception as e:
        print(f"❌ Valid request failed: {e}")

    # Test 2: Invalid query parameters (should trigger validation error)
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
        print(f"✅ Validation error caught correctly: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 3: Invalid date format (should trigger validation error)
    print("\n3️⃣ Testing date format validation...")
    try:
        invalid_activities = client.accounts.get_activities_by_date_range(
            from_date="2024-01-01",  # Wrong format (should be dd-mm-yyyy)
            to_date="2024-12-31",
        )
        print("❌ Date format validation test failed - should have raised exception")
    except IGValidationError as e:
        print(f"✅ Date format validation error caught correctly: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 4: Test with correct date format
    print("\n4️⃣ Testing correct date format...")
    try:
        valid_activities = client.accounts.get_activities_by_date_range(
            from_date="01-01-2024",  # Correct format
            to_date="31-12-2024",
        )
        print("✅ Correct date format succeeded")
    except Exception as e:
        print(f"❌ Correct date format failed: {e}")

    print("\n🎯 Error handling test completed!")


if __name__ == "__main__":
    test_error_handling()
