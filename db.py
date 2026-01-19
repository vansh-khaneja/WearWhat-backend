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
            profile_image_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Add profile_image_url column if it doesn't exist (for existing databases)
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name='users' AND column_name='profile_image_url') THEN
                ALTER TABLE users ADD COLUMN profile_image_url TEXT;
            END IF;
        END $$;
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

    # Create wardrobe_tags table - stores the tags tree per user
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wardrobe_tags (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tags_by_category JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Create index on user_id for wardrobe_tags
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_wardrobe_tags_user_id ON wardrobe_tags(user_id)
    """)

    # Create calendar_outfits table - stores outfit recommendations by date
    cur.execute("""
        CREATE TABLE IF NOT EXISTS calendar_outfits (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            outfit_date DATE NOT NULL,
            combined_image_url TEXT NOT NULL,
            prompt TEXT,
            temperature FLOAT,
            selected_categories JSONB DEFAULT '[]',
            items JSONB DEFAULT '[]',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(user_id, outfit_date)
        )
    """)

    # Create index on user_id and outfit_date for calendar_outfits
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_calendar_outfits_user_date ON calendar_outfits(user_id, outfit_date)
    """)

    # Create posts table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            image_url TEXT NOT NULL,
            text TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Create indexes for posts - user_id for filtering by user, created_at for feed ordering
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC)
    """)

    # Create post_comments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS post_comments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            user_name VARCHAR(200) NOT NULL,
            user_profile_image TEXT,
            text TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    # Add user_profile_image column to post_comments if it doesn't exist
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                          WHERE table_name='post_comments' AND column_name='user_profile_image') THEN
                ALTER TABLE post_comments ADD COLUMN user_profile_image TEXT;
            END IF;
        END $$;
    """)

    # Create index for comments by post
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_post_comments_post_id ON post_comments(post_id)
    """)

    conn.commit()
    cur.close()
    conn.close()
