from typing import Optional
from uuid import UUID
from fastapi import HTTPException, Request

from services.auth_service import decode_token, get_user_by_id

class CurrentUser:
    def __init__(self, id: UUID, email: str, first_name: str, last_name: str, profile_image_url: Optional[str] = None):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.profile_image_url = profile_image_url

def get_current_user(request: Request) -> CurrentUser:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = get_user_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return CurrentUser(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        profile_image_url=user.get("profile_image_url")
    )

def get_optional_user(request: Request) -> Optional[CurrentUser]:
    """Returns current user if authenticated, None otherwise. Does not raise errors."""
    token = request.cookies.get("access_token")
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = get_user_by_id(UUID(user_id))
    if not user:
        return None

    return CurrentUser(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        profile_image_url=user.get("profile_image_url")
    )
