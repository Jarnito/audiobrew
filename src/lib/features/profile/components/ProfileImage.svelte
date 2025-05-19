<script lang="ts">
    import { sessionStore } from "$lib/stores/sessionStore";
    import { onMount } from "svelte";
    import { placeholderImage, createImagePreview, uploadProfileImage, getProfileImageSrc } from "../utils/profileImage";
    import { createMessageClearer } from "../utils/validation";
    
    export let error = '';
    export let success = false;
    
    let loading = false;
    let profileImage: File | null = null;
    let imagePreview: string | null = null;
    
    // Client-side only handling to fix hydration mismatch
    let mounted = false;
    let profileImageSrc = placeholderImage; // Initial value for SSR
    
    // Set up message clearer
    const clearMessages = createMessageClearer();
    
    onMount(() => {
        // Mark component as mounted to enable client-side image handling
        mounted = true;
    });
    
    // Use a reactive statement to update the image source after mounting
    $: if (mounted) {
        profileImageSrc = getProfileImageSrc(imagePreview);
    }
    
    // Handle profile image change
    async function handleProfileImageChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (!input.files || !input.files[0]) return;
        
        const file = input.files[0];
        profileImage = file;
        
        try {
            // Create preview
            imagePreview = await createImagePreview(file);
            
            // Upload the image
            loading = true;
            error = '';
            success = false;
            
            await uploadProfileImage(profileImage);
            
            // Force a refresh of the profile image source
            profileImageSrc = getProfileImageSrc(imagePreview);
            
            success = true;
            clearMessages(() => {
                error = '';
                success = false;
            });
            
        } catch (e: any) {
            error = e.message || 'Failed to upload profile image';
            console.error('Error uploading profile image:', e);
            clearMessages(() => {
                error = '';
                success = false;
            });
            
            // Clear the preview if there was an error, but don't clear any existing avatar_url
            imagePreview = null;
        } finally {
            loading = false;
        }
    }
</script>

<style>
    .profile-pic-container {
        position: relative;
        width: 96px;
        height: 96px;
        border-radius: 50%;
        overflow: hidden;
    }
    
    .profile-pic-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        opacity: 0;
        transition: opacity 0.2s ease;
        cursor: pointer;
    }
    
    .profile-pic-container:hover .profile-pic-overlay {
        opacity: 1;
    }
</style>

<div class="mb-8 flex flex-col items-center">
    <label for="profile-upload" class="block text-sm font-medium text-gray-700 mb-1">
        Profile picture
    </label>
    <div class="profile-pic-container mb-2 border-2 border-gray-200">
        <!-- Use the function to get image source with fallback -->
        <img 
            src={profileImageSrc} 
            alt="Profile" 
            class="w-full h-full object-cover"
            onerror={(e) => {
                const img = e.currentTarget as HTMLImageElement;
                img.src = placeholderImage;
            }}
        />
        <label for="profile-upload" class="profile-pic-overlay">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            <input 
                type="file" 
                id="profile-upload" 
                accept="image/jpeg,image/jpg,image/png" 
                onchange={handleProfileImageChange}
                class="hidden" 
            />
        </label>
    </div>
    <span class="text-sm text-gray-500 text-center">Change profile picture</span>
</div> 