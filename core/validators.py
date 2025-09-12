"""
Centralized validation for path parameters and common data types.
"""

import re
from typing import Any
from core.exceptions import IGValidationError


class PathValidators:
    """Validators for URL path parameters"""
    
    @staticmethod
    def validate_epic(epic: str) -> str:
        """Validate epic format: [A-Za-z0-9._]{6,30}"""
        if not re.match(r'^[A-Za-z0-9._]{6,30}$', epic):
            raise IGValidationError(f"Invalid epic format: {epic}. Must be 6-30 characters, alphanumeric with dots and underscores only.")
        return epic
    
    @staticmethod
    def validate_deal_id(deal_id: str) -> str:
        """Validate deal ID format: .{1,30}"""
        if not re.match(r'^.{1,30}$', deal_id):
            raise IGValidationError(f"Invalid deal ID format: {deal_id}. Must be 1-30 characters.")
        return deal_id
    
    @staticmethod
    def validate_watchlist_id(watchlist_id: str) -> str:
        """Validate watchlist ID format"""
        if not watchlist_id or len(watchlist_id.strip()) == 0:
            raise IGValidationError(f"Invalid watchlist ID: {watchlist_id}. Cannot be empty.")
        return watchlist_id.strip()
    
    @staticmethod
    def validate_date_format(date_str: str) -> str:
        """Validate date format: dd-mm-yyyy"""
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
            raise IGValidationError(f"Invalid date format: {date_str}. Must be in dd-mm-yyyy format.")
        return date_str
    
    @staticmethod
    def validate_resolution(resolution: str) -> str:
        """Validate price resolution format"""
        valid_resolutions = [
            "SECOND", "MINUTE", "MINUTE_2", "MINUTE_3", "MINUTE_5", "MINUTE_10", 
            "MINUTE_15", "MINUTE_30", "HOUR", "HOUR_2", "HOUR_3", "HOUR_4", 
            "DAY", "WEEK", "MONTH"
        ]
        if resolution not in valid_resolutions:
            raise IGValidationError(f"Invalid resolution: {resolution}. Must be one of: {', '.join(valid_resolutions)}")
        return resolution
    
    @staticmethod
    def validate_num_points(num_points: int) -> int:
        """Validate number of data points"""
        if not isinstance(num_points, int) or num_points <= 0:
            raise IGValidationError(f"Invalid num_points: {num_points}. Must be a positive integer.")
        return num_points


class QueryValidators:
    """Validators for query parameters"""
    
    @staticmethod
    def validate_page_size(page_size: int) -> int:
        """Validate page size"""
        if not isinstance(page_size, int) or page_size < 0:
            raise IGValidationError(f"Invalid page_size: {page_size}. Must be a non-negative integer.")
        return page_size
    
    @staticmethod
    def validate_page_number(page_number: int) -> int:
        """Validate page number"""
        if not isinstance(page_number, int) or page_number < 1:
            raise IGValidationError(f"Invalid page_number: {page_number}. Must be a positive integer.")
        return page_number


def validate_path_params(**kwargs) -> dict:
    """
    Generic path parameter validator that applies appropriate validators based on parameter names.
    
    Usage:
        validate_path_params(epic="IX.D.NASDAQ.IFE.IP", deal_id="DIAAAAUZTYEFZAH")
    """
    validated = {}
    
    for key, value in kwargs.items():
        if key == "epic":
            validated[key] = PathValidators.validate_epic(value)
        elif key == "deal_id":
            validated[key] = PathValidators.validate_deal_id(value)
        elif key == "watchlist_id":
            validated[key] = PathValidators.validate_watchlist_id(value)
        elif key in ["from_date", "to_date"]:
            validated[key] = PathValidators.validate_date_format(value)
        elif key == "resolution":
            validated[key] = PathValidators.validate_resolution(value)
        elif key == "num_points":
            validated[key] = PathValidators.validate_num_points(value)
        else:
            # For unknown parameters, just pass through
            validated[key] = value
    
    return validated
