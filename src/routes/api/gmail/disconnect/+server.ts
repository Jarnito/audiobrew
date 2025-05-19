import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

/**
 * This route disconnects a user's Gmail account by proxying to our FastAPI backend.
 */
export const DELETE: RequestHandler = async ({ url, fetch }) => {
  // Get user ID from query parameter
  const userId = url.searchParams.get('user_id');
  
  if (!userId) {
    return json({ error: 'User ID is required' }, { status: 400 });
  }
  
  try {
    // Forward the delete request to our FastAPI backend
    const response = await fetch(`/api/gmail/disconnect?user_id=${userId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      return json(errorData, { status: response.status });
    }
    
    // Return the successful response from the backend
    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error('Error disconnecting Gmail:', error);
    return json({ error: 'Failed to disconnect Gmail' }, { status: 500 });
  }
}; 