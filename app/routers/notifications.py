from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def get_user_notifications(user_email: str, db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_email == user_email).order_by(Notification.created_at.desc()).all()

@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        return {"message": "Notification marked as read"}
    return {"error": "Notification not found"}
