import { createServerClient } from '@supabase/ssr';
import { type Handle, redirect } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

const supabase: Handle = async ({ event, resolve }) => {
  event.locals.supabase = createServerClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
    cookies: {
      getAll: () => event.cookies.getAll(),
      setAll: (cookiesToSet) => {
        cookiesToSet.forEach(({ name, value, options }) => {
          event.cookies.set(name, value, { ...options, path: '/' });
        });
      },
    },
  });

  event.locals.safeGetSession = async () => {
    const { data: { session } } = await event.locals.supabase.auth.getSession();
    if (!session) return { session: null, user: null };
    
    const { data: { user }, error } = await event.locals.supabase.auth.getUser();
    if (error) return { session: null, user: null };
    
    // Log the user metadata to debug avatar issues
    if (user) {
      console.log('Server: User metadata in safeGetSession:', user.user_metadata);
      
      // Make sure we're not losing any metadata fields, especially avatar_url
      if (session) {
        session.user.user_metadata = user.user_metadata;
      }
    }
    
    return { session, user };
  };

  return resolve(event, {
    filterSerializedResponseHeaders(name) {
      return name === 'content-range' || name === 'x-supabase-api-version';
    },
  });
};

const authGuard: Handle = async ({ event, resolve }) => {
  const { session, user } = await event.locals.safeGetSession();
  event.locals.session = session;
  event.locals.user = user;
  if (!event.locals.session && event.url.pathname.startsWith('/dashboard')) {
    throw redirect(303, '/auth');
  }
  if (event.locals.session && event.url.pathname === '/auth') {
    throw redirect(303, '/dashboard');
  }
  return resolve(event);
};

export const handle: Handle = sequence(supabase, authGuard);