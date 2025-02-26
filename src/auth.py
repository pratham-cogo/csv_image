from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from src.services.users.models.users import User
from configs.env import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

token_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return token_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return token_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(username: str, password: str):
    user: User = User.get_or_none(User.username == username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user