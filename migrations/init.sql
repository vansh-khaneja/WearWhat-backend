--
-- WearWhat Database Schema
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
SET default_tablespace = '';
SET default_table_access_method = heap;

--
-- Users table
--
CREATE TABLE IF NOT EXISTS public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    profile_image_url text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    tokens integer DEFAULT 2 NOT NULL,
    PRIMARY KEY (id)
);

--
-- User passwords table
--
CREATE TABLE IF NOT EXISTS public.user_passwords (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    UNIQUE (user_id),
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

--
-- Wardrobe items table
--
CREATE TABLE IF NOT EXISTS public.wardrobe_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    image_url text NOT NULL,
    category_group character varying(50) NOT NULL,
    category character varying(100) NOT NULL,
    attributes jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

--
-- Wardrobe tags table
--
CREATE TABLE IF NOT EXISTS public.wardrobe_tags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    tags_by_category jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    UNIQUE (user_id)
);

--
-- Studio images table
--
CREATE TABLE IF NOT EXISTS public.studio_images (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    item_id uuid NOT NULL,
    original_image_url text NOT NULL,
    studio_image_url text NOT NULL,
    category_group character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id uuid NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (user_id, item_id),
    FOREIGN KEY (item_id) REFERENCES public.wardrobe_items(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

--
-- Calendar outfits table
--
CREATE TABLE IF NOT EXISTS public.calendar_outfits (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    outfit_date date NOT NULL,
    combined_image_url text NOT NULL,
    prompt text,
    temperature double precision,
    selected_categories jsonb DEFAULT '[]'::jsonb,
    items jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    weather character varying(50),
    PRIMARY KEY (id),
    UNIQUE (user_id, outfit_date)
);

--
-- Posts table
--
CREATE TABLE IF NOT EXISTS public.posts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    image_url text NOT NULL,
    text text,
    likes_count integer DEFAULT 0,
    comments_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id)
);

--
-- Post comments table
--
CREATE TABLE IF NOT EXISTS public.post_comments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    user_name character varying(200) NOT NULL,
    user_profile_image text,
    text text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id)
);

--
-- Post likes table
--
CREATE TABLE IF NOT EXISTS public.post_likes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id),
    UNIQUE (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

--
-- Post saves table
--
CREATE TABLE IF NOT EXISTS public.post_saves (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    PRIMARY KEY (id),
    UNIQUE (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

--
-- Saved images table
--
CREATE TABLE IF NOT EXISTS public.saved_images (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    saved_at timestamp with time zone DEFAULT now(),
    image_url text,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

--
-- Indexes
--
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users USING btree (email);
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_user_id ON public.wardrobe_items USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_wardrobe_tags_user_id ON public.wardrobe_tags USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_studio_images_item_id ON public.studio_images USING btree (item_id);
CREATE INDEX IF NOT EXISTS idx_studio_images_user_id ON public.studio_images USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_outfits_user_date ON public.calendar_outfits USING btree (user_id, outfit_date);
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON public.posts USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON public.posts USING btree (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_post_comments_post_id ON public.post_comments USING btree (post_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_post_id ON public.post_likes USING btree (post_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_user_id ON public.post_likes USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_post_saves_post_id ON public.post_saves USING btree (post_id);
CREATE INDEX IF NOT EXISTS idx_post_saves_user_id ON public.post_saves USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_images_user_id ON public.saved_images USING btree (user_id);
