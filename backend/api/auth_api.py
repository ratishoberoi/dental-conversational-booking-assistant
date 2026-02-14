from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models.db import SessionLocal
from backend.models.entities import User
from backend.core.auth import hash_password, verify_password, create_token

router = APIRouter()


class RegisterIn(BaseModel):
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: RegisterIn):
    db = SessionLocal()

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email exists")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return {"user_id": user.id}


@router.post("/login")
def login(data: LoginIn):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    db.close()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user.id)
    return {"token": token, "user_id": user.id}
