<script lang="ts">
    import { page } from "$app/stores";

    // Get user from page data
    $: user = $page.data.user;

    // Simple placeholder image path
    const placeholderImage = "/nopicture_placeholder.png";

    // Get the profile image source with proper fallback
    $: profileImageSrc = (() => {
        if (!user) return placeholderImage;
        
        const metadata = user.user_metadata;
        
        // Priority 1: Custom avatar URL
        if (metadata?.custom_avatar_url && metadata.custom_avatar_url.trim() !== '') {
            return metadata.custom_avatar_url;
        }
        
        // Priority 2: Regular avatar URL (from OAuth)
        if (metadata?.avatar_url && metadata.avatar_url.trim() !== '') {
            return metadata.avatar_url;
        }
        
        // Fallback to placeholder
        return placeholderImage;
    })();
</script>

<div class="flex items-center mb-6">
    <div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mr-4">
        <img 
            src={profileImageSrc}
            alt="Profile"
            class="w-16 h-16 rounded-full object-cover border border-gray-200"
            on:error={(e) => {
                const img = e.currentTarget as HTMLImageElement;
                img.src = placeholderImage;
            }}
        />
    </div>
    <div>
        <h3 class="text-lg font-medium text-gray-900">
            {user?.user_metadata?.display_name || 'User'}
        </h3>
        <p class="text-sm text-gray-500">
            {user?.email || 'No email'}
        </p>
    </div>
</div> 