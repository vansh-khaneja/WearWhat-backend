from uuid import UUID
from typing import Optional, Dict
from repositories.wardrobe_tags_repository import WardrobeTagsRepository

class WardrobeTagsService:
    @staticmethod
    def get_tags(user_id: UUID) -> Optional[dict]:
        return WardrobeTagsRepository.get_by_user(user_id)

    @staticmethod
    def add_item_to_tag(user_id: UUID, category_group: str, category: str, item_id: str) -> dict:
        """Add a wardrobe item to the tags tree."""
        return WardrobeTagsRepository.add_item_to_tag(user_id, category_group, category, item_id)

    @staticmethod
    def remove_item(user_id: UUID, item_id: str) -> Optional[dict]:
        """Remove a wardrobe item from all tags. Used when deleting an item."""
        return WardrobeTagsRepository.remove_item_from_all(user_id, item_id)

    @staticmethod
    def update_tags(user_id: UUID, tags_by_category: Dict) -> Optional[dict]:
        existing = WardrobeTagsRepository.get_by_user(user_id)
        if existing is None:
            return WardrobeTagsRepository.create(user_id, tags_by_category)
        return WardrobeTagsRepository.update(user_id, tags_by_category)
