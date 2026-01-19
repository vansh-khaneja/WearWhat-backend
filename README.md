# WearWhat Backend API

A FastAPI-based backend for wardrobe management with image upload, auto-tagging, outfit recommendations, and social features.

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/wearwhat

# JWT
JWT_SECRET_KEY=your-secure-secret-key

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# OpenAI
OPENAI_API_KEY=your_openai_api_key
```

### Run the Server

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

---

## API Endpoints

### Authentication

All auth endpoints set/clear an `access_token` HTTP-only cookie for authentication.

#### POST `/auth/signup`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "User created successfully",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Errors:**
- `400` - Email already registered

---

#### POST `/auth/login`

Authenticate and get a new token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Errors:**
- `401` - Invalid email or password

---

#### POST `/auth/logout`

Clear the authentication cookie.

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### Wardrobe

All wardrobe endpoints require authentication (JWT cookie).

#### POST `/wardrobe/upload`

Upload one or more clothing images. Images are uploaded to Cloudinary and auto-tagged using CLIP.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `files` - One or more image files

**Response (200):**
```json
{
  "success": true,
  "count": 2,
  "user_id": "uuid-string",
  "items": [
    {
      "id": "uuid-string",
      "image_url": "https://res.cloudinary.com/...",
      "categoryGroup": "upperWear",
      "category": "Jacket",
      "attributes": {
        "color": "Black",
        "season": "Winter",
        "material": "Leather",
        "pattern": "Solid",
        "occasion": "Casual",
        "neckline": "Stand Collar",
        "sleeveLength": "Long Sleeve",
        "topLength": "Hip"
      }
    }
  ]
}
```

**Errors:**
- `401` - Not authenticated

---

#### GET `/wardrobe/`

Get all wardrobe items for the authenticated user.

**Query Parameters:** None

**Response (200):**
```json
{
  "success": true,
  "count": 5,
  "items": [
    {
      "id": "uuid-string",
      "image_url": "https://res.cloudinary.com/...",
      "categoryGroup": "upperWear",
      "category": "T-Shirt",
      "attributes": {
        "color": "White",
        "season": "Summer",
        "material": "Cotton",
        "pattern": "Solid",
        "occasion": "Casual",
        "neckline": "Round",
        "sleeveLength": "Short Sleeve",
        "topLength": "Waist"
      },
      "created_at": "2024-01-15T10:30:00+00:00"
    }
  ]
}
```

**Errors:**
- `401` - Not authenticated

---

#### DELETE `/wardrobe/{item_id}`

Delete a wardrobe item.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_id | string (UUID) | Yes | ID of the item to delete |

**Response (200):**
```json
{
  "success": true,
  "message": "Item deleted"
}
```

**Response (200 - Not found):**
```json
{
  "success": false,
  "message": "Item not found or not authorized"
}
```

---

### Saved Images

Save/bookmark wardrobe items for later reference.

#### POST `/saved-images/save`

Save a wardrobe item.

**Request Body:**
```json
{
  "image_id": "uuid-string",
  "note": "Love this for summer!"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| image_id | UUID | Yes | ID of the wardrobe item to save |
| note | string | No | Optional note about the saved item |

**Response (200):**
```json
{
  "id": "uuid-string",
  "user_id": "uuid-string",
  "image_id": "uuid-string",
  "note": "Love this for summer!",
  "saved_at": "2024-01-15T10:30:00+00:00"
}
```

---

#### GET `/saved-images`

Get all saved images for the authenticated user.

**Query Parameters:** None

**Response (200):**
```json
[
  {
    "id": "uuid-string",
    "user_id": "uuid-string",
    "image_id": "uuid-string",
    "note": "Love this for summer!",
    "saved_at": "2024-01-15T10:30:00+00:00"
  }
]
```

---

#### PUT `/saved-images/note`

Update the note on a saved image.

**Request Body:**
```json
{
  "saved_image_id": "uuid-string",
  "note": "Updated note text"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| saved_image_id | UUID | Yes | ID of the saved image record |
| note | string | Yes | New note text |

**Response (200):**
```json
{
  "id": "uuid-string",
  "user_id": "uuid-string",
  "image_id": "uuid-string",
  "note": "Updated note text",
  "saved_at": "2024-01-15T10:30:00+00:00"
}
```

**Response (Error):**
```json
{
  "error": "Saved image not found or unauthorized"
}
```

---

#### DELETE `/saved-images/{saved_image_id}`

Delete a saved image.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| saved_image_id | UUID | Yes | ID of the saved image record |

**Response (200):**
```json
{
  "success": true
}
```

**Response (Error):**
```json
{
  "error": "Saved image not found or unauthorized"
}
```

---

### Wardrobe Tags

Get the user's wardrobe organized by categories.

#### GET `/wardrobe-tags`

Get all tags/categories with their item IDs.

**Query Parameters:** None

**Response (200):**
```json
{
  "tags_by_category": {
    "upperWear": {
      "T-Shirt": ["item-uuid-1", "item-uuid-2"],
      "Jacket": ["item-uuid-3"]
    },
    "bottomWear": {
      "Jeans": ["item-uuid-4", "item-uuid-5"]
    },
    "footwear": {
      "Sneakers": ["item-uuid-6"]
    }
  }
}
```

---

### Recommendation

Get AI-powered outfit recommendations.

#### POST `/recommendation`

Get outfit recommendation based on a prompt.

**Request Body:**
```json
{
  "prompt": "Casual outfit for a coffee date"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | Yes | Description of the occasion/style wanted |

**Response (200):**
```json
{
  "success": true,
  "prompt": "Casual outfit for a coffee date",
  "reasoning": "For a casual coffee date, I selected a comfortable yet stylish combination...",
  "selected_categories": ["T-Shirt", "Jeans", "Sneakers"],
  "combined_image_url": "https://res.cloudinary.com/...",
  "items": [
    {
      "id": "uuid-string",
      "image_url": "https://res.cloudinary.com/...",
      "categoryGroup": "upperWear",
      "category": "T-Shirt",
      "attributes": {
        "color": "White",
        "material": "Cotton"
      }
    },
    {
      "id": "uuid-string",
      "image_url": "https://res.cloudinary.com/...",
      "categoryGroup": "bottomWear",
      "category": "Jeans",
      "attributes": {
        "color": "Blue",
        "fit": "Slim"
      }
    }
  ]
}
```

**Response (No items):**
```json
{
  "success": false,
  "message": "No items in wardrobe yet",
  "items": []
}
```

---

### Calendar Outfits

Save and manage outfit plans by date.

#### POST `/calendar-outfits`

Save an outfit for a specific date.

**Request Body:**
```json
{
  "outfit_date": "2024-01-20",
  "combined_image_url": "https://res.cloudinary.com/...",
  "prompt": "Business casual for Monday meeting",
  "temperature": 15.5,
  "selected_categories": ["Shirt", "Chinos", "Loafers"],
  "items": [
    {
      "id": "uuid-string",
      "image_url": "https://...",
      "category": "Shirt"
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| outfit_date | date (YYYY-MM-DD) | Yes | Date for the outfit |
| combined_image_url | string | Yes | URL of the combined outfit image |
| prompt | string | No | Original prompt used |
| temperature | float | No | Weather temperature |
| selected_categories | array | No | List of selected categories |
| items | array | No | List of item objects |

**Response (200):**
```json
{
  "success": true,
  "outfit": {
    "id": "uuid-string",
    "user_id": "uuid-string",
    "outfit_date": "2024-01-20",
    "combined_image_url": "https://res.cloudinary.com/...",
    "prompt": "Business casual for Monday meeting",
    "temperature": 15.5,
    "selected_categories": ["Shirt", "Chinos", "Loafers"],
    "items": [...],
    "created_at": "2024-01-15T10:30:00+00:00"
  }
}
```

---

#### GET `/calendar-outfits`

Get all saved outfits for the user.

**Query Parameters:** None

**Response (200):**
```json
{
  "success": true,
  "count": 3,
  "outfits": [
    {
      "id": "uuid-string",
      "user_id": "uuid-string",
      "outfit_date": "2024-01-20",
      "combined_image_url": "https://res.cloudinary.com/...",
      "prompt": "Business casual",
      "temperature": 15.5,
      "selected_categories": ["Shirt", "Chinos"],
      "items": [...],
      "created_at": "2024-01-15T10:30:00+00:00"
    }
  ]
}
```

---

#### GET `/calendar-outfits/{outfit_date}`

Get outfit for a specific date.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| outfit_date | date (YYYY-MM-DD) | Yes | Date to look up |

**Response (200):**
```json
{
  "success": true,
  "outfit": {
    "id": "uuid-string",
    "user_id": "uuid-string",
    "outfit_date": "2024-01-20",
    "combined_image_url": "https://res.cloudinary.com/...",
    "prompt": "Business casual",
    "temperature": 15.5,
    "selected_categories": ["Shirt", "Chinos"],
    "items": [...],
    "created_at": "2024-01-15T10:30:00+00:00"
  }
}
```

**Response (Not found):**
```json
{
  "success": false,
  "message": "No outfit found for this date"
}
```

---

#### DELETE `/calendar-outfits/{outfit_date}`

Delete outfit for a specific date.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| outfit_date | date (YYYY-MM-DD) | Yes | Date to delete |

**Response (200):**
```json
{
  "success": true,
  "message": "Outfit deleted"
}
```

**Response (Not found):**
```json
{
  "success": false,
  "message": "No outfit found for this date"
}
```

---

### Chat

Real-time fashion assistant chat (no message storage).

#### POST `/chat/send`

Send a message to the fashion assistant.

**Request Body:**
```json
{
  "message": "What should I wear for a job interview?",
  "history": [
    {
      "role": "user",
      "content": "Hi there"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help with your fashion needs today?"
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's message |
| history | array | No | Previous conversation messages |

**History Object:**
| Field | Type | Description |
|-------|------|-------------|
| role | string | "user" or "assistant" |
| content | string | Message content |

**Response (200):**
```json
{
  "success": true,
  "response": "For a job interview, I recommend dressing professionally..."
}
```

---

### Posts

Social feed with posts, likes, and comments.

#### POST `/posts/`

Create a new post.

**Request Body:**
```json
{
  "image_url": "https://res.cloudinary.com/...",
  "text": "My outfit for today!"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| image_url | string | Yes | URL of the post image |
| text | string | No | Post caption/text |

**Response (200):**
```json
{
  "success": true,
  "post": {
    "id": "uuid-string",
    "user_id": "uuid-string",
    "user_name": "John Doe",
    "image_url": "https://res.cloudinary.com/...",
    "text": "My outfit for today!",
    "likes_count": 0,
    "comments_count": 0,
    "created_at": "2024-01-15T10:30:00+00:00"
  }
}
```

---

#### GET `/posts/`

Get posts feed (all posts, most recent first).

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | int | 20 | Number of posts to return |
| offset | int | 0 | Number of posts to skip |

**Response (200):**
```json
{
  "success": true,
  "count": 10,
  "posts": [
    {
      "id": "uuid-string",
      "user_id": "uuid-string",
      "user_name": "John Doe",
      "image_url": "https://res.cloudinary.com/...",
      "text": "My outfit for today!",
      "likes_count": 5,
      "comments_count": 2,
      "created_at": "2024-01-15T10:30:00+00:00"
    }
  ]
}
```

---

#### GET `/posts/me`

Get current user's posts.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | int | 20 | Number of posts to return |
| offset | int | 0 | Number of posts to skip |

**Response (200):**
```json
{
  "success": true,
  "count": 3,
  "posts": [
    {
      "id": "uuid-string",
      "user_id": "uuid-string",
      "user_name": "John Doe",
      "image_url": "https://res.cloudinary.com/...",
      "text": "My outfit for today!",
      "likes_count": 5,
      "comments_count": 2,
      "created_at": "2024-01-15T10:30:00+00:00"
    }
  ]
}
```

---

#### DELETE `/posts/{post_id}`

Delete a post (only own posts).

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| post_id | string (UUID) | Yes | ID of the post to delete |

**Response (200):**
```json
{
  "success": true,
  "message": "Post deleted"
}
```

**Errors:**
- `404` - Post not found or not authorized

---

#### POST `/posts/{post_id}/like`

Like a post (increments likes count).

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| post_id | string (UUID) | Yes | ID of the post to like |

**Response (200):**
```json
{
  "success": true,
  "likes_count": 6
}
```

**Errors:**
- `404` - Post not found

---

#### GET `/posts/{post_id}/comments`

Get comments for a post.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| post_id | string (UUID) | Yes | ID of the post |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | int | 50 | Number of comments to return |
| offset | int | 0 | Number of comments to skip |

**Response (200):**
```json
{
  "success": true,
  "count": 2,
  "comments": [
    {
      "id": "uuid-string",
      "user_id": "uuid-string",
      "user_name": "Jane Smith",
      "text": "Love this outfit!",
      "created_at": "2024-01-15T11:00:00+00:00"
    }
  ]
}
```

---

#### POST `/posts/{post_id}/comments`

Add a comment to a post.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| post_id | string (UUID) | Yes | ID of the post |

**Request Body:**
```json
{
  "text": "Love this outfit!"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | Comment text |

**Response (200):**
```json
{
  "success": true,
  "comment": {
    "id": "uuid-string",
    "user_id": "uuid-string",
    "user_name": "Jane Smith",
    "text": "Love this outfit!",
    "created_at": "2024-01-15T11:00:00+00:00"
  }
}
```

---

#### DELETE `/posts/comments/{comment_id}`

Delete a comment (only own comments).

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| comment_id | string (UUID) | Yes | ID of the comment to delete |

**Response (200):**
```json
{
  "success": true,
  "message": "Comment deleted"
}
```

**Errors:**
- `404` - Comment not found or not authorized

---

## Data Models

### Category Groups

| Group | Categories |
|-------|------------|
| `upperWear` | T-Shirt, Shirt, Blouse, Sweater, Hoodie, Cardigan, Tank Top, Crop Top, Polo, Tunic, etc. |
| `bottomWear` | Jeans, Trousers, Shorts, Skirt, Leggings, Joggers, Chinos, Culottes, etc. |
| `outerWear` | Jacket, Coat, Blazer, Vest, Parka, Windbreaker, Puffer, Trench Coat, etc. |
| `footwear` | Sneakers, Boots, Sandals, Loafers, Heels, Flats, Oxfords, etc. |
| `otherItems` | Hat, Bag, Scarf, Belt, Watch, Sunglasses, Jewelry, etc. |

### Attributes

**Generic (all items):**
- `color` - Red, Blue, Black, White, etc.
- `season` - Spring, Summer, Fall, Winter, All Season
- `material` - Cotton, Denim, Leather, Wool, Silk, etc.
- `pattern` - Solid, Striped, Plaid, Floral, etc.
- `occasion` - Casual, Formal, Sports, Party, etc.

**Upper Wear Specific:**
- `neckline` - Round, V-Neck, Turtleneck, etc.
- `sleeveLength` - Sleeveless, Short Sleeve, Long Sleeve, etc.
- `topLength` - Crop, Waist, Hip, Knee

**Bottom Wear Specific:**
- `fit` - Slim, Regular, Relaxed, Skinny, Baggy
- `length` - Above Knee, Knee Length, Ankle, Full
- `rise` - Low Rise, Mid Rise, High Rise

**Outer Wear Specific:**
- `thickness` - Lightweight, Midweight, Heavy

**Footwear Specific:**
- `usageType` - Casual, Formal, Sports, Daily

---

## Database Schema

### users
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique, indexed |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### user_passwords
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| password_hash | VARCHAR(255) | bcrypt hash |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### wardrobe_items
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users, indexed |
| image_url | TEXT | Cloudinary URL |
| category_group | VARCHAR(50) | upperWear, bottomWear, etc. |
| category | VARCHAR(100) | T-Shirt, Jeans, etc. |
| attributes | JSONB | Color, material, etc. |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### saved_images
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users, indexed |
| image_id | UUID | FK to wardrobe_items |
| note | TEXT | Optional note |
| saved_at | TIMESTAMP | |

### wardrobe_tags
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users, unique |
| tags_by_category | JSONB | Category tree with item IDs |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### calendar_outfits
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| outfit_date | DATE | Unique per user |
| combined_image_url | TEXT | Combined outfit image |
| prompt | TEXT | Original prompt |
| temperature | FLOAT | Weather temp |
| selected_categories | JSONB | List of categories |
| items | JSONB | List of item objects |
| created_at | TIMESTAMP | |

### posts
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users, indexed |
| image_url | TEXT | Post image URL |
| text | TEXT | Post caption |
| likes_count | INTEGER | Default 0 |
| comments_count | INTEGER | Default 0 |
| created_at | TIMESTAMP | Indexed DESC |
| updated_at | TIMESTAMP | |

### post_comments
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| post_id | UUID | FK to posts, indexed |
| user_id | UUID | FK to users |
| user_name | VARCHAR(200) | Commenter name |
| text | TEXT | Comment text |
| created_at | TIMESTAMP | |

---

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py               # Environment config loader
├── db.py                   # Database connection & init
├── requirements.txt
├── .env
│
├── routers/
│   ├── auth.py             # Auth endpoints
│   ├── wardrobe.py         # Wardrobe endpoints
│   ├── saved_image.py      # Saved images endpoints
│   ├── wardrobe_tags.py    # Wardrobe tags endpoint
│   ├── recommendation.py   # Outfit recommendation endpoint
│   ├── calendar_outfit.py  # Calendar outfits endpoints
│   ├── chat.py             # Chat endpoint
│   └── post.py             # Posts & comments endpoints
│
├── controllers/
│   ├── wardrobe_controller.py
│   ├── saved_image_controller.py
│   ├── wardrobe_tags_controller.py
│   ├── recommendation_controller.py
│   └── calendar_outfit_controller.py
│
├── services/
│   ├── auth_service.py         # JWT, password hashing
│   ├── cloudinary_service.py   # Image upload
│   ├── clip_service.py         # CLIP image tagging
│   ├── chat_service.py         # OpenAI chat
│   ├── recommendation_service.py
│   ├── saved_image_service.py
│   ├── wardrobe_tags_service.py
│   ├── calendar_outfit_service.py
│   └── image_combiner_service.py
│
├── repositories/
│   ├── user_repository.py
│   ├── wardrobe_repository.py
│   ├── saved_image_repository.py
│   ├── wardrobe_tags_repository.py
│   ├── calendar_outfit_repository.py
│   └── post_repository.py
│
├── models/
│   ├── auth.py                 # Auth Pydantic schemas
│   ├── saved_image.py
│   ├── recommendation.py
│   └── calendar_outfit.py
│
├── dependencies/
│   └── auth.py                 # get_current_user
│
└── tags/
    └── clip_labels.json        # CLIP classification labels
```
