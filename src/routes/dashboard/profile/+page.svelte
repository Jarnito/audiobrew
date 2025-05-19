<script lang="ts">
    import ProfileImage from "$lib/features/profile/components/ProfileImage.svelte";
    import ProfileForm from "$lib/features/profile/components/ProfileForm.svelte";
    import EmailConnections from "$lib/features/profile/components/EmailConnections.svelte";
    import { page } from "$app/stores";
    
    // Get the current user from the page store
    const user = $page.data.user;
    
    // State variables for error and success messages
    // These are shared between components
    let error = '';
    let success = false;
</script>

<div class="flex justify-center items-center min-h-[calc(100vh-4rem)]">
    <div class="w-full max-w-2xl bg-white/15 backdrop-blur-5xl rounded-3xl shadow-md border border-gray-200 overflow-hidden transition-all duration-300 my-8">
        <div class="p-10 flex flex-col">
            <h1 class="text-3xl font-bold mb-10 text-center">Profile Settings</h1>
            
            {#if error}
                <p class="text-red-600 text-sm mb-4 w-[350px] mx-auto text-center">{error}</p>
            {/if}
            
            {#if success}
                <p class="text-green-600 text-sm mb-4 w-[350px] mx-auto text-center">Profile updated successfully!</p>
            {/if}
            
            <div class="flex flex-col max-h-[calc(100vh-12rem)] overflow-y-auto pr-4 -mr-4">
                <!-- Profile elements are aligned at the same starting position -->
                <div class="w-[350px] mx-auto">
                    <!-- Profile Picture Section -->
                    <ProfileImage bind:error bind:success />

                    <!-- Profile Form Section -->
                    <ProfileForm bind:error bind:success />

                    <!-- Email Integration Section -->
                    {#if user}
                        <EmailConnections userId={user.id} />
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>