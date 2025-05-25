<script lang="ts">
    import { page } from "$app/stores";
    import { invalidate } from "$app/navigation";
    import { supabase } from "$lib/supabaseClient";
    import { buttonVariants } from "$lib/components/ui/button";

    // Get user from page data
    $: user = $page.data.user;

    let displayName = '';
    let isLoading = false;
    let error = '';
    let success = '';

    // Initialize form when user data is available
    $: if (user) {
        displayName = user.user_metadata.display_name || '';
    }

    async function updateProfile() {
        if (!user) return;

        try {
            isLoading = true;
            error = '';
            success = '';

            const { data: { user: currentUser } } = await supabase.auth.getUser();
            if (!currentUser) {
                error = 'User not authenticated';
                return;
            }

            const { data, error: updateError } = await supabase.auth.updateUser({
                data: {
                    display_name: displayName,
                }
            });

            if (updateError) {
                error = updateError.message;
                return;
            }

            if (data.user) {
                success = 'Profile updated successfully!';
                // Force a refresh of the user data
                await invalidate('supabase:auth');
                
                // Clear success message after 3 seconds
                setTimeout(() => {
                    success = '';
                }, 3000);
            }

        } catch (err) {
            error = 'Failed to update profile';
            console.error('Error updating profile:', err);
        } finally {
            isLoading = false;
        }
    }

    function handleSubmit(event: Event) {
        event.preventDefault();
        updateProfile();
    }
</script>

<form on:submit={handleSubmit} class="space-y-4">
    <div>
        <label for="displayName" class="block text-sm font-medium text-gray-700 mb-1">
            Display Name
        </label>
        <input
            id="displayName"
            type="text"
            bind:value={displayName}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your display name"
            maxlength="50"
        />
        {#if error}
            <p class="text-red-600 text-xs mt-1">{error}</p>
        {/if}
    </div>

    <div>
        <button
            type="submit" 
            class={buttonVariants({ variant: "default" })}
            disabled={isLoading || !displayName.trim()}
        >
            {isLoading ? 'Updating...' : 'Update Profile'}
        </button>
    </div>

    {#if success}
        <div class="text-green-600 text-sm">
            {success}
        </div>
    {/if}
</form> 