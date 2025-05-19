<script lang="ts">
    import { sessionStore } from "$lib/stores/sessionStore";
    import { onMount } from "svelte";
    import { supabase } from "$lib/supabaseClient";
    import { buttonVariants } from "$lib/components/ui/button";
    import { MAX_NAME_LENGTH, validateDisplayName, createMessageClearer } from "../utils/validation";
    
    export let error = '';
    export let success = false;
    
    let displayName = '';
    let loading = false;
    let displayNameError = '';
    
    // Set up message clearer
    const clearMessages = createMessageClearer();
    
    onMount(async () => {
        if ($sessionStore?.user) {
            displayName = $sessionStore.user.user_metadata.display_name || '';
        }
    });
    
    async function updateProfile() {
        if (!$sessionStore) return;
        
        loading = true;
        error = '';
        displayNameError = '';
        success = false;
        
        // Validate display name
        const validation = validateDisplayName(displayName);
        if (!validation.isValid) {
            displayNameError = validation.error;
            loading = false;
            clearMessages(() => {
                displayNameError = '';
            });
            return;
        }
        
        try {
            // Update user metadata
            const { error: updateError } = await supabase.auth.updateUser({
                data: { display_name: displayName }
            });
            
            if (updateError) throw updateError;
            
            success = true;
            clearMessages(() => {
                error = '';
                displayNameError = '';
                success = false;
            });
            
            // Update the session store to reflect changes
            const { data } = await supabase.auth.getUser();
            if (data.user && $sessionStore) {
                sessionStore.set({...$sessionStore, user: data.user});
            }
        } catch (e: any) {
            error = e.message || 'Failed to update profile';
            console.error('Error updating profile:', e);
            clearMessages(() => {
                error = '';
                displayNameError = '';
                success = false;
            });
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
            class="bg-white/40 backdrop-blur-sm block w-full p-1.5 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" 
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