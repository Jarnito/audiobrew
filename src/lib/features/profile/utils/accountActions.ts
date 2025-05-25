/**
 * Account management utilities for user profile operations
 */

import { API_CONFIG } from '$lib/config';

/**
 * Delete user account and all associated data
 * @param userId - The user's ID  
 * @returns Promise<boolean> - True if deletion was successful
 */
export async function deleteAccount(userId: string): Promise<boolean> {
	try {
		const response = await fetch(API_CONFIG.url(`api/user/${userId}`), {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json',
			},
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
			throw new Error(`Failed to delete account: ${errorData.detail}`);
		}

		return true;
	} catch (error) {
		console.error('Error deleting account:', error);
		throw error;
	}
} 