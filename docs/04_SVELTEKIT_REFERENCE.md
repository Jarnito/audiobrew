# SvelteKit Quick Reference (2025‑05)

* **Routing:** `+page.svelte` / `+page.server.ts` conventions citeturn3view0  
* **Env vars:** `$env/static/public` for browser‑safe, `$env/static/private` for server‑only citeturn3view0  
* **Adapter‑vercel:** adds a build output that Vercel picks up automatically citeturn5view0  
* **Cron on Vercel:** declare in `vercel.json → "crons"` citeturn1search0  
* **Python runtime:** `runtime:"python3.11"` in `vercel.json` citeturn1search3  
* **Service‑workers & PWA:** register via `navigator.serviceWorker.register()`; cache for offline citeturn0search3  
* **Plyr player:** speeds array & skip buttons configured via options citeturn0search4  
* **Supabase auth helpers:** use `@supabase/ssr` (successor to auth‑helpers) for SvelteKit SSR citeturn8search3  
