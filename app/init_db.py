from app.database import Base, engine
from app.models.user import User
from app.models.job import Job

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
