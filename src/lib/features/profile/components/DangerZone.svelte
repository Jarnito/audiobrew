<script lang="ts">
    import { buttonVariants } from "$lib/components/ui/button";
    import { supabase } from "$lib/supabaseClient";
    import { goto } from "$app/navigation";
    import { deleteAccount as deleteAccountAction } from "../utils/accountActions";
    
    export let userId: string;
    
    let isDeleting = false;
    let showConfirmation = false;
    let error = '';
    
    async function deleteAccount() {
        if (!userId) return;
        
        try {
            isDeleting = true;
            error = '';
            
            // Use the modular deleteAccount function
            const errorMessage = await deleteAccountAction(userId);
            if (errorMessage) {
                error = errorMessage;
                showConfirmation = false;
                return;
            }
            
            // Sign out and redirect to home page after successful deletion
            await supabase.auth.signOut();
            await goto('/?deleted=true');
            
        } catch (e: any) {
            error = e.message || 'Failed to delete account';
            console.error('Error deleting account:', e);
            showConfirmation = false;
        } finally {
            isDeleting = false;
        }
    }
    
    function toggleConfirmation() {
        showConfirmation = !showConfirmation;
        error = '';
    }
</script>

<div class="mt-6 pt-5 border-t">
    <h2 class="text-lg font-semibold mb-3 text-red-600">Danger Zone</h2>
    
    <div class="p-3 rounded-md bg-red-50/30 backdrop-blur-sm border border-red-200">
        {#if !showConfirmation}
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium text-gray-900">Delete Account</p>
                    <p class="text-xs text-gray-500">Permanently delete your account and all associated data.</p>
                </div>
                <button 
                    onclick={toggleConfirmation}
                    class={buttonVariants({ variant: "outline", size: "sm" }) + " text-red-600 border-red-200"}
                >
                    Delete Account
                </button>
            </div>
        {:else}
            <div class="space-y-3">
                <p class="text-sm font-medium text-gray-900">Are you sure?</p>
                <p class="text-xs text-gray-500">This action cannot be undone. All your data will be permanently deleted.</p>
                
                {#if error}
                    <p class="text-red-600 text-xs">{error}</p>
                {/if}
                
                <div class="flex items-center space-x-2">
                    <button 
                        onclick={deleteAccount}
                        disabled={isDeleting}
                        class={buttonVariants({ variant: "destructive", size: "sm" })}
                    >
                        {isDeleting ? 'Deleting...' : 'Yes, Delete My Account'}
                    </button>
                    <button 
                        onclick={toggleConfirmation}
                        disabled={isDeleting}
                        class={buttonVariants({ variant: "outline", size: "sm" })}
                    >
                        Cancel
                    </button>
                </div>
            </div>
        {/if}
    </div>
</div> 