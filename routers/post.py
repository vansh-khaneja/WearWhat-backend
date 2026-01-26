from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from repositories.post_repository import PostRepository
from dependencies.auth import get_current_user, CurrentUser

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


class CreatePostRequest(BaseModel):
    image_url: str
    text: Optional[str] = None


class AddCommentRequest(BaseModel):
    text: str


@router.post("/")
def create_post(request: CreatePostRequest, user: CurrentUser = Depends(get_current_user)):
    """Create a new post."""
    post = PostRepository.create(
        user_id=UUID(user.id),
        image_url=request.image_url,
        text=request.text
    )

    return {
        "success": True,
        "post": {
            "id": str(post["id"]),
            "user_id": str(post["user_id"]),
            "user_name": f"{user.first_name} {user.last_name}",
            "user_profile_image": user.profile_image_url,
            "image_url": post["image_url"],
            "text": post["text"],
            "likes_count": post["likes_count"],
            "comments_count": post["comments_count"],
            "created_at": post["created_at"].isoformat()
        }
    }


@router.get("/")
def get_feed(
    limit: int = 20,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user)
):
    """Get posts feed (all posts, most recent first)."""
    posts = PostRepository.get_all(limit=limit, offset=offset)

    return {
        "success": True,
        "count": len(posts),
        "posts": [
            {
                "id": str(p["id"]),
                "user_id": str(p["user_id"]),
                "user_name": f"{p['first_name']} {p['last_name']}",
                "user_profile_image": p["user_profile_image"],
                "image_url": p["image_url"],
                "text": p["text"],
                "likes_count": p["likes_count"],
                "comments_count": p["comments_count"],
                "liked_by_user_ids": p.get("liked_by_user_ids", []),
                "is_liked": user.id in (p.get("liked_by_user_ids") or []),
                "saved_by_user_ids": p.get("saved_by_user_ids", []),
                "is_saved": user.id in (p.get("saved_by_user_ids") or []),
                "created_at": p["created_at"].isoformat()
            }
            for p in posts
        ]
    }


@router.get("/me")
def get_my_posts(
    limit: int = 20,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user)
):
    """Get current user's posts."""
    posts = PostRepository.get_by_user_id(UUID(user.id), limit=limit, offset=offset)

    return {
        "success": True,
        "count": len(posts),
        "posts": [
            {
                "id": str(p["id"]),
                "user_id": str(p["user_id"]),
                "user_name": f"{p['first_name']} {p['last_name']}",
                "user_profile_image": p["user_profile_image"],
                "image_url": p["image_url"],
                "text": p["text"],
                "likes_count": p["likes_count"],
                "comments_count": p["comments_count"],
                "liked_by_user_ids": p.get("liked_by_user_ids", []),
                "is_liked": user.id in (p.get("liked_by_user_ids") or []),
                "saved_by_user_ids": p.get("saved_by_user_ids", []),
                "is_saved": user.id in (p.get("saved_by_user_ids") or []),
                "created_at": p["created_at"].isoformat()
            }
            for p in posts
        ]
    }


@router.get("/saved")
def get_saved_posts(
    limit: int = 20,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user)
):
    """Get posts saved by current user."""
    posts = PostRepository.get_saved_posts(UUID(user.id), limit=limit, offset=offset)

    return {
        "success": True,
        "count": len(posts),
        "posts": [
            {
                "id": str(p["id"]),
                "user_id": str(p["user_id"]),
                "user_name": f"{p['first_name']} {p['last_name']}",
                "user_profile_image": p["user_profile_image"],
                "image_url": p["image_url"],
                "text": p["text"],
                "likes_count": p["likes_count"],
                "comments_count": p["comments_count"],
                "liked_by_user_ids": p.get("liked_by_user_ids", []),
                "is_liked": user.id in (p.get("liked_by_user_ids") or []),
                "saved_by_user_ids": p.get("saved_by_user_ids", []),
                "is_saved": True,
                "created_at": p["created_at"].isoformat()
            }
            for p in posts
        ]
    }


@router.delete("/{post_id}")
def delete_post(post_id: str, user: CurrentUser = Depends(get_current_user)):
    """Delete a post (only own posts)."""
    deleted = PostRepository.delete(post_id, UUID(user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found or not authorized")

    return {"success": True, "message": "Post deleted"}


@router.post("/{post_id}/like")
def like_post(post_id: str, user: CurrentUser = Depends(get_current_user)):
    """Like a post. User can only like once."""
    result = PostRepository.like_post(UUID(post_id), UUID(user.id))
    return result


@router.post("/{post_id}/save")
def save_post(post_id: str, user: CurrentUser = Depends(get_current_user)):
    """Save a post. User can only save once."""
    result = PostRepository.save_post(UUID(post_id), UUID(user.id))
    return result


@router.get("/{post_id}/comments")
def get_comments(
    post_id: str,
    limit: int = 50,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user)
):
    """Get comments for a post."""
    comments = PostRepository.get_comments(post_id, limit=limit, offset=offset)

    return {
        "success": True,
        "count": len(comments),
        "comments": [
            {
                "id": str(c["id"]),
                "user_id": str(c["user_id"]),
                "user_name": c["user_name"],
                "user_profile_image": c["user_profile_image"],
                "text": c["text"],
                "created_at": c["created_at"].isoformat()
            }
            for c in comments
        ]
    }


@router.post("/{post_id}/comments")
def add_comment(
    post_id: str,
    request: AddCommentRequest,
    user: CurrentUser = Depends(get_current_user)
):
    """Add a comment to a post."""
    user_name = f"{user.first_name} {user.last_name}"
    comment = PostRepository.add_comment(
        post_id=post_id,
        user_id=UUID(user.id),
        user_name=user_name,
        text=request.text,
        user_profile_image=user.profile_image_url
    )

    return {
        "success": True,
        "comment": {
            "id": str(comment["id"]),
            "user_id": str(comment["user_id"]),
            "user_name": comment["user_name"],
            "user_profile_image": comment["user_profile_image"],
            "text": comment["text"],
            "created_at": comment["created_at"].isoformat()
        }
    }


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: str, user: CurrentUser = Depends(get_current_user)):
    """Delete a comment (only own comments)."""
    deleted = PostRepository.delete_comment(comment_id, UUID(user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")

    return {"success": True, "message": "Comment deleted"}
