# AudioBrew — Front‑end (SvelteKit v2)

## 1  Route map

| Path | Files | SSR | Purpose |
|------|-------|-----|---------|
| `/login` | `+page.svelte` | no | `<Auth />` component from Supabase UI. |
| `/dashboard` | `+page.server.ts` + `+page.svelte` | yes | List & play digests. |
| `/settings` | `+page.svelte` + `+page.server.ts` | yes | Connect inbox, set `preferred_time`. |

## 2  Auth guard (hook)

```ts
import { createServerClient } from '@supabase/ssr';
export const handle = async ({ event, resolve }) => {
  const supabase = createServerClient(
    process.env.PUBLIC_SUPABASE_URL!,
    process.env.PUBLIC_SUPABASE_ANON_KEY!,
    { headers: event.request.headers }
  );
  event.locals.supabase = supabase;
  const { data: { session } } = await supabase.auth.getSession();
  event.locals.session = session;
  return resolve(event);
};
```

## 3  PWA & audio

* Add `manifest.webmanifest` with icons & theme.  
* Register `service-worker.ts` to precache `/audio/*`.  
* Use **Plyr** for player controls (speed & ±15 s).  
