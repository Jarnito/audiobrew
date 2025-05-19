-- Enable UUID generator (once per database)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ────────────────────────────────────────────────────────────
-- TABLE
-- One Gmail-credential row per Supabase user
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.gmail_connections (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID  NOT NULL           -- references auth.users(id)
                 REFERENCES auth.users(id) ON DELETE CASCADE,
    credentials  JSONB NOT NULL,          -- token, refresh_token, scopes, …
    email        TEXT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    updated_at   TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id)                       -- 1 row per user
);

-- ────────────────────────────────────────────────────────────
-- Trigger: keep updated_at fresh on every UPDATE
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.touch_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_touch_updated_at
BEFORE UPDATE ON public.gmail_connections
FOR EACH ROW EXECUTE PROCEDURE public.touch_updated_at();

-- ────────────────────────────────────────────────────────────
-- Row-Level Security
-- ────────────────────────────────────────────────────────────
ALTER TABLE public.gmail_connections ENABLE ROW LEVEL SECURITY;

-- 1.  Owner can SELECT / INSERT / UPDATE / DELETE its own row
CREATE POLICY user_manage_own
    ON public.gmail_connections
    FOR ALL
    USING      (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 2.  service-role (or any key that bypasses RLS) has full access
--     This policy is mainly a safety net if you ever disable bypass.
CREATE POLICY service_manage_all
    ON public.gmail_connections
    USING (true);