from app.database import Base, engine
from app.models import user, job

def init_db():
    Base.metadata.create_all(bind=engine)
