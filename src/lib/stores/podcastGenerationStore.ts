/**
 * Global store for podcast generation state
 * Persists across page navigation to maintain UI state
 */

import { writable } from 'svelte/store';
import { get } from 'svelte/store';

interface PodcastGenerationState {
  isGenerating: boolean;
  startTime: number | null;
  initialPodcastCount: number;
}

const defaultState: PodcastGenerationState = {
  isGenerating: false,
  startTime: null,
  initialPodcastCount: 0
};

// Create the store
export const podcastGenerationStore = writable<PodcastGenerationState>(defaultState);

// Helper functions
export const podcastGeneration = {
  start: (initialCount: number) => {
    podcastGenerationStore.set({
      isGenerating: true,
      startTime: Date.now(),
      initialPodcastCount: initialCount
    });
  },
  
  stop: () => {
    podcastGenerationStore.set(defaultState);
  },
  
  isActive: (currentPodcastCount: number): boolean => {
    const state = get(podcastGenerationStore);
    return state.isGenerating && currentPodcastCount <= state.initialPodcastCount;
  }
}; 