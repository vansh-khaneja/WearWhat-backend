from typing import List
from uuid import UUID
from db import get_connection


class SavedImageRepository:
    @staticmethod
    def save(user_id: UUID, image_url: str) -> dict:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO saved_images (user_id, image_url)
            VALUES (%s, %s)
            RETURNING id, user_id, image_url, saved_at
            """,
            (str(user_id), image_url)
        )
        item = dict(cur.fetchone())
        conn.commit()
        cur.close()
        conn.close()
        return item

    @staticmethod
    def get_by_user(user_id: UUID) -> List[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, image_url, saved_at
            FROM saved_images
            WHERE user_id = %s
            ORDER BY saved_at DESC
            """,
            (str(user_id),)
        )
        items = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return items

    @staticmethod
    def delete(saved_image_id: UUID, user_id: UUID) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM saved_images WHERE id = %s AND user_id = %s",
            (str(saved_image_id), str(user_id))
        )
        deleted = cur.rowcount > 0
        conn.commit()
        cur.close()
        conn.close()
        return deleted
