from fastapi import APIRouter, UploadFile, File, Depends
from controllers.wardrobe_controller import upload_wardrobe_item, get_user_wardrobe, delete_wardrobe_item
from dependencies.auth import get_current_user, CurrentUser

router = APIRouter(
    prefix="/wardrobe",
    tags=["Wardrobe"]
)

@router.post("/upload")
def upload_image(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user)
):
    return upload_wardrobe_item(file, user)

@router.get("/")
def get_wardrobe(user: CurrentUser = Depends(get_current_user)):
    return get_user_wardrobe(user)

@router.delete("/{item_id}")
def delete_item(item_id: str, user: CurrentUser = Depends(get_current_user)):
    return delete_wardrobe_item(item_id, user)
