from typing import Optional, List
from uuid import UUID
from datetime import date, timedelta
from db import get_connection
import json

class CalendarOutfitRepository:
    @staticmethod
    def save(
        user_id: UUID,
        outfit_date: date,
        combined_image_url: str,
        prompt: Optional[str],
        temperature: Optional[float],
        selected_categories: List[str],
        items: List[dict]
    ) -> dict:
        """
        Save an outfit for a specific date.
        - Uses UPSERT to replace if outfit already exists for that date
        - Automatically removes outfits older than 5 days from the outfit_date
        """
        conn = get_connection()
        cur = conn.cursor()

        # First, delete outfits older than 5 days from the new outfit_date
        cutoff_date = outfit_date - timedelta(days=5)
        cur.execute(
            "DELETE FROM calendar_outfits WHERE user_id = %s AND outfit_date < %s",
            (str(user_id), cutoff_date)
        )

        # Upsert the outfit (insert or update if date exists)
        cur.execute(
            """
            INSERT INTO calendar_outfits
                (user_id, outfit_date, combined_image_url, prompt, temperature, selected_categories, items)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, outfit_date)
            DO UPDATE SET
                combined_image_url = EXCLUDED.combined_image_url,
                prompt = EXCLUDED.prompt,
                temperature = EXCLUDED.temperature,
                selected_categories = EXCLUDED.selected_categories,
                items = EXCLUDED.items,
                created_at = NOW()
            RETURNING id, user_id, outfit_date, combined_image_url, prompt, temperature, selected_categories, items, created_at
            """,
            (
                str(user_id),
                outfit_date,
                combined_image_url,
                prompt,
                temperature,
                json.dumps(selected_categories),
                json.dumps(items)
            )
        )
        item = dict(cur.fetchone())
        conn.commit()
        cur.close()
        conn.close()
        return item

    @staticmethod
    def get_by_user(user_id: UUID) -> List[dict]:
        """Get all calendar outfits for a user (should be max 5)."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, outfit_date, combined_image_url, prompt, temperature, selected_categories, items, created_at
            FROM calendar_outfits
            WHERE user_id = %s
            ORDER BY outfit_date ASC
            """,
            (str(user_id),)
        )
        items = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return items

    @staticmethod
    def get_by_date(user_id: UUID, outfit_date: date) -> Optional[dict]:
        """Get outfit for a specific date."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, outfit_date, combined_image_url, prompt, temperature, selected_categories, items, created_at
            FROM calendar_outfits
            WHERE user_id = %s AND outfit_date = %s
            """,
            (str(user_id), outfit_date)
        )
        item = cur.fetchone()
        cur.close()
        conn.close()
        return dict(item) if item else None

    @staticmethod
    def delete(user_id: UUID, outfit_date: date) -> bool:
        """Delete outfit for a specific date."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM calendar_outfits WHERE user_id = %s AND outfit_date = %s",
            (str(user_id), outfit_date)
        )
        deleted = cur.rowcount > 0
        conn.commit()
        cur.close()
        conn.close()
        return deleted

    @staticmethod
    def cleanup_old_outfits(user_id: UUID, reference_date: date) -> int:
        """Remove outfits older than 5 days from reference_date. Returns count deleted."""
        conn = get_connection()
        cur = conn.cursor()
        cutoff_date = reference_date - timedelta(days=5)
        cur.execute(
            "DELETE FROM calendar_outfits WHERE user_id = %s AND outfit_date < %s",
            (str(user_id), cutoff_date)
        )
        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        return deleted_count
