<script lang="ts">
    import { buttonVariants } from "$lib/components/ui/button";
    import { supabase } from "$lib/supabaseClient";
    import { page } from "$app/stores";
    import { goto, invalidate } from "$app/navigation";

    // Get user from page data
    $: user = $page.data.user;

    // Get the current page path
    $: currentPath = $page.url.pathname;

    interface NavItem {
        href: string;
        label: string;
        icon: string;
        active?: boolean;
    }

    const navItems: NavItem[] = [
        {
            href: "/dashboard",
            label: "Generate",
            icon: "🎙️"
        },
        {
            href: "/dashboard/profile",
            label: "Profile",
            icon: "👤"
        }
    ];

    async function signOut() {
        if (!user) return;

        try {
            const metadata = user.user_metadata;
            
            // Remove from localStorage
            if (metadata?.email_url) {
                localStorage.removeItem('emailUrl');
            }
            if (metadata?.display_name) {
                localStorage.removeItem('displayName');
            }
            
            // Sign out from Supabase
            const { error } = await supabase.auth.signOut();
            if (error) {
                console.error('Error signing out:', error);
            } else {
                await goto('/');
                invalidate('supabase:auth');
            }
            
        } catch (error) {
            console.error('Error during sign out process:', error);
        }
    }
</script>

<aside class="w-64 border-r border-gray-200 bg-gray-50/30 backdrop-blur-sm p-6">
    <!-- Profile Section -->
    <div class="mb-8">
        <div class="flex items-center mb-4">
            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center mr-3">
                <span class="text-white font-medium text-sm">
                    {user?.user_metadata?.display_name?.charAt(0).toUpperCase() || 'U'}
                </span>
            </div>
            <div>
                <p class="font-medium text-gray-900">
                    {user?.user_metadata?.display_name ?? 'User'}
                </p>
                <p class="text-sm text-gray-500">Free Plan</p>
            </div>
        </div>
    </div>

    <!-- Navigation -->
    <nav class="space-y-2 mb-8">
        {#each navItems as item}
            <a
                href={item.href}
                class="flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
                       {currentPath === item.href 
                           ? 'bg-blue-100 text-blue-700' 
                           : 'text-gray-700 hover:bg-gray-100'
                       }"
            >
                <span class="mr-3">{item.icon}</span>
                {item.label}
            </a>
        {/each}
    </nav>

    <!-- Sign Out -->
    <div class="mt-auto pt-6 border-t border-gray-200">
        <button
            onclick={signOut}
            class={buttonVariants({ variant: "outline", size: "sm" }) + " w-full justify-start text-gray-700"}
        >
            <span class="mr-2">🚪</span>
            Sign Out
        </button>
    </div>
</aside>