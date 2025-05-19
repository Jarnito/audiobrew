import { supabase } from "$lib/supabaseClient";
import { sessionStore } from "$lib/stores/sessionStore";
import { get } from 'svelte/store';

// Default placeholder
export const placeholderImage = "/nopicture_placeholder.png";

// Get the profile image src with fallback
export function getProfileImageSrc(imagePreview: string | null = null) {
    const sessionValue = get(sessionStore);
    
    // Priority 0: First check if there's a preview from a newly selected image
    // This is important for immediate feedback during upload
    if (imagePreview) {
        return imagePreview;
    }
    
    if (!sessionValue?.user) {
        return placeholderImage;
    }
    
    // Get avatar URL from user metadata
    const metadata = sessionValue.user.user_metadata;
    
    // Priority 1: Check for our custom avatar URL field that persists across OAuth refreshes
    if (metadata?.custom_avatar_url && metadata.custom_avatar_url.trim() !== '') {
        return metadata.custom_avatar_url;
    }
    
    // Priority 2: Check regular avatar_url
    const avatarUrl = metadata?.avatar_url;
    
    if (avatarUrl && avatarUrl.trim() !== '') {
        // Check if this URL is from our Supabase bucket (user uploaded)
        if (avatarUrl.includes('profilepic')) {
            return avatarUrl;
        }
        
        // Priority 3: OAuth provider avatar URL (Google, etc.)
        return avatarUrl;
    }
    
    // Priority 4: Default placeholder if no avatar is available
    return placeholderImage;
}

// Create image preview
export function createImagePreview(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                // Create a canvas to resize the image preview
                const canvas = document.createElement('canvas');
                // Limit preview size to 150x150 pixels
                const MAX_SIZE = 150;
                let width = img.width;
                let height = img.height;
                
                // Calculate the new dimensions
                if (width > height) {
                    if (width > MAX_SIZE) {
                        height = Math.round(height * (MAX_SIZE / width));
                        width = MAX_SIZE;
                    }
                } else {
                    if (height > MAX_SIZE) {
                        width = Math.round(width * (MAX_SIZE / height));
                        height = MAX_SIZE;
                    }
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // Draw the resized image
                const ctx = canvas.getContext('2d');
                if (!ctx) {
                    reject(new Error('Could not get canvas context'));
                    return;
                }
                ctx.drawImage(img, 0, 0, width, height);
                
                // Get a compressed data URL for preview only
                resolve(canvas.toDataURL('image/jpeg', 0.7));
            };
            img.onerror = () => reject(new Error('Failed to load image'));
            img.src = e.target?.result as string;
        };
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsDataURL(file);
    });
}

// Upload profile image to Supabase
export async function uploadProfileImage(profileImage: File | null) {
    if (!profileImage) {
        throw new Error('No profile image provided');
    }
    
    const sessionValue = get(sessionStore);
    if (!sessionValue?.user) {
        throw new Error('User not authenticated');
    }
    
    // Validate file type and size
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(profileImage.type)) {
        throw new Error('Please upload a JPEG, JPG, or PNG image file');
    }
    
    // Check file size (max 5MB)
    const MAX_SIZE = 5 * 1024 * 1024; // 5MB
    if (profileImage.size > MAX_SIZE) {
        throw new Error('Image size must be less than 5MB');
    }
    
    // Check if user already has a custom avatar and delete it first
    const metadata = sessionValue.user.user_metadata;
    if (metadata?.custom_avatar_url && metadata.custom_avatar_url.includes('profilepic')) {
        try {
            // Extract the filename from the URL
            const oldFileUrl = metadata.custom_avatar_url;
            const oldFileName = oldFileUrl.split('/').pop();
            
            if (oldFileName) {
                console.log('Deleting old profile image:', oldFileName);
                // Delete the file from storage
                const { error: deleteError } = await supabase.storage
                    .from('profilepic')
                    .remove([oldFileName]);
                    
                if (deleteError) {
                    console.warn('Failed to delete old profile image:', deleteError);
                    // Continue with upload even if delete fails
                } else {
                    console.log('Successfully deleted old profile image');
                }
            }
        } catch (e) {
            console.warn('Error while trying to delete old profile image:', e);
            // Continue with upload even if delete fails
        }
    }
    
    // Create a unique file path
    const fileExt = profileImage.name.split('.').pop();
    const fileName = `${sessionValue.user.id}-${Date.now()}.${fileExt}`;
    const filePath = `${fileName}`;
    
    // Upload to storage
    const { error: uploadError } = await supabase.storage
        .from('profilepic')  // Use 'profilepic' bucket 
        .upload(filePath, profileImage);
        
    if (uploadError) {
        console.warn('Storage upload failed:', uploadError);
        throw new Error('Failed to upload profile image. Please try again later.');
    }
    
    // Get the public URL
    const { data: publicUrlData } = supabase.storage
        .from('profilepic')  // Use 'profilepic' bucket
        .getPublicUrl(filePath);
        
    // Update user metadata with ONLY the custom avatar URL field that won't be overwritten by OAuth
    const { error: updateError } = await supabase.auth.updateUser({
        data: { 
            custom_avatar_url: publicUrlData.publicUrl  // Only set the custom field
        }
    });
    
    if (updateError) throw updateError;
    
    // Update session store
    const { data } = await supabase.auth.getUser();
    if (data.user) {
        sessionStore.set({...sessionValue, user: data.user});
    }
    
    return publicUrlData.publicUrl;
} 