"""
Common utilities for the pAIssive Income project.

This package provides common utility functions used across the project,
including date handling, JSON serialization, file operations, and input validation.
"""

from .date_utils import (
    format_date, format_datetime, get_days_in_month, get_days_in_year,
    get_start_of_day, get_start_of_week, get_start_of_month, get_start_of_year,
    get_end_of_day, get_end_of_week, get_end_of_month, get_end_of_year,
    is_date_in_range, get_date_difference, add_days, add_months, add_years,
    is_future_date, is_past_date, is_same_day, is_same_month, is_same_year
)

from .json_utils import (
    to_json, from_json, save_to_json_file, load_from_json_file,
    json_serialize, json_deserialize
)

from .file_utils import (
    read_file, write_file, file_exists, create_directory,
    get_file_path, get_directory_path, list_files, list_directories,
    get_file_extension, get_file_name, get_file_size
)

from .string_utils import (
    is_empty, is_blank, truncate, slugify, camel_to_snake,
    snake_to_camel, format_currency, format_number, format_percentage
)

from .validation_utils import (
    is_valid_email, is_valid_url, is_valid_uuid, is_valid_phone,
    is_valid_username, is_valid_password, is_valid_slug, is_valid_json,
    is_valid_date, is_valid_file_path, is_valid_file, is_valid_directory,
    sanitize_string, sanitize_html, sanitize_filename, sanitize_path,
    validate_and_sanitize_input, validate_config_file
)

__all__ = [
    # Date utilities
    'format_date', 'format_datetime', 'get_days_in_month', 'get_days_in_year',
    'get_start_of_day', 'get_start_of_week', 'get_start_of_month', 'get_start_of_year',
    'get_end_of_day', 'get_end_of_week', 'get_end_of_month', 'get_end_of_year',
    'is_date_in_range', 'get_date_difference', 'add_days', 'add_months', 'add_years',
    'is_future_date', 'is_past_date', 'is_same_day', 'is_same_month', 'is_same_year',

    # JSON utilities
    'to_json', 'from_json', 'save_to_json_file', 'load_from_json_file',
    'json_serialize', 'json_deserialize',

    # File utilities
    'read_file', 'write_file', 'file_exists', 'create_directory',
    'get_file_path', 'get_directory_path', 'list_files', 'list_directories',
    'get_file_extension', 'get_file_name', 'get_file_size',

    # String utilities
    'is_empty', 'is_blank', 'truncate', 'slugify', 'camel_to_snake',
    'snake_to_camel', 'format_currency', 'format_number', 'format_percentage',

    # Validation utilities
    'is_valid_email', 'is_valid_url', 'is_valid_uuid', 'is_valid_phone',
    'is_valid_username', 'is_valid_password', 'is_valid_slug', 'is_valid_json',
    'is_valid_date', 'is_valid_file_path', 'is_valid_file', 'is_valid_directory',
    'sanitize_string', 'sanitize_html', 'sanitize_filename', 'sanitize_path',
    'validate_and_sanitize_input', 'validate_config_file'
]
