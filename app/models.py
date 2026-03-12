"""Notification ORM and Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String(255), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default=NotificationStatus.QUEUED.value)
    source_service = Column(String(80), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


class NotificationSendRequest(BaseModel):
    recipient: str = Field(min_length=3, max_length=255)
    type: NotificationType
    message: str = Field(min_length=1, max_length=2000)
    subject: Optional[str] = Field(default=None, max_length=255)
    source_service: Optional[str] = Field(default="payments-service", max_length=80)


class NotificationResponse(BaseModel):
    id: int
    recipient: str
    type: str
    subject: Optional[str]
    message: str
    status: str
    source_service: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True
