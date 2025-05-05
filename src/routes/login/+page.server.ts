import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
  login: async ({ request, locals: { supabase } }) => {
    const formData = await request.formData();
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      let message = error.message;
      if (message.toLowerCase().includes('invalid login credentials')) {
        message = "This account doesn't exist";
      }
      return fail(400, { error: message });
    } else {
      throw redirect(303, '/dashboard');
    }
  }
};