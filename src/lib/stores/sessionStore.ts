// src/lib/stores/session.ts
import { browser } from '$app/environment';
import { writable, type Writable } from 'svelte/store';
import { createBrowserClient } from '@supabase/ssr';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';
import type { Session } from '@supabase/supabase-js';

export const sessionStore: Writable<Session | null> = writable<Session | null>(null);

if (browser) {
  const supabase = createBrowserClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY);

  supabase.auth.getSession().then(({ data }) => {
    console.log('SessionStore: Initial session data:', data.session?.user?.user_metadata);
    sessionStore.set(data.session);
  });
  
  supabase.auth.onAuthStateChange((_e, s) => {
    console.log('SessionStore: Auth state changed:', s?.user?.user_metadata);
    sessionStore.set(s);
  });
}