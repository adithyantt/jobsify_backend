from app.database import engine
from app.models.notification import Notification

# Update the notification table with new columns
Notification.__table__.create(engine, checkfirst=True)
print("Notification table updated successfully with type and reference_id columns")
