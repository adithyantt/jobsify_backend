from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[dict])
def get_user_notifications(user_email: str = Query(...), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_email == user_email).order_by(Notification.created_at.desc()).all()
    return [
        {
            "id": n.id,
            "user_email": n.user_email,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "reference_id": n.reference_id,
            "is_read": n.is_read,
            "created_at": n.created_at
        }
        for n in notifications
    ]

@router.get("/", response_model=List[dict])
def get_user_notifications_slash(user_email: str = Query(...), db: Session = Depends(get_db)):
    return get_user_notifications(user_email, db)

@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        return {"message": "Notification marked as read"}
    return {"error": "Notification not found"}
