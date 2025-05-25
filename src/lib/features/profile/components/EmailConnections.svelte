<script lang="ts">
    import { buttonVariants } from "$lib/components/ui/button";
    import { onMount } from "svelte";
    import { page } from "$app/stores";
    import { goto } from "$app/navigation";
    import { API_CONFIG } from '$lib/config';

    // Get user from page data
    $: user = $page.data.user;

    // UI states for Gmail connection
    let isConnected = false;
    let userEmail = '';
    let isLoading = true;
    let error = '';
    let isHovering = false;

    // UI states for Outlook connection
    let outlookConnected = false;
    let outlookEmail = '';
    let outlookLoading = false;
    let outlookError = '';
    let outlookHovering = false;

     // Check if there are URL query parameters related to Gmail connection
    onMount(async () => {
        // Handle URL parameters if coming back from OAuth flow
        const gmailConnected = $page.url.searchParams.get("gmail_connected");
        const gmailError = $page.url.searchParams.get("gmail_error");
        const email = $page.url.searchParams.get("email");
        
        // Clear URL parameters if present
        if (gmailConnected || gmailError || email) {
            try {
                // Create a clean URL without the query parameters
                const url = new URL(window.location.href);
                if (gmailConnected) url.searchParams.delete("gmail_connected");
                if (gmailError) url.searchParams.delete("gmail_error");
                if (email) url.searchParams.delete("email");
                
                // Use goto to navigate to the clean URL
                await goto(url.pathname, { replaceState: true, noScroll: true });
            } catch (err) {
                console.error("Error clearing URL parameters:", err);
            }
        }
        
        if (gmailConnected === "true") {
            // Update local state immediately for better UX
            isConnected = true;
            userEmail = email || userEmail;
        } else if (gmailError) {
            error = decodeURIComponent(gmailError);
        }
        
        // Always check the connection status
        await checkConnectionStatus();
    });

    // Function to check if Gmail is connected
    async function checkConnectionStatus() {
        if (!user?.id) return;

        try {
            const response = await fetch(API_CONFIG.url(`api/gmail/status?user_id=${user.id}`));
            
            if (response.ok) {
                const data = await response.json();
                isConnected = data.is_connected;
                userEmail = data.email || '';
                error = '';
            } else {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to check connection status' }));
                error = `Failed to check Gmail connection status: ${errorData.detail}`;
                console.error('Failed to check Gmail connection status:', response.status, errorData.detail);
            }
        } catch (err) {
            error = `Failed to check Gmail connection status: ${(err as Error)?.message}`;
            console.error('Failed to check Gmail connection status:', err);
        }
    }
    
    // Function to start Gmail authentication
    async function connectGmail() {
        if (!user?.id) return;

        try {
            isLoading = true;
            error = '';
            
            const response = await fetch(API_CONFIG.url(`api/gmail/auth?user_id=${user.id}`));
            
            if (response.ok) {
                const data = await response.json();
                if (data.auth_url) {
                    window.location.href = data.auth_url;
                } else {
                    error = 'No authorization URL received';
                }
            } else {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to start authentication' }));
                error = `Failed to start Gmail authentication: ${errorData.detail}`;
                console.error('Failed to start Gmail authentication:', response.status, errorData.detail);
            }
        } catch (err) {
            error = `Failed to start Gmail authentication: ${(err as Error)?.message}`;
            console.error('Failed to start Gmail authentication:', err);
        } finally {
            isLoading = false;
        }
    }
    
    // Function to disconnect Gmail
    async function disconnectGmail() {
        if (!user?.id) return;

        try {
            isLoading = true;
            error = '';
            
            const response = await fetch(API_CONFIG.url(`api/gmail/disconnect?user_id=${user.id}`), {
                method: "DELETE"
            });
            
            if (response.ok) {
                isConnected = false;
                userEmail = "";
            } else {
                const errorText = await response.text();
                console.error("Failed to disconnect Gmail:", response.status, errorText);
                error = "Failed to disconnect Gmail";
            }
        } catch (err) {
            console.error("Error disconnecting Gmail:", err);
            error = "Failed to disconnect Gmail";
        } finally {
            isLoading = false;
        }
    }

    // Function to handle Gmail button click based on connection status
    function handleGmailClick() {
        if (isConnected) {
            disconnectGmail();
        } else {
            connectGmail();
        }
    }

    // Placeholder for future Outlook integration
    function connectOutlook() {
        // This will be implemented when Outlook integration is ready
        console.log("Outlook connection not yet implemented");
        outlookLoading = true;
        // Simulating API call
        setTimeout(() => {
            outlookLoading = false;
        }, 1000);
    }

    // Handle Gmail hover events
    function handleGmailMouseEnter() {
        if (isConnected) {
            isHovering = true;
        }
    }

    function handleGmailMouseLeave() {
        isHovering = false;
    }

    // Handle Outlook hover events
    function handleOutlookMouseEnter() {
        if (outlookConnected) {
            outlookHovering = true;
        }
    }

    function handleOutlookMouseLeave() {
        outlookHovering = false;
    }
</script>

<div class="mt-6 pt-5 border-t">
    <h2 class="text-lg font-semibold mb-3">Email Connections</h2>
    
    <!-- Gmail Connection -->
    <div class="flex items-center justify-between mb-2 p-2 rounded-md border bg-white/50 border-gray-275">
        <div class="flex items-center">
            <img src="/gmail.png" alt="Gmail" class="w-4 h-4 mr-2 ml-1" />
            <div>
                <span class="text-sm">Gmail</span>
            </div>
            
        </div>
        <button 
            onclick={handleGmailClick}
            onmouseenter={() => isConnected && (isHovering = true)}
            onmouseleave={() => (isHovering = false)}
            class={isConnected 
                ? buttonVariants({ variant: "outline", size: "sm" }) + " flex items-center gap-1" 
                : buttonVariants({ variant: "outline", size: "sm" })
            }>
            {#if isConnected}
                {#if isHovering}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    <span class="text-red-600">Disconnect</span>
                {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                    <span class="text-green-600">Connected</span>
                {/if}
            {:else}
                Connect
            {/if}
        </button>
    </div>
    
    <!-- Outlook Connection -->
    <div class="flex items-center justify-between p-2 rounded-md border border-gray-275 bg-white/50">
        <div class="flex items-center">
            <img src="/outlook.png" alt="Outlook" class="w-4 h-4 mr-2 ml-1" />
            <div>
                <span class="text-sm">Outlook</span>
                {#if outlookConnected}
                    <span class="text-xs text-gray-500 ml-1">({outlookEmail})</span>
                {/if}
            </div>
            {#if outlookLoading}
                <p class="animate-spin text-xs text-gray-500 ml-2">●</p>
            {/if}
        </div>
        <button 
            onclick={connectOutlook}
            onmouseenter={() => outlookConnected && (outlookHovering = true)}
            onmouseleave={() => (outlookHovering = false)}
            class={outlookConnected 
                ? buttonVariants({ variant: "outline", size: "sm" }) + " flex items-center gap-1" 
                : buttonVariants({ variant: "outline", size: "sm" })
            }
        >
            {#if outlookConnected}
                {#if outlookHovering}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    <span class="text-red-600">Disconnect</span>
                {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                    <span class="text-green-600">Connected</span>
                {/if}
            {:else}
                Connect
            {/if}
        </button>
    </div>

    {#if error}
        <div class="mt-2 text-sm text-red-600">
            {error}
        </div>
    {/if}
</div> 