"""
"""
Date utilities for the pAIssive Income project.
Date utilities for the pAIssive Income project.


This module provides common date handling functions used across the project.
This module provides common date handling functions used across the project.
"""
"""


import calendar
import calendar
import time
import time
from datetime import date, datetime, timedelta
from datetime import date, datetime, timedelta
from typing import Optional, Union
from typing import Optional, Union


# Type alias for date-like objects
# Type alias for date-like objects
DateLike = Union[datetime, date]
DateLike = Union[datetime, date]




def format_date(date_obj: DateLike, format_str: str = "%Y-%m-%d") -> str:
    def format_date(date_obj: DateLike, format_str: str = "%Y-%m-%d") -> str:
    """
    """
    Format a date object as a string.
    Format a date object as a string.


    Args:
    Args:
    date_obj: Date or datetime object to format
    date_obj: Date or datetime object to format
    format_str: Format string (default: "%Y-%m-%d")
    format_str: Format string (default: "%Y-%m-%d")


    Returns:
    Returns:
    Formatted date string
    Formatted date string
    """
    """
    return date_obj.strftime(format_str)
    return date_obj.strftime(format_str)




    def format_datetime(dt_obj: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    def format_datetime(dt_obj: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    """
    Format a datetime object as a string.
    Format a datetime object as a string.


    Args:
    Args:
    dt_obj: Datetime object to format
    dt_obj: Datetime object to format
    format_str: Format string (default: "%Y-%m-%d %H:%M:%S")
    format_str: Format string (default: "%Y-%m-%d %H:%M:%S")


    Returns:
    Returns:
    Formatted datetime string
    Formatted datetime string
    """
    """
    return dt_obj.strftime(format_str)
    return dt_obj.strftime(format_str)




    def get_days_in_month(year: int, month: int) -> int:
    def get_days_in_month(year: int, month: int) -> int:
    """
    """
    Get the number of days in a month.
    Get the number of days in a month.


    Args:
    Args:
    year: Year
    year: Year
    month: Month (1-12)
    month: Month (1-12)


    Returns:
    Returns:
    Number of days in the month
    Number of days in the month
    """
    """
    return calendar.monthrange(year, month)[1]
    return calendar.monthrange(year, month)[1]




    def get_days_in_year(year: int) -> int:
    def get_days_in_year(year: int) -> int:
    """
    """
    Get the number of days in a year.
    Get the number of days in a year.


    Args:
    Args:
    year: Year
    year: Year


    Returns:
    Returns:
    Number of days in the year
    Number of days in the year
    """
    """
    return 366 if calendar.isleap(year) else 365
    return 366 if calendar.isleap(year) else 365




    def get_start_of_day(dt: DateLike) -> datetime:
    def get_start_of_day(dt: DateLike) -> datetime:
    """
    """
    Get the start of the day (midnight).
    Get the start of the day (midnight).


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object


    Returns:
    Returns:
    Datetime object representing the start of the day
    Datetime object representing the start of the day
    """
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
    if isinstance(dt, date) and not isinstance(dt, datetime):
    return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    return datetime(dt.year, dt.month, dt.day, 0, 0, 0)




    def get_end_of_day(dt: DateLike) -> datetime:
    def get_end_of_day(dt: DateLike) -> datetime:
    """
    """
    Get the end of the day (23:59:59).
    Get the end of the day (23:59:59).


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object


    Returns:
    Returns:
    Datetime object representing the end of the day
    Datetime object representing the end of the day
    """
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
    if isinstance(dt, date) and not isinstance(dt, datetime):
    return datetime(dt.year, dt.month, dt.day, 23, 59, 59)
    return datetime(dt.year, dt.month, dt.day, 23, 59, 59)
    return datetime(dt.year, dt.month, dt.day, 23, 59, 59)
    return datetime(dt.year, dt.month, dt.day, 23, 59, 59)




    def get_start_of_week(dt: DateLike, start_day: int = calendar.MONDAY) -> datetime:
    def get_start_of_week(dt: DateLike, start_day: int = calendar.MONDAY) -> datetime:
    """
    """
    Get the start of the week.
    Get the start of the week.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object
    start_day: First day of the week (default: Monday)
    start_day: First day of the week (default: Monday)


    Returns:
    Returns:
    Datetime object representing the start of the week
    Datetime object representing the start of the week
    """
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
    if isinstance(dt, date) and not isinstance(dt, datetime):
    dt = datetime(dt.year, dt.month, dt.day)
    dt = datetime(dt.year, dt.month, dt.day)


    days_since_start = (dt.weekday() - start_day) % 7
    days_since_start = (dt.weekday() - start_day) % 7
    return get_start_of_day(dt - timedelta(days=days_since_start))
    return get_start_of_day(dt - timedelta(days=days_since_start))




    def get_end_of_week(dt: DateLike, start_day: int = calendar.MONDAY) -> datetime:
    def get_end_of_week(dt: DateLike, start_day: int = calendar.MONDAY) -> datetime:
    """
    """
    Get the end of the week.
    Get the end of the week.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object
    start_day: First day of the week (default: Monday)
    start_day: First day of the week (default: Monday)


    Returns:
    Returns:
    Datetime object representing the end of the week
    Datetime object representing the end of the week
    """
    """
    start_of_week = get_start_of_week(dt, start_day)
    start_of_week = get_start_of_week(dt, start_day)
    return get_end_of_day(start_of_week + timedelta(days=6))
    return get_end_of_day(start_of_week + timedelta(days=6))




    def get_start_of_month(dt: DateLike) -> datetime:
    def get_start_of_month(dt: DateLike) -> datetime:
    """
    """
    Get the start of the month.
    Get the start of the month.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object


    Returns:
    Returns:
    Datetime object representing the start of the month
    Datetime object representing the start of the month
    """
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
    if isinstance(dt, date) and not isinstance(dt, datetime):
    return datetime(dt.year, dt.month, 1, 0, 0, 0)
    return datetime(dt.year, dt.month, 1, 0, 0, 0)
    return datetime(dt.year, dt.month, 1, 0, 0, 0)
    return datetime(dt.year, dt.month, 1, 0, 0, 0)




    def get_end_of_month(dt: DateLike) -> datetime:
    def get_end_of_month(dt: DateLike) -> datetime:
    """
    """
    Get the end of the month.
    Get the end of the month.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object


    Returns:
    Returns:
    Datetime object representing the end of the month
    Datetime object representing the end of the month
    """
    """
    days_in_month = get_days_in_month(dt.year, dt.month)
    days_in_month = get_days_in_month(dt.year, dt.month)
    if isinstance(dt, date) and not isinstance(dt, datetime):
    if isinstance(dt, date) and not isinstance(dt, datetime):
    return datetime(dt.year, dt.month, days_in_month, 23, 59, 59)
    return datetime(dt.year, dt.month, days_in_month, 23, 59, 59)
    return datetime(dt.year, dt.month, days_in_month, 23, 59, 59)
    return datetime(dt.year, dt.month, days_in_month, 23, 59, 59)




    def get_start_of_year(dt: DateLike) -> datetime:
    def get_start_of_year(dt: DateLike) -> datetime:
    """
    """
    Get the start of the year.
    Get the start of the year.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object


    Returns:
    Returns:
    Datetime object representing the start of the year
    Datetime object representing the start of the year
    """
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
    if isinstance(dt, date) and not isinstance(dt, datetime):
    return datetime(dt.year, 1, 1, 0, 0, 0)
    return datetime(dt.year, 1, 1, 0, 0, 0)
    return datetime(dt.year, 1, 1, 0, 0, 0)
    return datetime(dt.year, 1, 1, 0, 0, 0)




    def get_end_of_year(dt: DateLike) -> datetime:
    def get_end_of_year(dt: DateLike) -> datetime:
    """
    """
    Get the end of the year.
    Get the end of the year.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object


    Returns:
    Returns:
    Datetime object representing the end of the year
    Datetime object representing the end of the year
    """
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
    if isinstance(dt, date) and not isinstance(dt, datetime):
    return datetime(dt.year, 12, 31, 23, 59, 59)
    return datetime(dt.year, 12, 31, 23, 59, 59)
    return datetime(dt.year, 12, 31, 23, 59, 59)
    return datetime(dt.year, 12, 31, 23, 59, 59)




    def is_date_in_range(dt: DateLike, start: DateLike, end: DateLike) -> bool:
    def is_date_in_range(dt: DateLike, start: DateLike, end: DateLike) -> bool:
    """
    """
    Check if a date is within a range.
    Check if a date is within a range.


    Args:
    Args:
    dt: Date or datetime object to check
    dt: Date or datetime object to check
    start: Start date of the range
    start: Start date of the range
    end: End date of the range
    end: End date of the range


    Returns:
    Returns:
    True if the date is within the range, False otherwise
    True if the date is within the range, False otherwise
    """
    """
    # Convert to date objects if they are datetime objects
    # Convert to date objects if they are datetime objects
    if isinstance(dt, datetime):
    if isinstance(dt, datetime):
    dt = dt.date()
    dt = dt.date()
    if isinstance(start, datetime):
    if isinstance(start, datetime):
    start = start.date()
    start = start.date()
    if isinstance(end, datetime):
    if isinstance(end, datetime):
    end = end.date()
    end = end.date()


    return start <= dt <= end
    return start <= dt <= end




    def get_date_difference(start: DateLike, end: DateLike) -> int:
    def get_date_difference(start: DateLike, end: DateLike) -> int:
    """
    """
    Get the number of days between two dates.
    Get the number of days between two dates.


    Args:
    Args:
    start: Start date
    start: Start date
    end: End date
    end: End date


    Returns:
    Returns:
    Number of days between the dates
    Number of days between the dates
    """
    """
    # Convert to date objects if they are datetime objects
    # Convert to date objects if they are datetime objects
    if isinstance(start, datetime):
    if isinstance(start, datetime):
    start = start.date()
    start = start.date()
    if isinstance(end, datetime):
    if isinstance(end, datetime):
    end = end.date()
    end = end.date()


    return (end - start).days
    return (end - start).days




    def add_days(dt: DateLike, days: int) -> DateLike:
    def add_days(dt: DateLike, days: int) -> DateLike:
    """
    """
    Add days to a date.
    Add days to a date.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object
    days: Number of days to add
    days: Number of days to add


    Returns:
    Returns:
    New date or datetime object
    New date or datetime object
    """
    """
    return dt + timedelta(days=days)
    return dt + timedelta(days=days)




    def add_months(dt: DateLike, months: int) -> DateLike:
    def add_months(dt: DateLike, months: int) -> DateLike:
    """
    """
    Add months to a date.
    Add months to a date.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object
    months: Number of months to add
    months: Number of months to add


    Returns:
    Returns:
    New date or datetime object
    New date or datetime object
    """
    """
    month = dt.month - 1 + months
    month = dt.month - 1 + months
    year = dt.year + month // 12
    year = dt.year + month // 12
    month = month % 12 + 1
    month = month % 12 + 1
    day = min(dt.day, get_days_in_month(year, month))
    day = min(dt.day, get_days_in_month(year, month))


    if isinstance(dt, datetime):
    if isinstance(dt, datetime):
    return datetime(year, month, day, dt.hour, dt.minute, dt.second, dt.microsecond)
    return datetime(year, month, day, dt.hour, dt.minute, dt.second, dt.microsecond)
    return date(year, month, day)
    return date(year, month, day)




    def add_years(dt: DateLike, years: int) -> DateLike:
    def add_years(dt: DateLike, years: int) -> DateLike:
    """
    """
    Add years to a date.
    Add years to a date.


    Args:
    Args:
    dt: Date or datetime object
    dt: Date or datetime object
    years: Number of years to add
    years: Number of years to add


    Returns:
    Returns:
    New date or datetime object
    New date or datetime object
    """
    """
    year = dt.year + years
    year = dt.year + years
    # Handle leap years
    # Handle leap years
    if dt.month == 2 and dt.day == 29 and not calendar.isleap(year):
    if dt.month == 2 and dt.day == 29 and not calendar.isleap(year):
    day = 28
    day = 28
    else:
    else:
    day = dt.day
    day = dt.day


    if isinstance(dt, datetime):
    if isinstance(dt, datetime):
    return datetime(
    return datetime(
    year, dt.month, day, dt.hour, dt.minute, dt.second, dt.microsecond
    year, dt.month, day, dt.hour, dt.minute, dt.second, dt.microsecond
    )
    )
    return date(year, dt.month, day)
    return date(year, dt.month, day)




    def is_future_date(dt: DateLike, reference: Optional[DateLike] = None) -> bool:
    def is_future_date(dt: DateLike, reference: Optional[DateLike] = None) -> bool:
    """
    """
    Check if a date is in the future.
    Check if a date is in the future.


    Args:
    Args:
    dt: Date or datetime object to check
    dt: Date or datetime object to check
    reference: Reference date (default: current date/time)
    reference: Reference date (default: current date/time)


    Returns:
    Returns:
    True if the date is in the future, False otherwise
    True if the date is in the future, False otherwise
    """
    """
    if reference is None:
    if reference is None:
    reference = datetime.now() if isinstance(dt, datetime) else date.today()
    reference = datetime.now() if isinstance(dt, datetime) else date.today()


    # Convert to date objects if they are datetime objects
    # Convert to date objects if they are datetime objects
    if isinstance(dt, datetime) and isinstance(reference, datetime):
    if isinstance(dt, datetime) and isinstance(reference, datetime):
    return dt > reference
    return dt > reference
    elif isinstance(dt, datetime):
    elif isinstance(dt, datetime):
    dt = dt.date()
    dt = dt.date()
    elif isinstance(reference, datetime):
    elif isinstance(reference, datetime):
    reference = reference.date()
    reference = reference.date()


    return dt > reference
    return dt > reference




    def is_past_date(dt: DateLike, reference: Optional[DateLike] = None) -> bool:
    def is_past_date(dt: DateLike, reference: Optional[DateLike] = None) -> bool:
    """
    """
    Check if a date is in the past.
    Check if a date is in the past.


    Args:
    Args:
    dt: Date or datetime object to check
    dt: Date or datetime object to check
    reference: Reference date (default: current date/time)
    reference: Reference date (default: current date/time)


    Returns:
    Returns:
    True if the date is in the past, False otherwise
    True if the date is in the past, False otherwise
    """
    """
    if reference is None:
    if reference is None:
    reference = datetime.now() if isinstance(dt, datetime) else date.today()
    reference = datetime.now() if isinstance(dt, datetime) else date.today()


    # Convert to date objects if they are datetime objects
    # Convert to date objects if they are datetime objects
    if isinstance(dt, datetime) and isinstance(reference, datetime):
    if isinstance(dt, datetime) and isinstance(reference, datetime):
    return dt < reference
    return dt < reference
    elif isinstance(dt, datetime):
    elif isinstance(dt, datetime):
    dt = dt.date()
    dt = dt.date()
    elif isinstance(reference, datetime):
    elif isinstance(reference, datetime):
    reference = reference.date()
    reference = reference.date()


    return dt < reference
    return dt < reference




    def is_same_day(dt1: DateLike, dt2: DateLike) -> bool:
    def is_same_day(dt1: DateLike, dt2: DateLike) -> bool:
    """
    """
    Check if two dates are on the same day.
    Check if two dates are on the same day.


    Args:
    Args:
    dt1: First date or datetime object
    dt1: First date or datetime object
    dt2: Second date or datetime object
    dt2: Second date or datetime object


    Returns:
    Returns:
    True if the dates are on the same day, False otherwise
    True if the dates are on the same day, False otherwise
    """
    """
    return dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day
    return dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day




    def is_same_month(dt1: DateLike, dt2: DateLike) -> bool:
    def is_same_month(dt1: DateLike, dt2: DateLike) -> bool:
    """
    """
    Check if two dates are in the same month.
    Check if two dates are in the same month.


    Args:
    Args:
    dt1: First date or datetime object
    dt1: First date or datetime object
    dt2: Second date or datetime object
    dt2: Second date or datetime object


    Returns:
    Returns:
    True if the dates are in the same month, False otherwise
    True if the dates are in the same month, False otherwise
    """
    """
    return dt1.year == dt2.year and dt1.month == dt2.month
    return dt1.year == dt2.year and dt1.month == dt2.month




    def is_same_year(dt1: DateLike, dt2: DateLike) -> bool:
    def is_same_year(dt1: DateLike, dt2: DateLike) -> bool:
    """
    """
    Check if two dates are in the same year.
    Check if two dates are in the same year.


    Args:
    Args:
    dt1: First date or datetime object
    dt1: First date or datetime object
    dt2: Second date or datetime object
    dt2: Second date or datetime object


    Returns:
    Returns:
    True if the dates are in the same year, False otherwise
    True if the dates are in the same year, False otherwise
    """
    """
    return dt1.year == dt2.year
    return dt1.year == dt2.year