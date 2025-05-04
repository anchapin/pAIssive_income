"""
"""
MongoDB adapter implementation of the database interface.
MongoDB adapter implementation of the database interface.


This module provides a concrete implementation of DatabaseInterface for MongoDB databases.
This module provides a concrete implementation of DatabaseInterface for MongoDB databases.
"""
"""




import json
import json
import logging
import logging
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


import pymongo
import pymongo
from pymongo import MongoClient
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.database import Database
from pymongo.errors import PyMongoError
from pymongo.errors import PyMongoError


MONGODB_AVAILABLE
MONGODB_AVAILABLE


from common_utils.db.interfaces import DatabaseInterface, UnitOfWork
from common_utils.db.interfaces import DatabaseInterface, UnitOfWork


logger
logger


# Use conditional import to avoid forcing pymongo as a dependency
# Use conditional import to avoid forcing pymongo as a dependency
try:
    try:


    = True
    = True
except ImportError:
except ImportError:
    MONGODB_AVAILABLE = False
    MONGODB_AVAILABLE = False
    = logging.getLogger(__name__)
    = logging.getLogger(__name__)




    class MongoDBAdapter(DatabaseInterface):
    class MongoDBAdapter(DatabaseInterface):
    """Implementation of DatabaseInterface for MongoDB."""

    def __init__(self, connection_string: str, db_name: str):
    """
    """
    Initialize the MongoDB adapter.
    Initialize the MongoDB adapter.


    Args:
    Args:
    connection_string: MongoDB connection string
    connection_string: MongoDB connection string
    db_name: Database name
    db_name: Database name


    Raises:
    Raises:
    ImportError: If pymongo is not installed
    ImportError: If pymongo is not installed
    """
    """
    if not MONGODB_AVAILABLE:
    if not MONGODB_AVAILABLE:
    raise ImportError(
    raise ImportError(
    "pymongo is not installed. Please install it using 'pip install pymongo'"
    "pymongo is not installed. Please install it using 'pip install pymongo'"
    )
    )


    self.connection_string = connection_string
    self.connection_string = connection_string
    self.db_name = db_name
    self.db_name = db_name
    self.client = None
    self.client = None
    self.db = None
    self.db = None


    def connect(self) -> None:
    def connect(self) -> None:
    """
    """
    Establish a connection to MongoDB.
    Establish a connection to MongoDB.


    Raises:
    Raises:
    PyMongoError: If there's an issue with the database connection
    PyMongoError: If there's an issue with the database connection
    """
    """
    try:
    try:
    self.client = MongoClient(self.connection_string)
    self.client = MongoClient(self.connection_string)
    self.db = self.client[self.db_name]
    self.db = self.client[self.db_name]
    # Test the connection
    # Test the connection
    self.client.server_info()
    self.client.server_info()
    logger.info(f"Connected to MongoDB database: {self.db_name}")
    logger.info(f"Connected to MongoDB database: {self.db_name}")
except PyMongoError as e:
except PyMongoError as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    logger.error(f"Error connecting to MongoDB: {e}")
    raise
    raise


    def disconnect(self) -> None:
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
    """
    Execute a command in MongoDB.
    Execute a command in MongoDB.


    Args:
    Args:
    query: JSON command string or collection name with operation
    query: JSON command string or collection name with operation
    params: Command parameters
    params: Command parameters


    Returns:
    Returns:
    Command result
    Command result


    Raises:
    Raises:
    PyMongoError: If there's an issue with the database operation
    PyMongoError: If there's an issue with the database operation
    ValueError: If the query format is invalid
    ValueError: If the query format is invalid
    """
    """
    try:
    try:
    self._ensure_connection()
    self._ensure_connection()


    # Parse the query to determine if it's a command or a collection operation
    # Parse the query to determine if it's a command or a collection operation
    if query.startswith("{") and query.endswith("}"):
    if query.startswith("{") and query.endswith("}"):
    # It's a raw command in JSON format
    # It's a raw command in JSON format
    try:
    try:
    command = json.loads(query)
    command = json.loads(query)
except json.JSONDecodeError as e:
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON command: {e}")
    raise ValueError(f"Invalid JSON command: {e}")
    return self.db.command(command)
    return self.db.command(command)
    else:
    else:
    # It's a simplified format like "collection_name:operation"
    # It's a simplified format like "collection_name:operation"
    parts = query.split(":", 1)
    parts = query.split(":", 1)
    if len(parts) != 2 or not all(parts):
    if len(parts) != 2 or not all(parts):
    raise ValueError(
    raise ValueError(
    "Query format should be 'collection:operation' with non-empty parts"
    "Query format should be 'collection:operation' with non-empty parts"
    )
    )


    collection_name, operation = parts
    collection_name, operation = parts
    collection = self.db[collection_name]
    collection = self.db[collection_name]


    if operation == "find":
    if operation == "find":
    filter_dict = params or {}
    filter_dict = params or {}
    return list(collection.find(filter_dict))
    return list(collection.find(filter_dict))
    elif operation == "findOne":
    elif operation == "findOne":
    filter_dict = params or {}
    filter_dict = params or {}
    return collection.find_one(filter_dict)
    return collection.find_one(filter_dict)
    elif operation == "insert":
    elif operation == "insert":
    if params:
    if params:
    return collection.insert_one(params)
    return collection.insert_one(params)
    raise ValueError("Parameters required for insert operation")
    raise ValueError("Parameters required for insert operation")
    elif operation == "update":
    elif operation == "update":
    if params and "filter" in params and "update" in params:
    if params and "filter" in params and "update" in params:
    return collection.update_many(
    return collection.update_many(
    params["filter"], {"$set": params["update"]}
    params["filter"], {"$set": params["update"]}
    )
    )
    raise ValueError(
    raise ValueError(
    "'filter' and 'update' required in params for update operation"
    "'filter' and 'update' required in params for update operation"
    )
    )
    elif operation == "delete":
    elif operation == "delete":
    if params:
    if params:
    return collection.delete_many(params)
    return collection.delete_many(params)
    raise ValueError("Parameters required for delete operation")
    raise ValueError("Parameters required for delete operation")
    else:
    else:
    raise ValueError(f"Unsupported operation: {operation}")
    raise ValueError(f"Unsupported operation: {operation}")
except PyMongoError as e:
except PyMongoError as e:
    logger.error(f"Error executing MongoDB operation: {e}")
    logger.error(f"Error executing MongoDB operation: {e}")
    raise
    raise
except Exception as e:
except Exception as e:
    logger.error(f"Error in MongoDB execution: {e}")
    logger.error(f"Error in MongoDB execution: {e}")
    raise
    raise


    def fetch_one(
    def fetch_one(
    self, query: str, params: Optional[Dict[str, Any]] = None
    self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
    ) -> Optional[Dict[str, Any]]:
    """
    """
    Fetch a single document from MongoDB.
    Fetch a single document from MongoDB.


    Args:
    Args:
    query: Collection name with operation (e.g., "collection:findOne")
    query: Collection name with operation (e.g., "collection:findOne")
    params: Filter conditions
    params: Filter conditions


    Returns:
    Returns:
    A single document as a dictionary or None if no documents found
    A single document as a dictionary or None if no documents found


    Raises:
    Raises:
    PyMongoError: If there's an issue with the database operation
    PyMongoError: If there's an issue with the database operation
    """
    """
    try:
    try:
    self._ensure_connection()
    self._ensure_connection()


    parts = query.split(":", 1)
    parts = query.split(":", 1)
    if len(parts) != 2:
    if len(parts) != 2:
    collection_name = query
    collection_name = query
    operation = "findOne"
    operation = "findOne"
    else:
    else:
    collection_name, operation = parts
    collection_name, operation = parts


    collection = self.db[collection_name]
    collection = self.db[collection_name]
    filter_dict = params or {}
    filter_dict = params or {}


    result = collection.find_one(filter_dict)
    result = collection.find_one(filter_dict)
    # Convert ObjectId to string for JSON serialization
    # Convert ObjectId to string for JSON serialization
    if result and "_id" in result:
    if result and "_id" in result:
    result["_id"] = str(result["_id"])
    result["_id"] = str(result["_id"])


    return result
    return result
except PyMongoError as e:
except PyMongoError as e:
    logger.error(f"Error fetching document from MongoDB: {e}")
    logger.error(f"Error fetching document from MongoDB: {e}")
    raise
    raise


    def fetch_all(
    def fetch_all(
    self, query: str, params: Optional[Dict[str, Any]] = None
    self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
    ) -> List[Dict[str, Any]]:
    """
    """
    Fetch multiple documents from MongoDB.
    Fetch multiple documents from MongoDB.


    Args:
    Args:
    query: Collection name with operation (e.g., "collection:find")
    query: Collection name with operation (e.g., "collection:find")
    params: Filter conditions
    params: Filter conditions


    Returns:
    Returns:
    A list of documents as dictionaries
    A list of documents as dictionaries


    Raises:
    Raises:
    PyMongoError: If there's an issue with the database operation
    PyMongoError: If there's an issue with the database operation
    """
    """
    try:
    try:
    self._ensure_connection()
    self._ensure_connection()


    parts = query.split(":", 1)
    parts = query.split(":", 1)
    if len(parts) != 2:
    if len(parts) != 2:
    collection_name = query
    collection_name = query
    operation = "find"
    operation = "find"
    else:
    else:
    collection_name, operation = parts
    collection_name, operation = parts


    collection = self.db[collection_name]
    collection = self.db[collection_name]
    filter_dict = params or {}
    filter_dict = params or {}


    cursor = collection.find(filter_dict)
    cursor = collection.find(filter_dict)
    results = list(cursor)
    results = list(cursor)


    # Convert ObjectId to string for JSON serialization
    # Convert ObjectId to string for JSON serialization
    for result in results:
    for result in results:
    if "_id" in result:
    if "_id" in result:
    result["_id"] = str(result["_id"])
    result["_id"] = str(result["_id"])


    return results
    return results
except PyMongoError as e:
except PyMongoError as e:
    logger.error(f"Error fetching documents from MongoDB: {e}")
    logger.error(f"Error fetching documents from MongoDB: {e}")
    raise
    raise


    def insert(self, table: str, data: Dict[str, Any]) -> Any:
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
    """
    """
    Insert a document into MongoDB.
    Insert a document into MongoDB.


    Args:
    Args:
    table: Collection name
    table: Collection name
    data: Document to insert
    data: Document to insert


    Returns:
    Returns:
    The ID of the inserted document
    The ID of the inserted document


    Raises:
    Raises:
    PyMongoError: If there's an issue with the database operation
    PyMongoError: If there's an issue with the database operation
    """
    """
    try:
    try:
    self._ensure_connection()
    self._ensure_connection()


    collection = self.db[table]
    collection = self.db[table]
    result = collection.insert_one(data)
    result = collection.insert_one(data)
    return str(result.inserted_id)
    return str(result.inserted_id)
except PyMongoError as e:
except PyMongoError as e:
    logger.error(f"Error inserting document into MongoDB: {e}")
    logger.error(f"Error inserting document into MongoDB: {e}")
    raise
    raise


    def update(
    def update(
    self,
    self,
    table: str,
    table: str,
    data: Dict[str, Any],
    data: Dict[str, Any],
    condition: str,
    condition: str,
    params: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    ) -> int:
    ) -> int:
    """
    """
    Update documents in MongoDB.
    Update documents in MongoDB.


    Args:
    Args:
    table: Collection name
    table: Collection name
    data: Document data to update
    data: Document data to update
    condition: Not used (MongoDB uses params for conditions)
    condition: Not used (MongoDB uses params for conditions)
    params: Filter conditions
    params: Filter conditions


    Returns:
    Returns:
    Number of documents modified
    Number of documents modified


    Raises:
    Raises:
    PyMongoError: If there's an issue with the database operation
    PyMongoError: If there's an issue with the database operation
    """
    """
    try:
    try:
    self._ensure_connection()
    self._ensure_connection()


    collection = self.db[table]
    collection = self.db[table]
    filter_dict = params or {}
    filter_dict = params or {}


    result = collection.update_many(filter_dict, {"$set": data})
    result = collection.update_many(filter_dict, {"$set": data})
    return result.modified_count
    return result.modified_count
except PyMongoError as e:
except PyMongoError as e:
    logger.error(f"Error updating documents in MongoDB: {e}")
    logger.error(f"Error updating documents in MongoDB: {e}")
    raise
    raise


    def delete(
    def delete(
    self, table: str, condition: str, params: Optional[Dict[str, Any]] = None
    self, table: str, condition: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
    ) -> int:
    """
    """
    Delete documents from MongoDB.
    Delete documents from MongoDB.


    Args:
    Args:
    table: Collection name
    table: Collection name
    condition: Not used (MongoDB uses params for conditions)
    condition: Not used (MongoDB uses params for conditions)
    params: Filter conditions
    params: Filter conditions


    Returns:
    Returns:
    Number of documents deleted
    Number of documents deleted


    Raises:
    Raises:
    PyMongoError: If there's an issue with the database operation
    PyMongoError: If there's an issue with the database operation
    """
    """
    try:
    try:
    self._ensure_connection()
    self._ensure_connection()


    collection = self.db[table]
    collection = self.db[table]
    filter_dict = params or {}
    filter_dict = params or {}


    result = collection.delete_many(filter_dict)
    result = collection.delete_many(filter_dict)
    return result.deleted_count
    return result.deleted_count
except PyMongoError as e:
except PyMongoError as e:
    logger.error(f"Error deleting documents from MongoDB: {e}")
    logger.error(f"Error deleting documents from MongoDB: {e}")
    raise
    raise




    class MongoDBUnitOfWork(UnitOfWork):
    class MongoDBUnitOfWork(UnitOfWork):
    """MongoDB implementation of the Unit of Work pattern."""

    def __init__(self, adapter: MongoDBAdapter):
    """
    """
    Initialize the MongoDB unit of work.
    Initialize the MongoDB unit of work.


    Args:
    Args:
    adapter: MongoDB adapter instance
    adapter: MongoDB adapter instance
    """
    """
    self.adapter = adapter
    self.adapter = adapter
    self.session = None
    self.session = None


    def __enter__(self):
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