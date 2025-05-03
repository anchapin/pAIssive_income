"""
MongoDB adapter implementation of the database interface.

This module provides a concrete implementation of DatabaseInterface for MongoDB databases.
"""


import json
import logging
from typing import Any, Dict, List, Optional


    import pymongo
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
    from pymongo.errors import PyMongoError

    MONGODB_AVAILABLE 

from common_utils.db.interfaces import DatabaseInterface, UnitOfWork

logger 

# Use conditional import to avoid forcing pymongo as a dependency
try:

= True
except ImportError:
    MONGODB_AVAILABLE = False
= logging.getLogger(__name__)


class MongoDBAdapter(DatabaseInterface):
    """Implementation of DatabaseInterface for MongoDB."""

    def __init__(self, connection_string: str, db_name: str):
        """
        Initialize the MongoDB adapter.

        Args:
            connection_string: MongoDB connection string
            db_name: Database name

        Raises:
            ImportError: If pymongo is not installed
        """
        if not MONGODB_AVAILABLE:
            raise ImportError(
                "pymongo is not installed. Please install it using 'pip install pymongo'"
            )

        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self) -> None:
        """
        Establish a connection to MongoDB.

        Raises:
            PyMongoError: If there's an issue with the database connection
        """
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            # Test the connection
            self.client.server_info()
            logger.info(f"Connected to MongoDB database: {self.db_name}")
        except PyMongoError as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise

    def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Disconnected from MongoDB")

    def _ensure_connection(self) -> None:
        """Ensure database connection is established."""
        if not self.db:
            self.connect()

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a command in MongoDB.

        Args:
            query: JSON command string or collection name with operation
            params: Command parameters

        Returns:
            Command result

        Raises:
            PyMongoError: If there's an issue with the database operation
            ValueError: If the query format is invalid
        """
        try:
            self._ensure_connection()

            # Parse the query to determine if it's a command or a collection operation
            if query.startswith("{") and query.endswith("}"):
                # It's a raw command in JSON format
                try:
                    command = json.loads(query)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON command: {e}")
                return self.db.command(command)
            else:
                # It's a simplified format like "collection_name:operation"
                parts = query.split(":", 1)
                if len(parts) != 2 or not all(parts):
                    raise ValueError(
                        "Query format should be 'collection:operation' with non-empty parts"
                    )

                collection_name, operation = parts
                collection = self.db[collection_name]

                if operation == "find":
                    filter_dict = params or {}
                    return list(collection.find(filter_dict))
                elif operation == "findOne":
                    filter_dict = params or {}
                    return collection.find_one(filter_dict)
                elif operation == "insert":
                    if params:
                        return collection.insert_one(params)
                    raise ValueError("Parameters required for insert operation")
                elif operation == "update":
                    if params and "filter" in params and "update" in params:
                        return collection.update_many(
                            params["filter"], {"$set": params["update"]}
                        )
                    raise ValueError(
                        "'filter' and 'update' required in params for update operation"
                    )
                elif operation == "delete":
                    if params:
                        return collection.delete_many(params)
                    raise ValueError("Parameters required for delete operation")
                else:
                    raise ValueError(f"Unsupported operation: {operation}")
        except PyMongoError as e:
            logger.error(f"Error executing MongoDB operation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in MongoDB execution: {e}")
            raise

    def fetch_one(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single document from MongoDB.

        Args:
            query: Collection name with operation (e.g., "collection:findOne")
            params: Filter conditions

        Returns:
            A single document as a dictionary or None if no documents found

        Raises:
            PyMongoError: If there's an issue with the database operation
        """
        try:
            self._ensure_connection()

            parts = query.split(":", 1)
            if len(parts) != 2:
                collection_name = query
                operation = "findOne"
            else:
                collection_name, operation = parts

            collection = self.db[collection_name]
            filter_dict = params or {}

            result = collection.find_one(filter_dict)
            # Convert ObjectId to string for JSON serialization
            if result and "_id" in result:
                result["_id"] = str(result["_id"])

            return result
        except PyMongoError as e:
            logger.error(f"Error fetching document from MongoDB: {e}")
            raise

    def fetch_all(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple documents from MongoDB.

        Args:
            query: Collection name with operation (e.g., "collection:find")
            params: Filter conditions

        Returns:
            A list of documents as dictionaries

        Raises:
            PyMongoError: If there's an issue with the database operation
        """
        try:
            self._ensure_connection()

            parts = query.split(":", 1)
            if len(parts) != 2:
                collection_name = query
                operation = "find"
            else:
                collection_name, operation = parts

            collection = self.db[collection_name]
            filter_dict = params or {}

            cursor = collection.find(filter_dict)
            results = list(cursor)

            # Convert ObjectId to string for JSON serialization
            for result in results:
                if "_id" in result:
                    result["_id"] = str(result["_id"])

            return results
        except PyMongoError as e:
            logger.error(f"Error fetching documents from MongoDB: {e}")
            raise

    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """
        Insert a document into MongoDB.

        Args:
            table: Collection name
            data: Document to insert

        Returns:
            The ID of the inserted document

        Raises:
            PyMongoError: If there's an issue with the database operation
        """
        try:
            self._ensure_connection()

            collection = self.db[table]
            result = collection.insert_one(data)
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error inserting document into MongoDB: {e}")
            raise

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        condition: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Update documents in MongoDB.

        Args:
            table: Collection name
            data: Document data to update
            condition: Not used (MongoDB uses params for conditions)
            params: Filter conditions

        Returns:
            Number of documents modified

        Raises:
            PyMongoError: If there's an issue with the database operation
        """
        try:
            self._ensure_connection()

            collection = self.db[table]
            filter_dict = params or {}

            result = collection.update_many(filter_dict, {"$set": data})
            return result.modified_count
        except PyMongoError as e:
            logger.error(f"Error updating documents in MongoDB: {e}")
            raise

    def delete(
        self, table: str, condition: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Delete documents from MongoDB.

        Args:
            table: Collection name
            condition: Not used (MongoDB uses params for conditions)
            params: Filter conditions

        Returns:
            Number of documents deleted

        Raises:
            PyMongoError: If there's an issue with the database operation
        """
        try:
            self._ensure_connection()

            collection = self.db[table]
            filter_dict = params or {}

            result = collection.delete_many(filter_dict)
            return result.deleted_count
        except PyMongoError as e:
            logger.error(f"Error deleting documents from MongoDB: {e}")
            raise


class MongoDBUnitOfWork(UnitOfWork):
    """MongoDB implementation of the Unit of Work pattern."""

    def __init__(self, adapter: MongoDBAdapter):
        """
        Initialize the MongoDB unit of work.

        Args:
            adapter: MongoDB adapter instance
        """
        self.adapter = adapter
        self.session = None

    def __enter__(self):
        """Start a transaction."""
        self.adapter._ensure_connection()
        if self.adapter.client:
            self.session = self.adapter.client.start_session()
            self.session.start_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End a transaction."""
        if self.session:
            if exc_type is not None:  # An exception occurred
                self.rollback()
            else:
                self.commit()
            self.session.end_session()
            self.session = None

    def commit(self):
        """Commit the transaction."""
        if self.session:
            self.session.commit_transaction()
            logger.debug("MongoDB transaction committed")

    def rollback(self):
        """Rollback the transaction."""
        if self.session:
            self.session.abort_transaction()
            logger.debug("MongoDB transaction rolled back")