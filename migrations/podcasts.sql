-- =========================================
--  PODCASTS TABLE + RLS + TRIGGER
-- =========================================

-- 1. Table
CREATE TABLE IF NOT EXISTS podcasts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL
                    REFERENCES auth.users(id)
                    ON DELETE CASCADE,

    title           TEXT        NOT NULL,

    -- MP3 URL is filled in after TTS is complete, so keep it nullable
    audio_url       TEXT UNIQUE,

    -- Store the generated script; never NULL
    script_markdown TEXT        NOT NULL DEFAULT '',

    duration        INTEGER     NOT NULL CHECK (duration > 0),     -- seconds
    source_emails   INTEGER     NOT NULL CHECK (source_emails >= 0),

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Index – fastest for “latest podcasts for user”
CREATE INDEX IF NOT EXISTS idx_podcasts_user_created
  ON podcasts (user_id, created_at DESC);

-- 3. Row-level security
ALTER TABLE podcasts ENABLE ROW LEVEL SECURITY;

CREATE POLICY select_own_podcasts
  ON podcasts FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY insert_own_podcasts
  ON podcasts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY update_own_podcasts
  ON podcasts FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY delete_own_podcasts
  ON podcasts FOR DELETE
  USING (auth.uid() = user_id);

GRANT SELECT, INSERT, UPDATE, DELETE
  ON podcasts
  TO authenticated;

-- 4. Trigger to keep updated_at fresh
CREATE OR REPLACE FUNCTION set_podcasts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_podcasts_updated_at
BEFORE UPDATE ON podcasts
FOR EACH ROW
EXECUTE FUNCTION set_podcasts_updated_at();