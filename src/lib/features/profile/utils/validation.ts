// Display name validation constants
export const MAX_NAME_LENGTH = 20;

// Validate display name
export function validateDisplayName(displayName: string): { isValid: boolean; error: string } {
    if (!displayName.trim()) {
        return { isValid: false, error: 'Username cannot be empty' };
    }
    
    if (displayName.length > MAX_NAME_LENGTH) {
        return { isValid: false, error: `Username cannot exceed ${MAX_NAME_LENGTH} characters` };
    }
    
    return { isValid: true, error: '' };
}

// Function to clear messages after timeout
export function createMessageClearer(timeout = 5000) {
    return (callback: () => void) => {
        setTimeout(callback, timeout);
    };
} 