from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class CommMessage(BaseModel):
    """
    Standard communication message format for COMM_QUEUE.
    
    All messages sent through the communication queue must follow this structure:
    - scope: The domain or context of the message (e.g., 'booking', 'user', 'notification')
    - action: The specific action to perform (e.g., 'create', 'update', 'delete', 'notify')
    - body: The message payload containing relevant data
    
    Example:
        {
            "scope": "booking",
            "action": "created",
            "body": {
                "booking_id": 123,
                "user_id": 456,
                "status": "confirmed"
            }
        }
    """
    
    scope: str = Field(
        ...,
        description="The domain or context of the message (e.g., 'booking', 'user', 'notification')",
        min_length=1
    )
    
    action: str = Field(
        ...,
        description="The specific action to perform (e.g., 'create', 'update', 'delete', 'notify')",
        min_length=1
    )
    
    body: Dict[str, Any] = Field(
        ...,
        description="The message payload containing relevant data"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata for tracking, debugging, or additional context"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "scope": "booking",
                    "action": "created",
                    "body": {
                        "booking_id": 123,
                        "user_id": 456,
                        "status": "confirmed"
                    },
                    "metadata": {
                        "timestamp": "2024-01-06T20:30:00Z",
                        "source": "gra-bff"
                    }
                },
                {
                    "scope": "notification",
                    "action": "send",
                    "body": {
                        "user_id": 789,
                        "type": "email",
                        "template": "booking_confirmation"
                    }
                }
            ]
        }
