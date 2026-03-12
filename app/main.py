from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.models import (
    Notification,
    NotificationResponse,
    NotificationSendRequest,
    NotificationStatus,
)

init_db()

app = FastAPI(
    title="MUL Notifications Service",
    version="1.0.0",
    description="Email, SMS, and push notifications via async queue",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    init_db()


@app.get("/", summary="Notifications Service Root")
async def root() -> dict[str, str]:
    return {"message": "MUL Notifications Service is running"}


@app.get("/health", summary="Health Check")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "notifications-service"}


@app.post(
    "/api/v1/notifications/send",
    summary="Send Notification",
    response_model=NotificationResponse,
    status_code=201,
)
async def send_notification(
    payload: NotificationSendRequest,
    db: Session = Depends(get_db),
) -> NotificationResponse:
    record = Notification(
        recipient=payload.recipient,
        type=payload.type.value,
        subject=payload.subject,
        message=payload.message,
        status=NotificationStatus.QUEUED.value,
        source_service=payload.source_service,
    )
    db.add(record)
    db.flush()

    # Simulated async dispatch (fast path, no blocking external call here)
    record.status = NotificationStatus.SENT.value
    record.sent_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


@app.get(
    "/api/v1/notifications/{notification_id}",
    summary="Get Notification",
    response_model=NotificationResponse,
)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
) -> NotificationResponse:
    record = db.query(Notification).filter(Notification.id == notification_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Notification not found")
    return record


@app.get(
    "/api/v1/notifications",
    summary="List Notifications",
    response_model=list[NotificationResponse],
)
async def list_notifications(
    recipient: str | None = None,
    db: Session = Depends(get_db),
) -> list[NotificationResponse]:
    query = db.query(Notification)
    if recipient:
        query = query.filter(Notification.recipient == recipient)
    return query.order_by(Notification.created_at.desc()).limit(100).all()
