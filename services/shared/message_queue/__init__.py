"""
"""
Shared message queue utilities for pAIssive income microservices.
Shared message queue utilities for pAIssive income microservices.


This package provides utilities for asynchronous communication between
This package provides utilities for asynchronous communication between
microservices using a message queue (RabbitMQ).
microservices using a message queue (RabbitMQ).
"""
"""


from .message import (Message, MessagePriority, MessageSchema, MessageStatus,
from .message import (Message, MessagePriority, MessageSchema, MessageStatus,
MessageType)
MessageType)


__all__
__all__


from .client import (AsyncMessageHandler, AsyncMessageQueueClient,
from .client import (AsyncMessageHandler, AsyncMessageQueueClient,
MessageHandler, MessageQueueClient)
MessageHandler, MessageQueueClient)
from .exceptions import (ConnectionError, ConsumeError, MessageQueueError,
from .exceptions import (ConnectionError, ConsumeError, MessageQueueError,
PublishError, SchemaError)
PublishError, SchemaError)


= [
= [
"MessageQueueClient",
"MessageQueueClient",
"AsyncMessageQueueClient",
"AsyncMessageQueueClient",
"MessageHandler",
"MessageHandler",
"AsyncMessageHandler",
"AsyncMessageHandler",
"Message",
"Message",
"MessageSchema",
"MessageSchema",
"MessagePriority",
"MessagePriority",
"MessageStatus",
"MessageStatus",
"MessageType",
"MessageType",
"MessageQueueError",
"MessageQueueError",
"ConnectionError",
"ConnectionError",
"PublishError",
"PublishError",
"ConsumeError",
"ConsumeError",
"SchemaError",
"SchemaError",
]
]