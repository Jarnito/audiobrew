import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

/**
 * This route fetches Gmail labels for a user
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
    const response = await fetch(`/api/gmail/labels?user_id=${userId}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      return json(errorData, { status: response.status });
    }
    
    // Return the labels from the backend
    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error('Error fetching Gmail labels:', error);
    return json({ error: 'Failed to fetch Gmail labels' }, { status: 500 });
  }
}; 