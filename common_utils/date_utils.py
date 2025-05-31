"""
Date utility functions for the pAIssive_income project.

This module provides common date manipulation functions used across the project.
"""

# Standard library imports
import datetime
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Union

# Third-party imports

# Local imports


def get_current_date() -> date:
    """
    Get the current date.

    Returns:
        The current date

    Examples:
        >>> isinstance(get_current_date(), date)
        True

    """
    return date.today()


def get_current_datetime(tz: Optional[timezone] = None) -> datetime:
    """
    Get the current datetime, optionally in a specific timezone.

    Args:
        tz: The timezone to use (default: UTC)

    Returns:
        The current datetime

    Examples:
        >>> isinstance(get_current_datetime(), datetime)
        True

    """
    if tz is None:
        return datetime.now(timezone.utc)
    return datetime.now(tz)


def format_date(dt: Union[date, datetime], format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date or datetime object as a string.

    Args:
        dt: The date or datetime to format
        format_str: The format string to use (default: "%Y-%m-%d")

    Returns:
        The formatted date string

    Examples:
        >>> format_date(date(2023, 1, 15))
        '2023-01-15'
        >>> format_date(date(2023, 1, 15), "%d/%m/%Y")
        '15/01/2023'

    """
    return dt.strftime(format_str)


def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> date:
    """
    Parse a date string into a date object.

    Args:
        date_str: The date string to parse
        format_str: The format string to use (default: "%Y-%m-%d")

    Returns:
        The parsed date object

    Raises:
        ValueError: If the date string cannot be parsed

    Examples:
        >>> parse_date("2023-01-15")
        datetime.date(2023, 1, 15)
        >>> parse_date("15/01/2023", "%d/%m/%Y")
        datetime.date(2023, 1, 15)

    """
    return datetime.strptime(date_str, format_str).date()


def parse_datetime(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse a datetime string into a datetime object.

    Args:
        datetime_str: The datetime string to parse
        format_str: The format string to use (default: "%Y-%m-%d %H:%M:%S")

    Returns:
        The parsed datetime object

    Raises:
        ValueError: If the datetime string cannot be parsed

    Examples:
        >>> parse_datetime("2023-01-15 14:30:00")
        datetime.datetime(2023, 1, 15, 14, 30)

    """
    return datetime.strptime(datetime_str, format_str)


def add_days(dt: Union[date, datetime], days: int) -> Union[date, datetime]:
    """
    Add a number of days to a date or datetime.

    Args:
        dt: The date or datetime to add days to
        days: The number of days to add (can be negative)

    Returns:
        The new date or datetime

    Examples:
        >>> add_days(date(2023, 1, 15), 5)
        datetime.date(2023, 1, 20)
        >>> add_days(date(2023, 1, 15), -5)
        datetime.date(2023, 1, 10)

    """
    return dt + timedelta(days=days)


def date_range(start_date: date, end_date: date) -> list[date]:
    """
    Generate a list of dates between start_date and end_date (inclusive).

    Args:
        start_date: The start date
        end_date: The end date

    Returns:
        A list of dates

    Examples:
        >>> date_range(date(2023, 1, 1), date(2023, 1, 3))
        [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2), datetime.date(2023, 1, 3)]

    """
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]


def get_month_start_end(year: int, month: int) -> tuple[date, date]:
    """
    Get the start and end dates of a month.

    Args:
        year: The year
        month: The month (1-12)

    Returns:
        A tuple of (start_date, end_date)

    Examples:
        >>> get_month_start_end(2023, 1)
        (datetime.date(2023, 1, 1), datetime.date(2023, 1, 31))
        >>> get_month_start_end(2023, 2)
        (datetime.date(2023, 2, 1), datetime.date(2023, 2, 28))

    """
    start_date = date(year, month, 1)

    # Get the last day of the month
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    return start_date, end_date


def is_weekend(dt: Union[date, datetime]) -> bool:
    """
    Check if a date is a weekend (Saturday or Sunday).

    Args:
        dt: The date or datetime to check

    Returns:
        True if the date is a weekend, False otherwise

    Examples:
        >>> is_weekend(date(2023, 1, 14))  # Saturday
        True
        >>> is_weekend(date(2023, 1, 15))  # Sunday
        True
        >>> is_weekend(date(2023, 1, 16))  # Monday
        False

    """
    return dt.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def get_quarter(dt: Union[date, datetime]) -> int:
    """
    Get the quarter (1-4) for a date.

    Args:
        dt: The date or datetime

    Returns:
        The quarter (1-4)

    Examples:
        >>> get_quarter(date(2023, 1, 15))
        1
        >>> get_quarter(date(2023, 4, 15))
        2
        >>> get_quarter(date(2023, 7, 15))
        3
        >>> get_quarter(date(2023, 10, 15))
        4

    """
    return (dt.month - 1) // 3 + 1
