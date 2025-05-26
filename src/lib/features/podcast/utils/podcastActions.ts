/**
 * Podcast action utilities for download, share, and delete operations
 */

import { API_CONFIG } from '$lib/config';

export interface Podcast {
    id: string;
    title: string;
    duration: number; // seconds
    created_at: string;
    audio_url: string;
    source_emails: number;
    script_markdown?: string;
}

/**
 * Downloads a podcast audio file directly to the user's device
 * @param podcast - The podcast object containing audio URL and metadata
 * @returns Promise<string | null> - Returns error message if failed, null if successful
 */
export async function downloadPodcast(podcast: Podcast): Promise<string | null> {
    const audioUrl = getAudioUrl(podcast.audio_url);
    
    // Skip if it's a placeholder URL
    if (audioUrl.includes('example.com')) {
        return 'Audio file is not available for download';
    }
    
    try {
        // Fetch the audio file as a blob
        const response = await fetch(audioUrl);
        if (!response.ok) {
            throw new Error('Failed to fetch audio file');
        }
        
        const blob = await response.blob();
        
        // Create a blob URL
        const blobUrl = URL.createObjectURL(blob);
        
        // Create a temporary link element for download
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = `${podcast.title.replace(/[<>:"/\\|?*]/g, '').trim()}.mp3`;
        
        // Trigger download immediately
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up the blob URL
        URL.revokeObjectURL(blobUrl);
        
        return null; // Success
    } catch (err) {
        console.error('Error downloading podcast:', err);
        return 'Failed to download audio file';
    }
}

/**
 * Shares a podcast audio file using the native Web Share API
 * @param podcast - The podcast object containing audio URL and metadata
 * @returns Promise<string | null> - Returns error message if failed, null if successful
 */
export async function sharePodcast(podcast: Podcast): Promise<string | null> {
    const audioUrl = getAudioUrl(podcast.audio_url);
    
    // Skip if it's a placeholder URL
    if (audioUrl.includes('example.com')) {
        return 'Audio file is not available for sharing';
    }
    
    try {
        // Check if Web Share API is supported
        if (!navigator.share) {
            return 'Sharing is not supported on this device';
        }
        
        // Fetch the audio file as a blob
        const response = await fetch(audioUrl);
        if (!response.ok) {
            throw new Error('Failed to fetch audio file');
        }
        
        const blob = await response.blob();
        const fileName = `${podcast.title.replace(/[<>:"/\\|?*]/g, '').trim()}.mp3`;
        
        // Create a File object from the blob
        const file = new File([blob], fileName, { type: 'audio/mpeg' });
        
        // Use native share API
        await navigator.share({
            title: podcast.title,
            text: `Check out this podcast: ${podcast.title}`,
            files: [file]
        });
        
        return null; // Success
    } catch (err) {
        console.error('Error sharing podcast:', err);
        // Check if user cancelled the share
        if ((err as Error)?.name === 'AbortError') {
            return null; // User cancelled, not an error
        }
        return 'Failed to share audio file';
    }
}

/**
 * Delete a podcast from the backend and Supabase storage
 * @param podcastId - The podcast ID to delete
 * @param userId - The user ID (for authorization)
 * @returns Promise<string | null> - Returns error message if failed, null if successful
 */
export async function deletePodcast(podcastId: string, userId: string): Promise<string | null> {
	try {
		const response = await fetch(API_CONFIG.url(`api/podcast/${podcastId}?user_id=${userId}`), {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json',
			},
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
			return `Failed to delete podcast: ${errorData.detail}`;
		}

		return null; // Success
	} catch (error) {
		console.error('Error deleting podcast:', error);
		return 'Failed to delete podcast due to network error';
	}
}

/**
 * Formats audio URL to ensure it's absolute
 * @param url - The audio URL to format
 * @returns Formatted audio URL
 */
function getAudioUrl(url: string): string {
    // If it's a valid URL, return as is
    if (url.startsWith('http')) {
        return url;
    }
    
    // Otherwise, return as is (might be a placeholder)
    return url;
} 