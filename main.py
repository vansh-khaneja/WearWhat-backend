from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import wardrobe, auth, saved_image, wardrobe_tags, recommendation
from db import init_db

# Create tables
init_db()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(wardrobe.router)
app.include_router(saved_image.router)
app.include_router(wardrobe_tags.router)
app.include_router(recommendation.router)
