<script lang="ts">
    import ResponsiveNavigation from "$lib/components/ResponsiveNavigation.svelte";
</script>

<div class="flex h-screen overflow-hidden">
    <ResponsiveNavigation />
    
    <!-- Main Content -->
    <div class="flex-1 md:pl-[95px] flex flex-col md:items-center md:justify-center overflow-hidden">
        <!-- Simple wrapper, let individual pages handle their own heights -->
        <div class="w-full max-w-5xl mx-auto px-4 md:px-0 pt-[80px] pb-4 md:pt-0 md:pb-0">
            <slot />
        </div>
    </div>
</div> 