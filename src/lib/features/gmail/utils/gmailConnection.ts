/**
 * Gmail connection utilities for checking connection status and handling errors
 */

export interface GmailConnectionStatus {
    isConnected: boolean;
    email?: string;
    error?: string;
}

/**
 * Checks if the user has connected their Gmail account
 * @param userId - The ID of the user to check
 * @returns Promise<GmailConnectionStatus> - Connection status with optional error
 */
export async function checkGmailConnection(userId: string): Promise<GmailConnectionStatus> {
    if (!userId) {
        return { isConnected: false, error: 'User ID is required' };
    }
    
    try {
        const response = await fetch(`/api/gmail/status?user_id=${userId}`);
        
        if (!response.ok) {
            return { isConnected: false, error: 'Failed to check Gmail connection' };
        }
        
        const data = await response.json();
        return {
            isConnected: data.is_connected,
            email: data.email
        };
    } catch (err) {
        console.error('Error checking Gmail connection:', err);
        return { isConnected: false, error: 'Network error while checking Gmail connection' };
    }
}

/**
 * Checks if the user has the AudioBrew label set up
 * @param userId - The ID of the user to check
 * @returns Promise<{ hasLabel: boolean; error?: string }> - Label status with optional error
 */
export async function checkAudioBrewLabel(userId: string): Promise<{ hasLabel: boolean; error?: string }> {
    if (!userId) {
        return { hasLabel: false, error: 'User ID is required' };
    }
    
    try {
        const response = await fetch(`/api/gmail/labels?user_id=${userId}`);
        
        if (!response.ok) {
            const data = await response.json();
            // Check if it's specifically a credentials not found error
            if (response.status === 404 && data.detail?.includes('Gmail credentials not found')) {
                return { hasLabel: false, error: 'gmail_not_connected' };
            }
            return { hasLabel: false, error: data.detail || 'Failed to check AudioBrew label' };
        }
        
        const data = await response.json();
        return { hasLabel: data.has_audiobrew_label };
    } catch (err) {
        console.error('Error checking AudioBrew label:', err);
        return { hasLabel: false, error: 'Network error while checking AudioBrew label' };
    }
} 