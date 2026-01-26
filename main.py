from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import wardrobe, auth, wardrobe_tags, recommendation, calendar_outfit, chat, post, studio
from db import init_db
from services.qdrant_service import init_collection

# Create tables
init_db()

# Initialize Qdrant collection
init_collection()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://wearwhat.vanshkhaneja.com",
        "https://wearwhat.yashverma.site",
    ],
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(wardrobe.router)
app.include_router(wardrobe_tags.router)
app.include_router(recommendation.router)
app.include_router(calendar_outfit.router)
app.include_router(chat.router)
app.include_router(post.router)
app.include_router(studio.router)
