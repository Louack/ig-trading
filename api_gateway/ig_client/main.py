import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from api_gateway.ig_client.master_client import IGClient
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
from api_gateway.ig_client.core.logging_config import setup_logging, error_tracker
from api_gateway.ig_client.core import (
    IGAuthenticationError,
    IGValidationError,
    IGRateLimitError,
    IGNotFoundError,
    IGServerError,
    IGAPIError,
    IGNetworkError,
    IGTimeoutError,
)

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)


def handle_api_error(error: Exception, operation: str):
    """Centralized error handling for API operations"""
    error_tracker.track_error(error, {"operation": operation})

    if isinstance(error, IGAuthenticationError):
        logger.error(f"Authentication failed for {operation}: {error}")
        # Handle auth failure (refresh tokens, re-authenticate, etc.)
        return "AUTH_FAILED"

    elif isinstance(error, IGValidationError):
        logger.error(f"Validation error for {operation}: {error}")
        logger.error(f"Error details: {error.details}")
        # Handle validation errors (fix request parameters)
        return "VALIDATION_ERROR"

    elif isinstance(error, IGRateLimitError):
        logger.error(f"Rate limited for {operation}: {error}")
        # Handle rate limiting (wait, use different endpoint, etc.)
        return "RATE_LIMITED"

    elif isinstance(error, IGNotFoundError):
        logger.error(f"Resource not found for {operation}: {error}")
        # Handle not found errors
        return "NOT_FOUND"

    elif isinstance(error, IGServerError):
        logger.error(f"Server error for {operation}: {error}")
        # Handle server errors (retry later, contact support)
        return "SERVER_ERROR"

    elif isinstance(error, (IGNetworkError, IGTimeoutError)):
        logger.error(f"Network/timeout error for {operation}: {error}")
        # Handle network issues
        return "NETWORK_ERROR"

    elif isinstance(error, IGAPIError):
        logger.error(f"IG API error for {operation}: {error}")
        # Handle other IG-specific errors
        return "API_ERROR"

    else:
        logger.error(f"Unexpected error for {operation}: {error}")
        # Handle unexpected errors
        return "UNKNOWN_ERROR"


def main():
    """Main function with comprehensive error handling"""
    try:
        # Initialize client
        account_type = "demo"
        client = IGClient(
            base_url=BASE_URLS[account_type],
            api_key=API_KEYS[account_type],
            identifier=IDENTIFIERS[account_type],
            password=PASSWORDS[account_type],
        )

        logger.info("IG Client initialized successfully")

        # Example 1: Get accounts with error handling
        print("\n=== Getting Accounts ===")
        try:
            accounts = client.accounts.get_accounts()
            print("Accounts retrieved successfully:", accounts)
        except Exception as e:
            result = handle_api_error(e, "get_accounts")
            print(f"Failed to get accounts: {result}")

        # Example 2: Get account preferences with error handling
        print("\n=== Getting Account Preferences ===")
        try:
            preferences = client.accounts.get_preferences()
            print("Preferences retrieved successfully:", preferences)
        except Exception as e:
            result = handle_api_error(e, "get_preferences")
            print(f"Failed to get preferences: {result}")

        # Example 3: Update preferences with validation
        print("\n=== Updating Account Preferences ===")
        try:
            update_data = {"trailingStopsEnabled": True}
            updated_prefs = client.accounts.update_preferences(update_data)
            print("Preferences updated successfully:", updated_prefs)
        except Exception as e:
            result = handle_api_error(e, "update_preferences")
            print(f"Failed to update preferences: {result}")

        # Example 4: Get activities with error handling
        print("\n=== Getting Account Activities ===")
        try:
            activities = client.accounts.get_activities()
            print("Activities retrieved successfully:", activities)
        except Exception as e:
            result = handle_api_error(e, "get_activities")
            print(f"Failed to get activities: {result}")

        # Example 5: Get activities by date range with validation
        print("\n=== Getting Activities by Date Range ===")
        try:
            activities_by_date = client.accounts.get_activities_by_date_range(
                from_date="01-01-2024", to_date="31-12-2024"
            )
            print("Date range activities retrieved successfully:", activities_by_date)
        except Exception as e:
            result = handle_api_error(e, "get_activities_by_date_range")
            print(f"Failed to get date range activities: {result}")

        # Example 6: Get transactions with error handling
        print("\n=== Getting Transaction History ===")
        try:
            transactions = client.accounts.get_transactions()
            print("Transactions retrieved successfully:", transactions)
        except Exception as e:
            result = handle_api_error(e, "get_transactions")
            print(f"Failed to get transactions: {result}")

        # Example 7: Get filtered transactions
        print("\n=== Getting Filtered Transactions ===")
        try:
            transaction_filters = {"type": "ALL_DEAL", "pageSize": 10, "pageNumber": 1}
            filtered_transactions = client.accounts.get_transactions(
                query_params=transaction_filters
            )
            print(
                "Filtered transactions retrieved successfully:", filtered_transactions
            )
        except Exception as e:
            result = handle_api_error(e, "get_filtered_transactions")
            print(f"Failed to get filtered transactions: {result}")

        # Example 8: Demonstrate validation error handling
        print("\n=== Testing Validation Error Handling ===")
        try:
            # This should trigger a validation error
            invalid_transactions = client.accounts.get_transactions(
                query_params={
                    "type": "INVALID_TYPE",  # Invalid transaction type
                    "pageSize": -1,  # Invalid page size
                }
            )
        except Exception as e:
            result = handle_api_error(e, "test_validation")
            print(f"Validation error test result: {result}")

        # Print error summary
        print("\n=== Error Summary ===")
        error_summary = error_tracker.get_error_summary()
        print(f"Total errors encountered: {error_summary['total_errors']}")
        if error_summary["error_counts"]:
            print("Error breakdown:")
            for error_type, count in error_summary["error_counts"].items():
                print(f"  {error_type}: {count}")
        else:
            print("No errors encountered!")

    except Exception as e:
        logger.critical(f"Critical error in main: {e}", exc_info=True)
        print(f"Critical error: {e}")


if __name__ == "__main__":
    account_type = "demo"
    client = IGClient(
        base_url=BASE_URLS[account_type],
        api_key=API_KEYS[account_type],
        identifier=IDENTIFIERS[account_type],
        password=PASSWORDS[account_type],
    )

    logger.info("IG Client initialized successfully")

    positions = client.dealing.get_positions()
    print(positions)

    logger.info(f"{len(positions.positions)} position(s)")
    for position in positions.positions:
        logger.info(f"Position 1: dealID '{position.position.dealId}'")

    position = positions.positions[0].position
    deleted = client.dealing.close_position_otc(
        body_data={
            "dealId": position.dealId,
            "direction": "SELL",
            "orderType": "MARKET",
            "size": 1,
        }
    )
    print(deleted)
