<script lang="ts">
    import DangerZone from "$lib/features/profile/components/DangerZone.svelte";
</script>

<div class="flex justify-center items-center min-h-[calc(100vh-4rem)]">
    <div class="w-full max-w-2xl bg-white/15 backdrop-blur-5xl rounded-3xl shadow-md border border-gray-200 overflow-hidden transition-all duration-300 my-8">
        <div class="p-10 flex flex-col">
            <h1 class="text-3xl font-bold mb-10 text-center">Settings</h1>
            
            <div class="flex flex-col max-h-[calc(100vh-12rem)] overflow-y-auto pr-4 -mr-4">
                <div class="w-[350px] mx-auto">
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
    </div>
</div>

