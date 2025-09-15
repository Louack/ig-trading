"""
Unit tests for IG Trading API validators.
"""

import pytest
from api_gateway.ig_client.core.validators import (
    PathValidators,
    QueryValidators,
    validate_path_params,
)
from api_gateway.ig_client.core.exceptions import IGValidationError


class TestPathValidators:
    """Test cases for PathValidators class."""

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_epic_valid(self, valid_epic):
        """Test valid epic validation."""
        result = PathValidators.validate_epic(valid_epic)
        assert result == valid_epic

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_epic_invalid(self):
        """Test invalid epic validation."""
        invalid_epic = "SHORT"  # Too short (5 chars)
        with pytest.raises(IGValidationError) as exc_info:
            PathValidators.validate_epic(invalid_epic)

        assert "Invalid epic format" in str(exc_info.value)
        assert invalid_epic in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "epic",
        [
            "IX.D.NASDAQ.IFE.IP",
            "CS.D.EURGBP.CFD.IP",
            "CS.D.GBPUSD.CFD.IP",
            "IX.D.FTSE.IFE.IP",
            "CC.D.CRUDEOIL.CFD.IP",
            "CS.D.AUDUSD.CFD.IP",
        ],
    )
    def test_validate_epic_valid_cases(self, epic):
        """Test various valid epic formats."""
        result = PathValidators.validate_epic(epic)
        assert result == epic

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "epic",
        [
            "SHORT",  # Too short (5 chars)
            "THIS_EPIC_IS_WAY_TOO_LONG_AND_EXCEEDS_THE_MAXIMUM_LENGTH",  # Too long (58 chars)
            "invalid@epic",  # Invalid character @
            "epic with spaces",  # Spaces not allowed
            "epic-with-dashes",  # Dashes not allowed
            "",  # Empty string
            "123",  # Too short
            "EPIC.WITH.SPECIAL.CHARS!",  # Invalid character !
        ],
    )
    def test_validate_epic_invalid_cases(self, epic):
        """Test various invalid epic formats."""
        with pytest.raises(IGValidationError):
            PathValidators.validate_epic(epic)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_deal_id_valid(self, valid_deal_id):
        """Test valid deal ID validation."""
        result = PathValidators.validate_deal_id(valid_deal_id)
        assert result == valid_deal_id

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_deal_id_invalid(self, invalid_deal_id):
        """Test invalid deal ID validation."""
        with pytest.raises(IGValidationError) as exc_info:
            PathValidators.validate_deal_id(invalid_deal_id)

        assert "Invalid deal ID format" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "deal_id",
        [
            "DIAAAAUZTYEFZAH",
            "DI123456789",
            "A",
            "123456789012345678901234567890",  # 30 chars
            "DEAL_ID_WITH_UNDERSCORES",
            "deal-with-dashes",
        ],
    )
    def test_validate_deal_id_valid_cases(self, deal_id):
        """Test various valid deal ID formats."""
        result = PathValidators.validate_deal_id(deal_id)
        assert result == deal_id

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "deal_id",
        [
            "",  # Empty string
            "1234567890123456789012345678901",  # 31 chars - too long
        ],
    )
    def test_validate_deal_id_invalid_cases(self, deal_id):
        """Test various invalid deal ID formats."""
        with pytest.raises(IGValidationError):
            PathValidators.validate_deal_id(deal_id)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_watchlist_id_valid(self):
        """Test valid watchlist ID validation."""
        valid_ids = ["123", "watchlist_1", "My Watchlist", "123456789"]
        for watchlist_id in valid_ids:
            result = PathValidators.validate_watchlist_id(watchlist_id)
            assert result == watchlist_id.strip()

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_watchlist_id_invalid(self):
        """Test invalid watchlist ID validation."""
        invalid_ids = ["", "   ", None]
        for watchlist_id in invalid_ids:
            with pytest.raises(IGValidationError):
                PathValidators.validate_watchlist_id(watchlist_id)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_date_format_valid(self, valid_date):
        """Test valid date format validation."""
        result = PathValidators.validate_date_format(valid_date)
        assert result == valid_date

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_date_format_invalid(self, invalid_date):
        """Test invalid date format validation."""
        with pytest.raises(IGValidationError) as exc_info:
            PathValidators.validate_date_format(invalid_date)

        assert "Invalid date format" in str(exc_info.value)
        assert "dd-mm-yyyy" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "date_str",
        [
            "01-01-2024",
            "31-12-2023",
            "15-06-2024",
            "29-02-2024",  # Leap year
        ],
    )
    def test_validate_date_format_valid_cases(self, date_str):
        """Test various valid date formats."""
        result = PathValidators.validate_date_format(date_str)
        assert result == date_str

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "date_str",
        [
            "2024-01-01",  # Wrong format
            "01/01/2024",  # Wrong separator
            "1-1-2024",  # Missing leading zeros
            "01-1-2024",  # Missing leading zero in month
            "01-01-24",  # Short year
            "invalid-date",
            "",
        ],
    )
    def test_validate_date_format_invalid_cases(self, date_str):
        """Test various invalid date formats."""
        with pytest.raises(IGValidationError):
            PathValidators.validate_date_format(date_str)

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "resolution",
        [
            "SECOND",
            "MINUTE",
            "MINUTE_2",
            "MINUTE_3",
            "MINUTE_5",
            "MINUTE_10",
            "MINUTE_15",
            "MINUTE_30",
            "HOUR",
            "HOUR_2",
            "HOUR_3",
            "HOUR_4",
            "DAY",
            "WEEK",
            "MONTH",
        ],
    )
    def test_validate_resolution_valid_cases(self, resolution):
        """Test various valid resolution formats."""
        result = PathValidators.validate_resolution(resolution)
        assert result == resolution

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "resolution", ["INVALID", "MINUTE_1", "HOUR_1", "YEAR", "DECADE", "CUSTOM", ""]
    )
    def test_validate_resolution_invalid_cases(self, resolution):
        """Test various invalid resolution formats."""
        with pytest.raises(IGValidationError) as exc_info:
            PathValidators.validate_resolution(resolution)

        assert "Invalid resolution" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize("num_points", [1, 5, 10, 100, 1000])
    def test_validate_num_points_valid_cases(self, num_points):
        """Test various valid num_points values."""
        result = PathValidators.validate_num_points(num_points)
        assert result == num_points

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize("num_points", [0, -1, -10, "invalid", 1.5, None])
    def test_validate_num_points_invalid_cases(self, num_points):
        """Test various invalid num_points values."""
        with pytest.raises(IGValidationError):
            PathValidators.validate_num_points(num_points)


class TestQueryValidators:
    """Test cases for QueryValidators class."""

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize("page_size", [0, 1, 10, 100, 1000])
    def test_validate_page_size_valid_cases(self, page_size):
        """Test various valid page_size values."""
        result = QueryValidators.validate_page_size(page_size)
        assert result == page_size

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize("page_size", [-1, -10, "invalid", 1.5, None])
    def test_validate_page_size_invalid_cases(self, page_size):
        """Test various invalid page_size values."""
        with pytest.raises(IGValidationError):
            QueryValidators.validate_page_size(page_size)

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize("page_number", [1, 2, 10, 100])
    def test_validate_page_number_valid_cases(self, page_number):
        """Test various valid page_number values."""
        result = QueryValidators.validate_page_number(page_number)
        assert result == page_number

    @pytest.mark.unit
    @pytest.mark.validation
    @pytest.mark.parametrize("page_number", [0, -1, -10, "invalid", 1.5, None])
    def test_validate_page_number_invalid_cases(self, page_number):
        """Test various invalid page_number values."""
        with pytest.raises(IGValidationError):
            QueryValidators.validate_page_number(page_number)


class TestValidatePathParams:
    """Test cases for validate_path_params function."""

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_path_params_single_epic(self, valid_epic):
        """Test validating a single epic parameter."""
        result = validate_path_params(epic=valid_epic)
        assert result == {"epic": valid_epic}

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_path_params_multiple_params(
        self, valid_epic, valid_deal_id, valid_date
    ):
        """Test validating multiple path parameters."""
        result = validate_path_params(
            epic=valid_epic,
            deal_id=valid_deal_id,
            from_date=valid_date,
            to_date=valid_date,
        )
        expected = {
            "epic": valid_epic,
            "deal_id": valid_deal_id,
            "from_date": valid_date,
            "to_date": valid_date,
        }
        assert result == expected

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_path_params_with_resolution_and_points(self):
        """Test validating resolution and num_points parameters."""
        result = validate_path_params(
            epic="IX.D.NASDAQ.IFE.IP", resolution="MINUTE", num_points=10
        )
        expected = {
            "epic": "IX.D.NASDAQ.IFE.IP",
            "resolution": "MINUTE",
            "num_points": 10,
        }
        assert result == expected

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_path_params_unknown_param(self, valid_epic):
        """Test that unknown parameters are passed through unchanged."""
        result = validate_path_params(epic=valid_epic, unknown_param="test")
        expected = {"epic": valid_epic, "unknown_param": "test"}
        assert result == expected

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_path_params_invalid_epic(self):
        """Test that invalid epic raises validation error."""
        invalid_epic = "SHORT"  # Too short (5 chars)
        with pytest.raises(IGValidationError):
            validate_path_params(epic=invalid_epic)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_path_params_invalid_date(self, invalid_date):
        """Test that invalid date raises validation error."""
        with pytest.raises(IGValidationError):
            validate_path_params(from_date=invalid_date)

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_path_params_empty_params(self):
        """Test validating empty parameters."""
        result = validate_path_params()
        assert result == {}

    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_path_params_mixed_valid_invalid(self, valid_epic, invalid_date):
        """Test that one invalid parameter causes the whole validation to fail."""
        with pytest.raises(IGValidationError):
            validate_path_params(epic=valid_epic, from_date=invalid_date)
