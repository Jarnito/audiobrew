<script lang="ts">
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { supabase } from "$lib/supabaseClient";
    import { sessionStore } from "$lib/stores/sessionStore";
    import { onMount } from "svelte";
    import { buttonVariants } from "$lib/components/ui/button";

    let displayName = '';
    let loading = false;
    let success = false;
    let error = '';
    let profileImage: File | null = null;
    let imagePreview: string | null = null;
    
    // Default placeholder
    const placeholderImage = "/nopicture_placeholder.png";
    
    // UI states for email connections (no logic yet)
    let gmailConnected = false;
    let outlookConnected = false;

    // For display name validation
    const MAX_NAME_LENGTH = 15;
    let displayNameError = '';

    // Function to clear messages after timeout
    function clearMessages() {
        setTimeout(() => {
            error = '';
            displayNameError = '';
            success = false;
        }, 5000);
    }

    // Client-side only handling to fix hydration mismatch
    let mounted = false;
    let profileImageSrc = placeholderImage; // Initial value for SSR

    onMount(async () => {
        if ($sessionStore?.user) {
            displayName = $sessionStore.user.user_metadata.display_name || '';
        }
        // Mark component as mounted to enable client-side image handling
        mounted = true;
    });
    
    // Use a reactive statement to update the image source after mounting
    $: if (mounted) {
        profileImageSrc = getProfileImageSrc();
    }
    
    // Get the profile image src with fallback
    function getProfileImageSrc() {
        // Priority 0: First check if there's a preview from a newly selected image
        // This is important for immediate feedback during upload
        if (imagePreview) {
            console.log('ProfilePage: Using local preview image');
            return imagePreview;
        }
        
        if (!$sessionStore?.user) {
            console.log('ProfilePage: No user in session store, using placeholder');
            return placeholderImage;
        }
        
        // Get avatar URL from user metadata
        const metadata = $sessionStore.user.user_metadata;
        console.log('ProfilePage: User metadata:', metadata);
        
        // Priority 1: Check for our custom avatar URL field that persists across OAuth refreshes
        if (metadata?.custom_avatar_url && metadata.custom_avatar_url.trim() !== '') {
            console.log('ProfilePage: Using custom avatar URL:', metadata.custom_avatar_url);
            return metadata.custom_avatar_url;
        }
        
        // Priority 2: Check regular avatar_url
        const avatarUrl = metadata?.avatar_url;
        console.log('ProfilePage: Avatar URL from metadata:', avatarUrl);
        
        if (avatarUrl && avatarUrl.trim() !== '') {
            // Check if this URL is from our Supabase bucket (user uploaded)
            if (avatarUrl.includes('profilepic')) {
                console.log('ProfilePage: Using Supabase profilepic image:', avatarUrl);
                return avatarUrl;
            }
            
            // Priority 3: OAuth provider avatar URL (Google, etc.)
            console.log('ProfilePage: Using OAuth provider image:', avatarUrl);
            return avatarUrl;
        }
        
        // Priority 4: Default placeholder if no avatar is available
        console.log('ProfilePage: No avatar URL found, using placeholder');
        return placeholderImage;
    }

    async function updateProfile() {
        if (!$sessionStore) return;
        
        loading = true;
        error = '';
        displayNameError = '';
        success = false;
        
        // Validate display name
        if (!displayName.trim()) {
            displayNameError = 'Username cannot be empty';
            loading = false;
            clearMessages();
            return;
        }
        
        // Validate display name length
        if (displayName.length > MAX_NAME_LENGTH) {
            displayNameError = `Username cannot exceed ${MAX_NAME_LENGTH} characters`;
            loading = false;
            clearMessages();
            return;
        }
        
        try {
            // Update user metadata
            const { error: updateError } = await supabase.auth.updateUser({
                data: { display_name: displayName }
            });
            
            if (updateError) throw updateError;
            
            success = true;
            clearMessages(); // Clear message after timeout
            
            // Update the session store to reflect changes
            const { data } = await supabase.auth.getUser();
            if (data.user && $sessionStore) {
                sessionStore.set({...$sessionStore, user: data.user});
                
                // Force a refresh of the profile image source
                // This helps ensure immediate UI update even before the reactive statement runs
                profileImageSrc = getProfileImageSrc();
            }
        } catch (e: any) {
            error = e.message || 'Failed to update profile';
            console.error('Error updating profile:', e);
            clearMessages(); // Clear message after timeout
        } finally {
            loading = false;
        }
    }

    // Handle profile image change
    async function handleProfileImageChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (!input.files || !input.files[0]) return;
        
        const file = input.files[0];
        profileImage = file;
        
        // Debug log user data before changes
        console.log('Before upload - User metadata:', $sessionStore?.user?.user_metadata);
        
        // Create preview with a size limit to avoid large data URLs
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
                ctx?.drawImage(img, 0, 0, width, height);
                
                // Get a compressed data URL for preview only
                imagePreview = canvas.toDataURL('image/jpeg', 0.7);
            };
            img.src = e.target?.result as string;
        };
        reader.readAsDataURL(file);
        
        // Upload the image
        await uploadProfileImage();
    }
    
    // Upload profile image to Supabase
    async function uploadProfileImage() {
        if (!profileImage || !$sessionStore?.user) return;
        
        loading = true;
        error = '';
        
        try {
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
            const metadata = $sessionStore.user.user_metadata;
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
            const fileName = `${$sessionStore.user.id}-${Date.now()}.${fileExt}`;
            const filePath = `${fileName}`;
            
            // Upload to storage
            const { error: uploadError } = await supabase.storage
                .from('profilepic')  // Use 'profilepic' bucket 
                .upload(filePath, profileImage);
                
            if (uploadError) {
                console.warn('Storage upload failed:', uploadError);
                error = 'Failed to upload profile image. Please try again later.';
                clearMessages(); // Clear message after timeout
                return;
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
                sessionStore.set({...$sessionStore, user: data.user});
                
                // Force a refresh of the profile image source
                // This helps ensure immediate UI update even before the reactive statement runs
                profileImageSrc = getProfileImageSrc();
            }
            
            success = true;
            clearMessages(); // Clear message after timeout
        } catch (e: any) {
            error = e.message || 'Failed to upload profile image';
            console.error('Error uploading profile image:', e);
            clearMessages(); // Clear message after timeout
            
            // Clear the preview if there was an error, but don't clear any existing avatar_url
            // This maintains our priority order even on error
            imagePreview = null;
        } finally {
            loading = false;
        }
    }

    // Handle form submission
    function handleSubmit(event: Event) {
        event.preventDefault();
        updateProfile();
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

<div class="flex h-screen">
    <Sidebar />
    <div class="flex-1 flex items-center justify-center p-6">
        <div class="w-full max-w-2xl bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300">
            <div class="p-10 flex flex-col">
                <h1 class="text-3xl font-bold mb-10 text-center">Profile Settings</h1>
                
                {#if error}
                    <p class="text-red-600 text-sm mb-4 w-[320px] mx-auto">{error}</p>
                {/if}
                
                {#if success}
                    <p class="text-green-600 text-sm mb-4 w-[320px] mx-auto">Profile updated successfully!</p>
                {/if}
                
                <div class="flex flex-col">
                    <!-- Profile elements are aligned at the same starting position -->
                    <div class="w-[320px] mx-auto">
                        <!-- Profile Picture Section -->
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

                        <form onsubmit={handleSubmit} class="space-y-3">
                            <!-- Display Name -->
                            <div>
                                <label for="displayName" class="block text-sm font-medium text-gray-700 mb-1">
                                    Username
                                </label>
                                <input 
                                    type="text" 
                                    id="displayName" 
                                    bind:value={displayName} 
                                    maxlength={MAX_NAME_LENGTH}
                                    required
                                    class="block w-full p-1.5 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" 
                                />
                                <div class="flex justify-between items-center mt-1">
                                    <span class="text-sm text-gray-500">Change your name</span>
                                    <span class="text-xs text-gray-400">{displayName.length}/{MAX_NAME_LENGTH}</span>
                                </div>
                                {#if displayNameError}
                                    <p class="text-red-600 text-xs mt-1">{displayNameError}</p>
                                {/if}
                            </div>
                            
                            <!-- Save Changes Button -->
                            <div class="py-2 pb-5">
                                <button 
                                    type="submit" 
                                    class={buttonVariants({ variant: "default" })}
                                    disabled={loading}
                                >
                                    {loading ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </form>

                        <!-- Email Integration Section -->
                        <div class="mt-6 pt-5 border-t">
                            <h2 class="text-lg font-semibold mb-3">Email Connections</h2>
                            
                            <!-- Gmail Connection -->
                            <div class="flex items-center justify-between mb-2 p-2 rounded-md {gmailConnected ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'}">
                                <div class="flex items-center">
                                    <img src="/gmail.png" alt="Gmail" class="w-4 h-4 mr-2 ml-1" />
                                    <div>
                                        <span class="text-sm">Gmail</span>
                                        {#if gmailConnected}
                                            <p class="text-xs text-gray-500">Connected</p>
                                        {/if}
                                    </div>
                                </div>
                                <button 
                                    class={gmailConnected 
                                        ? buttonVariants({ variant: "outline", size: "sm" }) + " text-green-600 border-green-600 flex items-center gap-1" 
                                        : buttonVariants({ variant: "outline", size: "sm" })
                                    }
                                >
                                    {#if gmailConnected}
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                        </svg>
                                        Connected
                                    {:else}
                                        Connect
                                    {/if}
                                </button>
                            </div>
                            
                            <!-- Outlook Connection -->
                            <div class="flex items-center justify-between p-2 rounded-md {outlookConnected ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'}">
                                <div class="flex items-center">
                                    <img src="/outlook.png" alt="Outlook" class="w-4 h-4 mr-2 ml-1" />
                                    <div>
                                        <span class="text-sm">Outlook</span>
                                        {#if outlookConnected}
                                            <p class="text-xs text-gray-500">Connected</p>
                                        {/if}
                                    </div>
                                </div>
                                <button 
                                    class={outlookConnected 
                                        ? buttonVariants({ variant: "outline", size: "sm" }) + " text-green-600 border-green-600 flex items-center gap-1" 
                                        : buttonVariants({ variant: "outline", size: "sm" })
                                    }
                                >
                                    {#if outlookConnected}
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                        </svg>
                                        Connected
                                    {:else}
                                        Connect
                                    {/if}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>