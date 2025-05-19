<script lang="ts">
    import Sidebar from "$lib/components/Sidebar.svelte";
</script>

<div class="flex h-screen overflow-hidden">
    <Sidebar />
    
    <!-- Main Content -->
    <div class="flex-1 pl-[95px] flex items-center justify-center">
        <div class="w-full max-w-5xl">
            <slot />
        </div>
    </div>
</div> 