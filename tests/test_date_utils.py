"""Tests for the common_utils.date_utils module."""

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


class TestDateUtils:
    """Test suite for date utility functions."""

    @freeze_time("2023-01-15")
    def test_get_current_date(self):
        """Test the get_current_date function."""
        # Test that the function returns the current date
        current_date = get_current_date()
        assert isinstance(current_date, date)
        assert current_date == date(2023, 1, 15)

    @freeze_time("2023-01-15 12:30:45")
    def test_get_current_datetime(self):
        """Test the get_current_datetime function."""
        # Test with default timezone (UTC)
        current_dt = get_current_datetime()
        assert isinstance(current_dt, datetime)
        assert current_dt.year == 2023
        assert current_dt.month == 1
        assert current_dt.day == 15
        assert current_dt.hour == 12
        assert current_dt.minute == 30
        assert current_dt.second == 45
        assert current_dt.tzinfo == timezone.utc

        # Test with custom timezone
        est = timezone(timedelta(hours=-5))
        current_dt_est = get_current_datetime(est)
        assert current_dt_est.tzinfo == est
        # When using a different timezone, the hour will be adjusted
        assert current_dt_est.hour == 7  # 12 UTC - 5 hours = 7 EST

    def test_format_date(self):
        """Test the format_date function."""
        # Test with date object
        test_date = date(2023, 1, 15)
        assert format_date(test_date) == "2023-01-15"
        assert format_date(test_date, "%d/%m/%Y") == "15/01/2023"
        assert format_date(test_date, "%B %d, %Y") == "January 15, 2023"

        # Test with datetime object
        test_datetime = datetime(2023, 1, 15, 12, 30, 45)
        assert format_date(test_datetime) == "2023-01-15"
        assert format_date(test_datetime, "%d/%m/%Y") == "15/01/2023"
        assert format_date(test_datetime, "%B %d, %Y") == "January 15, 2023"

    def test_parse_date(self):
        """Test the parse_date function."""
        # Test with default format
        assert parse_date("2023-01-15") == date(2023, 1, 15)

        # Test with custom format
        assert parse_date("15/01/2023", "%d/%m/%Y") == date(2023, 1, 15)
        assert parse_date("January 15, 2023", "%B %d, %Y") == date(2023, 1, 15)

        # Test with invalid date string
        with pytest.raises(ValueError):
            parse_date("invalid-date")

    def test_parse_datetime(self):
        """Test the parse_datetime function."""
        # Test with default format
        dt = parse_datetime("2023-01-15 12:30:45")
        assert dt == datetime(2023, 1, 15, 12, 30, 45)

        # Test with custom format
        dt = parse_datetime("15/01/2023 12:30:45", "%d/%m/%Y %H:%M:%S")
        assert dt == datetime(2023, 1, 15, 12, 30, 45)

        # Test with invalid datetime string
        with pytest.raises(ValueError):
            parse_datetime("invalid-datetime")

    def test_add_days(self):
        """Test the add_days function."""
        # Test with date object
        test_date = date(2023, 1, 15)
        assert add_days(test_date, 5) == date(2023, 1, 20)
        assert add_days(test_date, -5) == date(2023, 1, 10)
        assert add_days(test_date, 0) == test_date

        # Test with datetime object
        test_datetime = datetime(2023, 1, 15, 12, 30, 45)
        assert add_days(test_datetime, 5) == datetime(2023, 1, 20, 12, 30, 45)
        assert add_days(test_datetime, -5) == datetime(2023, 1, 10, 12, 30, 45)
        assert add_days(test_datetime, 0) == test_datetime

    def test_date_range(self):
        """Test the date_range function."""
        # Test with same start and end date
        start_date = date(2023, 1, 15)
        end_date = date(2023, 1, 15)
        assert date_range(start_date, end_date) == [date(2023, 1, 15)]

        # Test with different start and end date
        start_date = date(2023, 1, 15)
        end_date = date(2023, 1, 20)
        expected = [
            date(2023, 1, 15),
            date(2023, 1, 16),
            date(2023, 1, 17),
            date(2023, 1, 18),
            date(2023, 1, 19),
            date(2023, 1, 20),
        ]
        assert date_range(start_date, end_date) == expected

        # Test with end date before start date (should return empty list)
        start_date = date(2023, 1, 20)
        end_date = date(2023, 1, 15)
        assert date_range(start_date, end_date) == []

    def test_get_month_start_end(self):
        """Test the get_month_start_end function."""
        # Test for January
        start, end = get_month_start_end(2023, 1)
        assert start == date(2023, 1, 1)
        assert end == date(2023, 1, 31)

        # Test for February (non-leap year)
        start, end = get_month_start_end(2023, 2)
        assert start == date(2023, 2, 1)
        assert end == date(2023, 2, 28)

        # Test for February (leap year)
        start, end = get_month_start_end(2024, 2)
        assert start == date(2024, 2, 1)
        assert end == date(2024, 2, 29)

        # Test for December
        start, end = get_month_start_end(2023, 12)
        assert start == date(2023, 12, 1)
        assert end == date(2023, 12, 31)

    def test_is_weekend(self):
        """Test the is_weekend function."""
        # Test with weekdays
        assert not is_weekend(date(2023, 1, 16))  # Monday
        assert not is_weekend(date(2023, 1, 17))  # Tuesday
        assert not is_weekend(date(2023, 1, 18))  # Wednesday
        assert not is_weekend(date(2023, 1, 19))  # Thursday
        assert not is_weekend(date(2023, 1, 20))  # Friday

        # Test with weekend days
        assert is_weekend(date(2023, 1, 21))  # Saturday
        assert is_weekend(date(2023, 1, 22))  # Sunday

        # Test with datetime objects
        assert not is_weekend(datetime(2023, 1, 16, 12, 30, 45))  # Monday
        assert is_weekend(datetime(2023, 1, 21, 12, 30, 45))  # Saturday

    def test_get_quarter(self):
        """Test the get_quarter function."""
        # Test Q1
        assert get_quarter(date(2023, 1, 15)) == 1
        assert get_quarter(date(2023, 2, 15)) == 1
        assert get_quarter(date(2023, 3, 15)) == 1

        # Test Q2
        assert get_quarter(date(2023, 4, 15)) == 2
        assert get_quarter(date(2023, 5, 15)) == 2
        assert get_quarter(date(2023, 6, 15)) == 2

        # Test Q3
        assert get_quarter(date(2023, 7, 15)) == 3
        assert get_quarter(date(2023, 8, 15)) == 3
        assert get_quarter(date(2023, 9, 15)) == 3

        # Test Q4
        assert get_quarter(date(2023, 10, 15)) == 4
        assert get_quarter(date(2023, 11, 15)) == 4
        assert get_quarter(date(2023, 12, 15)) == 4

        # Test with datetime objects
        assert get_quarter(datetime(2023, 1, 15, 12, 30, 45)) == 1
        assert get_quarter(datetime(2023, 4, 15, 12, 30, 45)) == 2
