<script lang="ts">
    import { buttonVariants } from "$lib/components/ui/button";
    import { page } from "$app/state";
    import { onMount, onDestroy } from "svelte";
    import { fade } from "svelte/transition";
    import { downloadPodcast as downloadPodcastAction, sharePodcast as sharePodcastAction, deletePodcast as deletePodcastAction, type Podcast } from "../utils/podcastActions";
    import { checkGmailConnection, checkAudioBrewLabel as checkAudioBrewLabelUtil } from "../../gmail/utils/gmailConnection";
    import { API_CONFIG } from '$lib/config';
    
    // Get user from page data
    $: user = page.data.user;
    
    // Define types for Gmail emails
    interface GmailEmail {
        id: string;
        subject: string;
        from: string;
        date: string;
        snippet: string;
    }
    
    // State variables for podcast generation
    let isGenerating = false;
    let error = '';
    let isCheckingLabels = false;
    let hasAudioBrewLabel = false;
    let labelMessage = '';
    let emails: GmailEmail[] = [];
    let isLoadingEmails = false;
    let podcasts: Podcast[] = [];
    let isLoadingPodcasts = false;
    let refreshInterval: ReturnType<typeof setInterval> | undefined = undefined;
    let currentlyPlaying: string | null = null;
    let audioElement: HTMLAudioElement;
    let showEmails = false; // Toggle state for showing/hiding emails
    let isGmailConnected = false; // Track Gmail connection status
    
    // Variables for audio progress tracking
    let currentProgress = 0;
    let audioDuration = 0;
    let progressInterval: ReturnType<typeof setInterval> | undefined = undefined;
    let activePlayerPodcast: Podcast | null = null;
    
    // Add popover state variable in the script section after other state variables
    let showPodcastMenuId: string | null = null;
    
    // Add after state variables
    let ellipsis = '';
    let ellipsisInterval: ReturnType<typeof setInterval> | null = null;
    
    
    // Format duration from seconds to MM:SS
    function formatDuration(seconds: number): string {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    // Format date to a readable format
    function formatDate(dateString: string): string {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }
    
    // Check if user has Gmail connected and the AudioBrew label
    async function checkAudioBrewLabel() {
        if (!user) {
            error = 'You must be logged in to check Gmail labels';
            return;
        }
        
        try {
            isCheckingLabels = true;
            error = '';
            
            // First check if Gmail is connected
            const connectionStatus = await checkGmailConnection(user.id);
            isGmailConnected = connectionStatus.isConnected;
            
            if (!connectionStatus.isConnected) {
                labelMessage = '📧 Connect your Gmail or Outlook account in the <a href="/dashboard/profile" class="text-black hover:text-blue-800 underline">Profile page</a> to start generating podcasts from your newsletters.';
                hasAudioBrewLabel = false;
                return;
            }
            
            // If Gmail is connected, check for AudioBrew label
            const labelStatus = await checkAudioBrewLabelUtil(user.id);
            
            if (labelStatus.error === 'gmail_not_connected') {
                labelMessage = '📧 Connect your Gmail or Outlook account in the <a href="/dashboard/profile" class="text-black hover:text-blue-800 underline">Profile page</a> to start generating podcasts from your newsletters.';
                hasAudioBrewLabel = false;
                isGmailConnected = false;
                return;
            }
            
            if (labelStatus.error) {
                error = labelStatus.error;
                return;
            }
            
            hasAudioBrewLabel = labelStatus.hasLabel;
            
            if (hasAudioBrewLabel) {
                labelMessage = '💡 AudioBrew label found in your Gmail account.';
                // If label exists, fetch emails
                await fetchEmailsFromAudioBrewLabel();
            } else {
                labelMessage = '⚠️ AudioBrew label not found. Please create a label named "AudioBrew" in your Gmail account and add newsletters to this label.';
            }
            
        } catch (err) {
            console.error('Error checking Gmail labels:', err);
            error = 'Failed to check Gmail connection and labels';
        } finally {
            isCheckingLabels = false;
        }
    }
    
    // Fetch emails from the AudioBrew label
    async function fetchEmailsFromAudioBrewLabel() {
        if (!user) {
            error = 'You must be logged in to fetch emails';
            return;
        }
        
        try {
            isLoadingEmails = true;
            error = '';
            
            const response = await fetch(API_CONFIG.url(`api/gmail/emails?user_id=${user.id}`));
            
            if (!response.ok) {
                const data = await response.json();
                error = data.detail || 'Failed to fetch emails';
                return;
            }
            
            const data = await response.json();
            emails = data.emails || [];
            
            if (emails.length === 0) {
                labelMessage = '⏳ No emails found in the AudioBrew label. Please add some newsletters to this label.';
            } else {
                labelMessage = `💡 Found ${emails.length} emails in the AudioBrew label.`;
            }
            
        } catch (err) {
            console.error('Error fetching emails:', err);
            error = 'Failed to fetch emails from AudioBrew label';
        } finally {
            isLoadingEmails = false;
        }
    }
    
    // Fetch user's podcasts
    async function fetchPodcasts() {
        if (!user) {
            error = 'You must be logged in to fetch podcasts';
            return;
        }
        
        try {
            isLoadingPodcasts = true;
            error = '';
            
            const response = await fetch(API_CONFIG.url(`api/podcast/list?user_id=${user.id}`));
            
            if (!response.ok) {
                const data = await response.json();
                error = data.detail || 'Failed to fetch podcasts';
                return;
            }
            
            const data = await response.json();
            podcasts = data || [];
            
        } catch (err) {
            console.error('Error fetching podcasts:', err);
            error = 'Failed to fetch podcasts';
        } finally {
            isLoadingPodcasts = false;
        }
    }
    
    // Delete a podcast
    async function deletePodcast(podcastId: string) {
        if (!user) {
            error = 'You must be logged in to delete a podcast';
            return;
        }
        
        // Show confirmation dialog
        if (!confirm('Are you sure you want to delete this podcast?')) {
            return; // User canceled the deletion
        }
        
        const errorMessage = await deletePodcastAction(podcastId, user.id);
        if (errorMessage) {
            error = errorMessage;
            setTimeout(() => error = '', 3000);
            return;
        }
        
        // Show success notification
        showNotification('Podcast deleted successfully');
        
        // Refresh the podcast list
        await fetchPodcasts();
    }
    
    // Show notification
    function showNotification(message: string, duration: number = 3000) {
        error = ''; // Clear any existing error
        labelMessage = message;
        
        // Clear the message after the specified duration
        setTimeout(() => {
            if (labelMessage === message) {
                labelMessage = '';
            }
        }, duration);
    }
    
    // Handle podcast generation
    async function generatePodcast() {
        if (!user) {
            error = 'You must be logged in to generate a podcast';
            return;
        }
        
        // First check if the user has the AudioBrew label
        await checkAudioBrewLabel();
        
        if (!hasAudioBrewLabel || emails.length === 0) {
            // Don't proceed if there's no AudioBrew label or no emails
            return;
        }
        
        try {
            isGenerating = true;
            error = '';
            
            // Get email IDs
            const emailIds = emails.map(email => email.id);
            
            // Generate a default title
            // Format: "☕ Brew - May 21, 2025"
            const today = new Date();
            const formattedDate = today.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
            const title = `☕ Brew - ${formattedDate}`;
            
            // Call the API to generate the podcast
            const response = await fetch(API_CONFIG.url('api/podcast/generate'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: user.id,
                    email_ids: emailIds,
                    title: title
                })
            });
            
            if (!response.ok) {
                const data = await response.json();
                error = data.detail || 'Failed to start podcast generation';
                return;
            }
            
            const data = await response.json();
            console.log('Podcast generation started:', data);
            
            // Display confirmation to user
            labelMessage = '🎧 Podcast generation started! This may take a few minutes.';
            
            // Start refreshing podcasts every 5 seconds to check for the new one
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
            
            let initialPodcastCount = podcasts.length;
            
            refreshInterval = setInterval(async () => {
                // Fetch podcasts without setting loading state
                try {
                    const response = await fetch(API_CONFIG.url(`api/podcast/list?user_id=${user.id}`));
                    
                    if (response.ok) {
                        const data = await response.json();
                        podcasts = data || [];
                        
                        // Check if we have a new podcast
                        if (podcasts.length > initialPodcastCount) {
                            // Stop the interval once we have a new podcast
                            clearInterval(refreshInterval);
                            refreshInterval = undefined;
                            
                            // Show notification
                            showNotification('🎉 Your podcast has been generated successfully!', 5000);
                            isGenerating = false;
                        }
                    }
                } catch (err) {
                    console.error('Error checking for new podcasts:', err);
                }
            }, 5000);
            
        } catch (err) {
            console.error('Error generating podcast:', err);
            error = 'Failed to generate podcast. Please try again later.';
        } finally {
            // Note: we don't set isGenerating to false here because we want to keep showing the loading state
            // until the podcast is actually generated or an error occurs
        }
    }
    
    // Format audio URL to ensure it's absolute
    function getAudioUrl(url: string): string {
        // If it's a valid URL, return as is
        if (url.startsWith('http')) {
            return url;
        }
        
        // Otherwise, return as is (might be a placeholder)
        return url;
    }
    
    // Start tracking audio progress
    function startProgressTracking() {
        // Clear any existing interval
        if (progressInterval) {
            clearInterval(progressInterval);
        }
        
        // Update progress every 250ms for smooth progress bar
        progressInterval = setInterval(() => {
            if (audioElement && !audioElement.paused) {
                currentProgress = audioElement.currentTime;
                audioDuration = audioElement.duration || 0;
            }
        }, 250);
    }
    
    // Stop tracking audio progress
    function stopProgressTracking() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = undefined;
        }
    }
    
    // Handle seeking in the audio player
    function handleSeek(event: Event) {
        if (audioElement && audioDuration > 0) {
            const target = event.target as HTMLInputElement;
            const seekTime = parseFloat(target.value);
            audioElement.currentTime = seekTime;
            currentProgress = seekTime;
        }
    }
    
    // Play or pause audio
    function toggleAudio(podcast: Podcast): void {
        if (!audioElement) {
            audioElement = new Audio();
            
            // Set up event listeners
            audioElement.addEventListener('ended', () => {
                currentlyPlaying = null;
                activePlayerPodcast = null;
                stopProgressTracking();
                currentProgress = 0;
            });
            
            audioElement.addEventListener('error', () => {
                currentlyPlaying = null;
                activePlayerPodcast = null;
                stopProgressTracking();
                error = 'Failed to play audio. The file might not be available yet.';
                setTimeout(() => error = '', 3000);
            });
            
            audioElement.addEventListener('loadedmetadata', () => {
                audioDuration = audioElement.duration;
            });
            
            audioElement.addEventListener('play', () => {
                startProgressTracking();
            });
            
            audioElement.addEventListener('pause', () => {
                // Don't reset progress when paused
                stopProgressTracking();
            });
        }
        
        // If this podcast is already playing, pause it
        if (currentlyPlaying === podcast.id) {
            audioElement.pause();
            currentlyPlaying = null;
            // Keep the current progress and podcast
            return;
        }
        
        const audioUrl = getAudioUrl(podcast.audio_url);
        
        // If switching to a new podcast
        if (activePlayerPodcast?.id !== podcast.id) {
            // Reset progress and set new src
            currentProgress = 0;
            audioElement.src = audioUrl;
            activePlayerPodcast = podcast;
        }
        
        // Play the audio
        audioElement.play()
            .then(() => {
                currentlyPlaying = podcast.id;
            })
            .catch(err => {
                console.error('Error playing audio:', err);
                error = 'Failed to play audio. The file might not be available yet.';
                setTimeout(() => error = '', 3000);
            });
    }
    
    
    // Toggle the popover menu
    function togglePodcastMenu(podcastId: string, event: MouseEvent) {
        event.stopPropagation();
        showPodcastMenuId = showPodcastMenuId === podcastId ? null : podcastId;
    }
    
    // Close the menu when clicking outside
    function handleOutsideClick() {
        showPodcastMenuId = null;
    }
    
    // Set up error display
    $: errorMessage = error ? error : '';

    // In the script section, add a keydown handler for Escape
    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === 'Escape') {
            showPodcastMenuId = null;
        }
    }

    $: if (isGenerating) {
        if (!ellipsisInterval) {
            let step = 0;
            ellipsisInterval = setInterval(() => {
                step = (step + 1) % 4;
                ellipsis = '.'.repeat(step);
            }, 400);
        }
    } else {
        if (ellipsisInterval) {
            clearInterval(ellipsisInterval);
            ellipsisInterval = null;
        }
        ellipsis = '';
    }

    onMount(async () => {
        // Check if user is logged in
        if (user) {
            // Set loading state for podcasts immediately
            isLoadingPodcasts = true;
            
            // Check if user has AudioBrew label
            await checkAudioBrewLabel();
            
            // Fetch podcasts
            await fetchPodcasts();
        }
    });

    // Clean up interval on component destruction
    onDestroy(() => {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
        
        stopProgressTracking();
        
        // Clean up audio element
        if (audioElement) {
            audioElement.pause();
            audioElement.src = '';
        }
    });

    // Handle download action
    async function handleDownload(podcast: Podcast) {
        const errorMessage = await downloadPodcastAction(podcast);
        if (errorMessage) {
            error = errorMessage;
            setTimeout(() => error = '', 3000);
        }
    }
    
    // Handle share action
    async function handleShare(podcast: Podcast) {
        const errorMessage = await sharePodcastAction(podcast);
        if (errorMessage) {
            error = errorMessage;
            setTimeout(() => error = '', 3000);
        }
    }
</script>

<div class="w-full max-w-2xl bg-white/15 backdrop-blur-5xl rounded-3xl shadow-md border border-gray-200 overflow-visible transition-all duration-300 mx-auto my-8" onclick={handleOutsideClick} onkeydown={handleKeyDown} role="presentation" tabindex="-1">
    <div class="p-10 flex flex-col">
        <h1 class="text-3xl font-bold mb-10 text-center">Dashboard</h1>
        
        <div class="flex flex-col max-h-[calc(100vh-12rem)] overflow-y-auto pr-6 -mr-6 pb-4">
            <!-- Generate Section -->
            <div class="w-[350px] mx-auto">
                <h2 class="text-lg font-semibold mb-3">Generate</h2>
                
                {#if labelMessage}
                    <div class="text-xs mb-4 p-2 rounded {isGmailConnected && hasAudioBrewLabel ? 'bg-green-50/80' : !isGmailConnected ? 'bg-blue-50/80' : 'bg-yellow-50/80'}">
                        {@html labelMessage}
                    </div>
                {/if}
                
                {#if emails.length > 0}
                    <div class="mb-4">
                        <button 
                            class="flex items-center justify-between w-full text-xs font-medium text-gray-700 bg-gray-50/80 hover:bg-gray-100/80 py-2 px-3 rounded border border-gray-100 transition-colors"
                            onclick={() => showEmails = !showEmails}
                            aria-expanded={showEmails}
                            aria-label="Toggle email list"
                        >
                            <span>Available emails ({emails.length})</span>
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 transform transition-transform {showEmails ? 'rotate-180' : ''}" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                        
                        {#if showEmails}
                            <div class="mt-2" transition:fade={{ duration: 150 }}>
                                <ul class="list-disc pl-5 space-y-1 max-h-32 overflow-y-auto border border-gray-100 rounded p-2 bg-gray-50/80 text-xs">
                                    {#each emails as email}
                                        <li class="truncate">{email.subject} <span class="text-gray-500">from {email.from.split('<')[0]}</span></li>
                                    {/each}
                                </ul>
                            </div>
                        {/if}
                    </div>
                {/if}
                
                <div class="mb-2">
                    <button 
                        onclick={generatePodcast}
                        disabled={isGenerating || isCheckingLabels || isLoadingEmails}
                        class={buttonVariants({ variant: "default" }) + 
                            ((isGenerating || isCheckingLabels || isLoadingEmails) ? " opacity-70 cursor-not-allowed" : "") + 
                            " w-full"}
                        aria-label={isGenerating ? "Audio is brewing" : isCheckingLabels ? "Checking labels" : isLoadingEmails ? "Loading emails" : "Generate podcast"}
                    >
                        {#if isGenerating}
                            <span class="inline-block mr-2">☕</span>
                            Audio is brewing{ellipsis}
                        {:else if isCheckingLabels}
                            Checking...
                        {:else if isLoadingEmails}
                            Loading...
                        {:else}
                            Generate 🎙️
                        {/if}
                    </button>
                    
                    {#if errorMessage}
                        <p class="text-red-500 text-xs mt-2">{errorMessage}</p>
                    {/if}
                </div>
            </div>

            <!-- Your Podcasts Section -->
            <div class="mt-6 pt-5 border-t w-[350px] mx-auto overflow-visible">
                <h2 class="text-lg font-semibold mb-3">Your Podcasts</h2>
                
                {#if isLoadingPodcasts}
                    <div class="text-center py-4 text-gray-500">
                        Loading podcasts...
                    </div>
                {:else if podcasts.length === 0}
                    <div class="text-center py-4 text-gray-500">
                        <p>No podcasts created so far...</p>
                        <p class="mt-3">Click the "Generate" button to create your first podcast.</p>
                    </div>
                {:else}
                    <div class="space-y-3 overflow-visible">
                        {#each podcasts as podcast}
                            <div class="border border-gray-200/50 rounded-xl p-3 bg-gradient-to-br from-purple-100/90 to-pink-100/90 backdrop-blur-sm relative shadow-md">
                                <!-- Three dots menu button at top right -->
                                <div class="absolute top-3 right-3">
                                    <button 
                                        class="text-gray-700 hover:text-gray-900 transition-colors duration-200"
                                        aria-label="Show podcast options"
                                        onclick={(e) => togglePodcastMenu(podcast.id, e)}
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                                        </svg>
                                    </button>
                                </div>
                                
                                <div class="flex flex-col sm:flex-row gap-3 items-center sm:items-start">
                                    <!-- Podcast Icon/Play Button -->
                                    <div class="flex-shrink-0 self-center">
                                        <button 
                                            class="w-10 h-10 {currentlyPlaying === podcast.id ? 'bg-gray-600' : 'bg-black'} hover:bg-gray-800 rounded-full flex items-center justify-center text-white transition-colors duration-200"
                                            aria-label="{currentlyPlaying === podcast.id ? 'Pause' : 'Play'} podcast: {podcast.title}"
                                            onclick={() => toggleAudio(podcast)}
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                                                {#if currentlyPlaying === podcast.id}
                                                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                                                {:else}
                                                    <path d="M8 5v14l11-7z"/>
                                                {/if}
                                            </svg>
                                        </button>
                                    </div>
                                    
                                    <!-- Podcast Details -->
                                    <div class="flex-grow overflow-hidden pr-6">
                                        <h3 class="font-medium text-base truncate">{podcast.title}</h3>
                                        <div class="text-xs text-gray-500">
                                            <span>{podcast.source_emails} {podcast.source_emails === 1 ? 'source' : 'sources'}</span>
                                        </div>
                                        
                                        <!-- Audio Progress Bar - only show for active podcast -->
                                        {#if activePlayerPodcast?.id === podcast.id}
                                            <div class="mt-3 w-full">
                                                <div class="flex justify-between text-xs text-gray-700 mb-1">
                                                    <span>{formatDuration(Math.floor(currentProgress))}</span>
                                                    <span>{formatDuration(Math.floor(audioDuration))}</span>
                                                </div>
                                                <input 
                                                    type="range" 
                                                    min="0" 
                                                    max={audioDuration || podcast.duration} 
                                                    value={currentProgress} 
                                                    oninput={handleSeek}
                                                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-800"
                                                />
                                            </div>
                                        {/if}
                                    </div>
                                </div>
                                {#if showPodcastMenuId === podcast.id}
                                    <div 
                                        class="absolute left-full bottom-0 top-auto ml-4 w-12 bg-white/40 backdrop-blur-md rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 z-[9999] p-1 flex flex-col items-center space-y-2"
                                        role="menu"
                                        aria-orientation="vertical"
                                        aria-labelledby="options-menu"
                                    >
                                        <button 
                                            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-200 transition-colors"
                                            role="menuitem"
                                            aria-label="Download"
                                            onclick={() => handleDownload(podcast)}
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                                            </svg>
                                        </button>
                                        <button 
                                            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-200 transition-colors"
                                            role="menuitem"
                                            aria-label="Share"
                                            onclick={() => handleShare(podcast)}
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
                                            </svg>
                                        </button>
                                        <button 
                                            class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-red-100 transition-colors"
                                            role="menuitem"
                                            aria-label="Delete"
                                            onclick={() => deletePodcast(podcast.id)}
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-600" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                                            </svg>
                                        </button>
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div> 