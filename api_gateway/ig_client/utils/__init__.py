"""
Utility functions for IG Trading API client.

This module contains helper functions for common operations like deal confirmation polling,
position management, and other business logic that extends beyond simple API calls.
"""

from .deal_helpers import (
    wait_for_deal_confirmation,
    create_position_and_wait_for_confirmation,
    DEAL_CONFIRMATION_ATTEMPTS,
    DEAL_CONFIRMATION_DELAY,
)

__all__ = [
    "wait_for_deal_confirmation",
    "create_position_and_wait_for_confirmation",
    "DEAL_CONFIRMATION_ATTEMPTS",
    "DEAL_CONFIRMATION_DELAY",
]
