from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET = "change_this_secret"
ALGO = "HS256"

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(pw: str):
    return pwd_ctx.hash(pw)


def verify_password(pw, hashed):
    return pwd_ctx.verify(pw, hashed)


def create_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=12)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token: str):
    return jwt.decode(token, SECRET, algorithms=[ALGO])
