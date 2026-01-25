from uuid import UUID
from dependencies.auth import CurrentUser
from services.wardrobe_tags_service import WardrobeTagsService

def get_wardrobe_tags_controller(user: CurrentUser):
    result = WardrobeTagsService.get_tags(UUID(user.id))
    if not result:
        # Return empty structure if no tags exist yet
        return {"tags_by_category": {}}
    return result
