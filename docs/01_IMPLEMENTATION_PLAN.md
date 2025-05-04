# AudioBrew — Implementation Plan

> Build only one milestone at a time so Cursor stays focused.

| ID | Milestone | Scope (Done when …) |
|----|-----------|---------------------|
| **M0** | **Repo scaffold** | SvelteKit + Tailwind skeleton; `vercel.json`; empty `/api` folder; CI (Prettier, Ruff). |
| **M1** | **Auth** | Google + Microsoft sign‑up/sign‑in wired via Supabase; `/login` & session guard. |
| **M2** | **Inbox OAuth** | User can connect **one** inbox (Google or Microsoft). Tokens saved; disconnect button works. |
| **M3** | **Digest pipeline** | Vercel Cron (08 : 30 CET hard‑coded) calls FastAPI job; summarises dummy text → stores MP3 placeholder. |
| **M4** | **Dashboard v1** | `/dashboard` lists digests from DB; static MP3s stream in browser. |
| **M5** | **Real AI** | Replace dummy text with real IMAP fetch + GPT‑4o + OpenAI TTS. |
| **M6** | **User‑chosen time & notifications** | Settings field `preferred_time`, Cron runs every 15 min and filters rows; web‑push or e‑mail notice. |
| **M7** | **PWA polish** | Add manifest, service‑worker offline caching, install prompt. |

*ETA*: M0‑M3 ≈ 1 week evenings; M4‑M7 another 1‑2 weeks.
