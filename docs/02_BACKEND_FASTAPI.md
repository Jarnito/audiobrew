# AudioBrew — Backend (FastAPI)

## 1  Environment variables

```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=
OPENAI_API_KEY=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
MS_CLIENT_ID=
MS_CLIENT_SECRET=
```

## 2  Database schema (single inbox)

```sql
create table inbox_connection (
  user_id uuid references auth.users primary key,
  provider text check (provider in ('google','microsoft')),
  email_address text,
  access_token text,
  refresh_token text,
  token_expiry timestamptz,
  created_at timestamptz default now()
);

create table digests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users,
  digest_date date,
  summary_text text,
  audio_path text,
  created_at timestamptz default now()
);
```

## 3  API routes

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/api/oauth/google` | — | Start Gmail OAuth (offline). |
| GET | `/api/oauth/microsoft` | — | Start Outlook OAuth. |
| GET | `/api/digests` | ✅ | List digests for current user. |
| GET | `/api/digests/{id}` | ✅ | Signed URL + summary. |

## 4  Scheduled job (Vercel Cron)

* **Trigger:** Vercel Cron every 15 min (`*/15 * * * *`).  
* **Logic:** For each user whose `preferred_time` (CET) lies in `[now, now+15 min)` and who hasn’t received a digest today:  
  1. Refresh token if needed (expiry < 5 min).  
  2. IMAP search since `now‑24 h` with `List-Unsubscribe`.  
  3. Summarise chunks → merge → TTS.  
  4. Upload MP3 & text; insert `digests` row; send notification.

Job must finish within Vercel’s 10 s CPU window—fine for a personal inbox.
