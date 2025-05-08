<script lang="ts">
    import { buttonVariants } from "$lib/components/ui/button";
    
    // UI states for email connections (no logic yet)
    let gmailConnected = false;
    let outlookConnected = false;
</script>

<div class="mt-6 pt-5 border-t">
    <h2 class="text-lg font-semibold mb-3">Email Connections</h2>
    
    <!-- Gmail Connection -->
    <div class="flex items-center justify-between mb-2 p-2 rounded-md {gmailConnected ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'}">
        <div class="flex items-center">
            <img src="/gmail.png" alt="Gmail" class="w-4 h-4 mr-2 ml-1" />
            <div>
                <span class="text-sm">Gmail</span>
                {#if gmailConnected}
                    <p class="text-xs text-gray-500">Connected</p>
                {/if}
            </div>
        </div>
        <button 
            class={gmailConnected 
                ? buttonVariants({ variant: "outline", size: "sm" }) + " text-green-600 border-green-600 flex items-center gap-1" 
                : buttonVariants({ variant: "outline", size: "sm" })
            }
        >
            {#if gmailConnected}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                Connected
            {:else}
                Connect
            {/if}
        </button>
    </div>
    
    <!-- Outlook Connection -->
    <div class="flex items-center justify-between p-2 rounded-md {outlookConnected ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 border border-gray-200'}">
        <div class="flex items-center">
            <img src="/outlook.png" alt="Outlook" class="w-4 h-4 mr-2 ml-1" />
            <div>
                <span class="text-sm">Outlook</span>
                {#if outlookConnected}
                    <p class="text-xs text-gray-500">Connected</p>
                {/if}
            </div>
        </div>
        <button 
            class={outlookConnected 
                ? buttonVariants({ variant: "outline", size: "sm" }) + " text-green-600 border-green-600 flex items-center gap-1" 
                : buttonVariants({ variant: "outline", size: "sm" })
            }
        >
            {#if outlookConnected}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                Connected
            {:else}
                Connect
            {/if}
        </button>
    </div>
</div> 