from fastapi import APIRouter, HTTPException, Response, Depends, UploadFile, File

from models.auth import SignupRequest, LoginRequest, UpdateUserRequest, ClerkRegisterRequest
from services.s3_service import upload_profile_image
from services.auth_service import (
    create_user,
    get_user_by_email,
    authenticate_user,
    create_access_token
)
from dependencies.auth import get_current_user, CurrentUser
from repositories.user_repository import UserRepository

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

@router.get("/me")
def get_me(user: CurrentUser = Depends(get_current_user)):
    from uuid import UUID
    user_info = UserRepository.get_full_info(UUID(user.id))
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "user": {
            "id": str(user_info["id"]),
            "email": user_info["email"],
            "first_name": user_info["first_name"],
            "last_name": user_info["last_name"],
            "profile_image_url": user_info["profile_image_url"],
            "created_at": user_info["created_at"].isoformat() if user_info["created_at"] else None,
            "updated_at": user_info["updated_at"].isoformat() if user_info["updated_at"] else None
        }
    }

@router.put("/me")
def update_me(request: UpdateUserRequest, user: CurrentUser = Depends(get_current_user)):
    from uuid import UUID
    updated_user = UserRepository.update(
        user_id=UUID(user.id),
        first_name=request.first_name,
        last_name=request.last_name
    )

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "user": {
            "id": str(updated_user["id"]),
            "email": updated_user["email"],
            "first_name": updated_user["first_name"],
            "last_name": updated_user["last_name"],
            "profile_image_url": updated_user["profile_image_url"],
            "created_at": updated_user["created_at"].isoformat() if updated_user["created_at"] else None,
            "updated_at": updated_user["updated_at"].isoformat() if updated_user["updated_at"] else None
        }
    }

@router.post("/me/profile-image")
def upload_profile_image_endpoint(file: UploadFile = File(...), user: CurrentUser = Depends(get_current_user)):
    from uuid import UUID
    image_url = upload_profile_image(file.file)

    updated_user = UserRepository.update(
        user_id=UUID(user.id),
        profile_image_url=image_url
    )

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "profile_image_url": image_url,
        "user": {
            "id": str(updated_user["id"]),
            "email": updated_user["email"],
            "first_name": updated_user["first_name"],
            "last_name": updated_user["last_name"],
            "profile_image_url": updated_user["profile_image_url"],
            "created_at": updated_user["created_at"].isoformat() if updated_user["created_at"] else None,
            "updated_at": updated_user["updated_at"].isoformat() if updated_user["updated_at"] else None
        }
    }
