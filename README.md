# WearWhat Backend API

A FastAPI-based backend for wardrobe management with image upload, auto-tagging, and user authentication.

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

Upload one or more clothing images. Images are uploaded to Cloudinary and auto-tagged.

**Headers:**
- Cookie: `access_token=<jwt_token>` (set automatically after login)

**Request:**
- Content-Type: `multipart/form-data`
- Body: `files` - One or more image files

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/wardrobe/upload" \
  -H "Cookie: access_token=your_jwt_token" \
  -F "files=@jacket.jpg" \
  -F "files=@pants.jpg"
```

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
    },
    {
      "id": "uuid-string",
      "image_url": "https://res.cloudinary.com/...",
      "categoryGroup": "bottomWear",
      "category": "Jeans",
      "attributes": {
        "color": "Blue",
        "season": "All Season",
        "material": "Denim",
        "pattern": "Solid",
        "occasion": "Casual",
        "fit": "Slim",
        "length": "Full",
        "rise": "Mid Rise"
      }
    }
  ]
}
```

**Errors:**
- `401` - Not authenticated / Invalid token

---

#### GET `/wardrobe/`

Get all wardrobe items for the authenticated user.

**Headers:**
- Cookie: `access_token=<jwt_token>`

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
- `401` - Not authenticated / Invalid token

---

#### DELETE `/wardrobe/{item_id}`

Delete a wardrobe item.

**Path Parameters:**
- `item_id` (string, required) - UUID of the item to delete

**Headers:**
- Cookie: `access_token=<jwt_token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Item deleted"
}
```

**Response (200 - Item not found):**
```json
{
  "success": false,
  "message": "Item not found or not authorized"
}
```

**Errors:**
- `401` - Not authenticated / Invalid token

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
│   └── wardrobe.py         # Wardrobe endpoints
│
├── controllers/
│   └── wardrobe_controller.py
│
├── services/
│   ├── auth_service.py     # JWT, password hashing
│   ├── cloudinary_service.py
│   └── clip_service.py     # Image tagging (mock)
│
├── repositories/
│   ├── user_repository.py
│   └── wardrobe_repository.py
│
├── models/
│   └── auth.py             # Pydantic schemas
│
├── dependencies/
│   └── auth.py             # get_current_user
│
└── tags/
    ├── categories.json
    ├── generic_attributes.json
    └── specific_attributes.json
```

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
