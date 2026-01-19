from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from services.chat_service import chat
from dependencies.auth import get_current_user, CurrentUser

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class SendMessageRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


@router.post("/send")
def send_message(request: SendMessageRequest, user: CurrentUser = Depends(get_current_user)):
    """
    Send a message to the fashion assistant.
    Pass conversation history from frontend for context.
    No server-side storage - real-time only.
    """
    # Convert history to format expected by chat service
    conversation_history = None
    if request.history:
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]

    # Get AI response
    response = chat(
        message=request.message,
        conversation_history=conversation_history
    )

    return {
        "success": True,
        "response": response
    }
