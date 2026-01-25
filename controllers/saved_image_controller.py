from uuid import UUID
from dependencies.auth import CurrentUser
from services.saved_image_service import SavedImageService
from models.saved_image import SaveImageRequest, UpdateNoteRequest

def save_image_controller(request: SaveImageRequest, user: CurrentUser):
    return SavedImageService.save_image(UUID(user.id), request.image_id, request.note)

def get_saved_images_controller(user: CurrentUser):
    return SavedImageService.get_saved_images(UUID(user.id))

def update_note_controller(request: UpdateNoteRequest, user: CurrentUser):
    result = SavedImageService.update_note(request.saved_image_id, request.note)
    if not result or result["user_id"] != str(user.id):
        return {"error": "Saved image not found or unauthorized"}
    return result

def delete_saved_image_controller(saved_image_id: UUID, user: CurrentUser):
    success = SavedImageService.delete_saved_image(saved_image_id, UUID(user.id))
    if not success:
        return {"error": "Saved image not found or unauthorized"}
    return {"success": True}
