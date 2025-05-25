import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { API_CONFIG } from '$lib/config';

/**
 * This route initiates the Gmail OAuth flow by proxying to our FastAPI backend on Render.
 * It returns the authorization URL that the user should be redirected to.
 */
export const GET: RequestHandler = async ({ url }) => {
  // Get user ID from query parameter
  const userId = url.searchParams.get('user_id');
  
  if (!userId) {
    return json({ error: 'User ID is required' }, { status: 400 });
  }

  try {
    // Forward the request to our FastAPI backend on Render
    const response = await fetch(API_CONFIG.url(`api/gmail/auth?user_id=${userId}`));
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      return json(errorData, { status: response.status });
    }

    // Return the authorization URL from the backend
    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error('Error initiating Gmail auth:', error);
    return json({ error: 'Failed to initiate Gmail authentication' }, { status: 500 });
  }
}; 