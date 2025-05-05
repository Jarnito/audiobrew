<script lang="ts">
	import '../app.css';
	import { sessionStore } from '$lib/stores/sessionStore';
	import { buttonVariants } from "$lib/components/ui/button";
	import { invalidate, goto } from '$app/navigation';
	import { onMount } from 'svelte';
	let { data, children } = $props();
	let { session, supabase } = data;

	async function signOut() {
		const { error } = await supabase.auth.signOut();
		if (error) {
			console.error('Error signing out:', error);
		} else {
			await goto('/');
			invalidate('supabase:auth');
		}
	}

	onMount(() => {
		const { data: authListener } = supabase.auth.onAuthStateChange((_, newSession) => {
			if (newSession?.expires_at !== session?.expires_at) {
				invalidate('supabase:auth');
			}
		});
		return () => authListener.subscription.unsubscribe();
	});
</script>

<style>
	@keyframes gradientMove {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}
	.animated-gradient-bg {
		position: fixed;
		inset: 0;
		z-index: -10;
		width: 100vw;
		height: 100vh;
		background: linear-gradient(120deg, #f5f6fa, #ece9fc, #e0e7ff, #fdf6fb, #f5f6fa);
		background-size: 400% 400%;
		animation: gradientMove 10s ease-in-out infinite;
	}
	@keyframes blob1 {
		0%, 100% { transform: translate(0, 0) scale(1); }
		50% { transform: translate(48px, 36px) scale(1.12); }
	}
	@keyframes blob2 {
		0%, 100% { transform: translate(0, 0) scale(1); }
		50% { transform: translate(-36px, 60px) scale(1.16); }
	}
	@keyframes blob3 {
		0%, 100% { transform: translate(0, 0) scale(1); }
		50% { transform: translate(64px, -48px) scale(1.01); }
	}
	.bg-blob {
		position: fixed;
		border-radius: 9999px;
		filter: blur(36px);
		opacity: 0.38;
		z-index: -9;
		pointer-events: none;
		transition: opacity 0.3s;
	}
	.blob1 {
		width: 340px; height: 340px;
		background: #a3a6fd;
		top: 10%; left: 5%;
		animation: blob1 16s ease-in-out infinite;
	}
	.blob2 {
		width: 260px; height: 260px;
		background: #f7b6e9;
		bottom: 8%; right: 10%;
		animation: blob2 20s ease-in-out infinite;
	}
	.blob3 {
		width: 200px; height: 200px;
		background: #b6c7fa;
		top: 60%; right: 25%;
		animation: blob3 18s ease-in-out infinite;
	}
</style>

<div class="animated-gradient-bg"></div>
<div class="bg-blob blob1"></div>
<div class="bg-blob blob2"></div>
<div class="bg-blob blob3"></div>

<div class="min-h-[calc(100vh-4rem)]">
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
					{$sessionStore.user.user_metadata.display_name}
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
	{@render children()}
</div>
