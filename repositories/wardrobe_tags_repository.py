from typing import Optional, Dict, List
from uuid import UUID
from db import get_connection
import json

# Structure: tags_by_category = {
#   "topwear": {
#       "t-shirt": ["item-id-1", "item-id-2"],
#       "formal-shirt": ["item-id-3"]
#   },
#   "bottomwear": {
#       "jeans": ["item-id-4"]
#   }
# }

class WardrobeTagsRepository:
    @staticmethod
    def get_by_user(user_id: UUID) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, tags_by_category, created_at, updated_at
            FROM wardrobe_tags
            WHERE user_id = %s
            """,
            (str(user_id),)
        )
        item = cur.fetchone()
        cur.close()
        conn.close()
        return dict(item) if item else None

    @staticmethod
    def create(user_id: UUID, tags_by_category: Dict = None) -> dict:
        if tags_by_category is None:
            tags_by_category = {}
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO wardrobe_tags (user_id, tags_by_category)
            VALUES (%s, %s)
            RETURNING id, user_id, tags_by_category, created_at, updated_at
            """,
            (str(user_id), json.dumps(tags_by_category))
        )
        item = dict(cur.fetchone())
        conn.commit()
        cur.close()
        conn.close()
        return item

    @staticmethod
    def update(user_id: UUID, tags_by_category: Dict) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE wardrobe_tags
            SET tags_by_category = %s, updated_at = NOW()
            WHERE user_id = %s
            RETURNING id, user_id, tags_by_category, created_at, updated_at
            """,
            (json.dumps(tags_by_category), str(user_id))
        )
        item = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(item) if item else None

    @staticmethod
    def add_item_to_tag(user_id: UUID, category_group: str, category: str, item_id: str) -> dict:
        """Add an item ID to a tag. Creates the record/category/tag if they don't exist."""
        existing = WardrobeTagsRepository.get_by_user(user_id)

        if existing is None:
            # Create new record
            tags_by_category = {category_group: {category: [item_id]}}
            return WardrobeTagsRepository.create(user_id, tags_by_category)

        tags_by_category = existing['tags_by_category'] or {}

        # Ensure category_group exists
        if category_group not in tags_by_category:
            tags_by_category[category_group] = {}

        # Ensure category exists under category_group
        if category not in tags_by_category[category_group]:
            tags_by_category[category_group][category] = []

        # Add item_id if not already present
        if item_id not in tags_by_category[category_group][category]:
            tags_by_category[category_group][category].append(item_id)
            return WardrobeTagsRepository.update(user_id, tags_by_category)

        return existing

    @staticmethod
    def remove_item_from_tag(user_id: UUID, category_group: str, category: str, item_id: str) -> Optional[dict]:
        """Remove an item ID from a tag. Cleans up empty categories/groups."""
        existing = WardrobeTagsRepository.get_by_user(user_id)

        if existing is None:
            return None

        tags_by_category = existing['tags_by_category'] or {}

        # Check if path exists
        if category_group not in tags_by_category:
            return existing
        if category not in tags_by_category[category_group]:
            return existing

        # Remove item_id if present
        if item_id in tags_by_category[category_group][category]:
            tags_by_category[category_group][category].remove(item_id)

            # If category is now empty, remove it
            if not tags_by_category[category_group][category]:
                del tags_by_category[category_group][category]

                # If category_group is now empty, remove it
                if not tags_by_category[category_group]:
                    del tags_by_category[category_group]

            return WardrobeTagsRepository.update(user_id, tags_by_category)

        return existing

    @staticmethod
    def remove_item_from_all(user_id: UUID, item_id: str) -> Optional[dict]:
        """Remove an item ID from all tags. Used when deleting a wardrobe item."""
        existing = WardrobeTagsRepository.get_by_user(user_id)

        if existing is None:
            return None

        tags_by_category = existing['tags_by_category'] or {}
        modified = False

        # Iterate through all category_groups and categories
        groups_to_delete = []
        for category_group in tags_by_category:
            categories_to_delete = []
            for category in tags_by_category[category_group]:
                if item_id in tags_by_category[category_group][category]:
                    tags_by_category[category_group][category].remove(item_id)
                    modified = True

                    # Mark empty category for deletion
                    if not tags_by_category[category_group][category]:
                        categories_to_delete.append(category)

            # Delete empty categories
            for category in categories_to_delete:
                del tags_by_category[category_group][category]

            # Mark empty category_group for deletion
            if not tags_by_category[category_group]:
                groups_to_delete.append(category_group)

        # Delete empty category_groups
        for group in groups_to_delete:
            del tags_by_category[group]

        if modified:
            return WardrobeTagsRepository.update(user_id, tags_by_category)

        return existing

    @staticmethod
    def delete(user_id: UUID) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM wardrobe_tags WHERE user_id = %s",
            (str(user_id),)
        )
        deleted = cur.rowcount > 0
        conn.commit()
        cur.close()
        conn.close()
        return deleted
