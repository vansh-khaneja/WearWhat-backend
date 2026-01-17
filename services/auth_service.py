from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
from repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: UUID, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def create_user(email: str, first_name: str, last_name: str, password: str) -> dict:
    return UserRepository.create(email, first_name, last_name, hash_password(password))

def get_user_by_email(email: str) -> Optional[dict]:
    return UserRepository.get_by_email(email)

def get_user_by_id(user_id: UUID) -> Optional[dict]:
    return UserRepository.get_by_id(user_id)

def authenticate_user(email: str, password: str) -> Optional[dict]:
    result = UserRepository.get_with_password(email)
    if not result:
        return None

    if not verify_password(password, result["password_hash"]):
        return None

    return {
        "id": result["id"],
        "email": result["email"],
        "first_name": result["first_name"],
        "last_name": result["last_name"],
        "created_at": result["created_at"]
    }
