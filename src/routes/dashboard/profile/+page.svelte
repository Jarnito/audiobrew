<script lang="ts">
    import ProfileImage from "$lib/features/profile/components/ProfileImage.svelte";
    import ProfileForm from "$lib/features/profile/components/ProfileForm.svelte";
    import EmailConnections from "$lib/features/profile/components/EmailConnections.svelte";
    import { page } from "$app/state";
    
    // Get the current user from the page store
    const user = page.data.user;
    
    // State variables for error and success messages
    // These are shared between components
    let error = '';
    let success = false;
</script>

<div class="bg-white/15 backdrop-blur-5xl rounded-3xl shadow-md border border-gray-200 overflow-y-auto transition-all duration-300 h-[calc(100vh-96px)] md:h-[calc(100vh-4rem)] p-6 md:p-8">
    <div class="min-h-full flex flex-col justify-center">
        <div class="w-full max-w-[350px] mx-auto">
            <h1 class="text-3xl font-bold mb-6 md:mb-10 text-center">Profile Settings</h1>
            
            {#if error}
                <p class="text-red-600 text-sm mb-4 text-center">{error}</p>
            {/if}
            
            {#if success}
                <p class="text-green-600 text-sm mb-4 text-center">Profile updated successfully!</p>
            {/if}
            
            <!-- Profile Picture Section -->
            <ProfileImage bind:error bind:success />

            <!-- Profile Form Section -->
            <ProfileForm bind:error bind:success />

            <!-- Email Integration Section -->
            <EmailConnections />
        </div>
    </div>
</div>