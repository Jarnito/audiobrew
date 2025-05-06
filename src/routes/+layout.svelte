<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/components/Navbar.svelte';
	import { invalidate } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	let { data, children } = $props();
	let { session, supabase } = data;

	onMount(() => {
		const { data: authListener } = supabase.auth.onAuthStateChange((_, newSession) => {
			if (newSession?.expires_at !== session?.expires_at) {
				invalidate('supabase:auth');
			}
		});
		return () => authListener.subscription.unsubscribe();
	});
</script>

{#if !$page.url.pathname.startsWith('/dashboard')}
	<Navbar />
{/if}

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

<div>
	{@render children()}
</div>
