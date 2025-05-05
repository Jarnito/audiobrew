import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, locals: { supabase } }) => {
  const code = url.searchParams.get('code');

  if (code) {
    await supabase.auth.exchangeCodeForSession(code);
  }

  // Get the current user
  const { data: { user } } = await supabase.auth.getUser();

  if (user) {
    const meta = user.user_metadata;
    // If display_name is missing, set it from name or full_name
    if (!meta.display_name && (meta.name || meta.full_name)) {
      await supabase.auth.updateUser({
        data: {
          display_name: meta.name || meta.full_name
        }
      });
    }
  }

  throw redirect(303, '/dashboard');
};