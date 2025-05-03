"""
Date utilities for the pAIssive Income project.

This module provides common date handling functions used across the project.
"""

import calendar
from datetime import date, datetime, timedelta
from typing import Optional, Union

# Type alias for date - like objects
DateLike = Union[datetime, date]


def format_date(date_obj: DateLike, format_str: str = " % Y-%m-%d") -> str:
    """
    Format a date object as a string.

    Args:
        date_obj: Date or datetime object to format
        format_str: Format string (default: " % Y-%m-%d")

    Returns:
        Formatted date string
    """
    return date_obj.strftime(format_str)


def format_datetime(dt_obj: datetime, format_str: str = " % Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object as a string.

    Args:
        dt_obj: Datetime object to format
        format_str: Format string (default: " % Y-%m-%d %H:%M:%S")

    Returns:
        Formatted datetime string
    """
    return dt_obj.strftime(format_str)


def get_days_in_month(year: int, month: int) -> int:
    """
    Get the number of days in a month.

    Args:
        year: Year
        month: Month (1 - 12)

    Returns:
        Number of days in the month
    """
    return calendar.monthrange(year, month)[1]


def get_days_in_year(year: int) -> int:
    """
    Get the number of days in a year.

    Args:
        year: Year

    Returns:
        Number of days in the year
    """
    return 366 if calendar.isleap(year) else 365


def get_start_of_day(dt: DateLike) -> datetime:
    """
    Get the start of the day (midnight).

    Args:
        dt: Date or datetime object

    Returns:
        Datetime object representing the start of the day
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    return datetime(dt.year, dt.month, dt.day, 0, 0, 0)


def get_end_of_day(dt: DateLike) -> datetime:
    """
    Get the end of the day (23:59:59).

    Args:
        dt: Date or datetime object

    Returns:
        Datetime object representing the end of the day
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, dt.month, dt.day, 23, 59, 59)
    return datetime(dt.year, dt.month, dt.day, 23, 59, 59)


def get_start_of_week(dt: DateLike, start_day: int = calendar.MONDAY) -> datetime:
    """
    Get the start of the week.

    Args:
        dt: Date or datetime object
        start_day: First day of the week (default: Monday)

    Returns:
        Datetime object representing the start of the week
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime(dt.year, dt.month, dt.day)

    days_since_start = (dt.weekday() - start_day) % 7
    return get_start_of_day(dt - timedelta(days=days_since_start))


def get_end_of_week(dt: DateLike, start_day: int = calendar.MONDAY) -> datetime:
    """
    Get the end of the week.

    Args:
        dt: Date or datetime object
        start_day: First day of the week (default: Monday)

    Returns:
        Datetime object representing the end of the week
    """
    start_of_week = get_start_of_week(dt, start_day)
    return get_end_of_day(start_of_week + timedelta(days=6))


def get_start_of_month(dt: DateLike) -> datetime:
    """
    Get the start of the month.

    Args:
        dt: Date or datetime object

    Returns:
        Datetime object representing the start of the month
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, dt.month, 1, 0, 0, 0)
    return datetime(dt.year, dt.month, 1, 0, 0, 0)


def get_end_of_month(dt: DateLike) -> datetime:
    """
    Get the end of the month.

    Args:
        dt: Date or datetime object

    Returns:
        Datetime object representing the end of the month
    """
    days_in_month = get_days_in_month(dt.year, dt.month)
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, dt.month, days_in_month, 23, 59, 59)
    return datetime(dt.year, dt.month, days_in_month, 23, 59, 59)


def get_start_of_year(dt: DateLike) -> datetime:
    """
    Get the start of the year.

    Args:
        dt: Date or datetime object

    Returns:
        Datetime object representing the start of the year
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, 1, 1, 0, 0, 0)
    return datetime(dt.year, 1, 1, 0, 0, 0)


def get_end_of_year(dt: DateLike) -> datetime:
    """
    Get the end of the year.

    Args:
        dt: Date or datetime object

    Returns:
        Datetime object representing the end of the year
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime(dt.year, 12, 31, 23, 59, 59)
    return datetime(dt.year, 12, 31, 23, 59, 59)


def is_date_in_range(dt: DateLike, start: DateLike, end: DateLike) -> bool:
    """
    Check if a date is within a range.

    Args:
        dt: Date or datetime object to check
        start: Start date of the range
        end: End date of the range

    Returns:
        True if the date is within the range, False otherwise
    """
    # Convert to date objects if they are datetime objects
    if isinstance(dt, datetime):
        dt = dt.date()
    if isinstance(start, datetime):
        start = start.date()
    if isinstance(end, datetime):
        end = end.date()

    return start <= dt <= end


def get_date_difference(start: DateLike, end: DateLike) -> int:
    """
    Get the number of days between two dates.

    Args:
        start: Start date
        end: End date

    Returns:
        Number of days between the dates
    """
    # Convert to date objects if they are datetime objects
    if isinstance(start, datetime):
        start = start.date()
    if isinstance(end, datetime):
        end = end.date()

    return (end - start).days


def add_days(dt: DateLike, days: int) -> DateLike:
    """
    Add days to a date.

    Args:
        dt: Date or datetime object
        days: Number of days to add

    Returns:
        New date or datetime object
    """
    return dt + timedelta(days=days)


def add_months(dt: DateLike, months: int) -> DateLike:
    """
    Add months to a date.

    Args:
        dt: Date or datetime object
        months: Number of months to add

    Returns:
        New date or datetime object
    """
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, get_days_in_month(year, month))

    if isinstance(dt, datetime):
        return datetime(year, month, day, dt.hour, dt.minute, dt.second, dt.microsecond)
    return date(year, month, day)


def add_years(dt: DateLike, years: int) -> DateLike:
    """
    Add years to a date.

    Args:
        dt: Date or datetime object
        years: Number of years to add

    Returns:
        New date or datetime object
    """
    year = dt.year + years
    # Handle leap years
    if dt.month == 2 and dt.day == 29 and not calendar.isleap(year):
        day = 28
    else:
        day = dt.day

    if isinstance(dt, datetime):
        return datetime(year, dt.month, day, dt.hour, dt.minute, dt.second, 
            dt.microsecond)
    return date(year, dt.month, day)


def is_future_date(dt: DateLike, reference: Optional[DateLike] = None) -> bool:
    """
    Check if a date is in the future.

    Args:
        dt: Date or datetime object to check
        reference: Reference date (default: current date / time)

    Returns:
        True if the date is in the future, False otherwise
    """
    if reference is None:
        reference = datetime.now() if isinstance(dt, datetime) else date.today()

    # Convert to date objects if they are datetime objects
    if isinstance(dt, datetime) and isinstance(reference, datetime):
        return dt > reference
    elif isinstance(dt, datetime):
        dt = dt.date()
    elif isinstance(reference, datetime):
        reference = reference.date()

    return dt > reference


def is_past_date(dt: DateLike, reference: Optional[DateLike] = None) -> bool:
    """
    Check if a date is in the past.

    Args:
        dt: Date or datetime object to check
        reference: Reference date (default: current date / time)

    Returns:
        True if the date is in the past, False otherwise
    """
    if reference is None:
        reference = datetime.now() if isinstance(dt, datetime) else date.today()

    # Convert to date objects if they are datetime objects
    if isinstance(dt, datetime) and isinstance(reference, datetime):
        return dt < reference
    elif isinstance(dt, datetime):
        dt = dt.date()
    elif isinstance(reference, datetime):
        reference = reference.date()

    return dt < reference


def is_same_day(dt1: DateLike, dt2: DateLike) -> bool:
    """
    Check if two dates are on the same day.

    Args:
        dt1: First date or datetime object
        dt2: Second date or datetime object

    Returns:
        True if the dates are on the same day, False otherwise
    """
    return dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day


def is_same_month(dt1: DateLike, dt2: DateLike) -> bool:
    """
    Check if two dates are in the same month.

    Args:
        dt1: First date or datetime object
        dt2: Second date or datetime object

    Returns:
        True if the dates are in the same month, False otherwise
    """
    return dt1.year == dt2.year and dt1.month == dt2.month


def is_same_year(dt1: DateLike, dt2: DateLike) -> bool:
    """
    Check if two dates are in the same year.

    Args:
        dt1: First date or datetime object
        dt2: Second date or datetime object

    Returns:
        True if the dates are in the same year, False otherwise
    """
    return dt1.year == dt2.year
