"""
SQLite cache backend for the model cache system.

This module provides a SQLite-based cache backend.
"""

import json
import os
import pickle
import re
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

from .base import CacheBackend


class SQLiteCache(CacheBackend):
    """
    SQLite-based cache backend.
    """

    def __init__(self, db_path: str, serialization: str = "json", **kwargs):
        """
        Initialize the SQLite cache.

        Args:
            db_path: Path to the SQLite database file
            serialization: Serialization format (json, pickle)
            **kwargs: Additional parameters for the cache
        """
        self.db_path = os.path.abspath(db_path)
        self.serialization = serialization.lower()

        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Lock for thread safety
        self.lock = threading.RLock()

        # Initialize database
        self._init_db()

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
            "clears": 0,
        }
        self._load_stats()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Get the item
                cursor.execute("SELECT value, expiration_time FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()

                if row is None:
                    self.stats["misses"] += 1
                    self._save_stats()
                    return None

                value_blob, expiration_time = row

                # Check if expired
                if expiration_time is not None and time.time() > expiration_time:
                    self.delete(key)
                    self.stats["misses"] += 1
                    self._save_stats()
                    return None

                # Deserialize value
                value = self._deserialize(value_blob)

                # Update access statistics
                cursor.execute(
                    "UPDATE cache SET access_count = access_count + 1, last_access_time = ? WHERE key = ?",
                    (time.time(), key),
                )
                conn.commit()

                self.stats["hits"] += 1
                self._save_stats()
                return value

            except Exception as e:
                conn.rollback()
                self.stats["misses"] += 1
                self._save_stats()
                return None

            finally:
                conn.close()

    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Calculate expiration time
                expiration_time = None
                if ttl is not None:
                    expiration_time = time.time() + ttl

                # Serialize value
                value_blob = self._serialize(value)

                # Check if key exists
                cursor.execute("SELECT 1 FROM cache WHERE key = ?", (key,))
                exists = cursor.fetchone() is not None

                if exists:
                    # Update existing item
                    cursor.execute(
                        """
                        UPDATE cache SET
                            value = ?,
                            expiration_time = ?,
                            last_access_time = ?,
                            update_time = ?
                        WHERE key = ?
                        """,
                        (value_blob, expiration_time, time.time(), time.time(), key),
                    )
                else:
                    # Insert new item
                    cursor.execute(
                        """
                        INSERT INTO cache (
                            key, value, expiration_time, creation_time,
                            last_access_time, update_time, access_count
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            key,
                            value_blob,
                            expiration_time,
                            time.time(),
                            time.time(),
                            time.time(),
                            0,
                        ),
                    )

                conn.commit()

                self.stats["sets"] += 1
                self._save_stats()
                return True

            except Exception as e:
                conn.rollback()
                return False

            finally:
                conn.close()

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Delete the item
                cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()

                self.stats["deletes"] += 1
                self._save_stats()
                return True

            except Exception as e:
                conn.rollback()
                return False

            finally:
                conn.close()

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: Cache key

        Returns:
            True if the key exists, False otherwise
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Get the item
                cursor.execute("SELECT expiration_time FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()

                if row is None:
                    return False

                expiration_time = row[0]

                # Check if expired
                if expiration_time is not None and time.time() > expiration_time:
                    self.delete(key)
                    return False

                return True

            except Exception as e:
                return False

            finally:
                conn.close()

    def clear(self) -> bool:
        """
        Clear all values from the cache.

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Delete all items
                cursor.execute("DELETE FROM cache")
                conn.commit()

                self.stats["clears"] += 1
                self._save_stats()
                return True

            except Exception as e:
                conn.rollback()
                return False

            finally:
                conn.close()

    def get_size(self) -> int:
        """
        Get the size of the cache.

        Returns:
            Number of items in the cache
        """
        with self.lock:
            # Remove expired items
            self._remove_expired_items()

            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Count items
                cursor.execute("SELECT COUNT(*) FROM cache")
                count = cursor.fetchone()[0]

                return count

            except Exception as e:
                return 0

            finally:
                conn.close()

    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all keys in the cache.

        Args:
            pattern: Optional pattern to filter keys

        Returns:
            List of keys
        """
        with self.lock:
            # Remove expired items
            self._remove_expired_items()

            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Get all keys
                cursor.execute("SELECT key FROM cache")
                keys = [row[0] for row in cursor.fetchall()]

                if pattern is None:
                    return keys

                # Filter keys by pattern
                regex = re.compile(pattern)
                return [key for key in keys if regex.match(key)]

            except Exception as e:
                return []

            finally:
                conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            stats = self.stats.copy()
            stats["size"] = self.get_size()
            stats["serialization"] = self.serialization
            stats["db_path"] = self.db_path

            # Get database size
            if os.path.exists(self.db_path):
                stats["db_size"] = os.path.getsize(self.db_path)
            else:
                stats["db_size"] = 0

            return stats

    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get the time to live for a key.

        Args:
            key: Cache key

        Returns:
            Time to live in seconds or None if no expiration
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Get expiration time
                cursor.execute("SELECT expiration_time FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()

                if row is None:
                    return None

                expiration_time = row[0]

                if expiration_time is None:
                    return None

                ttl = int(expiration_time - time.time())
                return ttl if ttl > 0 else 0

            except Exception as e:
                return None

            finally:
                conn.close()

    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Set the time to live for a key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Calculate expiration time
                expiration_time = time.time() + ttl

                # Update expiration time
                cursor.execute(
                    "UPDATE cache SET expiration_time = ? WHERE key = ?",
                    (expiration_time, key),
                )
                conn.commit()

                return cursor.rowcount > 0

            except Exception as e:
                conn.rollback()
                return False

            finally:
                conn.close()

    def _init_db(self) -> None:
        """
        Initialize the database.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Create cache table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL,
                    expiration_time REAL,
                    creation_time REAL NOT NULL,
                    last_access_time REAL NOT NULL,
                    update_time REAL NOT NULL,
                    access_count INTEGER NOT NULL
                )
            """
            )

            # Create stats table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stats (
                    name TEXT PRIMARY KEY,
                    value INTEGER NOT NULL
                )
            """
            )

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise

        finally:
            conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.

        Returns:
            SQLite connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _serialize(self, value: Dict[str, Any]) -> bytes:
        """
        Serialize a value.

        Args:
            value: Value to serialize

        Returns:
            Serialized value
        """
        if self.serialization == "json":
            return json.dumps(value).encode("utf-8")
        elif self.serialization == "pickle":
            return pickle.dumps(value)
        else:
            # Default to JSON
            return json.dumps(value).encode("utf-8")

    def _deserialize(self, value_blob: bytes) -> Dict[str, Any]:
        """
        Deserialize a value.

        Args:
            value_blob: Serialized value

        Returns:
            Deserialized value
        """
        if self.serialization == "json":
            return json.loads(value_blob.decode("utf-8"))
        elif self.serialization == "pickle":
            return pickle.loads(value_blob)
        else:
            # Default to JSON
            return json.loads(value_blob.decode("utf-8"))

    def _load_stats(self) -> None:
        """
        Load statistics from the database.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Get all stats
            cursor.execute("SELECT name, value FROM stats")
            rows = cursor.fetchall()

            for row in rows:
                self.stats[row["name"]] = row["value"]

        except Exception:
            pass

        finally:
            conn.close()

    def _save_stats(self) -> None:
        """
        Save statistics to the database.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Save all stats
            for name, value in self.stats.items():
                cursor.execute(
                    "INSERT OR REPLACE INTO stats (name, value) VALUES (?, ?)",
                    (name, value),
                )

            conn.commit()

        except Exception:
            conn.rollback()

        finally:
            conn.close()

    def _remove_expired_items(self) -> None:
        """
        Remove expired items from the cache.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Delete expired items
            cursor.execute(
                "DELETE FROM cache WHERE expiration_time IS NOT NULL AND expiration_time < ?",
                (time.time(),),
            )

            conn.commit()

        except Exception:
            conn.rollback()

        finally:
            conn.close()
