from typing import List
from fastapi import UploadFile

from services.cloudinary_service import upload_image
from services.clip_service import generate_tags
from services.wardrobe_tags_service import WardrobeTagsService
from dependencies.auth import CurrentUser
from repositories.wardrobe_repository import WardrobeRepository

def upload_wardrobe_items(files: List[UploadFile], user: CurrentUser):
    results = []

    for file in files:
        image_url = upload_image(file.file)
        tags = generate_tags(image_url)

        # Save to database
        item = WardrobeRepository.create(
            user_id=user.id,
            image_url=image_url,
            category_group=tags["categoryGroup"],
            category=tags["category"],
            attributes=tags["attributes"]
        )

        # Update the wardrobe tags tree with item ID
        WardrobeTagsService.add_item_to_tag(
            user_id=user.id,
            category_group=tags["categoryGroup"],
            category=tags["category"],
            item_id=str(item["id"])
        )

        results.append({
            "id": str(item["id"]),
            "image_url": item["image_url"],
            "categoryGroup": item["category_group"],
            "category": item["category"],
            "attributes": item["attributes"]
        })

    return {
        "success": True,
        "count": len(results),
        "user_id": str(user.id),
        "items": results
    }

def get_user_wardrobe(user: CurrentUser):
    items = WardrobeRepository.get_by_user_id(user.id)

    # Get all saved image ids for this user
    from repositories.saved_image_repository import SavedImageRepository
    saved_images = SavedImageRepository.get_by_user(user.id)
    image_id_to_saved = {str(img["image_id"]): str(img["id"]) for img in saved_images}

    return {
        "success": True,
        "count": len(items),
        "items": [
            {
                "id": str(item["id"]),
                "image_url": item["image_url"],
                "categoryGroup": item["category_group"],
                "category": item["category"],
                "attributes": item["attributes"],
                "created_at": item["created_at"].isoformat(),
                "saved": str(item["id"]) in image_id_to_saved,
                "saved_image_id": image_id_to_saved.get(str(item["id"]))
            }
            for item in items
        ]
    }

def delete_wardrobe_item(item_id: str, user: CurrentUser):
    deleted = WardrobeRepository.delete(item_id, user.id)

    if not deleted:
        return {"success": False, "message": "Item not found or not authorized"}

    # Remove item from wardrobe tags tree
    WardrobeTagsService.remove_item(user.id, item_id)

    return {"success": True, "message": "Item deleted"}
