from typing import List, Optional
from uuid import UUID
from db import get_connection


class PostRepository:

    @staticmethod
    def create(user_id: UUID, image_url: str, text: Optional[str] = None) -> dict:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO posts (user_id, image_url, text)
            VALUES (%s, %s, %s)
            RETURNING id, user_id, image_url, text, likes_count, comments_count, created_at, updated_at
            """,
            (str(user_id), image_url, text)
        )
        post = dict(cur.fetchone())

        conn.commit()
        cur.close()
        conn.close()
        return post

    @staticmethod
    def get_by_id(post_id: UUID) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT p.*, u.first_name, u.last_name, u.profile_image_url as user_profile_image,
                   COALESCE(
                       (SELECT array_agg(pl.user_id::text) FROM post_likes pl WHERE pl.post_id = p.id),
                       ARRAY[]::text[]
                   ) as liked_by_user_ids,
                   COALESCE(
                       (SELECT array_agg(ps.user_id::text) FROM post_saves ps WHERE ps.post_id = p.id),
                       ARRAY[]::text[]
                   ) as saved_by_user_ids
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
            """,
            (str(post_id),)
        )
        post = cur.fetchone()

        cur.close()
        conn.close()
        return dict(post) if post else None

    @staticmethod
    def get_all(limit: int = 20, offset: int = 0) -> List[dict]:
        """Get all posts for feed, ordered by most recent."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT p.*, u.first_name, u.last_name, u.profile_image_url as user_profile_image,
                   COALESCE(
                       (SELECT array_agg(pl.user_id::text) FROM post_likes pl WHERE pl.post_id = p.id),
                       ARRAY[]::text[]
                   ) as liked_by_user_ids,
                   COALESCE(
                       (SELECT array_agg(ps.user_id::text) FROM post_saves ps WHERE ps.post_id = p.id),
                       ARRAY[]::text[]
                   ) as saved_by_user_ids
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )
        posts = cur.fetchall()

        cur.close()
        conn.close()
        return [dict(p) for p in posts]

    @staticmethod
    def get_by_user_id(user_id: UUID, limit: int = 20, offset: int = 0) -> List[dict]:
        """Get posts by a specific user."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT p.*, u.first_name, u.last_name, u.profile_image_url as user_profile_image,
                   COALESCE(
                       (SELECT array_agg(pl.user_id::text) FROM post_likes pl WHERE pl.post_id = p.id),
                       ARRAY[]::text[]
                   ) as liked_by_user_ids,
                   COALESCE(
                       (SELECT array_agg(ps.user_id::text) FROM post_saves ps WHERE ps.post_id = p.id),
                       ARRAY[]::text[]
                   ) as saved_by_user_ids
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = %s
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (str(user_id), limit, offset)
        )
        posts = cur.fetchall()

        cur.close()
        conn.close()
        return [dict(p) for p in posts]

    @staticmethod
    def delete(post_id: UUID, user_id: UUID) -> bool:
        """Delete a post (only if owned by user)."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM posts
            WHERE id = %s AND user_id = %s
            RETURNING id
            """,
            (str(post_id), str(user_id))
        )
        deleted = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()
        return deleted is not None

    @staticmethod
    def like_post(post_id: UUID, user_id: UUID) -> dict:
        """Like a post. Returns success status and updated likes count."""
        conn = get_connection()
        cur = conn.cursor()

        try:
            # Insert like (will fail if already liked due to UNIQUE constraint)
            cur.execute(
                """
                INSERT INTO post_likes (post_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (post_id, user_id) DO NOTHING
                RETURNING id
                """,
                (str(post_id), str(user_id))
            )
            inserted = cur.fetchone()

            if inserted:
                # Increment likes count only if new like was added
                cur.execute(
                    """
                    UPDATE posts
                    SET likes_count = likes_count + 1, updated_at = NOW()
                    WHERE id = %s
                    RETURNING likes_count
                    """,
                    (str(post_id),)
                )
                result = cur.fetchone()
                conn.commit()
                cur.close()
                conn.close()
                return {"success": True, "liked": True, "likes_count": result["likes_count"]}
            else:
                # Already liked
                cur.close()
                conn.close()
                return {"success": True, "liked": False, "message": "Already liked"}

        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_post_likes(post_id: UUID) -> List[str]:
        """Get list of user IDs who liked a post."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT user_id FROM post_likes
            WHERE post_id = %s
            ORDER BY created_at DESC
            """,
            (str(post_id),)
        )
        likes = cur.fetchall()

        cur.close()
        conn.close()
        return [str(like["user_id"]) for like in likes]

    @staticmethod
    def is_liked_by_user(post_id: UUID, user_id: UUID) -> bool:
        """Check if a post is liked by a specific user."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 1 FROM post_likes
            WHERE post_id = %s AND user_id = %s
            """,
            (str(post_id), str(user_id))
        )
        result = cur.fetchone()

        cur.close()
        conn.close()
        return result is not None

    @staticmethod
    def save_post(post_id: UUID, user_id: UUID) -> dict:
        """Save a post. Returns success status."""
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO post_saves (post_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (post_id, user_id) DO NOTHING
                RETURNING id
                """,
                (str(post_id), str(user_id))
            )
            inserted = cur.fetchone()

            conn.commit()
            cur.close()
            conn.close()

            if inserted:
                return {"success": True, "saved": True}
            else:
                return {"success": True, "saved": False, "message": "Already saved"}

        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_saved_posts(user_id: UUID, limit: int = 20, offset: int = 0) -> List[dict]:
        """Get posts saved by a user."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT p.*, u.first_name, u.last_name, u.profile_image_url as user_profile_image,
                   COALESCE(
                       (SELECT array_agg(pl.user_id::text) FROM post_likes pl WHERE pl.post_id = p.id),
                       ARRAY[]::text[]
                   ) as liked_by_user_ids,
                   COALESCE(
                       (SELECT array_agg(ps2.user_id::text) FROM post_saves ps2 WHERE ps2.post_id = p.id),
                       ARRAY[]::text[]
                   ) as saved_by_user_ids
            FROM posts p
            JOIN users u ON p.user_id = u.id
            JOIN post_saves ps ON ps.post_id = p.id
            WHERE ps.user_id = %s
            ORDER BY ps.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (str(user_id), limit, offset)
        )
        posts = cur.fetchall()

        cur.close()
        conn.close()
        return [dict(p) for p in posts]

    @staticmethod
    def add_comment(post_id: UUID, user_id: UUID, user_name: str, text: str, user_profile_image: Optional[str] = None) -> dict:
        """Add a comment to a post."""
        conn = get_connection()
        cur = conn.cursor()

        # Insert comment
        cur.execute(
            """
            INSERT INTO post_comments (post_id, user_id, user_name, user_profile_image, text)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, post_id, user_id, user_name, user_profile_image, text, created_at
            """,
            (str(post_id), str(user_id), user_name, user_profile_image, text)
        )
        comment = dict(cur.fetchone())

        # Update comments count
        cur.execute(
            """
            UPDATE posts
            SET comments_count = comments_count + 1, updated_at = NOW()
            WHERE id = %s
            """,
            (str(post_id),)
        )

        conn.commit()
        cur.close()
        conn.close()
        return comment

    @staticmethod
    def get_comments(post_id: UUID, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get comments for a post."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, post_id, user_id, user_name, user_profile_image, text, created_at
            FROM post_comments
            WHERE post_id = %s
            ORDER BY created_at ASC
            LIMIT %s OFFSET %s
            """,
            (str(post_id), limit, offset)
        )
        comments = cur.fetchall()

        cur.close()
        conn.close()
        return [dict(c) for c in comments]

    @staticmethod
    def delete_comment(comment_id: UUID, user_id: UUID) -> bool:
        """Delete a comment (only if owned by user)."""
        conn = get_connection()
        cur = conn.cursor()

        # Get post_id before deleting
        cur.execute(
            """
            DELETE FROM post_comments
            WHERE id = %s AND user_id = %s
            RETURNING post_id
            """,
            (str(comment_id), str(user_id))
        )
        deleted = cur.fetchone()

        if deleted:
            # Decrement comments count
            cur.execute(
                """
                UPDATE posts
                SET comments_count = GREATEST(comments_count - 1, 0), updated_at = NOW()
                WHERE id = %s
                """,
                (str(deleted["post_id"]),)
            )

        conn.commit()
        cur.close()
        conn.close()
        return deleted is not None
