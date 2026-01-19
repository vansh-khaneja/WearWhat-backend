from openai import OpenAI
from typing import List, Optional
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a friendly and knowledgeable fashion stylist assistant for WearWhat, a wardrobe management app.

Your expertise includes:
- Outfit recommendations and styling tips
- Color coordination and pattern matching
- Seasonal fashion advice
- Occasion-appropriate dressing (casual, formal, party, work, etc.)
- Wardrobe organization and capsule wardrobe building
- Fashion trends and timeless style advice
- Body type styling suggestions
- Accessorizing tips

Guidelines:
- Be friendly, helpful, and encouraging
- Give practical, actionable advice
- Consider the user's personal style preferences
- Suggest outfit combinations when relevant
- Keep responses concise but informative
- If asked about non-fashion topics, politely redirect to fashion-related help

Remember: You're here to help users look and feel their best!"""


def chat(
    message: str,
    conversation_history: Optional[List[dict]] = None,
    user_context: Optional[dict] = None
) -> str:
    """
    Send a message to the fashion assistant and get a response.

    Args:
        message: User's message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        user_context: Optional context about user's wardrobe

    Returns:
        Assistant's response
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add user context if provided
    if user_context:
        context_msg = f"\n\nUser's wardrobe context:\n"
        if user_context.get("wardrobe_summary"):
            context_msg += f"- Wardrobe: {user_context['wardrobe_summary']}\n"
        if user_context.get("preferences"):
            context_msg += f"- Preferences: {user_context['preferences']}\n"
        messages[0]["content"] += context_msg

    # Add conversation history
    if conversation_history:
        messages.extend(conversation_history)

    # Add current message
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )

    return response.choices[0].message.content


def get_outfit_suggestion(
    occasion: str,
    weather: Optional[str] = None,
    style_preference: Optional[str] = None,
    available_items: Optional[List[dict]] = None
) -> str:
    """
    Get outfit suggestion for a specific occasion.

    Args:
        occasion: The occasion (e.g., "casual date", "job interview", "beach party")
        weather: Current weather conditions
        style_preference: User's style preference
        available_items: List of items from user's wardrobe

    Returns:
        Outfit suggestion
    """
    prompt = f"Suggest an outfit for: {occasion}"

    if weather:
        prompt += f"\nWeather: {weather}"

    if style_preference:
        prompt += f"\nStyle preference: {style_preference}"

    if available_items:
        items_str = ", ".join([
            f"{item.get('category', 'item')} ({item.get('color', 'unknown color')})"
            for item in available_items[:10]  # Limit to 10 items
        ])
        prompt += f"\nAvailable items: {items_str}"

    return chat(prompt)
