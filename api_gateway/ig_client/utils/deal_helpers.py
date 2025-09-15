"""
Deal confirmation and position management utilities.

This module provides helper functions for common deal-related operations like
polling for deal confirmations and managing position creation workflows.
"""

import time
import logging
from typing import Optional, Dict, Any

from api_gateway.ig_client.clients.dealing import DealingClient
from api_gateway.ig_client.core.models.dealing.ig_responses import (
    DealConfirmation,
)

logger = logging.getLogger(__name__)

DEAL_CONFIRMATION_ATTEMPTS = 10
DEAL_CONFIRMATION_DELAY = 1


def wait_for_deal_confirmation(
    dealing_client: DealingClient,
    deal_reference: str,
    max_attempts: int = DEAL_CONFIRMATION_ATTEMPTS,
    delay: int = DEAL_CONFIRMATION_DELAY,
) -> Optional[DealConfirmation]:
    """
    Poll for deal confirmation until it's available or max attempts reached.

    Args:
        dealing_client: The dealing client instance
        deal_reference: The deal reference to check
        max_attempts: Maximum number of polling attempts (default: 10)
        delay: Delay between attempts in seconds (default: 1)

    Returns:
        DealConfirmation if found, None if max attempts reached
    """
    logger.info(f"Starting deal confirmation polling for {deal_reference}")

    for attempt in range(max_attempts):
        try:
            logger.debug(
                f"Attempt {attempt + 1}/{max_attempts} for deal {deal_reference}"
            )
            deal_confirmation = dealing_client.get_deal_confirmation(deal_reference)

            if deal_confirmation:
                logger.info(
                    f"Deal confirmation found for {deal_reference}: {deal_confirmation.status}"
                )
                return deal_confirmation

        except Exception as e:
            logger.warning(
                f"Error checking deal confirmation (attempt {attempt + 1}): {str(e)}"
            )

        if attempt < max_attempts - 1:
            time.sleep(delay)

    logger.warning(
        f"Deal confirmation timeout for {deal_reference} after {max_attempts} attempts"
    )
    return None


def create_position_and_wait_for_confirmation(
    dealing_client: DealingClient,
    body_data: Dict[str, Any],
    max_attempts: int = DEAL_CONFIRMATION_ATTEMPTS,
    delay: int = DEAL_CONFIRMATION_DELAY,
) -> Optional[DealConfirmation]:
    """
    Create a position and wait for deal confirmation.

    This is a convenience function that combines position creation with
    automatic deal confirmation polling.

    Args:
        dealing_client: The dealing client instance
        body_data: Position creation data
        max_attempts: Maximum number of confirmation polling attempts
        delay: Delay between confirmation attempts in seconds

    Returns:
        DealConfirmation or None

    """
    logger.info("Creating position and waiting for confirmation")

    position = dealing_client.create_position_otc(body_data)
    logger.info(f"Position created with deal reference: {position.dealReference}")

    confirmation = wait_for_deal_confirmation(
        dealing_client,
        position.dealReference,
        max_attempts=max_attempts,
        delay=delay,
    )

    return confirmation
