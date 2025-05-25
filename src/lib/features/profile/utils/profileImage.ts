import { supabase } from "$lib/supabaseClient";

// Default placeholder
export const placeholderImage = "/nopicture_placeholder.png";

// Simple function to get profile image source with fallback
export function getProfileImageSrc(user: any | null, imagePreview: string | null = null): string {
    // Priority 0: Preview from newly selected image
    if (imagePreview) {
        return imagePreview;
    }
    
    if (!user) {
        return placeholderImage;
    }
    
    const metadata = user.user_metadata;
    
    // Priority 1: Custom avatar URL 
    if (metadata?.custom_avatar_url && metadata.custom_avatar_url.trim() !== '') {
        return metadata.custom_avatar_url;
    }
    
    // Priority 2: Regular avatar URL (from OAuth)
    if (metadata?.avatar_url && metadata.avatar_url.trim() !== '') {
        return metadata.avatar_url;
    }
    
    // Priority 3: Default placeholder
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
                
                // Get a compressed data URL for preview
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
export async function uploadProfileImage(profileImage: File, userId: string): Promise<string> {
    if (!profileImage) {
        throw new Error('No profile image provided');
    }
    
    if (!userId) {
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
    
    // Create a unique file path
    const fileExt = profileImage.name.split('.').pop();
    const fileName = `${userId}-${Date.now()}.${fileExt}`;
    const filePath = `${fileName}`;
    
    // Upload to storage
    const { error: uploadError } = await supabase.storage
        .from('profilepic')
        .upload(filePath, profileImage);
        
    if (uploadError) {
        console.warn('Storage upload failed:', uploadError);
        throw new Error('Failed to upload profile image. Please try again later.');
    }
    
    // Get the public URL
    const { data: publicUrlData } = supabase.storage
        .from('profilepic')
        .getPublicUrl(filePath);
        
    // Update user metadata
    const { error: updateError } = await supabase.auth.updateUser({
        data: { 
            custom_avatar_url: publicUrlData.publicUrl
        }
    });
    
    if (updateError) throw updateError;
    
    return publicUrlData.publicUrl;
} 