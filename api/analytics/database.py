"""
"""
API Analytics Database.
API Analytics Database.


This module provides a database for storing and retrieving API analytics data.
This module provides a database for storing and retrieving API analytics data.
"""
"""


import json
import json
import logging
import logging
import os
import os
import sqlite3
import sqlite3
import threading
import threading
import time
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
from typing import Any, Dict, List, Tuple


# Set up logging
# Set up logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Constants
# Constants
DB_SCHEMA_VERSION = "1.0"
DB_SCHEMA_VERSION = "1.0"
DEFAULT_DB_PATH = os.path.expanduser("~/.paissive_income/api_analytics.db")
DEFAULT_DB_PATH = os.path.expanduser("~/.paissive_income/api_analytics.db")
DEFAULT_ANALYTICS_RETENTION_DAYS = 365  # Keep analytics for 1 year by default
DEFAULT_ANALYTICS_RETENTION_DAYS = 365  # Keep analytics for 1 year by default




class AnalyticsDatabase:
    class AnalyticsDatabase:
    """
    """
    Manages storage and retrieval of API analytics data in SQLite.
    Manages storage and retrieval of API analytics data in SQLite.
    """
    """


    def __init__(self, db_path: str = None):
    def __init__(self, db_path: str = None):
    """
    """
    Initialize the analytics database.
    Initialize the analytics database.


    Args:
    Args:
    db_path: Path to the SQLite database file
    db_path: Path to the SQLite database file
    """
    """
    self.db_path = db_path or DEFAULT_DB_PATH
    self.db_path = db_path or DEFAULT_DB_PATH
    self._ensure_db_dir()
    self._ensure_db_dir()
    self._connect()
    self._connect()
    self._init_schema()
    self._init_schema()
    self._lock = threading.Lock()
    self._lock = threading.Lock()


    def _ensure_db_dir(self) -> None:
    def _ensure_db_dir(self) -> None:
    """Ensure the database directory exists."""
    db_dir = os.path.dirname(self.db_path)
    if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

    def _connect(self) -> None:
    """Connect to the SQLite database."""
    self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
    self.conn.row_factory = sqlite3.Row

    def _init_schema(self) -> None:
    """Initialize the database schema if it doesn't exist."""
    cursor = self.conn.cursor()

    # Check if schema exists
    cursor.execute("PRAGMA user_version")
    user_version = cursor.fetchone()[0]

    if user_version == 0:
    logger.info(
    f"Initializing API analytics database schema v{DB_SCHEMA_VERSION}"
    )

    # Create tables
    cursor.execute(
    """
    """
    CREATE TABLE api_requests (
    CREATE TABLE api_requests (
    id TEXT PRIMARY KEY,
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    method TEXT NOT NULL,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    path TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    version TEXT,
    version TEXT,
    status_code INTEGER,
    status_code INTEGER,
    response_time REAL,
    response_time REAL,
    user_id TEXT,
    user_id TEXT,
    api_key_id TEXT,
    api_key_id TEXT,
    client_ip TEXT,
    client_ip TEXT,
    user_agent TEXT,
    user_agent TEXT,
    request_size INTEGER,
    request_size INTEGER,
    response_size INTEGER,
    response_size INTEGER,
    query_params TEXT,
    query_params TEXT,
    error_type TEXT,
    error_type TEXT,
    error_message TEXT,
    error_message TEXT,
    metadata TEXT
    metadata TEXT
    )
    )
    """
    """
    )
    )


    # Create indexes
    # Create indexes
    cursor.execute(
    cursor.execute(
    "CREATE INDEX idx_api_requests_timestamp ON api_requests(timestamp)"
    "CREATE INDEX idx_api_requests_timestamp ON api_requests(timestamp)"
    )
    )
    cursor.execute(
    cursor.execute(
    "CREATE INDEX idx_api_requests_endpoint ON api_requests(endpoint)"
    "CREATE INDEX idx_api_requests_endpoint ON api_requests(endpoint)"
    )
    )
    cursor.execute(
    cursor.execute(
    "CREATE INDEX idx_api_requests_version ON api_requests(version)"
    "CREATE INDEX idx_api_requests_version ON api_requests(version)"
    )
    )
    cursor.execute(
    cursor.execute(
    "CREATE INDEX idx_api_requests_status_code ON api_requests(status_code)"
    "CREATE INDEX idx_api_requests_status_code ON api_requests(status_code)"
    )
    )
    cursor.execute(
    cursor.execute(
    "CREATE INDEX idx_api_requests_user_id ON api_requests(user_id)"
    "CREATE INDEX idx_api_requests_user_id ON api_requests(user_id)"
    )
    )
    cursor.execute(
    cursor.execute(
    "CREATE INDEX idx_api_requests_api_key_id ON api_requests(api_key_id)"
    "CREATE INDEX idx_api_requests_api_key_id ON api_requests(api_key_id)"
    )
    )


    # Create daily aggregated metrics table
    # Create daily aggregated metrics table
    cursor.execute(
    cursor.execute(
    """
    """
    CREATE TABLE daily_metrics (
    CREATE TABLE daily_metrics (
    date TEXT NOT NULL,
    date TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    version TEXT,
    version TEXT,
    request_count INTEGER DEFAULT 0,
    request_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    total_response_time REAL DEFAULT 0,
    total_response_time REAL DEFAULT 0,
    avg_response_time REAL DEFAULT 0,
    avg_response_time REAL DEFAULT 0,
    min_response_time REAL DEFAULT 0,
    min_response_time REAL DEFAULT 0,
    max_response_time REAL DEFAULT 0,
    max_response_time REAL DEFAULT 0,
    p95_response_time REAL DEFAULT 0,
    p95_response_time REAL DEFAULT 0,
    total_request_size INTEGER DEFAULT 0,
    total_request_size INTEGER DEFAULT 0,
    total_response_size INTEGER DEFAULT 0,
    total_response_size INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    unique_api_keys INTEGER DEFAULT 0,
    unique_api_keys INTEGER DEFAULT 0,
    PRIMARY KEY (date, endpoint, version)
    PRIMARY KEY (date, endpoint, version)
    )
    )
    """
    """
    )
    )


    # Create index for daily metrics
    # Create index for daily metrics
    cursor.execute("CREATE INDEX idx_daily_metrics_date ON daily_metrics(date)")
    cursor.execute("CREATE INDEX idx_daily_metrics_date ON daily_metrics(date)")


    # Create user metrics table
    # Create user metrics table
    cursor.execute(
    cursor.execute(
    """
    """
    CREATE TABLE user_metrics (
    CREATE TABLE user_metrics (
    date TEXT NOT NULL,
    date TEXT NOT NULL,
    user_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    request_count INTEGER DEFAULT 0,
    request_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    total_response_time REAL DEFAULT 0,
    total_response_time REAL DEFAULT 0,
    endpoints_used TEXT,
    endpoints_used TEXT,
    PRIMARY KEY (date, user_id)
    PRIMARY KEY (date, user_id)
    )
    )
    """
    """
    )
    )


    # Create API key metrics table
    # Create API key metrics table
    cursor.execute(
    cursor.execute(
    """
    """
    CREATE TABLE api_key_metrics (
    CREATE TABLE api_key_metrics (
    date TEXT NOT NULL,
    date TEXT NOT NULL,
    api_key_id TEXT NOT NULL,
    api_key_id TEXT NOT NULL,
    request_count INTEGER DEFAULT 0,
    request_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    total_response_time REAL DEFAULT 0,
    total_response_time REAL DEFAULT 0,
    endpoints_used TEXT,
    endpoints_used TEXT,
    PRIMARY KEY (date, api_key_id)
    PRIMARY KEY (date, api_key_id)
    )
    )
    """
    """
    )
    )


    # Set schema version
    # Set schema version
    cursor.execute("PRAGMA user_version = 100")  # v1.0.0
    cursor.execute("PRAGMA user_version = 100")  # v1.0.0


    self.conn.commit()
    self.conn.commit()


    def save_request(self, request_data: Dict[str, Any]) -> None:
    def save_request(self, request_data: Dict[str, Any]) -> None:
    """
    """
    Save API request data to the database.
    Save API request data to the database.


    Args:
    Args:
    request_data: Dictionary containing request data
    request_data: Dictionary containing request data
    """
    """
    with self._lock:
    with self._lock:
    cursor = self.conn.cursor()
    cursor = self.conn.cursor()


    # Convert metadata dict to JSON string
    # Convert metadata dict to JSON string
    metadata_json = (
    metadata_json = (
    json.dumps(request_data.get("metadata", {}))
    json.dumps(request_data.get("metadata", {}))
    if request_data.get("metadata")
    if request_data.get("metadata")
    else "{}"
    else "{}"
    )
    )
    query_params_json = (
    query_params_json = (
    json.dumps(request_data.get("query_params", {}))
    json.dumps(request_data.get("query_params", {}))
    if request_data.get("query_params")
    if request_data.get("query_params")
    else "{}"
    else "{}"
    )
    )


    # Insert the request data
    # Insert the request data
    cursor.execute(
    cursor.execute(
    """
    """
    INSERT OR REPLACE INTO api_requests (
    INSERT OR REPLACE INTO api_requests (
    id, timestamp, method, path, endpoint, version,
    id, timestamp, method, path, endpoint, version,
    status_code, response_time, user_id, api_key_id,
    status_code, response_time, user_id, api_key_id,
    client_ip, user_agent, request_size, response_size,
    client_ip, user_agent, request_size, response_size,
    query_params, error_type, error_message, metadata
    query_params, error_type, error_message, metadata
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    """,
    (
    (
    request_data.get("id"),
    request_data.get("id"),
    request_data.get("timestamp"),
    request_data.get("timestamp"),
    request_data.get("method"),
    request_data.get("method"),
    request_data.get("path"),
    request_data.get("path"),
    request_data.get("endpoint"),
    request_data.get("endpoint"),
    request_data.get("version"),
    request_data.get("version"),
    request_data.get("status_code"),
    request_data.get("status_code"),
    request_data.get("response_time"),
    request_data.get("response_time"),
    request_data.get("user_id"),
    request_data.get("user_id"),
    request_data.get("api_key_id"),
    request_data.get("api_key_id"),
    request_data.get("client_ip"),
    request_data.get("client_ip"),
    request_data.get("user_agent"),
    request_data.get("user_agent"),
    request_data.get("request_size"),
    request_data.get("request_size"),
    request_data.get("response_size"),
    request_data.get("response_size"),
    query_params_json,
    query_params_json,
    request_data.get("error_type"),
    request_data.get("error_type"),
    request_data.get("error_message"),
    request_data.get("error_message"),
    metadata_json,
    metadata_json,
    ),
    ),
    )
    )


    self.conn.commit()
    self.conn.commit()


    def update_daily_metrics(self, date: str) -> None:
    def update_daily_metrics(self, date: str) -> None:
    """
    """
    Update daily aggregated metrics for a specific date.
    Update daily aggregated metrics for a specific date.


    Args:
    Args:
    date: Date string in YYYY-MM-DD format
    date: Date string in YYYY-MM-DD format
    """
    """
    with self._lock:
    with self._lock:
    cursor = self.conn.cursor()
    cursor = self.conn.cursor()


    # Clear existing metrics for the date
    # Clear existing metrics for the date
    cursor.execute("DELETE FROM daily_metrics WHERE date = ?", (date,))
    cursor.execute("DELETE FROM daily_metrics WHERE date = ?", (date,))


    # Calculate start and end timestamps for the day
    # Calculate start and end timestamps for the day
    start_timestamp = f"{date}T00:00:00"
    start_timestamp = f"{date}T00:00:00"
    end_timestamp = f"{date}T23:59:59.999999"
    end_timestamp = f"{date}T23:59:59.999999"


    # Aggregate metrics by endpoint and version
    # Aggregate metrics by endpoint and version
    cursor.execute(
    cursor.execute(
    """
    """
    INSERT INTO daily_metrics (
    INSERT INTO daily_metrics (
    date, endpoint, version, request_count, error_count,
    date, endpoint, version, request_count, error_count,
    total_response_time, avg_response_time, min_response_time,
    total_response_time, avg_response_time, min_response_time,
    max_response_time, p95_response_time, total_request_size,
    max_response_time, p95_response_time, total_request_size,
    total_response_size, unique_users, unique_api_keys
    total_response_size, unique_users, unique_api_keys
    )
    )
    SELECT
    SELECT
    ?, endpoint, version,
    ?, endpoint, version,
    COUNT(*) as request_count,
    COUNT(*) as request_count,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
    SUM(response_time) as total_response_time,
    SUM(response_time) as total_response_time,
    AVG(response_time) as avg_response_time,
    AVG(response_time) as avg_response_time,
    MIN(response_time) as min_response_time,
    MIN(response_time) as min_response_time,
    MAX(response_time) as max_response_time,
    MAX(response_time) as max_response_time,
    -- Approximation of p95 (not accurate but gives a rough estimate)
    -- Approximation of p95 (not accurate but gives a rough estimate)
    -- For accurate percentiles, we'd need a more complex calculation
    -- For accurate percentiles, we'd need a more complex calculation
    (SELECT response_time FROM api_requests r2
    (SELECT response_time FROM api_requests r2
    WHERE r2.endpoint = r1.endpoint AND r2.version = r1.version
    WHERE r2.endpoint = r1.endpoint AND r2.version = r1.version
    AND r2.timestamp BETWEEN ? AND ?
    AND r2.timestamp BETWEEN ? AND ?
    ORDER BY response_time DESC
    ORDER BY response_time DESC
    LIMIT 1
    LIMIT 1
    OFFSET (SELECT COUNT(*) FROM api_requests r3
    OFFSET (SELECT COUNT(*) FROM api_requests r3
    WHERE r3.endpoint = r1.endpoint AND r3.version = r1.version
    WHERE r3.endpoint = r1.endpoint AND r3.version = r1.version
    AND r3.timestamp BETWEEN ? AND ?) * 95 / 100) as p95_response_time,
    AND r3.timestamp BETWEEN ? AND ?) * 95 / 100) as p95_response_time,
    SUM(request_size) as total_request_size,
    SUM(request_size) as total_request_size,
    SUM(response_size) as total_response_size,
    SUM(response_size) as total_response_size,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT api_key_id) as unique_api_keys
    COUNT(DISTINCT api_key_id) as unique_api_keys
    FROM api_requests r1
    FROM api_requests r1
    WHERE timestamp BETWEEN ? AND ?
    WHERE timestamp BETWEEN ? AND ?
    GROUP BY endpoint, version
    GROUP BY endpoint, version
    """,
    """,
    (
    (
    date,
    date,
    start_timestamp,
    start_timestamp,
    end_timestamp,
    end_timestamp,
    start_timestamp,
    start_timestamp,
    end_timestamp,
    end_timestamp,
    start_timestamp,
    start_timestamp,
    end_timestamp,
    end_timestamp,
    ),
    ),
    )
    )


    # Update user metrics
    # Update user metrics
    cursor.execute("DELETE FROM user_metrics WHERE date = ?", (date,))
    cursor.execute("DELETE FROM user_metrics WHERE date = ?", (date,))
    cursor.execute(
    cursor.execute(
    """
    """
    INSERT INTO user_metrics (
    INSERT INTO user_metrics (
    date, user_id, request_count, error_count,
    date, user_id, request_count, error_count,
    total_response_time, endpoints_used
    total_response_time, endpoints_used
    )
    )
    SELECT
    SELECT
    ?, user_id,
    ?, user_id,
    COUNT(*) as request_count,
    COUNT(*) as request_count,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
    SUM(response_time) as total_response_time,
    SUM(response_time) as total_response_time,
    json_group_array(DISTINCT endpoint) as endpoints_used
    json_group_array(DISTINCT endpoint) as endpoints_used
    FROM api_requests
    FROM api_requests
    WHERE timestamp BETWEEN ? AND ? AND user_id IS NOT NULL
    WHERE timestamp BETWEEN ? AND ? AND user_id IS NOT NULL
    GROUP BY user_id
    GROUP BY user_id
    """,
    """,
    (date, start_timestamp, end_timestamp),
    (date, start_timestamp, end_timestamp),
    )
    )


    # Update API key metrics
    # Update API key metrics
    cursor.execute("DELETE FROM api_key_metrics WHERE date = ?", (date,))
    cursor.execute("DELETE FROM api_key_metrics WHERE date = ?", (date,))
    cursor.execute(
    cursor.execute(
    """
    """
    INSERT INTO api_key_metrics (
    INSERT INTO api_key_metrics (
    date, api_key_id, request_count, error_count,
    date, api_key_id, request_count, error_count,
    total_response_time, endpoints_used
    total_response_time, endpoints_used
    )
    )
    SELECT
    SELECT
    ?, api_key_id,
    ?, api_key_id,
    COUNT(*) as request_count,
    COUNT(*) as request_count,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
    SUM(response_time) as total_response_time,
    SUM(response_time) as total_response_time,
    json_group_array(DISTINCT endpoint) as endpoints_used
    json_group_array(DISTINCT endpoint) as endpoints_used
    FROM api_requests
    FROM api_requests
    WHERE timestamp BETWEEN ? AND ? AND api_key_id IS NOT NULL
    WHERE timestamp BETWEEN ? AND ? AND api_key_id IS NOT NULL
    GROUP BY api_key_id
    GROUP BY api_key_id
    """,
    """,
    (date, start_timestamp, end_timestamp),
    (date, start_timestamp, end_timestamp),
    )
    )


    self.conn.commit()
    self.conn.commit()


    def get_requests(
    def get_requests(
    self,
    self,
    endpoint: str = None,
    endpoint: str = None,
    version: str = None,
    version: str = None,
    user_id: str = None,
    user_id: str = None,
    api_key_id: str = None,
    api_key_id: str = None,
    status_code: int = None,
    status_code: int = None,
    time_range: Tuple[datetime, datetime] = None,
    time_range: Tuple[datetime, datetime] = None,
    limit: int = 1000,
    limit: int = 1000,
    offset: int = 0,
    offset: int = 0,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get API requests from the database.
    Get API requests from the database.


    Args:
    Args:
    endpoint: Filter by endpoint
    endpoint: Filter by endpoint
    version: Filter by API version
    version: Filter by API version
    user_id: Filter by user ID
    user_id: Filter by user ID
    api_key_id: Filter by API key ID
    api_key_id: Filter by API key ID
    status_code: Filter by status code
    status_code: Filter by status code
    time_range: Filter by time range (start_time, end_time)
    time_range: Filter by time range (start_time, end_time)
    limit: Maximum number of records to return
    limit: Maximum number of records to return
    offset: Number of records to skip
    offset: Number of records to skip


    Returns:
    Returns:
    List of request dictionaries
    List of request dictionaries
    """
    """
    cursor = self.conn.cursor()
    cursor = self.conn.cursor()


    query = "SELECT * FROM api_requests"
    query = "SELECT * FROM api_requests"
    params = []
    params = []
    where_clauses = []
    where_clauses = []


    if endpoint:
    if endpoint:
    where_clauses.append("endpoint = ?")
    where_clauses.append("endpoint = ?")
    params.append(endpoint)
    params.append(endpoint)


    if version:
    if version:
    where_clauses.append("version = ?")
    where_clauses.append("version = ?")
    params.append(version)
    params.append(version)


    if user_id:
    if user_id:
    where_clauses.append("user_id = ?")
    where_clauses.append("user_id = ?")
    params.append(user_id)
    params.append(user_id)


    if api_key_id:
    if api_key_id:
    where_clauses.append("api_key_id = ?")
    where_clauses.append("api_key_id = ?")
    params.append(api_key_id)
    params.append(api_key_id)


    if status_code:
    if status_code:
    where_clauses.append("status_code = ?")
    where_clauses.append("status_code = ?")
    params.append(status_code)
    params.append(status_code)


    if time_range:
    if time_range:
    start_time, end_time = time_range
    start_time, end_time = time_range
    where_clauses.append("timestamp BETWEEN ? AND ?")
    where_clauses.append("timestamp BETWEEN ? AND ?")
    params.append(start_time.isoformat())
    params.append(start_time.isoformat())
    params.append(end_time.isoformat())
    params.append(end_time.isoformat())


    if where_clauses:
    if where_clauses:
    query += " WHERE " + " AND ".join(where_clauses)
    query += " WHERE " + " AND ".join(where_clauses)


    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.append(limit)
    params.append(limit)
    params.append(offset)
    params.append(offset)


    cursor.execute(query, params)
    cursor.execute(query, params)


    # Convert rows to dictionaries
    # Convert rows to dictionaries
    result = []
    result = []
    for row in cursor.fetchall():
    for row in cursor.fetchall():
    row_dict = dict(row)
    row_dict = dict(row)


    # Parse JSON fields
    # Parse JSON fields
    if row_dict.get("metadata"):
    if row_dict.get("metadata"):
    try:
    try:
    row_dict["metadata"] = json.loads(row_dict["metadata"])
    row_dict["metadata"] = json.loads(row_dict["metadata"])
except Exception:
except Exception:
    row_dict["metadata"] = {}
    row_dict["metadata"] = {}


    if row_dict.get("query_params"):
    if row_dict.get("query_params"):
    try:
    try:
    row_dict["query_params"] = json.loads(row_dict["query_params"])
    row_dict["query_params"] = json.loads(row_dict["query_params"])
except Exception:
except Exception:
    row_dict["query_params"] = {}
    row_dict["query_params"] = {}


    result.append(row_dict)
    result.append(row_dict)


    return result
    return result


    def get_daily_metrics(
    def get_daily_metrics(
    self,
    self,
    start_date: str = None,
    start_date: str = None,
    end_date: str = None,
    end_date: str = None,
    endpoint: str = None,
    endpoint: str = None,
    version: str = None,
    version: str = None,
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get daily aggregated metrics.
    Get daily aggregated metrics.


    Args:
    Args:
    start_date: Start date in YYYY-MM-DD format
    start_date: Start date in YYYY-MM-DD format
    end_date: End date in YYYY-MM-DD format
    end_date: End date in YYYY-MM-DD format
    endpoint: Filter by endpoint
    endpoint: Filter by endpoint
    version: Filter by API version
    version: Filter by API version


    Returns:
    Returns:
    List of daily metrics dictionaries
    List of daily metrics dictionaries
    """
    """
    cursor = self.conn.cursor()
    cursor = self.conn.cursor()


    query = "SELECT * FROM daily_metrics"
    query = "SELECT * FROM daily_metrics"
    params = []
    params = []
    where_clauses = []
    where_clauses = []


    if start_date:
    if start_date:
    where_clauses.append("date >= ?")
    where_clauses.append("date >= ?")
    params.append(start_date)
    params.append(start_date)


    if end_date:
    if end_date:
    where_clauses.append("date <= ?")
    where_clauses.append("date <= ?")
    params.append(end_date)
    params.append(end_date)


    if endpoint:
    if endpoint:
    where_clauses.append("endpoint = ?")
    where_clauses.append("endpoint = ?")
    params.append(endpoint)
    params.append(endpoint)


    if version:
    if version:
    where_clauses.append("version = ?")
    where_clauses.append("version = ?")
    params.append(version)
    params.append(version)


    if where_clauses:
    if where_clauses:
    query += " WHERE " + " AND ".join(where_clauses)
    query += " WHERE " + " AND ".join(where_clauses)


    query += " ORDER BY date DESC, request_count DESC"
    query += " ORDER BY date DESC, request_count DESC"


    cursor.execute(query, params)
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]
    return [dict(row) for row in cursor.fetchall()]


    def get_user_metrics(
    def get_user_metrics(
    self, start_date: str = None, end_date: str = None, user_id: str = None
    self, start_date: str = None, end_date: str = None, user_id: str = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get user metrics.
    Get user metrics.


    Args:
    Args:
    start_date: Start date in YYYY-MM-DD format
    start_date: Start date in YYYY-MM-DD format
    end_date: End date in YYYY-MM-DD format
    end_date: End date in YYYY-MM-DD format
    user_id: Filter by user ID
    user_id: Filter by user ID


    Returns:
    Returns:
    List of user metrics dictionaries
    List of user metrics dictionaries
    """
    """
    cursor = self.conn.cursor()
    cursor = self.conn.cursor()


    query = "SELECT * FROM user_metrics"
    query = "SELECT * FROM user_metrics"
    params = []
    params = []
    where_clauses = []
    where_clauses = []


    if start_date:
    if start_date:
    where_clauses.append("date >= ?")
    where_clauses.append("date >= ?")
    params.append(start_date)
    params.append(start_date)


    if end_date:
    if end_date:
    where_clauses.append("date <= ?")
    where_clauses.append("date <= ?")
    params.append(end_date)
    params.append(end_date)


    if user_id:
    if user_id:
    where_clauses.append("user_id = ?")
    where_clauses.append("user_id = ?")
    params.append(user_id)
    params.append(user_id)


    if where_clauses:
    if where_clauses:
    query += " WHERE " + " AND ".join(where_clauses)
    query += " WHERE " + " AND ".join(where_clauses)


    query += " ORDER BY date DESC, request_count DESC"
    query += " ORDER BY date DESC, request_count DESC"


    cursor.execute(query, params)
    cursor.execute(query, params)


    # Convert rows to dictionaries and parse JSON fields
    # Convert rows to dictionaries and parse JSON fields
    result = []
    result = []
    for row in cursor.fetchall():
    for row in cursor.fetchall():
    row_dict = dict(row)
    row_dict = dict(row)


    # Parse endpoints_used JSON
    # Parse endpoints_used JSON
    if row_dict.get("endpoints_used"):
    if row_dict.get("endpoints_used"):
    try:
    try:
    row_dict["endpoints_used"] = json.loads(row_dict["endpoints_used"])
    row_dict["endpoints_used"] = json.loads(row_dict["endpoints_used"])
except Exception:
except Exception:
    row_dict["endpoints_used"] = []
    row_dict["endpoints_used"] = []


    result.append(row_dict)
    result.append(row_dict)


    return result
    return result


    def get_api_key_metrics(
    def get_api_key_metrics(
    self, start_date: str = None, end_date: str = None, api_key_id: str = None
    self, start_date: str = None, end_date: str = None, api_key_id: str = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get API key metrics.
    Get API key metrics.


    Args:
    Args:
    start_date: Start date in YYYY-MM-DD format
    start_date: Start date in YYYY-MM-DD format
    end_date: End date in YYYY-MM-DD format
    end_date: End date in YYYY-MM-DD format
    api_key_id: Filter by API key ID
    api_key_id: Filter by API key ID


    Returns:
    Returns:
    List of API key metrics dictionaries
    List of API key metrics dictionaries
    """
    """
    cursor = self.conn.cursor()
    cursor = self.conn.cursor()


    query = "SELECT * FROM api_key_metrics"
    query = "SELECT * FROM api_key_metrics"
    params = []
    params = []
    where_clauses = []
    where_clauses = []


    if start_date:
    if start_date:
    where_clauses.append("date >= ?")
    where_clauses.append("date >= ?")
    params.append(start_date)
    params.append(start_date)


    if end_date:
    if end_date:
    where_clauses.append("date <= ?")
    where_clauses.append("date <= ?")
    params.append(end_date)
    params.append(end_date)


    if api_key_id:
    if api_key_id:
    where_clauses.append("api_key_id = ?")
    where_clauses.append("api_key_id = ?")
    params.append(api_key_id)
    params.append(api_key_id)


    if where_clauses:
    if where_clauses:
    query += " WHERE " + " AND ".join(where_clauses)
    query += " WHERE " + " AND ".join(where_clauses)


    query += " ORDER BY date DESC, request_count DESC"
    query += " ORDER BY date DESC, request_count DESC"


    cursor.execute(query, params)
    cursor.execute(query, params)


    # Convert rows to dictionaries and parse JSON fields
    # Convert rows to dictionaries and parse JSON fields
    result = []
    result = []
    for row in cursor.fetchall():
    for row in cursor.fetchall():
    row_dict = dict(row)
    row_dict = dict(row)


    # Parse endpoints_used JSON
    # Parse endpoints_used JSON
    if row_dict.get("endpoints_used"):
    if row_dict.get("endpoints_used"):
    try:
    try:
    row_dict["endpoints_used"] = json.loads(row_dict["endpoints_used"])
    row_dict["endpoints_used"] = json.loads(row_dict["endpoints_used"])
except Exception:
except Exception:
    row_dict["endpoints_used"] = []
    row_dict["endpoints_used"] = []


    result.append(row_dict)
    result.append(row_dict)


    return result
    return result


    def get_endpoint_stats(
    def get_endpoint_stats(
    self, start_date: str = None, end_date: str = None
    self, start_date: str = None, end_date: str = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Get aggregated statistics for each endpoint.
    Get aggregated statistics for each endpoint.


    Args:
    Args:
    start_date: Start date in YYYY-MM-DD format
    start_date: Start date in YYYY-MM-DD format
    end_date: End date in YYYY-MM-DD format
    end_date: End date in YYYY-MM-DD format


    Returns:
    Returns:
    List of endpoint statistics dictionaries
    List of endpoint statistics dictionaries
    """
    """
    cursor = self.conn.cursor()
    cursor = self.conn.cursor()


    query = """
    query = """
    SELECT
    SELECT
    endpoint,
    endpoint,
    version,
    version,
    SUM(request_count) as total_requests,
    SUM(request_count) as total_requests,
    SUM(error_count) as total_errors,
    SUM(error_count) as total_errors,
    SUM(total_response_time) / SUM(request_count) as avg_response_time,
    SUM(total_response_time) / SUM(request_count) as avg_response_time,
    MIN(min_response_time) as min_response_time,
    MIN(min_response_time) as min_response_time,
    MAX(max_response_time) as max_response_time,
    MAX(max_response_time) as max_response_time,
    SUM(total_request_size) as total_request_size,
    SUM(total_request_size) as total_request_size,
    SUM(total_response_size) as total_response_size,
    SUM(total_response_size) as total_response_size,
    SUM(unique_users) as total_unique_users,
    SUM(unique_users) as total_unique_users,
    SUM(unique_api_keys) as total_unique_api_keys
    SUM(unique_api_keys) as total_unique_api_keys
    FROM daily_metrics
    FROM daily_metrics
    """
    """


    params = []
    params = []
    where_clauses = []
    where_clauses = []


    if start_date:
    if start_date:
    where_clauses.append("date >= ?")
    where_clauses.append("date >= ?")
    params.append(start_date)
    params.append(start_date)


    if end_date:
    if end_date:
    where_clauses.append("date <= ?")
    where_clauses.append("date <= ?")
    params.append(end_date)
    params.append(end_date)


    if where_clauses:
    if where_clauses:
    query += " WHERE " + " AND ".join(where_clauses)
    query += " WHERE " + " AND ".join(where_clauses)


    query += " GROUP BY endpoint, version ORDER BY total_requests DESC"
    query += " GROUP BY endpoint, version ORDER BY total_requests DESC"


    cursor.execute(query, params)
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]
    return [dict(row) for row in cursor.fetchall()]


    def cleanup_old_data(self, days: int = DEFAULT_ANALYTICS_RETENTION_DAYS) -> int:
    def cleanup_old_data(self, days: int = DEFAULT_ANALYTICS_RETENTION_DAYS) -> int:
    """
    """
    Remove data older than the specified number of days.
    Remove data older than the specified number of days.


    Args:
    Args:
    days: Number of days to keep
    days: Number of days to keep


    Returns:
    Returns:
    Number of records deleted
    Number of records deleted
    """
    """
    if days <= 0:
    if days <= 0:
    return 0
    return 0


    with self._lock:
    with self._lock:
    cursor = self.conn.cursor()
    cursor = self.conn.cursor()
    threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
    threshold_date = (datetime.now() - timedelta(days=days)).isoformat()


    # Delete old API requests
    # Delete old API requests
    cursor.execute(
    cursor.execute(
    "DELETE FROM api_requests WHERE timestamp < ?", (threshold_date,)
    "DELETE FROM api_requests WHERE timestamp < ?", (threshold_date,)
    )
    )
    request_count = cursor.rowcount
    request_count = cursor.rowcount


    # Delete old daily metrics
    # Delete old daily metrics
    threshold_day = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    threshold_day = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cursor.execute("DELETE FROM daily_metrics WHERE date < ?", (threshold_day,))
    cursor.execute("DELETE FROM daily_metrics WHERE date < ?", (threshold_day,))
    metrics_count = cursor.rowcount
    metrics_count = cursor.rowcount


    # Delete old user metrics
    # Delete old user metrics
    cursor.execute("DELETE FROM user_metrics WHERE date < ?", (threshold_day,))
    cursor.execute("DELETE FROM user_metrics WHERE date < ?", (threshold_day,))
    user_count = cursor.rowcount
    user_count = cursor.rowcount


    # Delete old API key metrics
    # Delete old API key metrics
    cursor.execute(
    cursor.execute(
    "DELETE FROM api_key_metrics WHERE date < ?", (threshold_day,)
    "DELETE FROM api_key_metrics WHERE date < ?", (threshold_day,)
    )
    )
    api_key_count = cursor.rowcount
    api_key_count = cursor.rowcount


    self.conn.commit()
    self.conn.commit()


    return request_count + metrics_count + user_count + api_key_count
    return request_count + metrics_count + user_count + api_key_count


    def close(self) -> None:
    def close(self) -> None:
    """Close the database connection."""
    if hasattr(self, "conn"):
    self.conn.close()