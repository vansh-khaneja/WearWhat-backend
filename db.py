import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Create users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Create user_passwords table (separate for security)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_passwords (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Create index on email for faster lookups
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
    """)

    # Create wardrobe_items table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wardrobe_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            image_url TEXT NOT NULL,
            category_group VARCHAR(50) NOT NULL,
            category VARCHAR(100) NOT NULL,
            attributes JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Create index on user_id for faster lookups
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_wardrobe_items_user_id ON wardrobe_items(user_id)
    """)

    # Create saved_images table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_images (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            image_id UUID NOT NULL REFERENCES wardrobe_items(id) ON DELETE CASCADE,
            note TEXT,
            saved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Create index on user_id for saved_images
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_saved_images_user_id ON saved_images(user_id)
    """)

    conn.commit()
    cur.close()
    conn.close()
