<script lang="ts">
	import { buttonVariants } from "$lib/components/ui/button";
	import { page } from "$app/stores";
	import { goto, invalidate } from "$app/navigation";
	import { supabase } from "$lib/supabaseClient";

    // Get user from page data
    $: user = $page.data.user;
    $: session = $page.data.session;

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
            class="flex items-center gap-2 text-xl font-bold tracking-tight text-gray-800">
            <img src="/audiobrew_logo.png" alt="AudioBrew Logo" class="h-8 w-8" />
            AudioBrew
        </a>
    </div>

	<!-- Right: Signup button -->

    {#if session}
        <div class="flex items-center gap-3">
            <span class="font-medium text-gray-700">
                {user?.user_metadata?.display_name ?? 'User'}
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