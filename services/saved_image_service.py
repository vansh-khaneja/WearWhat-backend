from uuid import UUID
from typing import Optional, List
from repositories.saved_image_repository import SavedImageRepository

class SavedImageService:
    @staticmethod
    def save_image(user_id: UUID, image_id: UUID, note: Optional[str] = None) -> dict:
        return SavedImageRepository.save(user_id, image_id, note)

    @staticmethod
    def get_saved_images(user_id: UUID) -> List[dict]:
        return SavedImageRepository.get_by_user(user_id)

    @staticmethod
    def update_note(saved_image_id: UUID, note: str) -> Optional[dict]:
        return SavedImageRepository.update_note(saved_image_id, note)

    @staticmethod
    def delete_saved_image(saved_image_id: UUID, user_id: UUID) -> bool:
        return SavedImageRepository.delete(saved_image_id, user_id)
