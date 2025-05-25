<script lang="ts">
    import DangerZone from "$lib/features/profile/components/DangerZone.svelte";
</script>

<div class="bg-white/15 backdrop-blur-5xl rounded-3xl shadow-md border border-gray-200 overflow-y-auto transition-all duration-300 h-[calc(100vh-96px)] md:h-[calc(100vh-4rem)] p-6 md:p-8">
    <div class="min-h-full flex flex-col justify-center">
        <div class="w-full max-w-[350px] mx-auto">
            <h1 class="text-3xl font-bold mb-6 md:mb-10 text-center">Settings</h1>
            
            <div class="mb-8">
                <h2 class="text-lg font-semibold mb-3">General Settings</h2>
                <p class="text-gray-500 text-sm">General settings options will appear here.</p>
            </div>
            
            <div class="mb-8">
                <h2 class="text-lg font-semibold mb-3">Notification Settings</h2>
                <p class="text-gray-500 text-sm">Notification settings options will appear here.</p>
            </div>
            
            <DangerZone />
        </div>
    </div>
</div>

