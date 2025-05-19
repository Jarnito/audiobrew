import { redirect } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

/**
 * This route handles the callback from Google's OAuth server.
 * It proxies the OAuth code to our FastAPI backend which exchanges it for tokens
 * and stores the credentials in Supabase.
 */
export const GET = async ({ url, fetch }: RequestEvent) => {
  // Extract the code and state (user_id) from the URL
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');

  if (!code || !state) {
    // Redirect to dashboard with error if missing params
    return redirect(302, '/dashboard/profile?gmail_error=Missing parameters in callback');
  }

  try {
    // Forward the code and state to our FastAPI backend
    const response = await fetch(`/api/auth/gmail/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error: ${response.status} - ${errorText}`);
      return redirect(302, `/dashboard/profile?gmail_error=${encodeURIComponent('Failed to connect Gmail')}`);
    }

    // Success - FastAPI will have already saved the credentials to Supabase
    // Redirect back to profile page with success flag
    return redirect(302, '/dashboard/profile?gmail_connected=true');
  } catch (error) {
    console.error('Error in Gmail callback:', error);
    return redirect(302, `/dashboard/profile?gmail_error=${encodeURIComponent('Failed to process Gmail connection')}`);
  }
}; 