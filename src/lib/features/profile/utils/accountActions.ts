/**
 * Account action utilities for user account management
 */

/**
 * Deletes a user account and all associated data
 * @param userId - The ID of the user account to delete
 * @returns Promise<string | null> - Returns error message if failed, null if successful
 */
export async function deleteAccount(userId: string): Promise<string | null> {
    if (!userId) {
        return 'User ID is required';
    }
    
    try {
        const response = await fetch(`/api/user/${userId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            return data.detail || `Failed to delete account (${response.status})`;
        }
        
        return null; // Success
    } catch (err) {
        console.error('Error deleting account:', err);
        return 'Failed to delete account due to network error';
    }
} 