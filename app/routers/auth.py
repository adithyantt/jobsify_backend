from fastapi import APIRouter,Depends,
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

router = APIRouter

#Dataabse dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        @router.post("/register")
        def register_user(
            name: str,
            email: str,
            password: str,
            role: str,
                   db: Session = Depends(get_db)
        ):
            
            user = User(
                name=name,
                email=email,
                password=password,
                role=role   
            
            )
    
db.add(user)
db.commit()
db.refresh(user)
return {"message" :"User regiistered successfully"}
