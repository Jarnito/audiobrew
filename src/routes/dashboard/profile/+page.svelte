<script lang="ts">
    import ProfileImage from "$lib/features/profile/components/ProfileImage.svelte";
    import ProfileForm from "$lib/features/profile/components/ProfileForm.svelte";
    import EmailConnections from "$lib/features/profile/components/EmailConnections.svelte";
</script>

<div class="flex justify-center items-center min-h-[calc(100vh-4rem)]">
    <div class="w-full max-w-2xl bg-white/15 backdrop-blur-5xl rounded-3xl shadow-md border border-gray-200 overflow-hidden transition-all duration-300 my-8">
        <div class="p-10 flex flex-col">
            <h1 class="text-3xl font-bold mb-10 text-center">Profile Settings</h1>
            
            <div class="flex flex-col max-h-[calc(100vh-12rem)] overflow-y-auto pr-4 -mr-4">
                <!-- Profile elements are aligned at the same starting position -->
                <div class="w-[350px] mx-auto">
                    <!-- Profile Picture Section -->
                    <ProfileImage />

                    <!-- Profile Form Section -->
                    <ProfileForm />

                    <!-- Email Integration Section -->
                    <EmailConnections />
                </div>
            </div>
        </div>
    </div>
</div>