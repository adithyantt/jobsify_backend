from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ConversationCreate(BaseModel):
    sender_email: str
    recipient_email: str
    worker_id: Optional[int] = None
    initial_message: Optional[str] = None

    @field_validator("sender_email", "recipient_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value:
            raise ValueError("Valid email is required")
        return value

    @field_validator("initial_message")
    @classmethod
    def validate_initial_message(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = " ".join(value.split())
        if value and len(value) > 2000:
            raise ValueError("Message must not exceed 2000 characters")
        return value or None


class MessageCreate(BaseModel):
    sender_email: str
    content: str

    @field_validator("sender_email")
    @classmethod
    def validate_sender_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value:
            raise ValueError("Valid sender email is required")
        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 1:
            raise ValueError("Message cannot be empty")
        if len(value) > 2000:
            raise ValueError("Message must not exceed 2000 characters")
        return value


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender_email: str
    recipient_email: str
    content: str
    is_read: bool
    created_at: datetime


class ConversationResponse(BaseModel):
    id: int
    participant_email: str
    participant_name: str
    worker_id: Optional[int] = None
    worker_name: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0


class ConversationDetailResponse(BaseModel):
    id: int
    participant_email: str
    participant_name: str
    worker_id: Optional[int] = None
    worker_name: Optional[str] = None
    messages: list[MessageResponse]
