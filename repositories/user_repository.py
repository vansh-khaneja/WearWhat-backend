from typing import Optional
from uuid import UUID
from db import get_connection

class UserRepository:

    @staticmethod
    def create(email: str, first_name: str, last_name: str, password_hash: str) -> dict:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO users (email, first_name, last_name)
            VALUES (%s, %s, %s)
            RETURNING id, email, first_name, last_name, created_at
            """,
            (email, first_name, last_name)
        )
        user = dict(cur.fetchone())

        cur.execute(
            """
            INSERT INTO user_passwords (user_id, password_hash)
            VALUES (%s, %s)
            """,
            (user["id"], password_hash)
        )

        conn.commit()
        cur.close()
        conn.close()
        return user

    @staticmethod
    def create_clerk_user(user_id: UUID, email: str, first_name: str, last_name: str, profile_image_url: str = None) -> dict:
        """Create a user from Clerk (no password needed). Uses UPSERT to handle existing users."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (id, email, first_name, last_name, profile_image_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                email = COALESCE(NULLIF(EXCLUDED.email, ''), users.email),
                first_name = COALESCE(NULLIF(EXCLUDED.first_name, ''), users.first_name),
                last_name = COALESCE(NULLIF(EXCLUDED.last_name, ''), users.last_name),
                profile_image_url = COALESCE(NULLIF(EXCLUDED.profile_image_url, ''), users.profile_image_url)
            RETURNING id, email, first_name, last_name, profile_image_url, created_at
            """,
            (str(user_id), email, first_name, last_name, profile_image_url or '')
        )
        user = dict(cur.fetchone())
        conn.commit()
        cur.close()
        conn.close()
        return user

    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, first_name, last_name, created_at FROM users WHERE email = %s",
            (email,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def get_by_id(user_id: UUID) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, first_name, last_name, profile_image_url, created_at FROM users WHERE id = %s",
            (str(user_id),)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def get_with_password(email: str) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT u.id, u.email, u.first_name, u.last_name, u.created_at, up.password_hash
            FROM users u
            JOIN user_passwords up ON u.id = up.user_id
            WHERE u.email = %s
            """,
            (email,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        return dict(result) if result else None

    @staticmethod
    def get_full_info(user_id: UUID) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, email, first_name, last_name, profile_image_url, created_at, updated_at
            FROM users WHERE id = %s
            """,
            (str(user_id),)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def update(user_id: UUID, first_name: str = None, last_name: str = None, profile_image_url: str = None) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()

        # Build dynamic update query
        updates = []
        values = []

        if first_name is not None:
            updates.append("first_name = %s")
            values.append(first_name)
        if last_name is not None:
            updates.append("last_name = %s")
            values.append(last_name)
        if profile_image_url is not None:
            updates.append("profile_image_url = %s")
            values.append(profile_image_url)

        if not updates:
            cur.close()
            conn.close()
            return UserRepository.get_full_info(user_id)

        updates.append("updated_at = NOW()")
        values.append(str(user_id))

        query = f"""
            UPDATE users SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, email, first_name, last_name, profile_image_url, created_at, updated_at
        """

        cur.execute(query, values)
        user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(user) if user else None
