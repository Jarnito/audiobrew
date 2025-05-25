<script lang="ts">
    import PodcastGenerator from "$lib/features/podcast/components/PodcastGenerator.svelte";
</script>

<div class="bg-white/15 backdrop-blur-5xl rounded-3xl shadow-md border border-gray-200 overflow-y-auto transition-all duration-300 h-[calc(100vh-96px)] md:h-[calc(100vh-4rem)] p-6 md:p-8">
    <div class="min-h-full flex flex-col justify-center">
        <PodcastGenerator />
    </div>
</div>