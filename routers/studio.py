from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID

from controllers.studio_controller import (
    generate_studio_image_controller,
    get_available_prompts
)
from repositories.studio_repository import StudioRepository
from repositories.user_repository import UserRepository
from dependencies.auth import get_current_user, CurrentUser

router = APIRouter(
    prefix="/studio",
    tags=["Studio Image Generation"]
)


class GenerateStudioImageRequest(BaseModel):
    item_id: str  # Wardrobe item ID


@router.post("/generate")
def generate_studio_image(
    request: GenerateStudioImageRequest,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Generate a clean studio-quality product image from a wardrobe item.

    Pass the wardrobe item_id and the service will:
    1. Fetch the item's image from your wardrobe
    2. Automatically detect the category (upperWear, bottomWear, etc.)
    3. Use the appropriate prompt for that category
    4. Generate a clean, professional studio image via Gemini
    5. Upload to Cloudinary and return the URL
    """
    return generate_studio_image_controller(user_id=user.id, item_id=request.item_id)


@router.get("/prompts")
def get_prompts():
    """
    Get all available category prompts.
    Shows what prompts are used for each category group.
    """
    return get_available_prompts()


@router.get("/tokens")
def get_tokens(user: CurrentUser = Depends(get_current_user)):
    """
    Get current token balance for the user.
    """
    tokens = UserRepository.get_tokens(UUID(user.id))
    return {
        "success": True,
        "tokens": tokens
    }


@router.get("/all")
def get_all_studio_images(
    limit: int = 20,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Get all studio images for the current user with pagination.
    Returns list sorted by newest first, includes token balance.
    """
    images = StudioRepository.get_all_by_user(UUID(user.id), limit=limit, offset=offset)
    tokens = UserRepository.get_tokens(UUID(user.id))
    return {
        "success": True,
        "count": len(images),
        "tokens": tokens,
        "images": images
    }


@router.get("/item/{item_id}")
def get_studio_images_for_item(
    item_id: str,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Get all studio images generated for a wardrobe item.
    Returns list of all generations sorted by newest first.
    """
    images = StudioRepository.get_by_item_id(UUID(user.id), UUID(item_id))
    return {
        "success": True,
        "count": len(images),
        "images": images
    }


@router.get("/item/{item_id}/latest")
def get_latest_studio_image(
    item_id: str,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Get the latest studio image generated for a wardrobe item.
    """
    image = StudioRepository.get_latest_by_item_id(UUID(user.id), UUID(item_id))
    if not image:
        return {"success": False, "message": "No studio image found for this item"}
    return {
        "success": True,
        "image": image
    }
