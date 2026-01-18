from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user, CurrentUser
from controllers.wardrobe_tags_controller import get_wardrobe_tags_controller

router = APIRouter(
    prefix="/wardrobe-tags",
    tags=["Wardrobe Tags"]
)

@router.get("")
def get_wardrobe_tags(user: CurrentUser = Depends(get_current_user)):
    return get_wardrobe_tags_controller(user)
