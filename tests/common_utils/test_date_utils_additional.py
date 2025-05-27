"""Additional tests for the common_utils.date_utils module to improve coverage."""

from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from common_utils.date_utils import (
    add_days,
    date_range,
    format_date,
    get_current_date,
    get_current_datetime,
    get_month_start_end,
    get_quarter,
    is_weekend,
    parse_date,
    parse_datetime,
)


class TestDateUtilsAdditional:
    """Additional test suite for date utility functions to improve coverage."""

    def test_get_current_datetime_with_timezone(self):
        """Test get_current_datetime with a specific timezone."""
        # Test with UTC timezone
        dt = get_current_datetime(timezone.utc)
        assert dt.tzinfo == timezone.utc

        # Test with Eastern timezone
        eastern = timezone(timedelta(hours=-5))
        dt = get_current_datetime(eastern)
        assert dt.tzinfo == eastern

        # Test with custom timezone
        custom_tz = timezone(timedelta(hours=2))
        dt = get_current_datetime(custom_tz)
        assert dt.tzinfo == custom_tz

    @freeze_time("2023-01-15 12:30:45")
    def test_get_current_datetime_frozen(self):
        """Test get_current_datetime with frozen time."""
        dt = get_current_datetime()
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 12
        assert dt.minute == 30
        assert dt.second == 45
        assert dt.tzinfo == timezone.utc

    def test_format_date_with_different_formats(self):
        """Test format_date with various format strings."""
        test_date = date(2023, 1, 15)

        # Test with different format strings
        assert format_date(test_date, "%Y/%m/%d") == "2023/01/15"
        assert format_date(test_date, "%d-%m-%Y") == "15-01-2023"
        assert format_date(test_date, "%A, %B %d, %Y") == "Sunday, January 15, 2023"
        assert format_date(test_date, "%a %b %d %Y") == "Sun Jan 15 2023"

        # Test with datetime object
        test_datetime = datetime(2023, 1, 15, 12, 30, 45)
        assert format_date(test_datetime, "%Y/%m/%d %H:%M:%S") == "2023/01/15 12:30:45"

    def test_parse_date_with_different_formats(self):
        """Test parse_date with various format strings."""
        # Test with different format strings
        assert parse_date("2023/01/15", "%Y/%m/%d") == date(2023, 1, 15)
        assert parse_date("15-01-2023", "%d-%m-%Y") == date(2023, 1, 15)
        assert parse_date("Sunday, January 15, 2023", "%A, %B %d, %Y") == date(2023, 1, 15)
        assert parse_date("Sun Jan 15 2023", "%a %b %d %Y") == date(2023, 1, 15)

        # Test with invalid format
        with pytest.raises(ValueError):
            parse_date("2023-01-15", "%d/%m/%Y")

    def test_parse_datetime_with_different_formats(self):
        """Test parse_datetime with various format strings."""
        # Test with different format strings
        assert parse_datetime("2023-01-15 12:30:45") == datetime(2023, 1, 15, 12, 30, 45)
        assert parse_datetime("2023/01/15 12:30:45", "%Y/%m/%d %H:%M:%S") == datetime(2023, 1, 15, 12, 30, 45)
        assert parse_datetime("15-01-2023 12:30:45", "%d-%m-%Y %H:%M:%S") == datetime(2023, 1, 15, 12, 30, 45)
        assert parse_datetime("Sunday, January 15, 2023 12:30:45", "%A, %B %d, %Y %H:%M:%S") == datetime(2023, 1, 15, 12, 30, 45)

        # Test with invalid format
        with pytest.raises(ValueError):
            parse_datetime("2023-01-15 12:30:45", "%d/%m/%Y %H:%M:%S")

    def test_add_days_with_large_values(self):
        """Test add_days with large positive and negative values."""
        test_date = date(2023, 1, 15)

        # Test with large positive value
        assert add_days(test_date, 1000) == date(2025, 10, 11)

        # Test with large negative value
        assert add_days(test_date, -1000) == date(2020, 4, 20)

        # Test with datetime object
        test_datetime = datetime(2023, 1, 15, 12, 30, 45)
        assert add_days(test_datetime, 1000) == datetime(2025, 10, 11, 12, 30, 45)
        assert add_days(test_datetime, -1000) == datetime(2020, 4, 20, 12, 30, 45)

    def test_date_range_with_large_range(self):
        """Test date_range with a large range of dates."""
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)

        # Generate a range for the entire month
        dates = date_range(start_date, end_date)

        # Verify the range
        assert len(dates) == 31
        assert dates[0] == date(2023, 1, 1)
        assert dates[-1] == date(2023, 1, 31)

        # Verify each date is one day after the previous
        for i in range(1, len(dates)):
            assert dates[i] == dates[i-1] + timedelta(days=1)

    def test_date_range_with_reversed_dates(self):
        """Test date_range with end date before start date."""
        start_date = date(2023, 1, 31)
        end_date = date(2023, 1, 1)

        # Generate a range with reversed dates (should be empty)
        dates = date_range(start_date, end_date)

        # Verify the range is empty
        assert len(dates) == 0

    def test_get_month_start_end_for_all_months(self):
        """Test get_month_start_end for all months of the year."""
        # Test for each month of 2023
        expected_results = [
            ((2023, 1, 1), (2023, 1, 31)),
            ((2023, 2, 1), (2023, 2, 28)),
            ((2023, 3, 1), (2023, 3, 31)),
            ((2023, 4, 1), (2023, 4, 30)),
            ((2023, 5, 1), (2023, 5, 31)),
            ((2023, 6, 1), (2023, 6, 30)),
            ((2023, 7, 1), (2023, 7, 31)),
            ((2023, 8, 1), (2023, 8, 31)),
            ((2023, 9, 1), (2023, 9, 30)),
            ((2023, 10, 1), (2023, 10, 31)),
            ((2023, 11, 1), (2023, 11, 30)),
            ((2023, 12, 1), (2023, 12, 31)),
        ]

        for month, ((start_year, start_month, start_day), (end_year, end_month, end_day)) in enumerate(expected_results, 1):
            start_date, end_date = get_month_start_end(2023, month)
            assert start_date == date(start_year, start_month, start_day)
            assert end_date == date(end_year, end_month, end_day)

    def test_get_month_start_end_for_leap_year(self):
        """Test get_month_start_end for February in leap years."""
        # Test February in a leap year (2020)
        start_date, end_date = get_month_start_end(2020, 2)
        assert start_date == date(2020, 2, 1)
        assert end_date == date(2020, 2, 29)

        # Test February in a non-leap year (2023)
        start_date, end_date = get_month_start_end(2023, 2)
        assert start_date == date(2023, 2, 1)
        assert end_date == date(2023, 2, 28)

    def test_is_weekend_for_all_days_of_week(self):
        """Test is_weekend for all days of the week."""
        # Test for each day of a week in January 2023
        # January 2023: Sun=1, Mon=2, Tue=3, Wed=4, Thu=5, Fri=6, Sat=7
        weekdays = [
            (date(2023, 1, 1), True),   # Sunday
            (date(2023, 1, 2), False),  # Monday
            (date(2023, 1, 3), False),  # Tuesday
            (date(2023, 1, 4), False),  # Wednesday
            (date(2023, 1, 5), False),  # Thursday
            (date(2023, 1, 6), False),  # Friday
            (date(2023, 1, 7), True),   # Saturday
        ]

        for test_date, expected_result in weekdays:
            assert is_weekend(test_date) == expected_result

            # Also test with datetime objects
            test_datetime = datetime.combine(test_date, datetime.min.time())
            assert is_weekend(test_datetime) == expected_result

    def test_get_quarter_for_all_months(self):
        """Test get_quarter for all months of the year."""
        # Test for each month of 2023
        expected_quarters = [
            (1, 1),  # January -> Q1
            (2, 1),  # February -> Q1
            (3, 1),  # March -> Q1
            (4, 2),  # April -> Q2
            (5, 2),  # May -> Q2
            (6, 2),  # June -> Q2
            (7, 3),  # July -> Q3
            (8, 3),  # August -> Q3
            (9, 3),  # September -> Q3
            (10, 4), # October -> Q4
            (11, 4), # November -> Q4
            (12, 4), # December -> Q4
        ]

        for month, expected_quarter in expected_quarters:
            test_date = date(2023, month, 15)
            assert get_quarter(test_date) == expected_quarter

            # Also test with datetime objects
            test_datetime = datetime.combine(test_date, datetime.min.time())
            assert get_quarter(test_datetime) == expected_quarter
