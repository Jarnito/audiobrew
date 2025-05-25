/**
 * Utilities for checking Gmail connection status and AudioBrew label
 */

import { API_CONFIG } from '$lib/config';

export interface GmailConnectionStatus {
	isConnected: boolean;
	email?: string;
	error?: string;
}

export interface AudioBrewLabelStatus {
	hasLabel: boolean;
	error?: string;
}

/**
 * Check if user has connected their Gmail account
 * @param userId - The user's ID
 * @returns Promise<GmailConnectionStatus> - Connection status with optional error
 */
export async function checkGmailConnection(userId: string): Promise<GmailConnectionStatus> {
	try {
		const response = await fetch(API_CONFIG.url(`api/gmail/status?user_id=${userId}`));
		
		if (!response.ok) {
			console.error('Failed to check Gmail connection status:', response.status, response.statusText);
			return { isConnected: false, error: 'Failed to check Gmail connection' };
		}
		
		const data = await response.json();
		return {
			isConnected: data.is_connected === true,
			email: data.email
		};
	} catch (error) {
		console.error('Error checking Gmail connection:', error);
		return { isConnected: false, error: 'Network error while checking Gmail connection' };
	}
}

/**
 * Check if user has the AudioBrew label in their Gmail
 * @param userId - The user's ID  
 * @returns Promise<AudioBrewLabelStatus> - Label status with optional error
 */
export async function checkAudioBrewLabel(userId: string): Promise<AudioBrewLabelStatus> {
	try {
		const response = await fetch(API_CONFIG.url(`api/gmail/labels?user_id=${userId}`));
		
		if (!response.ok) {
			console.error('Failed to check AudioBrew label:', response.status, response.statusText);
			// Check if it's specifically a credentials not found error
			if (response.status === 404) {
				return { hasLabel: false, error: 'gmail_not_connected' };
			}
			return { hasLabel: false, error: 'Failed to check AudioBrew label' };
		}
		
		const data = await response.json();
		
		// Check if AudioBrew label exists in the labels array
		let hasLabel = false;
		if (data.labels && Array.isArray(data.labels)) {
			hasLabel = data.labels.some((label: any) => 
				label.name === 'AudioBrew' || 
				label.name?.toLowerCase().includes('audiobrew')
			);
		}
		
		return { hasLabel };
	} catch (error) {
		console.error('Error checking AudioBrew label:', error);
		return { hasLabel: false, error: 'Network error while checking AudioBrew label' };
	}
} 