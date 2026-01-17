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
            "SELECT id, email, first_name, last_name, created_at FROM users WHERE id = %s",
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
