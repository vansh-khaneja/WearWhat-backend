from typing import List, Optional
from uuid import UUID
import json
from db import get_connection

class WardrobeRepository:

    @staticmethod
    def create(user_id: UUID, image_url: str, category_group: str, category: str, attributes: dict) -> dict:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO wardrobe_items (user_id, image_url, category_group, category, attributes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, user_id, image_url, category_group, category, attributes, created_at
            """,
            (str(user_id), image_url, category_group, category, json.dumps(attributes))
        )
        item = dict(cur.fetchone())

        conn.commit()
        cur.close()
        conn.close()
        return item

    @staticmethod
    def get_by_id(item_id: UUID) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM wardrobe_items WHERE id = %s",
            (str(item_id),)
        )
        item = cur.fetchone()

        cur.close()
        conn.close()
        return dict(item) if item else None

    @staticmethod
    def get_by_user_id(user_id: UUID) -> List[dict]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM wardrobe_items WHERE user_id = %s ORDER BY created_at DESC",
            (str(user_id),)
        )
        items = cur.fetchall()

        cur.close()
        conn.close()
        return [dict(item) for item in items]

    @staticmethod
    def delete(item_id: UUID, user_id: UUID) -> bool:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM wardrobe_items WHERE id = %s AND user_id = %s RETURNING id",
            (str(item_id), str(user_id))
        )
        deleted = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()
        return deleted is not None
