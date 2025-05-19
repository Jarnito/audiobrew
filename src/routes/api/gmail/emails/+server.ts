import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

/**
 * This route fetches emails from a specific Gmail label (defaults to AudioBrew)
 * by proxying to our FastAPI backend.
 */
export const GET: RequestHandler = async ({ url, fetch }) => {
  // Get user ID from query parameter
  const userId = url.searchParams.get('user_id');
  const labelId = url.searchParams.get('label_id'); // Optional
  
  if (!userId) {
    return json({ error: 'User ID is required' }, { status: 400 });
  }
  
  try {
    // Build the URL with optional label_id
    let apiUrl = `/api/gmail/emails?user_id=${userId}`;
    if (labelId) {
      apiUrl += `&label_id=${labelId}`;
    }
    
    // Forward the request to our FastAPI backend
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      return json(errorData, { status: response.status });
    }
    
    // Return the emails from the backend
    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error('Error fetching Gmail emails:', error);
    return json({ error: 'Failed to fetch Gmail emails' }, { status: 500 });
  }
}; 