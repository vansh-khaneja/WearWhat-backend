from typing import List, Optional
from uuid import UUID
from db import get_connection

class SavedImageRepository:
    @staticmethod
    def save(user_id: UUID, image_id: UUID, note: Optional[str] = None) -> dict:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO saved_images (user_id, image_id, note)
            VALUES (%s, %s, %s)
            RETURNING id, user_id, image_id, note, saved_at
            """,
            (str(user_id), str(image_id), note)
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
            SELECT s.*, w.image_url
            FROM saved_images s
            JOIN wardrobe_items w ON s.image_id = w.id
            WHERE s.user_id = %s
            ORDER BY s.saved_at DESC
            """,
            (str(user_id),)
        )
        items = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return items

    @staticmethod
    def update_note(saved_image_id: UUID, note: str) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE saved_images SET note = %s WHERE id = %s RETURNING id, user_id, image_id, note, saved_at
            """,
            (note, str(saved_image_id))
        )
        item = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(item) if item else None

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
