import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

/**
 * This route checks if a user has connected their Gmail account
 * by proxying to our FastAPI backend.
 */
export const GET: RequestHandler = async ({ url, fetch }) => {
  // Get user ID from query parameter
  const userId = url.searchParams.get('user_id');
  
  if (!userId) {
    return json({ error: 'User ID is required' }, { status: 400 });
  }
  
  try {
    // Forward the request to our FastAPI backend
    const response = await fetch(`/api/gmail/status?user_id=${userId}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      return json(errorData, { status: response.status });
    }
    
    // Return the connection status from the backend
    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error('Error checking Gmail connection status:', error);
    return json({ error: 'Failed to check Gmail connection status' }, { status: 500 });
  }
}; 