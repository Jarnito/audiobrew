import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals: { supabase, safeGetSession } }) => {
    // Ensure the user is authenticated
    const { session } = await safeGetSession();
    if (!session) {
        throw error(401, { message: 'Unauthorized' });
    }
    
    // Simply return the user data without attempting to create buckets
    // Buckets should be created manually in the Supabase dashboard
    return {
        user: session.user
    };
}) satisfies PageServerLoad; 