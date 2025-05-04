"""
"""
Comments and feedback system for the collaboration module.
Comments and feedback system for the collaboration module.


This module provides classes for adding comments and reactions to projects,
This module provides classes for adding comments and reactions to projects,
resources, and other items, enabling team members to provide feedback and
resources, and other items, enabling team members to provide feedback and
collaborate effectively.
collaborate effectively.
"""
"""


import json
import json
import logging
import logging
import os
import os
import time
import time
import uuid
import uuid
from datetime import datetime
from datetime import datetime
from enum import Enum
from enum import Enum
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




class ReactionType(Enum):
    class ReactionType(Enum):
    """Types of reactions that can be added to comments."""

    LIKE = "like"
    DISLIKE = "dislike"
    LAUGH = "laugh"
    CONFUSED = "confused"
    HEART = "heart"
    ROCKET = "rocket"
    EYES = "eyes"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"


    class Comment:
    """
    """
    Represents a comment on a project, resource, or other item.
    Represents a comment on a project, resource, or other item.


    This class stores the content of a comment, who created it, and when,
    This class stores the content of a comment, who created it, and when,
    as well as any reactions to the comment.
    as well as any reactions to the comment.
    """
    """


    def __init__(
    def __init__(
    self,
    self,
    comment_id: Optional[str] = None,
    comment_id: Optional[str] = None,
    content: Optional[str] = None,
    content: Optional[str] = None,
    user_id: Optional[str] = None,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    ):
    ):
    """
    """
    Initialize a comment.
    Initialize a comment.


    Args:
    Args:
    comment_id: Optional ID for the comment (generated if not provided)
    comment_id: Optional ID for the comment (generated if not provided)
    content: Content of the comment
    content: Content of the comment
    user_id: ID of the user who created the comment
    user_id: ID of the user who created the comment
    resource_type: Type of resource the comment is on (e.g., "project", "file")
    resource_type: Type of resource the comment is on (e.g., "project", "file")
    resource_id: ID of the resource the comment is on
    resource_id: ID of the resource the comment is on
    parent_id: Optional ID of the parent comment (for replies)
    parent_id: Optional ID of the parent comment (for replies)
    """
    """
    self.comment_id = comment_id or str(uuid.uuid4())
    self.comment_id = comment_id or str(uuid.uuid4())
    self.content = content
    self.content = content
    self.user_id = user_id
    self.user_id = user_id
    self.resource_type = resource_type
    self.resource_type = resource_type
    self.resource_id = resource_id
    self.resource_id = resource_id
    self.parent_id = parent_id
    self.parent_id = parent_id
    self.created_at = datetime.now().isoformat()
    self.created_at = datetime.now().isoformat()
    self.updated_at = self.created_at
    self.updated_at = self.created_at
    self.reactions: Dict[str, Dict[str, Any]] = {}
    self.reactions: Dict[str, Dict[str, Any]] = {}
    self.metadata: Dict[str, Any] = {}
    self.metadata: Dict[str, Any] = {}
    self.edited = False
    self.edited = False


    def update_content(self, content: str):
    def update_content(self, content: str):
    """
    """
    Update the content of the comment.
    Update the content of the comment.


    Args:
    Args:
    content: New content for the comment
    content: New content for the comment
    """
    """
    self.content = content
    self.content = content
    self.updated_at = datetime.now().isoformat()
    self.updated_at = datetime.now().isoformat()
    self.edited = True
    self.edited = True


    def add_reaction(self, reaction_type: ReactionType, user_id: str) -> Dict[str, Any]:
    def add_reaction(self, reaction_type: ReactionType, user_id: str) -> Dict[str, Any]:
    """
    """
    Add a reaction to the comment.
    Add a reaction to the comment.


    Args:
    Args:
    reaction_type: Type of reaction
    reaction_type: Type of reaction
    user_id: ID of the user adding the reaction
    user_id: ID of the user adding the reaction


    Returns:
    Returns:
    Reaction information
    Reaction information
    """
    """
    reaction_id = str(uuid.uuid4())
    reaction_id = str(uuid.uuid4())


    reaction = {
    reaction = {
    "reaction_id": reaction_id,
    "reaction_id": reaction_id,
    "reaction_type": reaction_type.value,
    "reaction_type": reaction_type.value,
    "user_id": user_id,
    "user_id": user_id,
    "created_at": datetime.now().isoformat(),
    "created_at": datetime.now().isoformat(),
    }
    }


    self.reactions[reaction_id] = reaction
    self.reactions[reaction_id] = reaction
    return reaction
    return reaction


    def remove_reaction(self, reaction_id: str) -> bool:
    def remove_reaction(self, reaction_id: str) -> bool:
    """
    """
    Remove a reaction from the comment.
    Remove a reaction from the comment.


    Args:
    Args:
    reaction_id: ID of the reaction to remove
    reaction_id: ID of the reaction to remove


    Returns:
    Returns:
    True if the reaction was removed, False otherwise
    True if the reaction was removed, False otherwise
    """
    """
    if reaction_id in self.reactions:
    if reaction_id in self.reactions:
    del self.reactions[reaction_id]
    del self.reactions[reaction_id]
    return True
    return True
    return False
    return False


    def get_reactions_by_type(self) -> Dict[str, int]:
    def get_reactions_by_type(self) -> Dict[str, int]:
    """
    """
    Get a count of reactions by type.
    Get a count of reactions by type.


    Returns:
    Returns:
    Dictionary mapping reaction types to counts
    Dictionary mapping reaction types to counts
    """
    """
    counts = {}
    counts = {}
    for reaction in self.reactions.values():
    for reaction in self.reactions.values():
    reaction_type = reaction["reaction_type"]
    reaction_type = reaction["reaction_type"]
    counts[reaction_type] = counts.get(reaction_type, 0) + 1
    counts[reaction_type] = counts.get(reaction_type, 0) + 1
    return counts
    return counts


    def get_user_reaction(self, user_id: str) -> Optional[Dict[str, Any]]:
    def get_user_reaction(self, user_id: str) -> Optional[Dict[str, Any]]:
    """
    """
    Get a user's reaction to the comment.
    Get a user's reaction to the comment.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user


    Returns:
    Returns:
    Reaction information or None if the user has not reacted
    Reaction information or None if the user has not reacted
    """
    """
    for reaction in self.reactions.values():
    for reaction in self.reactions.values():
    if reaction["user_id"] == user_id:
    if reaction["user_id"] == user_id:
    return reaction
    return reaction
    return None
    return None


    def add_metadata(self, key: str, value: Any):
    def add_metadata(self, key: str, value: Any):
    """
    """
    Add metadata to the comment.
    Add metadata to the comment.


    Args:
    Args:
    key: Metadata key
    key: Metadata key
    value: Metadata value
    value: Metadata value
    """
    """
    self.metadata[key] = value
    self.metadata[key] = value


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the comment to a dictionary.
    Convert the comment to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the comment
    Dictionary representation of the comment
    """
    """
    return {
    return {
    "comment_id": self.comment_id,
    "comment_id": self.comment_id,
    "content": self.content,
    "content": self.content,
    "user_id": self.user_id,
    "user_id": self.user_id,
    "resource_type": self.resource_type,
    "resource_type": self.resource_type,
    "resource_id": self.resource_id,
    "resource_id": self.resource_id,
    "parent_id": self.parent_id,
    "parent_id": self.parent_id,
    "created_at": self.created_at,
    "created_at": self.created_at,
    "updated_at": self.updated_at,
    "updated_at": self.updated_at,
    "reactions": self.reactions,
    "reactions": self.reactions,
    "metadata": self.metadata,
    "metadata": self.metadata,
    "edited": self.edited,
    "edited": self.edited,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Comment":
    def from_dict(cls, data: Dict[str, Any]) -> "Comment":
    """
    """
    Create a comment from a dictionary.
    Create a comment from a dictionary.


    Args:
    Args:
    data: Dictionary representation of a comment
    data: Dictionary representation of a comment


    Returns:
    Returns:
    Comment object
    Comment object
    """
    """
    comment = cls(
    comment = cls(
    comment_id=data["comment_id"],
    comment_id=data["comment_id"],
    content=data["content"],
    content=data["content"],
    user_id=data["user_id"],
    user_id=data["user_id"],
    resource_type=data["resource_type"],
    resource_type=data["resource_type"],
    resource_id=data["resource_id"],
    resource_id=data["resource_id"],
    parent_id=data.get("parent_id"),
    parent_id=data.get("parent_id"),
    )
    )


    comment.created_at = data["created_at"]
    comment.created_at = data["created_at"]
    comment.updated_at = data["updated_at"]
    comment.updated_at = data["updated_at"]
    comment.reactions = data.get("reactions", {})
    comment.reactions = data.get("reactions", {})
    comment.metadata = data.get("metadata", {})
    comment.metadata = data.get("metadata", {})
    comment.edited = data.get("edited", False)
    comment.edited = data.get("edited", False)


    return comment
    return comment




    class CommentSystem:
    class CommentSystem:
    """
    """
    Manages comments and reactions on projects and resources.
    Manages comments and reactions on projects and resources.


    This class provides functionality for creating, updating, and querying
    This class provides functionality for creating, updating, and querying
    comments and reactions, enabling team members to provide feedback and
    comments and reactions, enabling team members to provide feedback and
    collaborate effectively.
    collaborate effectively.
    """
    """


    def __init__(self, storage_path: Optional[str] = None):
    def __init__(self, storage_path: Optional[str] = None):
    """
    """
    Initialize the comment system.
    Initialize the comment system.


    Args:
    Args:
    storage_path: Path where comment data will be stored
    storage_path: Path where comment data will be stored
    """
    """
    self.storage_path = storage_path or "comments"
    self.storage_path = storage_path or "comments"
    os.makedirs(self.storage_path, exist_ok=True)
    os.makedirs(self.storage_path, exist_ok=True)


    self.comments: Dict[str, Dict[str, Any]] = {}
    self.comments: Dict[str, Dict[str, Any]] = {}
    self.resource_comments: Dict[str, Dict[str, List[str]]] = {}
    self.resource_comments: Dict[str, Dict[str, List[str]]] = {}
    self.user_comments: Dict[str, List[str]] = {}
    self.user_comments: Dict[str, List[str]] = {}


    self._load_comment_data()
    self._load_comment_data()


    def _load_comment_data(self):
    def _load_comment_data(self):
    """Load comment data from disk."""
    comments_file = os.path.join(self.storage_path, "comments.json")
    resource_comments_file = os.path.join(
    self.storage_path, "resource_comments.json"
    )
    user_comments_file = os.path.join(self.storage_path, "user_comments.json")

    if os.path.exists(comments_file):
    try:
    with open(comments_file, "r") as f:
    self.comments = json.load(f)
    logger.info(f"Loaded {len(self.comments)} comments")
except Exception as e:
    logger.error(f"Failed to load comments: {e}")
    self.comments = {}

    if os.path.exists(resource_comments_file):
    try:
    with open(resource_comments_file, "r") as f:
    self.resource_comments = json.load(f)
except Exception as e:
    logger.error(f"Failed to load resource comments: {e}")
    self.resource_comments = {}

    if os.path.exists(user_comments_file):
    try:
    with open(user_comments_file, "r") as f:
    self.user_comments = json.load(f)
except Exception as e:
    logger.error(f"Failed to load user comments: {e}")
    self.user_comments = {}

    def _save_comment_data(self):
    """Save comment data to disk."""
    comments_file = os.path.join(self.storage_path, "comments.json")
    resource_comments_file = os.path.join(
    self.storage_path, "resource_comments.json"
    )
    user_comments_file = os.path.join(self.storage_path, "user_comments.json")

    with open(comments_file, "w") as f:
    json.dump(self.comments, f, indent=2)

    with open(resource_comments_file, "w") as f:
    json.dump(self.resource_comments, f, indent=2)

    with open(user_comments_file, "w") as f:
    json.dump(self.user_comments, f, indent=2)

    def add_comment(
    self,
    content: str,
    user_id: str,
    resource_type: str,
    resource_id: str,
    parent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ) -> Comment:
    """
    """
    Add a comment to a resource.
    Add a comment to a resource.


    Args:
    Args:
    content: Content of the comment
    content: Content of the comment
    user_id: ID of the user adding the comment
    user_id: ID of the user adding the comment
    resource_type: Type of resource (e.g., "project", "file")
    resource_type: Type of resource (e.g., "project", "file")
    resource_id: ID of the resource
    resource_id: ID of the resource
    parent_id: Optional ID of the parent comment (for replies)
    parent_id: Optional ID of the parent comment (for replies)
    metadata: Optional metadata for the comment
    metadata: Optional metadata for the comment


    Returns:
    Returns:
    Comment object
    Comment object


    Raises:
    Raises:
    ValueError: If the parent comment does not exist
    ValueError: If the parent comment does not exist
    """
    """
    # Check if parent comment exists
    # Check if parent comment exists
    if parent_id and parent_id not in self.comments:
    if parent_id and parent_id not in self.comments:
    raise ValueError(f"Parent comment {parent_id} does not exist")
    raise ValueError(f"Parent comment {parent_id} does not exist")


    # Create comment
    # Create comment
    comment = Comment(
    comment = Comment(
    content=content,
    content=content,
    user_id=user_id,
    user_id=user_id,
    resource_type=resource_type,
    resource_type=resource_type,
    resource_id=resource_id,
    resource_id=resource_id,
    parent_id=parent_id,
    parent_id=parent_id,
    )
    )


    # Add metadata if provided
    # Add metadata if provided
    if metadata:
    if metadata:
    for key, value in metadata.items():
    for key, value in metadata.items():
    comment.add_metadata(key, value)
    comment.add_metadata(key, value)


    # Store comment
    # Store comment
    self.comments[comment.comment_id] = comment.to_dict()
    self.comments[comment.comment_id] = comment.to_dict()


    # Update resource comments
    # Update resource comments
    resource_key = f"{resource_type}:{resource_id}"
    resource_key = f"{resource_type}:{resource_id}"
    if resource_key not in self.resource_comments:
    if resource_key not in self.resource_comments:
    self.resource_comments[resource_key] = {"top_level": [], "replies": {}}
    self.resource_comments[resource_key] = {"top_level": [], "replies": {}}


    if parent_id:
    if parent_id:
    if parent_id not in self.resource_comments[resource_key]["replies"]:
    if parent_id not in self.resource_comments[resource_key]["replies"]:
    self.resource_comments[resource_key]["replies"][parent_id] = []
    self.resource_comments[resource_key]["replies"][parent_id] = []
    self.resource_comments[resource_key]["replies"][parent_id].append(
    self.resource_comments[resource_key]["replies"][parent_id].append(
    comment.comment_id
    comment.comment_id
    )
    )
    else:
    else:
    self.resource_comments[resource_key]["top_level"].append(comment.comment_id)
    self.resource_comments[resource_key]["top_level"].append(comment.comment_id)


    # Update user comments
    # Update user comments
    if user_id not in self.user_comments:
    if user_id not in self.user_comments:
    self.user_comments[user_id] = []
    self.user_comments[user_id] = []
    self.user_comments[user_id].append(comment.comment_id)
    self.user_comments[user_id].append(comment.comment_id)


    self._save_comment_data()
    self._save_comment_data()


    logger.info(
    logger.info(
    f"Added comment {comment.comment_id} to {resource_type} {resource_id}"
    f"Added comment {comment.comment_id} to {resource_type} {resource_id}"
    )
    )
    return comment
    return comment


    def update_comment(
    def update_comment(
    self, comment_id: str, content: str, user_id: str
    self, comment_id: str, content: str, user_id: str
    ) -> Optional[Comment]:
    ) -> Optional[Comment]:
    """
    """
    Update a comment.
    Update a comment.


    Args:
    Args:
    comment_id: ID of the comment to update
    comment_id: ID of the comment to update
    content: New content for the comment
    content: New content for the comment
    user_id: ID of the user updating the comment
    user_id: ID of the user updating the comment


    Returns:
    Returns:
    Updated Comment object or None if the comment does not exist or the user is not authorized
    Updated Comment object or None if the comment does not exist or the user is not authorized
    """
    """
    if comment_id not in self.comments:
    if comment_id not in self.comments:
    logger.error(f"Comment {comment_id} not found")
    logger.error(f"Comment {comment_id} not found")
    return None
    return None


    comment_data = self.comments[comment_id]
    comment_data = self.comments[comment_id]


    # Check if the user is authorized to update the comment
    # Check if the user is authorized to update the comment
    if comment_data["user_id"] != user_id:
    if comment_data["user_id"] != user_id:
    logger.error(
    logger.error(
    f"User {user_id} is not authorized to update comment {comment_id}"
    f"User {user_id} is not authorized to update comment {comment_id}"
    )
    )
    return None
    return None


    # Update comment
    # Update comment
    comment = Comment.from_dict(comment_data)
    comment = Comment.from_dict(comment_data)
    comment.update_content(content)
    comment.update_content(content)


    self.comments[comment_id] = comment.to_dict()
    self.comments[comment_id] = comment.to_dict()
    self._save_comment_data()
    self._save_comment_data()


    logger.info(f"Updated comment {comment_id}")
    logger.info(f"Updated comment {comment_id}")
    return comment
    return comment


    def delete_comment(self, comment_id: str, user_id: str) -> bool:
    def delete_comment(self, comment_id: str, user_id: str) -> bool:
    """
    """
    Delete a comment.
    Delete a comment.


    Args:
    Args:
    comment_id: ID of the comment to delete
    comment_id: ID of the comment to delete
    user_id: ID of the user deleting the comment
    user_id: ID of the user deleting the comment


    Returns:
    Returns:
    True if the comment was deleted, False otherwise
    True if the comment was deleted, False otherwise
    """
    """
    if comment_id not in self.comments:
    if comment_id not in self.comments:
    logger.error(f"Comment {comment_id} not found")
    logger.error(f"Comment {comment_id} not found")
    return False
    return False


    comment_data = self.comments[comment_id]
    comment_data = self.comments[comment_id]


    # Check if the user is authorized to delete the comment
    # Check if the user is authorized to delete the comment
    if comment_data["user_id"] != user_id:
    if comment_data["user_id"] != user_id:
    logger.error(
    logger.error(
    f"User {user_id} is not authorized to delete comment {comment_id}"
    f"User {user_id} is not authorized to delete comment {comment_id}"
    )
    )
    return False
    return False


    # Get comment information
    # Get comment information
    resource_type = comment_data["resource_type"]
    resource_type = comment_data["resource_type"]
    resource_id = comment_data["resource_id"]
    resource_id = comment_data["resource_id"]
    parent_id = comment_data.get("parent_id")
    parent_id = comment_data.get("parent_id")


    # Remove comment from resource comments
    # Remove comment from resource comments
    resource_key = f"{resource_type}:{resource_id}"
    resource_key = f"{resource_type}:{resource_id}"
    if resource_key in self.resource_comments:
    if resource_key in self.resource_comments:
    if parent_id:
    if parent_id:
    if parent_id in self.resource_comments[resource_key]["replies"]:
    if parent_id in self.resource_comments[resource_key]["replies"]:
    if (
    if (
    comment_id
    comment_id
    in self.resource_comments[resource_key]["replies"][parent_id]
    in self.resource_comments[resource_key]["replies"][parent_id]
    ):
    ):
    self.resource_comments[resource_key]["replies"][
    self.resource_comments[resource_key]["replies"][
    parent_id
    parent_id
    ].remove(comment_id)
    ].remove(comment_id)
    else:
    else:
    if comment_id in self.resource_comments[resource_key]["top_level"]:
    if comment_id in self.resource_comments[resource_key]["top_level"]:
    self.resource_comments[resource_key]["top_level"].remove(comment_id)
    self.resource_comments[resource_key]["top_level"].remove(comment_id)


    # Remove comment from user comments
    # Remove comment from user comments
    comment_user_id = comment_data["user_id"]
    comment_user_id = comment_data["user_id"]
    if (
    if (
    comment_user_id in self.user_comments
    comment_user_id in self.user_comments
    and comment_id in self.user_comments[comment_user_id]
    and comment_id in self.user_comments[comment_user_id]
    ):
    ):
    self.user_comments[comment_user_id].remove(comment_id)
    self.user_comments[comment_user_id].remove(comment_id)


    # Remove comment
    # Remove comment
    del self.comments[comment_id]
    del self.comments[comment_id]


    self._save_comment_data()
    self._save_comment_data()


    logger.info(f"Deleted comment {comment_id}")
    logger.info(f"Deleted comment {comment_id}")
    return True
    return True


    def get_comment(self, comment_id: str) -> Optional[Comment]:
    def get_comment(self, comment_id: str) -> Optional[Comment]:
    """
    """
    Get a comment by ID.
    Get a comment by ID.


    Args:
    Args:
    comment_id: ID of the comment
    comment_id: ID of the comment


    Returns:
    Returns:
    Comment object or None if not found
    Comment object or None if not found
    """
    """
    if comment_id not in self.comments:
    if comment_id not in self.comments:
    return None
    return None


    return Comment.from_dict(self.comments[comment_id])
    return Comment.from_dict(self.comments[comment_id])


    def get_resource_comments(
    def get_resource_comments(
    self, resource_type: str, resource_id: str, include_replies: bool = True
    self, resource_type: str, resource_id: str, include_replies: bool = True
    ) -> List[Comment]:
    ) -> List[Comment]:
    """
    """
    Get comments for a resource.
    Get comments for a resource.


    Args:
    Args:
    resource_type: Type of resource (e.g., "project", "file")
    resource_type: Type of resource (e.g., "project", "file")
    resource_id: ID of the resource
    resource_id: ID of the resource
    include_replies: If True, include replies to comments
    include_replies: If True, include replies to comments


    Returns:
    Returns:
    List of Comment objects
    List of Comment objects
    """
    """
    resource_key = f"{resource_type}:{resource_id}"
    resource_key = f"{resource_type}:{resource_id}"
    if resource_key not in self.resource_comments:
    if resource_key not in self.resource_comments:
    return []
    return []


    comments = []
    comments = []


    # Get top-level comments
    # Get top-level comments
    for comment_id in self.resource_comments[resource_key]["top_level"]:
    for comment_id in self.resource_comments[resource_key]["top_level"]:
    comment = self.get_comment(comment_id)
    comment = self.get_comment(comment_id)
    if comment:
    if comment:
    comments.append(comment)
    comments.append(comment)


    # Get replies if requested
    # Get replies if requested
    if (
    if (
    include_replies
    include_replies
    and comment_id in self.resource_comments[resource_key]["replies"]
    and comment_id in self.resource_comments[resource_key]["replies"]
    ):
    ):
    for reply_id in self.resource_comments[resource_key]["replies"][
    for reply_id in self.resource_comments[resource_key]["replies"][
    comment_id
    comment_id
    ]:
    ]:
    reply = self.get_comment(reply_id)
    reply = self.get_comment(reply_id)
    if reply:
    if reply:
    comments.append(reply)
    comments.append(reply)


    # Sort by creation time (oldest first)
    # Sort by creation time (oldest first)
    comments.sort(key=lambda c: c.created_at)
    comments.sort(key=lambda c: c.created_at)


    return comments
    return comments


    def get_comment_replies(self, comment_id: str) -> List[Comment]:
    def get_comment_replies(self, comment_id: str) -> List[Comment]:
    """
    """
    Get replies to a comment.
    Get replies to a comment.


    Args:
    Args:
    comment_id: ID of the comment
    comment_id: ID of the comment


    Returns:
    Returns:
    List of Comment objects
    List of Comment objects
    """
    """
    if comment_id not in self.comments:
    if comment_id not in self.comments:
    return []
    return []


    comment_data = self.comments[comment_id]
    comment_data = self.comments[comment_id]
    resource_type = comment_data["resource_type"]
    resource_type = comment_data["resource_type"]
    resource_id = comment_data["resource_id"]
    resource_id = comment_data["resource_id"]


    resource_key = f"{resource_type}:{resource_id}"
    resource_key = f"{resource_type}:{resource_id}"
    if resource_key not in self.resource_comments:
    if resource_key not in self.resource_comments:
    return []
    return []


    if comment_id not in self.resource_comments[resource_key]["replies"]:
    if comment_id not in self.resource_comments[resource_key]["replies"]:
    return []
    return []


    replies = []
    replies = []
    for reply_id in self.resource_comments[resource_key]["replies"][comment_id]:
    for reply_id in self.resource_comments[resource_key]["replies"][comment_id]:
    reply = self.get_comment(reply_id)
    reply = self.get_comment(reply_id)
    if reply:
    if reply:
    replies.append(reply)
    replies.append(reply)


    # Sort by creation time (oldest first)
    # Sort by creation time (oldest first)
    replies.sort(key=lambda c: c.created_at)
    replies.sort(key=lambda c: c.created_at)


    return replies
    return replies


    def get_user_comments(self, user_id: str) -> List[Comment]:
    def get_user_comments(self, user_id: str) -> List[Comment]:
    """
    """
    Get comments by a user.
    Get comments by a user.


    Args:
    Args:
    user_id: ID of the user
    user_id: ID of the user


    Returns:
    Returns:
    List of Comment objects
    List of Comment objects
    """
    """
    if user_id not in self.user_comments:
    if user_id not in self.user_comments:
    return []
    return []


    comments = []
    comments = []
    for comment_id in self.user_comments[user_id]:
    for comment_id in self.user_comments[user_id]:
    comment = self.get_comment(comment_id)
    comment = self.get_comment(comment_id)
    if comment:
    if comment:
    comments.append(comment)
    comments.append(comment)


    # Sort by creation time (newest first)
    # Sort by creation time (newest first)
    comments.sort(key=lambda c: c.created_at, reverse=True)
    comments.sort(key=lambda c: c.created_at, reverse=True)


    return comments
    return comments


    def add_reaction(
    def add_reaction(
    self, comment_id: str, reaction_type: ReactionType, user_id: str
    self, comment_id: str, reaction_type: ReactionType, user_id: str
    ) -> Optional[Dict[str, Any]]:
    ) -> Optional[Dict[str, Any]]:
    """
    """
    Add a reaction to a comment.
    Add a reaction to a comment.


    Args:
    Args:
    comment_id: ID of the comment
    comment_id: ID of the comment
    reaction_type: Type of reaction
    reaction_type: Type of reaction
    user_id: ID of the user adding the reaction
    user_id: ID of the user adding the reaction


    Returns:
    Returns:
    Reaction information or None if the comment does not exist
    Reaction information or None if the comment does not exist
    """
    """
    if comment_id not in self.comments:
    if comment_id not in self.comments:
    logger.error(f"Comment {comment_id} not found")
    logger.error(f"Comment {comment_id} not found")
    return None
    return None


    # Remove any existing reaction from this user
    # Remove any existing reaction from this user
    comment = Comment.from_dict(self.comments[comment_id])
    comment = Comment.from_dict(self.comments[comment_id])
    existing_reaction = comment.get_user_reaction(user_id)
    existing_reaction = comment.get_user_reaction(user_id)
    if existing_reaction:
    if existing_reaction:
    comment.remove_reaction(existing_reaction["reaction_id"])
    comment.remove_reaction(existing_reaction["reaction_id"])


    # Add new reaction
    # Add new reaction
    reaction = comment.add_reaction(reaction_type, user_id)
    reaction = comment.add_reaction(reaction_type, user_id)


    self.comments[comment_id] = comment.to_dict()
    self.comments[comment_id] = comment.to_dict()
    self._save_comment_data()
    self._save_comment_data()


    logger.info(
    logger.info(
    f"Added {reaction_type.value} reaction to comment {comment_id} by user {user_id}"
    f"Added {reaction_type.value} reaction to comment {comment_id} by user {user_id}"
    )
    )
    return reaction
    return reaction


    def remove_reaction(self, comment_id: str, user_id: str) -> bool:
    def remove_reaction(self, comment_id: str, user_id: str) -> bool:
    """
    """
    Remove a user's reaction from a comment.
    Remove a user's reaction from a comment.


    Args:
    Args:
    comment_id: ID of the comment
    comment_id: ID of the comment
    user_id: ID of the user
    user_id: ID of the user


    Returns:
    Returns:
    True if the reaction was removed, False otherwise
    True if the reaction was removed, False otherwise
    """
    """
    if comment_id not in self.comments:
    if comment_id not in self.comments:
    logger.error(f"Comment {comment_id} not found")
    logger.error(f"Comment {comment_id} not found")
    return False
    return False


    comment = Comment.from_dict(self.comments[comment_id])
    comment = Comment.from_dict(self.comments[comment_id])
    existing_reaction = comment.get_user_reaction(user_id)
    existing_reaction = comment.get_user_reaction(user_id)


    if not existing_reaction:
    if not existing_reaction:
    return False
    return False


    result = comment.remove_reaction(existing_reaction["reaction_id"])
    result = comment.remove_reaction(existing_reaction["reaction_id"])


    if result:
    if result:
    self.comments[comment_id] = comment.to_dict()
    self.comments[comment_id] = comment.to_dict()
    self._save_comment_data()
    self._save_comment_data()


    logger.info(f"Removed reaction from comment {comment_id} by user {user_id}")
    logger.info(f"Removed reaction from comment {comment_id} by user {user_id}")


    return result
    return result


    def search_comments(
    def search_comments(
    self,
    self,
    query: str,
    query: str,
    resource_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    user_id: Optional[str] = None,
    ) -> List[Comment]:
    ) -> List[Comment]:
    """
    """
    Search for comments.
    Search for comments.


    Args:
    Args:
    query: Search query
    query: Search query
    resource_type: Optional resource type to filter by
    resource_type: Optional resource type to filter by
    resource_id: Optional resource ID to filter by
    resource_id: Optional resource ID to filter by
    user_id: Optional user ID to filter by
    user_id: Optional user ID to filter by


    Returns:
    Returns:
    List of Comment objects
    List of Comment objects
    """
    """
    results = []
    results = []
    query = query.lower()
    query = query.lower()


    for comment_data in self.comments.values():
    for comment_data in self.comments.values():
    # Apply filters
    # Apply filters
    if resource_type and comment_data["resource_type"] != resource_type:
    if resource_type and comment_data["resource_type"] != resource_type:
    continue
    continue


    if resource_id and comment_data["resource_id"] != resource_id:
    if resource_id and comment_data["resource_id"] != resource_id:
    continue
    continue


    if user_id and comment_data["user_id"] != user_id:
    if user_id and comment_data["user_id"] != user_id:
    continue
    continue


    # Check if query matches
    # Check if query matches
    if query in comment_data["content"].lower():
    if query in comment_data["content"].lower():
    comment = Comment.from_dict(comment_data)
    comment = Comment.from_dict(comment_data)
    results.append(comment)
    results.append(comment)


    # Sort by creation time (newest first)
    # Sort by creation time (newest first)
    results.sort(key=lambda c: c.created_at, reverse=True)
    results.sort(key=lambda c: c.created_at, reverse=True)


    return results
    return results