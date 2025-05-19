<script lang="ts">
    import { goto, invalidate } from '$app/navigation';
    import { supabase } from '$lib/supabaseClient';
    import { sessionStore } from '$lib/stores/sessionStore';
    import { onMount } from 'svelte';

    let sidebarOpen = false;
    async function signOut() {
		const { error } = await supabase.auth.signOut();
		if (error) {
			console.error('Error signing out:', error);
		} else {
			await goto('/');
			invalidate('supabase:auth');
		}
	}
    
    // Make sure to use the same default placeholder across components
    const placeholderImage = "/nopicture_placeholder.png";
    
    // Client-side only code to avoid hydration mismatches
    let mounted = false;
    
    // Create a derived value for the profile image
    $: profileImageSrc = (() => {
        // Only run client-side logic after mounting
        if (!mounted) return placeholderImage;
        
        if (!$sessionStore?.user) {
            return placeholderImage;
        }
        
        const metadata = $sessionStore.user.user_metadata;
        
        // Priority 1: Check for custom_avatar_url field that persists across OAuth refreshes
        if (metadata?.custom_avatar_url && metadata.custom_avatar_url.trim() !== '') {
            return metadata.custom_avatar_url;
        }
        
        // Priority 2: Check regular (Google Auth) avatar_url
        const avatarUrl = metadata?.avatar_url;
        
        if (avatarUrl && avatarUrl.trim() !== '') {
            return avatarUrl;
        }
        
        // Priority 3: Default placeholder if no avatar is available
        return placeholderImage;
    })();
    
    onMount(() => {
        mounted = true;
    });
    
    let labelState = 'open';
    $: if (!sidebarOpen) {
      labelState = 'closing';
      setTimeout(() => { labelState = ''; }, 200);
    } else {
      labelState = 'open';
    }
  </script>
  
  <style>
    .sidebar-label {
      transition-property: opacity, transform;
      transition-timing-function: cubic-bezier(0.4,0,0.2,1);
      transition-duration: 0.7s;
      transition-delay: 0.1s;
      opacity: 0;
      transform: translateX(-12px);
      pointer-events: none;
      white-space: nowrap;
      margin-left: 0.25rem; /* closer to icon */
    }
    .sidebar-label.open {
      opacity: 1;
      transform: translateX(0);
      pointer-events: auto;
      transition-duration: 0.7s;
      transition-delay: 0.1s;
    }
    .sidebar-label.closing {
      transition-duration: 0.2s;
      transition-delay: 0s;
    }
    .sidebar-user-label {
      transition: opacity 0.7s cubic-bezier(0.4,0,0.2,1), transform 0.7s cubic-bezier(0.4,0,0.2,1);
      transition-delay: 0.1s;
      opacity: 0;
      transform: translateX(-12px);
      pointer-events: none;
      white-space: nowrap;
    }
    .sidebar-user-label.open {
      opacity: 1;
      transform: translateX(0);
      pointer-events: auto;
      transition-delay: 0.1s;
    }
  </style>
  
  <div class="fixed top-0 left-0 h-screen z-40">
    <!-- Sidebar -->
    <aside
      class={`transition-all duration-500 ease-in-out bg-white/15 backdrop-blur-5xl shadow h-full flex flex-col
        ${sidebarOpen ? 'w-[250px]' : 'w-[85px]'} rounded-r-3xl py-6 px-2 border-r border-gray-200`}
      onmouseenter={() => (sidebarOpen = true)}
      onmouseleave={() => (sidebarOpen = false)}
    >
      <!-- Top: AudioBrew Logo + Text -->
      <div class="flex items-center h-16 mb-10">
        <span class="flex items-center min-w-[70px] w-[50px] justify-center">
          <img src="/audiobrew_logo.png" alt="AudioBrew Logo" class="w-[40px] h-[40px] object-contain" />
        </span>
        <span class={`sidebar-label${sidebarOpen ? ' open' : ''}${!sidebarOpen && labelState === 'closing' ? ' closing' : ''} font-bold text-xl tracking-tight text-gray-800`} style="font-family: 'Inter', sans-serif; display: flex; align-items: center; height: 50px;">AudioBrew</span>
      </div>
  
      <!-- Navigation -->
      <nav class="flex-1 flex flex-col gap-2">
        <!-- Dashboard -->
        <a href="/dashboard" class="flex items-center px-3 py-3 hover:bg-gray-300/30 rounded-lg transition-colors duration-200">
          <span class="flex items-center justify-center min-w-[40px] w-[40px] h-6">
            <!-- Dashboard Icon -->
            <svg width="22" height="18" viewBox="0 0 32 32" fill="none"><rect x="3" y="3" width="10" height="10" stroke="black" stroke-width="2" fill="none"/><rect x="19" y="3" width="10" height="10" stroke="black" stroke-width="2" fill="none"/><rect x="3" y="19" width="10" height="10" stroke="black" stroke-width="2" fill="none"/><rect x="19" y="19" width="10" height="10" stroke="black" stroke-width="2" fill="none"/></svg>
          </span>
          <span class={`sidebar-label${sidebarOpen ? ' open' : ''}${!sidebarOpen && labelState === 'closing' ? ' closing' : ''}`}>Dashboard</span>
        </a>
        <!-- Profile -->
        <a href="/dashboard/profile" class="flex items-center px-3 py-3 hover:bg-gray-300/30 rounded-lg transition-colors duration-200">
          <span class="flex items-center justify-center min-w-[40px] w-[40px] h-6">
            <!-- Symmetrical Profile Icon -->
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 8-4 8-4s8 0 8 4"/></svg>
          </span>
          <span class={`sidebar-label${sidebarOpen ? ' open' : ''}${!sidebarOpen && labelState === 'closing' ? ' closing' : ''}`}>Profile</span>
        </a>
        <!-- Settings -->
        <a href="/dashboard/settings" class="flex items-center px-3 py-3 hover:bg-gray-300/30 rounded-lg transition-colors duration-200">
          <span class="flex items-center justify-center min-w-[40px] w-[40px] h-6">
            <!-- Settings Icon (user SVG) -->
            <svg class="feather feather-settings" fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="22" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          </span>
          <span class={`sidebar-label${sidebarOpen ? ' open' : ''}${!sidebarOpen && labelState === 'closing' ? ' closing' : ''}`}>Settings</span>
        </a>
        <!-- Log out -->
        <button type="button" onclick={signOut} class="flex items-center px-3 py-3 hover:bg-gray-300/30 rounded-lg transition-colors duration-200">
          <span class="flex items-center justify-center min-w-[40px] w-[40px] h-6">
            <!-- Logout Icon (user SVG) -->
            <svg class="feather feather-log-out" fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="22" xmlns="http://www.w3.org/2000/svg"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
          </span>
          <span class={`sidebar-label${sidebarOpen ? ' open' : ''}${!sidebarOpen && labelState === 'closing' ? ' closing' : ''}`}>Logout</span>
        </button>
      </nav>
  
      <!-- User info at the bottom -->
      <div class="mt-auto flex flex-row items-center gap-2 pb-4 pl-4">
        <span class="flex items-center min-w-[40px] w-[40px] justify-center">
          <img 
            src={profileImageSrc} 
            alt="ProfilePicture" 
            class="w-8 h-8 rounded-full object-cover border border-gray-200/50"
            onerror={(e) => {
                const img = e.currentTarget as HTMLImageElement;
                img.src = placeholderImage;
            }} 
          />
        </span>
        <span class={`sidebar-label${sidebarOpen ? ' open' : ''}${!sidebarOpen && labelState === 'closing' ? ' closing' : ''}`}>
          {$sessionStore?.user?.user_metadata?.display_name ?? 'User'}
        </span>
      </div>
    </aside>
  </div>