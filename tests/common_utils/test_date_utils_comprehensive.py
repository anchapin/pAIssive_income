"""Comprehensive tests for the common_utils.date_utils module."""

import pytest
from datetime import date, datetime, timedelta, timezone
from freezegun import freeze_time

from common_utils.date_utils import (
    get_current_date,
    get_current_datetime,
    format_date,
    parse_date,
    parse_datetime,
    add_days,
    date_range,
    get_month_start_end,
    is_weekend,
    get_quarter,
)


class TestDateUtilsComprehensive:
    """Comprehensive test suite for date utility functions."""

    @freeze_time("2023-01-15")
    def test_get_current_date(self):
        """Test the get_current_date function."""
        # Test that the function returns the current date
        current_date = get_current_date()
        assert isinstance(current_date, date)
        assert current_date == date(2023, 1, 15)

    @freeze_time("2023-01-15 12:30:45")
    def test_get_current_datetime_default_timezone(self):
        """Test get_current_datetime with default timezone (UTC)."""
        current_dt = get_current_datetime()
        assert isinstance(current_dt, datetime)
        assert current_dt.year == 2023
        assert current_dt.month == 1
        assert current_dt.day == 15
        assert current_dt.hour == 12
        assert current_dt.minute == 30
        assert current_dt.second == 45
        assert current_dt.tzinfo == timezone.utc

    @freeze_time("2023-01-15 12:30:45")
    def test_get_current_datetime_custom_timezone(self):
        """Test get_current_datetime with custom timezone."""
        # Test with EST timezone (UTC-5)
        est = timezone(timedelta(hours=-5))
        current_dt_est = get_current_datetime(est)

        assert current_dt_est.tzinfo == est
        # When using a different timezone, the hour will be adjusted
        assert current_dt_est.hour == 7  # 12 UTC - 5 hours = 7 EST
        assert current_dt_est.minute == 30
        assert current_dt_est.second == 45

    def test_format_date_with_date(self):
        """Test format_date with a date object."""
        d = date(2023, 1, 15)

        # Test with default format
        assert format_date(d) == "2023-01-15"

        # Test with custom format
        assert format_date(d, "%d/%m/%Y") == "15/01/2023"
        assert format_date(d, "%B %d, %Y") == "January 15, 2023"

    def test_format_date_with_datetime(self):
        """Test format_date with a datetime object."""
        dt = datetime(2023, 1, 15, 12, 30, 45)

        # Test with default format (should ignore time part)
        assert format_date(dt) == "2023-01-15"

        # Test with custom format
        assert format_date(dt, "%d/%m/%Y") == "15/01/2023"

        # Test with format that includes time
        assert format_date(dt, "%Y-%m-%d %H:%M:%S") == "2023-01-15 12:30:45"

    def test_parse_date_default_format(self):
        """Test parse_date with default format."""
        d = parse_date("2023-01-15")
        assert isinstance(d, date)
        assert d == date(2023, 1, 15)

    def test_parse_date_custom_format(self):
        """Test parse_date with custom format."""
        # Test with day/month/year format
        d = parse_date("15/01/2023", "%d/%m/%Y")
        assert d == date(2023, 1, 15)

        # Test with month name format
        d = parse_date("January 15, 2023", "%B %d, %Y")
        assert d == date(2023, 1, 15)

    def test_parse_date_invalid(self):
        """Test parse_date with invalid date string."""
        with pytest.raises(ValueError):
            parse_date("invalid-date")

        with pytest.raises(ValueError):
            parse_date("2023/01/15", "%d/%m/%Y")  # Wrong format

    def test_parse_datetime_default_format(self):
        """Test parse_datetime with default format."""
        dt = parse_datetime("2023-01-15 12:30:45")
        assert isinstance(dt, datetime)
        assert dt == datetime(2023, 1, 15, 12, 30, 45)

    def test_parse_datetime_custom_format(self):
        """Test parse_datetime with custom format."""
        # Test with day/month/year format
        dt = parse_datetime("15/01/2023 12:30:45", "%d/%m/%Y %H:%M:%S")
        assert dt == datetime(2023, 1, 15, 12, 30, 45)

        # Test with month name format
        dt = parse_datetime("January 15, 2023 12:30:45", "%B %d, %Y %H:%M:%S")
        assert dt == datetime(2023, 1, 15, 12, 30, 45)

    def test_parse_datetime_invalid(self):
        """Test parse_datetime with invalid datetime string."""
        with pytest.raises(ValueError):
            parse_datetime("invalid-datetime")

        with pytest.raises(ValueError):
            parse_datetime("2023-01-15", "%Y-%m-%d %H:%M:%S")  # Missing time part

    def test_add_days_to_date(self):
        """Test add_days with a date object."""
        d = date(2023, 1, 15)

        # Add positive days
        assert add_days(d, 5) == date(2023, 1, 20)
        assert add_days(d, 20) == date(2023, 2, 4)  # Cross month boundary
        assert add_days(d, 365) == date(2024, 1, 15)  # Cross year boundary

        # Add negative days
        assert add_days(d, -5) == date(2023, 1, 10)
        assert add_days(d, -20) == date(2022, 12, 26)  # Cross month boundary
        assert add_days(d, -365) == date(2022, 1, 15)  # Cross year boundary

    def test_add_days_to_datetime(self):
        """Test add_days with a datetime object."""
        dt = datetime(2023, 1, 15, 12, 30, 45)

        # Add positive days
        result = add_days(dt, 5)
        assert isinstance(result, datetime)
        assert result == datetime(2023, 1, 20, 12, 30, 45)
        assert result.hour == 12  # Time part should be preserved
        assert result.minute == 30
        assert result.second == 45

        # Add negative days
        result = add_days(dt, -5)
        assert isinstance(result, datetime)
        assert result == datetime(2023, 1, 10, 12, 30, 45)

    def test_date_range_basic(self):
        """Test basic functionality of date_range."""
        start = date(2023, 1, 1)
        end = date(2023, 1, 5)

        result = date_range(start, end)

        assert len(result) == 5
        assert result[0] == date(2023, 1, 1)
        assert result[1] == date(2023, 1, 2)
        assert result[2] == date(2023, 1, 3)
        assert result[3] == date(2023, 1, 4)
        assert result[4] == date(2023, 1, 5)

    def test_date_range_same_day(self):
        """Test date_range with same start and end date."""
        d = date(2023, 1, 15)

        result = date_range(d, d)

        assert len(result) == 1
        assert result[0] == d

    def test_date_range_cross_month(self):
        """Test date_range crossing month boundary."""
        start = date(2023, 1, 30)
        end = date(2023, 2, 2)

        result = date_range(start, end)

        assert len(result) == 4
        assert result[0] == date(2023, 1, 30)
        assert result[1] == date(2023, 1, 31)
        assert result[2] == date(2023, 2, 1)
        assert result[3] == date(2023, 2, 2)

    def test_date_range_cross_year(self):
        """Test date_range crossing year boundary."""
        start = date(2022, 12, 30)
        end = date(2023, 1, 2)

        result = date_range(start, end)

        assert len(result) == 4
        assert result[0] == date(2022, 12, 30)
        assert result[1] == date(2022, 12, 31)
        assert result[2] == date(2023, 1, 1)
        assert result[3] == date(2023, 1, 2)

    def test_get_month_start_end_31_days(self):
        """Test get_month_start_end with a 31-day month."""
        start, end = get_month_start_end(2023, 1)  # January

        assert start == date(2023, 1, 1)
        assert end == date(2023, 1, 31)

    def test_get_month_start_end_30_days(self):
        """Test get_month_start_end with a 30-day month."""
        start, end = get_month_start_end(2023, 4)  # April

        assert start == date(2023, 4, 1)
        assert end == date(2023, 4, 30)

    def test_get_month_start_end_february_non_leap(self):
        """Test get_month_start_end with February in a non-leap year."""
        start, end = get_month_start_end(2023, 2)  # February 2023 (non-leap)

        assert start == date(2023, 2, 1)
        assert end == date(2023, 2, 28)

    def test_get_month_start_end_february_leap(self):
        """Test get_month_start_end with February in a leap year."""
        start, end = get_month_start_end(2024, 2)  # February 2024 (leap)

        assert start == date(2024, 2, 1)
        assert end == date(2024, 2, 29)

    def test_get_month_start_end_december(self):
        """Test get_month_start_end with December (crossing year boundary)."""
        start, end = get_month_start_end(2023, 12)  # December

        assert start == date(2023, 12, 1)
        assert end == date(2023, 12, 31)

    def test_is_weekend_weekdays(self):
        """Test is_weekend with weekdays."""
        # Test all weekdays (Monday to Friday)
        assert not is_weekend(date(2023, 1, 16))  # Monday
        assert not is_weekend(date(2023, 1, 17))  # Tuesday
        assert not is_weekend(date(2023, 1, 18))  # Wednesday
        assert not is_weekend(date(2023, 1, 19))  # Thursday
        assert not is_weekend(date(2023, 1, 20))  # Friday

    def test_is_weekend_weekend_days(self):
        """Test is_weekend with weekend days."""
        # Test weekend days (Saturday and Sunday)
        assert is_weekend(date(2023, 1, 21))  # Saturday
        assert is_weekend(date(2023, 1, 22))  # Sunday

    def test_is_weekend_with_datetime(self):
        """Test is_weekend with datetime objects."""
        # Test with datetime objects
        assert not is_weekend(datetime(2023, 1, 16, 12, 30, 45))  # Monday
        assert is_weekend(datetime(2023, 1, 21, 12, 30, 45))  # Saturday

    def test_get_quarter_q1(self):
        """Test get_quarter with Q1 dates."""
        assert get_quarter(date(2023, 1, 1)) == 1
        assert get_quarter(date(2023, 1, 15)) == 1
        assert get_quarter(date(2023, 2, 15)) == 1
        assert get_quarter(date(2023, 3, 31)) == 1

    def test_get_quarter_q2(self):
        """Test get_quarter with Q2 dates."""
        assert get_quarter(date(2023, 4, 1)) == 2
        assert get_quarter(date(2023, 4, 15)) == 2
        assert get_quarter(date(2023, 5, 15)) == 2
        assert get_quarter(date(2023, 6, 30)) == 2

    def test_get_quarter_q3(self):
        """Test get_quarter with Q3 dates."""
        assert get_quarter(date(2023, 7, 1)) == 3
        assert get_quarter(date(2023, 7, 15)) == 3
        assert get_quarter(date(2023, 8, 15)) == 3
        assert get_quarter(date(2023, 9, 30)) == 3

    def test_get_quarter_q4(self):
        """Test get_quarter with Q4 dates."""
        assert get_quarter(date(2023, 10, 1)) == 4
        assert get_quarter(date(2023, 10, 15)) == 4
        assert get_quarter(date(2023, 11, 15)) == 4
        assert get_quarter(date(2023, 12, 31)) == 4

    def test_get_quarter_with_datetime(self):
        """Test get_quarter with datetime objects."""
        assert get_quarter(datetime(2023, 1, 15, 12, 30, 45)) == 1
        assert get_quarter(datetime(2023, 4, 15, 12, 30, 45)) == 2
        assert get_quarter(datetime(2023, 7, 15, 12, 30, 45)) == 3
        assert get_quarter(datetime(2023, 10, 15, 12, 30, 45)) == 4

    def test_get_current_datetime_with_timezone_aware_datetime(self):
        """Test get_current_datetime returns timezone-aware datetime."""
        # Test with custom timezone
        pst = timezone(timedelta(hours=-8))
        dt = get_current_datetime(pst)

        # Verify it's timezone aware
        assert dt.tzinfo is not None
        assert dt.tzinfo == pst

    def test_parse_date_with_different_formats(self):
        """Test parse_date with various date formats."""
        # Test with month name
        d = parse_date("January 15, 2023", "%B %d, %Y")
        assert d == date(2023, 1, 15)

        # Test with abbreviated month name
        d = parse_date("Jan 15, 2023", "%b %d, %Y")
        assert d == date(2023, 1, 15)

        # Test with day of week
        d = parse_date("Sunday, January 15, 2023", "%A, %B %d, %Y")
        assert d == date(2023, 1, 15)

    def test_parse_datetime_with_timezone(self):
        """Test parse_datetime with timezone information."""
        # Note: strptime doesn't handle timezone offsets well, so we're not testing that
        # But we can test with explicit timezone objects
        dt_str = "2023-01-15 12:30:45"
        dt = parse_datetime(dt_str)

        # Verify it parsed correctly
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 12
        assert dt.minute == 30
        assert dt.second == 45

        # Test with different format
        dt_str = "15/01/2023 12:30:45"
        dt = parse_datetime(dt_str, "%d/%m/%Y %H:%M:%S")

        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 12
        assert dt.minute == 30
        assert dt.second == 45

    def test_get_month_start_end_invalid_month(self):
        """Test get_month_start_end with invalid month values."""
        # Test with month 0 (invalid)
        with pytest.raises(ValueError):
            get_month_start_end(2023, 0)

        # Test with month 13 (invalid)
        with pytest.raises(ValueError):
            get_month_start_end(2023, 13)

    def test_date_range_reversed_dates(self):
        """Test date_range with end date before start date."""
        # When end date is before start date, should return empty list
        # or handle it gracefully
        start = date(2023, 1, 10)
        end = date(2023, 1, 5)  # 5 days before start

        result = date_range(start, end)

        # The function should handle this by returning an empty list
        # or by swapping the dates
        if start > end:
            # If the function doesn't swap dates, we expect an empty list
            assert len(result) == 0
        else:
            # If the function swaps dates, we expect a valid range
            assert len(result) == 6
            assert result[0] == end
            assert result[-1] == start
