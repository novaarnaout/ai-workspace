from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        email=user.email,
        name=user.name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()