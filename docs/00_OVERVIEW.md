# AudioBrew — Project Overview

AudioBrew turns yesterday’s e‑mail newsletters into a single, human‑sounding podcast you can listen to on the go.

## 1  Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| **Frontend / PWA** | **SvelteKit v2 + TypeScript + Tailwind CSS** | Filesystem routing & SSR citeturn3view0 |
| **Backend API** | **FastAPI (Python 3.12)** in **Vercel Serverless Functions** | Native Python runtime on Vercel citeturn1search3 |
| **Scheduled Job** | Vercel **Cron Job** (Serverless) | Supports cron expressions and runs up to 10 s CPU per invocation citeturn1search0 |
| **DB / Auth / Storage** | **Supabase** (Google + Microsoft social login, Postgres, Storage) | Managed Postgres + first‑class Auth providers citeturn8search6 |
| **AI services** | OpenAI GPT‑4o (summaries) + OpenAI `audio.speech` TTS | Best-in-class text & voice quality |
| **Audio player** | **Plyr** JS wrapper around `<audio>` | Built‑in speed control & skip buttons citeturn0search4 |

All pieces deploy on **Vercel only**, so you manage one dashboard and zero Docker files.

## 2  Core features (v1)

1. **Sign in** with Google or Microsoft.  
2. **Connect exactly one inbox** (Gmail **or** Outlook) through server‑side OAuth.  
3. At a **user‑chosen time** (default 08 : 30 CET), fetch the last 24 h of e‑mail, filter newsletters (`List‑Unsubscribe` header).  
4. Summarise via GPT‑4o, merge, convert to speech.  
5. Store summary + MP3, send a push/e‑mail notification.  
6. Responsive dashboard & PWA: play at 1 × – 2 × with ±15 s skip.  

*Prepared May 2025.*