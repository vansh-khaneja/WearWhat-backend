from typing import List, Optional
from uuid import UUID
from db import get_connection


class StudioRepository:
    """Repository for studio image generation records."""

    @staticmethod
    def save(user_id: UUID, item_id: UUID, original_image_url: str, studio_image_url: str, category_group: str) -> dict:
        """Save or update a studio image record. Overwrites existing record for same item."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO studio_images (user_id, item_id, original_image_url, studio_image_url, category_group, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (user_id, item_id) DO UPDATE SET
                original_image_url = EXCLUDED.original_image_url,
                studio_image_url = EXCLUDED.studio_image_url,
                category_group = EXCLUDED.category_group,
                created_at = NOW()
            RETURNING id, created_at
            """,
            (str(user_id), str(item_id), original_image_url, studio_image_url, category_group)
        )
        result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return {
            "id": str(result["id"]),
            "created_at": result["created_at"].isoformat()
        }

    @staticmethod
    def get_by_item_id(user_id: UUID, item_id: UUID) -> List[dict]:
        """Get all studio images for a wardrobe item belonging to user."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, item_id, original_image_url, studio_image_url, category_group, created_at
            FROM studio_images
            WHERE user_id = %s AND item_id = %s
            ORDER BY created_at DESC
            """,
            (str(user_id), str(item_id))
        )
        records = cur.fetchall()

        cur.close()
        conn.close()

        return [
            {
                "id": str(r["id"]),
                "item_id": str(r["item_id"]),
                "original_image_url": r["original_image_url"],
                "studio_image_url": r["studio_image_url"],
                "category_group": r["category_group"],
                "created_at": r["created_at"].isoformat()
            }
            for r in records
        ]

    @staticmethod
    def get_latest_by_item_id(user_id: UUID, item_id: UUID) -> Optional[dict]:
        """Get the latest studio image for a wardrobe item belonging to user."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, item_id, original_image_url, studio_image_url, category_group, created_at
            FROM studio_images
            WHERE user_id = %s AND item_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (str(user_id), str(item_id))
        )
        record = cur.fetchone()

        cur.close()
        conn.close()

        if not record:
            return None

        return {
            "id": str(record["id"]),
            "item_id": str(record["item_id"]),
            "original_image_url": record["original_image_url"],
            "studio_image_url": record["studio_image_url"],
            "category_group": record["category_group"],
            "created_at": record["created_at"].isoformat()
        }

    @staticmethod
    def get_all_by_user(user_id: UUID, limit: int = 20, offset: int = 0) -> List[dict]:
        """Get all studio images for a user with pagination, sorted by newest first."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, item_id, original_image_url, studio_image_url, category_group, created_at
            FROM studio_images
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (str(user_id), limit, offset)
        )
        records = cur.fetchall()

        cur.close()
        conn.close()

        return [
            {
                "id": str(r["id"]),
                "item_id": str(r["item_id"]),
                "original_image_url": r["original_image_url"],
                "studio_image_url": r["studio_image_url"],
                "category_group": r["category_group"],
                "created_at": r["created_at"].isoformat()
            }
            for r in records
        ]
