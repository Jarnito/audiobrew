<script lang="ts">
	import { buttonVariants } from "$lib/components/ui/button";
	import { sessionStore } from "$lib/stores/sessionStore";
	import { goto, invalidate } from "$app/navigation";
	import { supabase } from "$lib/supabaseClient";

    async function signOut() {
		const { error } = await supabase.auth.signOut();
		if (error) {
			console.error('Error signing out:', error);
		} else {
			await goto('/');
			invalidate('supabase:auth');
		}
	}
</script>

<nav class="flex items-center justify-between border-b border-transparent px-8 py-5 bg-transparent">
	<!-- Left: Brand/Logo -->
    <div class="flex items-center gap-2">
        <a
            href="/"
            class="text-xl font-bold tracking-tight text-gray-800 transition hover:text-blue-600">
            AudioBrew
        </a>
    </div>

	<!-- Right: Signup button -->

    {#if $sessionStore}
        <div class="flex items-center gap-3">
            <span class="font-medium text-gray-700">
                {$sessionStore?.user?.user_metadata?.display_name ?? 'User'}
            </span>
            <button
                onclick={signOut}
                class={buttonVariants({ variant: "outline" })}
                type="button">
                Sign out
            </button>
        </div>
    {:else}
        <div class="flex gap-2">
            <a href="/login" class={buttonVariants({ variant: "outline" })}>
                Login
            </a>
            <a href="/signup" class={buttonVariants({ variant: "default" })}>
                Sign up
            </a>
        </div>
    {/if}
</nav>