from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user, CurrentUser
from models.saved_image import SaveImageRequest, UpdateNoteRequest
from controllers.saved_image_controller import (
    save_image_controller,
    get_saved_images_controller,
    update_note_controller,
    delete_saved_image_controller
)
from uuid import UUID

router = APIRouter(
    prefix="/saved-images",
    tags=["Saved Images"]
)

@router.post("/save")
def save_image(request: SaveImageRequest, user: CurrentUser = Depends(get_current_user)):
    return save_image_controller(request, user)

@router.get("")
def get_saved_images(user: CurrentUser = Depends(get_current_user)):
    return get_saved_images_controller(user)

@router.put("/note")
def update_note(request: UpdateNoteRequest, user: CurrentUser = Depends(get_current_user)):
    return update_note_controller(request, user)

@router.delete("/{saved_image_id}")
def delete_saved_image(saved_image_id: UUID, user: CurrentUser = Depends(get_current_user)):
    return delete_saved_image_controller(saved_image_id, user)
