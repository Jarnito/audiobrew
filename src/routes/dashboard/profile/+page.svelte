<script lang="ts">
    import Sidebar from "$lib/components/Sidebar.svelte";
    import ProfileImage from "$lib/features/profile/components/ProfileImage.svelte";
    import ProfileForm from "$lib/features/profile/components/ProfileForm.svelte";
    import EmailConnections from "$lib/features/profile/components/EmailConnections.svelte";
    
    // State variables for error and success messages
    // These are shared between components
    let error = '';
    let success = false;
</script>

<div class="flex h-screen">
    <Sidebar />
    <div class="flex-1 flex items-center justify-center p-6">
        <div class="w-full max-w-2xl bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300">
            <div class="p-10 flex flex-col">
                <h1 class="text-3xl font-bold mb-10 text-center">Profile Settings</h1>
                
                {#if error}
                    <p class="text-red-600 text-sm mb-4 w-[320px] mx-auto text-center">{error}</p>
                {/if}
                
                {#if success}
                    <p class="text-green-600 text-sm mb-4 w-[320px] mx-auto text-center">Profile updated successfully!</p>
                {/if}
                
                <div class="flex flex-col">
                    <!-- Profile elements are aligned at the same starting position -->
                    <div class="w-[320px] mx-auto">
                        <!-- Profile Picture Section -->
                        <ProfileImage bind:error bind:success />

                        <!-- Profile Form Section -->
                        <ProfileForm bind:error bind:success />

                        <!-- Email Integration Section -->
                        <EmailConnections />
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>