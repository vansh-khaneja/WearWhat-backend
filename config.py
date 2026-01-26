import os
from dotenv import load_dotenv

load_dotenv()

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/wearwhat")

# JWT (Legacy - kept for backward compatibility)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Clerk Authentication
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "https://literate-wahoo-99.clerk.accounts.dev")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Qdrant Cloud
QDRANT_URL = os.getenv("QDRANT_URL")  # e.g., https://xxx.cloud.qdrant.io
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# OpenWeatherMap
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
