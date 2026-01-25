import uuid
from typing import Optional
from uuid import UUID

import requests
from fastapi import HTTPException, Request
from jose import jwt

from config import CLERK_ISSUER
from services.auth_service import get_user_by_id
from repositories.user_repository import UserRepository

# Clerk JWKS URL
JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json"

# Cache for JWKS (public keys)
_jwks_cache = None


def get_jwks():
    """Fetch Clerk public keys (with caching)."""
    global _jwks_cache
    if _jwks_cache is None:
        try:
            response = requests.get(JWKS_URL)
            response.raise_for_status()
            _jwks_cache = response.json()
        except Exception as e:
            print(f"Error fetching JWKS: {e}")
            return None
    return _jwks_cache


def verify_clerk_jwt(token: str) -> Optional[dict]:
    """
    Verify a Clerk JWT token and return the payload.
    Returns None if token is invalid.
    """
    try:
        jwks = get_jwks()
        if not jwks:
            return None

        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
            options={"verify_aud": False},
        )
        return payload
    except Exception as e:
        print(f"Token invalid: {e}")
        return None


def clerk_id_to_uuid(clerk_user_id: str) -> str:
    """
    Deterministically convert a Clerk user ID into a UUID v5.
    Same input will always produce the same UUID.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_URL, clerk_user_id))

class CurrentUser:
    def __init__(self, id: str, clerk_id: str, email: str, first_name: str, last_name: str, profile_image_url: Optional[str] = None):
        # id is the UUID (converted from Clerk ID) used in database
        # clerk_id is the original Clerk user ID string
        self.id = id  # UUID string for database queries
        self.clerk_id = clerk_id  # Original Clerk ID
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.profile_image_url = profile_image_url
    
    def get_uuid(self) -> UUID:
        """Get UUID object for database operations."""
        return UUID(self.id)

def get_current_user(request: Request) -> CurrentUser:
    # Try to get token from Authorization header first (Clerk style)
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Fallback to cookie (legacy)
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Verify Clerk JWT token
    payload = verify_clerk_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Extract Clerk user ID from token
    clerk_user_id = payload.get("sub")
    if not clerk_user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Convert Clerk ID to UUID for database lookup
    user_uuid = clerk_id_to_uuid(clerk_user_id)
    
    # Get user from database using UUID
    user = get_user_by_id(UUID(user_uuid))

    # Auto-create user if they don't exist (first Clerk login)
    if not user:
        email = payload.get("email", "")
        first_name = payload.get("first_name", "")
        last_name = payload.get("last_name", "")
        user = UserRepository.create_clerk_user(
            user_id=UUID(user_uuid),
            email=email,
            first_name=first_name,
            last_name=last_name
        )

    return CurrentUser(
        id=str(user["id"]),  # UUID string from database
        clerk_id=clerk_user_id,  # Original Clerk ID
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        profile_image_url=user.get("profile_image_url")
    )

def get_optional_user(request: Request) -> Optional[CurrentUser]:
    """Returns current user if authenticated, None otherwise. Does not raise errors."""
    # Try to get token from Authorization header first (Clerk style)
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Fallback to cookie (legacy)
        token = request.cookies.get("access_token")
    
    if not token:
        return None

    # Verify Clerk JWT token
    payload = verify_clerk_jwt(token)
    if not payload:
        return None

    # Extract Clerk user ID from token
    clerk_user_id = payload.get("sub")
    if not clerk_user_id:
        return None

    # Convert Clerk ID to UUID for database lookup
    user_uuid = clerk_id_to_uuid(clerk_user_id)
    
    # Get user from database using UUID
    user = get_user_by_id(UUID(user_uuid))

    # Auto-create user if they don't exist (first Clerk login)
    if not user:
        email = payload.get("email", "")
        first_name = payload.get("first_name", "")
        last_name = payload.get("last_name", "")
        try:
            user = UserRepository.create_clerk_user(
                user_id=UUID(user_uuid),
                email=email,
                first_name=first_name,
                last_name=last_name
            )
        except Exception:
            return None

    return CurrentUser(
        id=str(user["id"]),  # UUID string from database
        clerk_id=clerk_user_id,  # Original Clerk ID
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        profile_image_url=user.get("profile_image_url")
    )
