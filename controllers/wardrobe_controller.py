from uuid import UUID
from fastapi import UploadFile

from services.cloudinary_service import upload_image
from services.clip_service import generate_tags
from services.wardrobe_tags_service import WardrobeTagsService
from services.background_removal_service import remove_background
from services.qdrant_service import store_embedding, delete_embedding
from dependencies.auth import CurrentUser
from repositories.wardrobe_repository import WardrobeRepository


def upload_wardrobe_item(file: UploadFile, user: CurrentUser):
    # Remove background and add white background
    processed_image = remove_background(file.file)

    # Upload processed image to Cloudinary
    image_url = upload_image(processed_image)
    tags = generate_tags(image_url)

    # Save to database
    item = WardrobeRepository.create(
        user_id=UUID(user.id),
        image_url=image_url,
        category_group=tags["categoryGroup"],
        category=tags["category"],
        attributes=tags["attributes"]
    )

    # Update the wardrobe tags tree with item ID
    WardrobeTagsService.add_item_to_tag(
        user_id=UUID(user.id),
        category_group=tags["categoryGroup"],
        category=tags["category"],
        item_id=str(item["id"])
    )

    # Store embedding in Qdrant for similarity search
    store_embedding(
        item_id=str(item["id"]),
        user_id=str(user.id),
        embedding=tags["embedding"],
        category_group=tags["categoryGroup"],
        category=tags["category"],
        attributes=tags["attributes"],
        image_url=image_url
    )

    return {
        "success": True,
        "user_id": str(user.id),
        "item": {
            "id": str(item["id"]),
            "image_url": item["image_url"],
            "categoryGroup": item["category_group"],
            "category": item["category"],
            "attributes": item["attributes"]
        }
    }

def get_user_wardrobe(user: CurrentUser):
    items = WardrobeRepository.get_by_user_id(UUID(user.id))

    # Get all saved image ids for this user (if saved_images table has image_id column)
    image_id_to_saved = {}
    try:
        from repositories.saved_image_repository import SavedImageRepository
        saved_images = SavedImageRepository.get_by_user(UUID(user.id))
        # Only process if we got results and they have image_id
        if saved_images and len(saved_images) > 0 and "image_id" in saved_images[0]:
            image_id_to_saved = {str(img["image_id"]): str(img["id"]) for img in saved_images}
    except Exception:
        # If saved_images functionality isn't available, just continue without it
        pass

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
    deleted = WardrobeRepository.delete(item_id, UUID(user.id))

    if not deleted:
        return {"success": False, "message": "Item not found or not authorized"}

    # Remove item from wardrobe tags tree
    WardrobeTagsService.remove_item(UUID(user.id), item_id)

    # Remove embedding from Qdrant
    delete_embedding(item_id)

    return {"success": True, "message": "Item deleted"}
