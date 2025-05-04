"""
"""
SQLite cache backend for the model cache system.
SQLite cache backend for the model cache system.


This module provides a SQLite-based cache backend.
This module provides a SQLite-based cache backend.
"""
"""




import json
import json
import os
import os
import pickle
import pickle
import re
import re
import sqlite3
import sqlite3
import threading
import threading
import time
import time
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from .base import CacheBackend
from .base import CacheBackend




class SQLiteCache:
    class SQLiteCache:


    pass  # Added missing block
    pass  # Added missing block
    """
    """
    SQLite-based cache backend.
    SQLite-based cache backend.
    """
    """


    def __init__(self, db_path: str, serialization: str = "json", **kwargs):
    def __init__(self, db_path: str, serialization: str = "json", **kwargs):
    """
    """
    Initialize the SQLite cache.
    Initialize the SQLite cache.


    Args:
    Args:
    db_path: Path to the SQLite database file
    db_path: Path to the SQLite database file
    serialization: Serialization format (json, pickle)
    serialization: Serialization format (json, pickle)
    **kwargs: Additional parameters for the cache
    **kwargs: Additional parameters for the cache
    """
    """
    self.db_path = os.path.abspath(db_path)
    self.db_path = os.path.abspath(db_path)
    self.serialization = serialization.lower()
    self.serialization = serialization.lower()


    # Create database directory if it doesn't exist
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    os.makedirs(os.path.dirname(self.db_path), exist_ok=True)


    # Lock for thread safety
    # Lock for thread safety
    self.lock = threading.RLock()
    self.lock = threading.RLock()


    # Initialize database
    # Initialize database
    self._init_db()
    self._init_db()


    # Statistics
    # Statistics
    self.stats = {
    self.stats = {
    "hits": 0,
    "hits": 0,
    "misses": 0,
    "misses": 0,
    "sets": 0,
    "sets": 0,
    "deletes": 0,
    "deletes": 0,
    "evictions": 0,
    "evictions": 0,
    "clears": 0,
    "clears": 0,
    }
    }
    self._load_stats()
    self._load_stats()


    def get(self, key: str) -> Optional[Dict[str, Any]]:
    def get(self, key: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a value from the cache.
    Get a value from the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    Cached value or None if not found
    Cached value or None if not found
    """
    """
    with self.lock:
    with self.lock:
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Get the item
    # Get the item
    cursor.execute(
    cursor.execute(
    "SELECT value, expiration_time FROM cache WHERE key = ?", (key,)
    "SELECT value, expiration_time FROM cache WHERE key = ?", (key,)
    )
    )
    row = cursor.fetchone()
    row = cursor.fetchone()


    if row is None:
    if row is None:
    self.stats["misses"] += 1
    self.stats["misses"] += 1
    self._save_stats()
    self._save_stats()
    return None
    return None


    value_blob, expiration_time = row
    value_blob, expiration_time = row


    # Check if expired
    # Check if expired
    if expiration_time is not None and time.time() > expiration_time:
    if expiration_time is not None and time.time() > expiration_time:
    self.delete(key)
    self.delete(key)
    self.stats["misses"] += 1
    self.stats["misses"] += 1
    self._save_stats()
    self._save_stats()
    return None
    return None


    # Deserialize value
    # Deserialize value
    value = self._deserialize(value_blob)
    value = self._deserialize(value_blob)


    # Update access statistics
    # Update access statistics
    cursor.execute(
    cursor.execute(
    "UPDATE cache SET access_count = access_count + 1, last_access_time = ? WHERE key = ?",
    "UPDATE cache SET access_count = access_count + 1, last_access_time = ? WHERE key = ?",
    (time.time(), key),
    (time.time(), key),
    )
    )
    conn.commit()
    conn.commit()


    self.stats["hits"] += 1
    self.stats["hits"] += 1
    self._save_stats()
    self._save_stats()
    return value
    return value


except Exception:
except Exception:
    conn.rollback()
    conn.rollback()
    self.stats["misses"] += 1
    self.stats["misses"] += 1
    self._save_stats()
    self._save_stats()
    return None
    return None


finally:
finally:
    conn.close()
    conn.close()


    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
    """
    """
    Set a value in the cache.
    Set a value in the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key
    value: Value to cache
    value: Value to cache
    ttl: Time to live in seconds (None for no expiration)
    ttl: Time to live in seconds (None for no expiration)


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    with self.lock:
    with self.lock:
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Calculate expiration time
    # Calculate expiration time
    expiration_time = None
    expiration_time = None
    if ttl is not None:
    if ttl is not None:
    expiration_time = time.time() + ttl
    expiration_time = time.time() + ttl


    # Serialize value
    # Serialize value
    value_blob = self._serialize(value)
    value_blob = self._serialize(value)


    # Check if key exists
    # Check if key exists
    cursor.execute("SELECT 1 FROM cache WHERE key = ?", (key,))
    cursor.execute("SELECT 1 FROM cache WHERE key = ?", (key,))
    exists = cursor.fetchone() is not None
    exists = cursor.fetchone() is not None


    if exists:
    if exists:
    # Update existing item
    # Update existing item
    cursor.execute(
    cursor.execute(
    """
    """
    UPDATE cache SET
    UPDATE cache SET
    value = ?,
    value = ?,
    expiration_time = ?,
    expiration_time = ?,
    last_access_time = ?,
    last_access_time = ?,
    update_time = ?
    update_time = ?
    WHERE key = ?
    WHERE key = ?
    """,
    """,
    (value_blob, expiration_time, time.time(), time.time(), key),
    (value_blob, expiration_time, time.time(), time.time(), key),
    )
    )
    else:
    else:
    # Insert new item
    # Insert new item
    cursor.execute(
    cursor.execute(
    """
    """
    INSERT INTO cache (
    INSERT INTO cache (
    key, value, expiration_time, creation_time,
    key, value, expiration_time, creation_time,
    last_access_time, update_time, access_count
    last_access_time, update_time, access_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    """,
    (
    (
    key,
    key,
    value_blob,
    value_blob,
    expiration_time,
    expiration_time,
    time.time(),
    time.time(),
    time.time(),
    time.time(),
    time.time(),
    time.time(),
    0,
    0,
    ),
    ),
    )
    )


    conn.commit()
    conn.commit()


    self.stats["sets"] += 1
    self.stats["sets"] += 1
    self._save_stats()
    self._save_stats()
    return True
    return True


except Exception:
except Exception:
    conn.rollback()
    conn.rollback()
    return False
    return False


finally:
finally:
    conn.close()
    conn.close()


    def delete(self, key: str) -> bool:
    def delete(self, key: str) -> bool:
    """
    """
    Delete a value from the cache.
    Delete a value from the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    with self.lock:
    with self.lock:
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Delete the item
    # Delete the item
    cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
    cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
    conn.commit()
    conn.commit()


    self.stats["deletes"] += 1
    self.stats["deletes"] += 1
    self._save_stats()
    self._save_stats()
    return True
    return True


except Exception:
except Exception:
    conn.rollback()
    conn.rollback()
    return False
    return False


finally:
finally:
    conn.close()
    conn.close()


    def exists(self, key: str) -> bool:
    def exists(self, key: str) -> bool:
    """
    """
    Check if a key exists in the cache.
    Check if a key exists in the cache.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    True if the key exists, False otherwise
    True if the key exists, False otherwise
    """
    """
    with self.lock:
    with self.lock:
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Get the item
    # Get the item
    cursor.execute(
    cursor.execute(
    "SELECT expiration_time FROM cache WHERE key = ?", (key,)
    "SELECT expiration_time FROM cache WHERE key = ?", (key,)
    )
    )
    row = cursor.fetchone()
    row = cursor.fetchone()


    if row is None:
    if row is None:
    return False
    return False


    expiration_time = row[0]
    expiration_time = row[0]


    # Check if expired
    # Check if expired
    if expiration_time is not None and time.time() > expiration_time:
    if expiration_time is not None and time.time() > expiration_time:
    self.delete(key)
    self.delete(key)
    return False
    return False


    return True
    return True


except Exception:
except Exception:
    return False
    return False


finally:
finally:
    conn.close()
    conn.close()


    def clear(self) -> bool:
    def clear(self) -> bool:
    """
    """
    Clear all values from the cache.
    Clear all values from the cache.


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    with self.lock:
    with self.lock:
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Delete all items
    # Delete all items
    cursor.execute("DELETE FROM cache")
    cursor.execute("DELETE FROM cache")
    conn.commit()
    conn.commit()


    self.stats["clears"] += 1
    self.stats["clears"] += 1
    self._save_stats()
    self._save_stats()
    return True
    return True


except Exception:
except Exception:
    conn.rollback()
    conn.rollback()
    return False
    return False


finally:
finally:
    conn.close()
    conn.close()


    def get_size(self) -> int:
    def get_size(self) -> int:
    """
    """
    Get the size of the cache.
    Get the size of the cache.


    Returns:
    Returns:
    Number of items in the cache
    Number of items in the cache
    """
    """
    with self.lock:
    with self.lock:
    # Remove expired items
    # Remove expired items
    self._remove_expired_items()
    self._remove_expired_items()


    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Count items
    # Count items
    cursor.execute("SELECT COUNT(*) FROM cache")
    cursor.execute("SELECT COUNT(*) FROM cache")
    count = cursor.fetchone()[0]
    count = cursor.fetchone()[0]


    return count
    return count


except Exception:
except Exception:
    return 0
    return 0


finally:
finally:
    conn.close()
    conn.close()


    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
    """
    """
    Get all keys in the cache.
    Get all keys in the cache.


    Args:
    Args:
    pattern: Optional pattern to filter keys
    pattern: Optional pattern to filter keys


    Returns:
    Returns:
    List of keys
    List of keys
    """
    """
    with self.lock:
    with self.lock:
    # Remove expired items
    # Remove expired items
    self._remove_expired_items()
    self._remove_expired_items()


    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Get all keys
    # Get all keys
    cursor.execute("SELECT key FROM cache")
    cursor.execute("SELECT key FROM cache")
    keys = [row[0] for row in cursor.fetchall()]
    keys = [row[0] for row in cursor.fetchall()]


    if pattern is None:
    if pattern is None:
    return keys
    return keys


    # Filter keys by pattern
    # Filter keys by pattern
    regex = re.compile(pattern)
    regex = re.compile(pattern)
    return [key for key in keys if regex.match(key)]
    return [key for key in keys if regex.match(key)]


except Exception:
except Exception:
    return []
    return []


finally:
finally:
    conn.close()
    conn.close()


    def get_stats(self) -> Dict[str, Any]:
    def get_stats(self) -> Dict[str, Any]:
    """
    """
    Get statistics about the cache.
    Get statistics about the cache.


    Returns:
    Returns:
    Dictionary with cache statistics
    Dictionary with cache statistics
    """
    """
    with self.lock:
    with self.lock:
    stats = self.stats.copy()
    stats = self.stats.copy()
    stats["size"] = self.get_size()
    stats["size"] = self.get_size()
    stats["serialization"] = self.serialization
    stats["serialization"] = self.serialization
    stats["db_path"] = self.db_path
    stats["db_path"] = self.db_path


    # Get database size
    # Get database size
    if os.path.exists(self.db_path):
    if os.path.exists(self.db_path):
    stats["db_size"] = os.path.getsize(self.db_path)
    stats["db_size"] = os.path.getsize(self.db_path)
    else:
    else:
    stats["db_size"] = 0
    stats["db_size"] = 0


    return stats
    return stats


    def get_ttl(self, key: str) -> Optional[int]:
    def get_ttl(self, key: str) -> Optional[int]:
    """
    """
    Get the time to live for a key.
    Get the time to live for a key.


    Args:
    Args:
    key: Cache key
    key: Cache key


    Returns:
    Returns:
    Time to live in seconds or None if no expiration
    Time to live in seconds or None if no expiration
    """
    """
    with self.lock:
    with self.lock:
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Get expiration time
    # Get expiration time
    cursor.execute(
    cursor.execute(
    "SELECT expiration_time FROM cache WHERE key = ?", (key,)
    "SELECT expiration_time FROM cache WHERE key = ?", (key,)
    )
    )
    row = cursor.fetchone()
    row = cursor.fetchone()


    if row is None:
    if row is None:
    return None
    return None


    expiration_time = row[0]
    expiration_time = row[0]


    if expiration_time is None:
    if expiration_time is None:
    return None
    return None


    ttl = int(expiration_time - time.time())
    ttl = int(expiration_time - time.time())
    return ttl if ttl > 0 else 0
    return ttl if ttl > 0 else 0


except Exception:
except Exception:
    return None
    return None


finally:
finally:
    conn.close()
    conn.close()


    def set_ttl(self, key: str, ttl: int) -> bool:
    def set_ttl(self, key: str, ttl: int) -> bool:
    """
    """
    Set the time to live for a key.
    Set the time to live for a key.


    Args:
    Args:
    key: Cache key
    key: Cache key
    ttl: Time to live in seconds
    ttl: Time to live in seconds


    Returns:
    Returns:
    True if successful, False otherwise
    True if successful, False otherwise
    """
    """
    with self.lock:
    with self.lock:
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Calculate expiration time
    # Calculate expiration time
    expiration_time = time.time() + ttl
    expiration_time = time.time() + ttl


    # Update expiration time
    # Update expiration time
    cursor.execute(
    cursor.execute(
    "UPDATE cache SET expiration_time = ? WHERE key = ?",
    "UPDATE cache SET expiration_time = ? WHERE key = ?",
    (expiration_time, key),
    (expiration_time, key),
    )
    )
    conn.commit()
    conn.commit()


    return cursor.rowcount > 0
    return cursor.rowcount > 0


except Exception:
except Exception:
    conn.rollback()
    conn.rollback()
    return False
    return False


finally:
finally:
    conn.close()
    conn.close()


    def _init_db(self) -> None:
    def _init_db(self) -> None:
    """
    """
    Initialize the database.
    Initialize the database.
    """
    """
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Create cache table
    # Create cache table
    cursor.execute(
    cursor.execute(
    """
    """
    CREATE TABLE IF NOT EXISTS cache (
    CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    key TEXT PRIMARY KEY,
    value BLOB NOT NULL,
    value BLOB NOT NULL,
    expiration_time REAL,
    expiration_time REAL,
    creation_time REAL NOT NULL,
    creation_time REAL NOT NULL,
    last_access_time REAL NOT NULL,
    last_access_time REAL NOT NULL,
    update_time REAL NOT NULL,
    update_time REAL NOT NULL,
    access_count INTEGER NOT NULL
    access_count INTEGER NOT NULL
    )
    )
    """
    """
    )
    )


    # Create stats table
    # Create stats table
    cursor.execute(
    cursor.execute(
    """
    """
    CREATE TABLE IF NOT EXISTS stats (
    CREATE TABLE IF NOT EXISTS stats (
    name TEXT PRIMARY KEY,
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL
    value INTEGER NOT NULL
    )
    )
    """
    """
    )
    )


    conn.commit()
    conn.commit()


except Exception:
except Exception:
    conn.rollback()
    conn.rollback()
    raise
    raise


finally:
finally:
    conn.close()
    conn.close()


    def _get_connection(self) -> sqlite3.Connection:
    def _get_connection(self) -> sqlite3.Connection:
    """
    """
    Get a database connection.
    Get a database connection.


    Returns:
    Returns:
    SQLite connection
    SQLite connection
    """
    """
    conn = sqlite3.connect(self.db_path)
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    conn.row_factory = sqlite3.Row
    return conn
    return conn


    def _serialize(self, value: Dict[str, Any]) -> bytes:
    def _serialize(self, value: Dict[str, Any]) -> bytes:
    """
    """
    Serialize a value.
    Serialize a value.


    Args:
    Args:
    value: Value to serialize
    value: Value to serialize


    Returns:
    Returns:
    Serialized value
    Serialized value
    """
    """
    if self.serialization == "json":
    if self.serialization == "json":
    return json.dumps(value).encode("utf-8")
    return json.dumps(value).encode("utf-8")
    elif self.serialization == "pickle":
    elif self.serialization == "pickle":
    return pickle.dumps(value)
    return pickle.dumps(value)
    else:
    else:
    # Default to JSON
    # Default to JSON
    return json.dumps(value).encode("utf-8")
    return json.dumps(value).encode("utf-8")


    def _deserialize(self, value_blob: bytes) -> Dict[str, Any]:
    def _deserialize(self, value_blob: bytes) -> Dict[str, Any]:
    """
    """
    Deserialize a value.
    Deserialize a value.


    Args:
    Args:
    value_blob: Serialized value
    value_blob: Serialized value


    Returns:
    Returns:
    Deserialized value
    Deserialized value
    """
    """
    if self.serialization == "json":
    if self.serialization == "json":
    return json.loads(value_blob.decode("utf-8"))
    return json.loads(value_blob.decode("utf-8"))
    elif self.serialization == "pickle":
    elif self.serialization == "pickle":
    return pickle.loads(value_blob)
    return pickle.loads(value_blob)
    else:
    else:
    # Default to JSON
    # Default to JSON
    return json.loads(value_blob.decode("utf-8"))
    return json.loads(value_blob.decode("utf-8"))


    def _load_stats(self) -> None:
    def _load_stats(self) -> None:
    """
    """
    Load statistics from the database.
    Load statistics from the database.
    """
    """
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Get all stats
    # Get all stats
    cursor.execute("SELECT name, value FROM stats")
    cursor.execute("SELECT name, value FROM stats")
    rows = cursor.fetchall()
    rows = cursor.fetchall()


    for row in rows:
    for row in rows:
    self.stats[row["name"]] = row["value"]
    self.stats[row["name"]] = row["value"]


except Exception:
except Exception:
    pass
    pass


finally:
finally:
    conn.close()
    conn.close()


    def _save_stats(self) -> None:
    def _save_stats(self) -> None:
    """
    """
    Save statistics to the database.
    Save statistics to the database.
    """
    """
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Save all stats
    # Save all stats
    for name, value in self.stats.items():
    for name, value in self.stats.items():
    cursor.execute(
    cursor.execute(
    "INSERT OR REPLACE INTO stats (name, value) VALUES (?, ?)",
    "INSERT OR REPLACE INTO stats (name, value) VALUES (?, ?)",
    (name, value),
    (name, value),
    )
    )


    conn.commit()
    conn.commit()


except Exception:
except Exception:
    conn.rollback()
    conn.rollback()


finally:
finally:
    conn.close()
    conn.close()


    def _remove_expired_items(self) -> None:
    def _remove_expired_items(self) -> None:
    """
    """
    Remove expired items from the cache.
    Remove expired items from the cache.
    """
    """
    conn = self._get_connection()
    conn = self._get_connection()
    try:
    try:
    cursor = conn.cursor()
    cursor = conn.cursor()


    # Delete expired items
    # Delete expired items
    cursor.execute(
    cursor.execute(
    "DELETE FROM cache WHERE expiration_time IS NOT NULL AND expiration_time < ?",
    "DELETE FROM cache WHERE expiration_time IS NOT NULL AND expiration_time < ?",
    (time.time(),),
    (time.time(),),
    )
    )


    conn.commit()
    conn.commit()


except Exception:
except Exception:
    conn.rollback()
    conn.rollback()


finally:
finally:
    conn.close()
    conn.close()