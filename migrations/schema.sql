--
-- PostgreSQL database dump
--

\restrict XNyAbTOPNNGAR6gbarR4SBXLQcO383zNPxrHsbsMjVd16eGsQhhtOLYahqVScwR

-- Dumped from database version 17.7 (bdd1736)
-- Dumped by pg_dump version 17.7 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: calendar_outfits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.calendar_outfits (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    outfit_date date NOT NULL,
    combined_image_url text NOT NULL,
    prompt text,
    temperature double precision,
    selected_categories jsonb DEFAULT '[]'::jsonb,
    items jsonb DEFAULT '[]'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    weather character varying(50)
);


--
-- Name: post_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_comments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    user_name character varying(200) NOT NULL,
    user_profile_image text,
    text text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: post_likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_likes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: post_saves; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_saves (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    image_url text NOT NULL,
    text text,
    likes_count integer DEFAULT 0,
    comments_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: saved_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.saved_images (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    saved_at timestamp with time zone DEFAULT now(),
    image_url text
);


--
-- Name: studio_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.studio_images (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    item_id uuid NOT NULL,
    original_image_url text NOT NULL,
    studio_image_url text NOT NULL,
    category_group character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id uuid NOT NULL
);


--
-- Name: user_passwords; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_passwords (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    profile_image_url text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    tokens integer DEFAULT 2 NOT NULL
);


--
-- Name: wardrobe_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wardrobe_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    image_url text NOT NULL,
    category_group character varying(50) NOT NULL,
    category character varying(100) NOT NULL,
    attributes jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: wardrobe_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wardrobe_tags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    tags_by_category jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: calendar_outfits calendar_outfits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calendar_outfits
    ADD CONSTRAINT calendar_outfits_pkey PRIMARY KEY (id);


--
-- Name: calendar_outfits calendar_outfits_user_id_outfit_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.calendar_outfits
    ADD CONSTRAINT calendar_outfits_user_id_outfit_date_key UNIQUE (user_id, outfit_date);


--
-- Name: post_comments post_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_comments
    ADD CONSTRAINT post_comments_pkey PRIMARY KEY (id);


--
-- Name: post_likes post_likes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_likes
    ADD CONSTRAINT post_likes_pkey PRIMARY KEY (id);


--
-- Name: post_likes post_likes_post_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_likes
    ADD CONSTRAINT post_likes_post_id_user_id_key UNIQUE (post_id, user_id);


--
-- Name: post_saves post_saves_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_saves
    ADD CONSTRAINT post_saves_pkey PRIMARY KEY (id);


--
-- Name: post_saves post_saves_post_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_saves
    ADD CONSTRAINT post_saves_post_id_user_id_key UNIQUE (post_id, user_id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: saved_images saved_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_images
    ADD CONSTRAINT saved_images_pkey PRIMARY KEY (id);


--
-- Name: studio_images studio_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.studio_images
    ADD CONSTRAINT studio_images_pkey PRIMARY KEY (id);


--
-- Name: studio_images unique_user_item; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.studio_images
    ADD CONSTRAINT unique_user_item UNIQUE (user_id, item_id);


--
-- Name: user_passwords user_passwords_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_passwords
    ADD CONSTRAINT user_passwords_pkey PRIMARY KEY (id);


--
-- Name: user_passwords user_passwords_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_passwords
    ADD CONSTRAINT user_passwords_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: wardrobe_items wardrobe_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wardrobe_items
    ADD CONSTRAINT wardrobe_items_pkey PRIMARY KEY (id);


--
-- Name: wardrobe_tags wardrobe_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wardrobe_tags
    ADD CONSTRAINT wardrobe_tags_pkey PRIMARY KEY (id);


--
-- Name: wardrobe_tags wardrobe_tags_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wardrobe_tags
    ADD CONSTRAINT wardrobe_tags_user_id_key UNIQUE (user_id);


--
-- Name: idx_calendar_outfits_user_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_calendar_outfits_user_date ON public.calendar_outfits USING btree (user_id, outfit_date);


--
-- Name: idx_post_comments_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_comments_post_id ON public.post_comments USING btree (post_id);


--
-- Name: idx_post_likes_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_likes_post_id ON public.post_likes USING btree (post_id);


--
-- Name: idx_post_likes_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_likes_user_id ON public.post_likes USING btree (user_id);


--
-- Name: idx_post_saves_post_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_saves_post_id ON public.post_saves USING btree (post_id);


--
-- Name: idx_post_saves_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_post_saves_user_id ON public.post_saves USING btree (user_id);


--
-- Name: idx_posts_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posts_created_at ON public.posts USING btree (created_at DESC);


--
-- Name: idx_posts_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_posts_user_id ON public.posts USING btree (user_id);


--
-- Name: idx_saved_images_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_saved_images_user_id ON public.saved_images USING btree (user_id);


--
-- Name: idx_studio_images_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_studio_images_item_id ON public.studio_images USING btree (item_id);


--
-- Name: idx_studio_images_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_studio_images_user_id ON public.studio_images USING btree (user_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_wardrobe_items_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wardrobe_items_user_id ON public.wardrobe_items USING btree (user_id);


--
-- Name: idx_wardrobe_tags_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wardrobe_tags_user_id ON public.wardrobe_tags USING btree (user_id);


--
-- Name: post_likes post_likes_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_likes
    ADD CONSTRAINT post_likes_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE;


--
-- Name: post_likes post_likes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_likes
    ADD CONSTRAINT post_likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: post_saves post_saves_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_saves
    ADD CONSTRAINT post_saves_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE;


--
-- Name: post_saves post_saves_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_saves
    ADD CONSTRAINT post_saves_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: saved_images saved_images_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.saved_images
    ADD CONSTRAINT saved_images_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: studio_images studio_images_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.studio_images
    ADD CONSTRAINT studio_images_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.wardrobe_items(id) ON DELETE CASCADE;


--
-- Name: studio_images studio_images_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.studio_images
    ADD CONSTRAINT studio_images_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_passwords user_passwords_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_passwords
    ADD CONSTRAINT user_passwords_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: wardrobe_items wardrobe_items_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.wardrobe_items
    ADD CONSTRAINT wardrobe_items_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict XNyAbTOPNNGAR6gbarR4SBXLQcO383zNPxrHsbsMjVd16eGsQhhtOLYahqVScwR

