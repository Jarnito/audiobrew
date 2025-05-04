<script lang="ts">
    import { Button } from '$lib/index';
    // No logic needed for static hero
  </script>
  
  <div class="min-h-[calc(100vh-4rem)] flex flex-col justify-center">
    <div class="max-w-8xl mx-auto flex flex-col md:flex-row items-center justify-between px-6 py-4 gap-4">
      <!-- Left: Text Content -->
      <div class="flex-1 max-w-xl">
        <div class="mb-4">
          <span class="inline-flex items-center px-3 py-1 rounded-full bg-white/80 text-sm font-medium text-green-600 shadow">
            <span class="mr-2 h-2 w-2 rounded-full bg-green-500 animate-pulse inline-block"></span>
            Beta Access Available Now
          </span>
        </div>
        <h1 class="text-4xl md:text-4xl font-extrabold text-black mb-6 leading-tight">
          Turn Your<br />
          Newsletters Into<br />
          Engaging Podcasts
        </h1>
        <p class="text-lg text-gray-700 mb-8">
          Transform your written content into professional audio episodes automatically. Expand your audience reach with the power of AI-generated podcasts.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 mb-8">
          <Button size="lg" class="font-semibold">
            <a href="/signup">Try Now</a>
          </Button>
          <Button size="lg" variant="outline" class="font-semibold">
            <a href="#examples">Listen to examples</a>
          </Button>
        </div>
      </div>
  
    <!-- Right: AI Engine Visualization -->
    <div class="flex-1 flex items-center justify-center relative">
      <div class="relative w-full max-w-lg mx-auto">
        <!-- Decorative circle (top left) -->
        <div class="absolute -top-8 -left-8 w-16 h-16 bg-indigo-200 rounded-full opacity-70 z-0"></div>
        <!-- Decorative square (bottom right) -->
        <div class="absolute -bottom-8 -right-8 w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-400 rounded-xl opacity-80 z-0"></div>
  
        <!-- Main card -->
        <div class="relative bg-white rounded-3xl shadow-xl p-4 pt-3 z-10">
          <!-- Step 1: Connect Email -->
          <div class="flex items-center gap-2 mb-3">
            <span class="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-purple-100">
              <!-- Link icon -->
              <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path d="M10 13a5 5 0 007.07 0l1.41-1.41a5 5 0 00-7.07-7.07l-1.41 1.41" />
                <path d="M14 11a5 5 0 00-7.07 0l-1.41 1.41a5 5 0 007.07 7.07l1.41-1.41" />
              </svg>
            </span>
            <span class="font-semibold text-purple-700 text-lg">Connect Your Email</span>
          </div>
          <div class="mb-4">
            <div class="flex gap-2 mb-2">
              <button class="flex-1 px-4 py-2 rounded-lg bg-purple-100 text-purple-700 font-medium flex items-center justify-center gap-2">
                <!-- Mail icon, fixed baseline -->
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="5" width="18" height="14" rx="2" fill="#fff"/>
                  <path d="M3 7l9 6 9-6" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <rect x="3" y="5" width="18" height="14" rx="2" stroke="#a78bfa" stroke-width="2"/>
                </svg>
                Gmail
              </button>
              <button class="flex-1 px-4 py-2 rounded-lg bg-blue-100 text-blue-700 font-medium flex items-center justify-center gap-2">
                <!-- Mail icon, fixed baseline (same as Gmail) -->
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="5" width="18" height="14" rx="2" fill="#fff"/>
                  <path d="M3 7l9 6 9-6" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <rect x="3" y="5" width="18" height="14" rx="2" stroke="#2563eb" stroke-width="2"/>
                </svg>
                Outlook
              </button>
            </div>
            <!-- Mock inbox -->
            <div class="bg-gray-50 rounded-xl border border-gray-200 p-3 space-y-1">
              <div class="h-2 w-3/4 bg-purple-200 rounded"></div>
              <div class="h-2 w-2/3 bg-gray-200 rounded"></div>
              <div class="h-2 w-1/2 bg-gray-100 rounded"></div>
            </div>
          </div>
  
          <!-- Step 2: AI Engine -->
          <div class="flex flex-col items-center my-4">
            <div class="relative flex flex-col items-center">
              <div class="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center shadow-lg">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="currentColor" stroke="currentColor" stroke-linejoin="round"/>
                </svg>
              </div>
              <span class="mt-1 px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold shadow">
                AudioBrew AI Engine
              </span>
            </div>
            <div class="h-6 w-1 bg-gradient-to-b from-indigo-400 to-purple-400 opacity-40 my-1"></div>
          </div>
  
          <!-- Step 3: Podcast Output -->
          <div>
            <div class="flex items-center gap-2 mb-1">
              <!-- Headphones icon (centered, not distorted) -->
              <span class="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-100">
                <svg class="w-6 h-6 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path d="M4 17v-2a8 8 0 0116 0v2" stroke="#6366f1" stroke-width="2" stroke-linecap="round"/>
                  <circle cx="6" cy="19" r="2" fill="#6366f1"/>
                  <circle cx="18" cy="19" r="2" fill="#6366f1"/>
                </svg>
              </span>
              <span class="font-semibold text-indigo-700 text-lg">Your Podcast</span>
            </div>
            <div class="bg-indigo-50 rounded-xl p-3 flex items-center justify-between mb-1">
              <div>
                <div class="text-sm text-indigo-900 font-medium mb-0.5">Now Playing</div>
                <div class="text-xs text-indigo-400">01:24</div>
              </div>
              <div class="flex gap-2">
                <div class="w-4 h-4 rounded-full bg-indigo-300"></div>
                <div class="w-4 h-4 rounded-full bg-purple-300"></div>
              </div>
            </div>
            <div class="flex justify-end">
              <span class="text-xs text-gray-400 italic">Listen on the go</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    </div>
  </div>
