from fastapi import APIRouter, HTTPException, Response

from models.auth import SignupRequest, LoginRequest
from services.auth_service import (
    create_user,
    get_user_by_email,
    authenticate_user,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/signup")
def signup(request: SignupRequest, response: Response):
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        password=request.password
    )

    token = create_access_token(user["id"], user["email"])

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24  # 24 hours
    )

    return {
        "success": True,
        "message": "User created successfully",
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"]
        }
    }

@router.post("/login")
def login(request: LoginRequest, response: Response):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user["id"], user["email"])

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24  # 24 hours
    )

    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"]
        }
    }

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"success": True, "message": "Logged out successfully"}
