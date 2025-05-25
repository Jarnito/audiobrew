// Maximum length for display name
export const MAX_NAME_LENGTH = 20;

// Validate display name
export function validateDisplayName(displayName: string): { isValid: boolean; error: string } {
    if (!displayName || displayName.trim().length === 0) {
        return { isValid: false, error: 'Display name is required' };
    }
    
    if (displayName.length > MAX_NAME_LENGTH) {
        return { isValid: false, error: `Username must be ${MAX_NAME_LENGTH} characters or less` };
    }
    
    return { isValid: true, error: '' };
}

// Create a message clearer function
export function createMessageClearer() {
    return function clearMessages(callback: () => void, delay: number = 3000) {
        setTimeout(callback, delay);
    };
} 