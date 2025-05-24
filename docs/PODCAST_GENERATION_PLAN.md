# AudioBrew Podcast Generation Plan

This document outlines the step-by-step implementation plan for the podcast generation feature in AudioBrew, which converts newsletter emails into audio podcasts.

## Overview

AudioBrew will access emails in a specific Gmail label ("AudioBrew"), extract their content, generate a podcast script using AI, and then convert that script into an audio file.

## Implementation Steps

### 1. Gmail Integration

- [x] Set up Gmail OAuth authentication (already implemented)
- [ ] Add functionality to access emails with the "AudioBrew" label
- [ ] Create an API endpoint to fetch emails from the specified label
- [ ] Implement email content extraction (HTML to text conversion)

### 2. Dashboard UI

- [ ] Create a "Generate Podcast" button on the dashboard
- [ ] Design a section to display generated podcasts
- [ ] Add loading states and error handling for the generation process
- [ ] Implement podcast playback functionality

### 3. Backend Processing

- [ ] Create an API endpoint to trigger podcast generation
- [ ] Implement a queue system for podcast generation jobs
- [ ] Set up email content aggregation from multiple sources
- [ ] Add error handling and logging

### 4. AI Integration

- [ ] Set up OpenAI API integration
- [ ] Create a prompt template for generating podcast scripts
- [ ] Implement script generation from email content
- [ ] Add quality checks for generated scripts

### 5. Audio Generation

- [ ] Set up OpenAI Text-to-Speech API integration
- [ ] Implement audio file generation from scripts
- [ ] Add audio post-processing (normalization, intro/outro)
- [ ] Set up storage for generated audio files

### 6. User Experience

- [ ] Add podcast history and management
- [ ] Implement podcast sharing functionality
- [ ] Add customization options (voice, style, length)
- [ ] Create email notifications when podcasts are ready

## Technical Flow

1. User clicks "Generate Podcast" button
2. System fetches all emails with "AudioBrew" label
3. Email content is extracted and preprocessed
4. Content is sent to OpenAI API to generate a podcast script
5. Script is sent to OpenAI TTS API to generate audio
6. Audio file is stored and linked to the user's account
7. User is notified that their podcast is ready
8. Podcast appears in the user's dashboard for playback

## Data Model

```
Podcast {
  id: string
  user_id: string
  title: string
  description: string
  audio_url: string
  script: string
  duration: number
  created_at: timestamp
  source_emails: number (count of emails used)
  status: enum (processing, completed, failed)
}
```

## API Endpoints

- `GET /api/podcasts` - List user's podcasts
- `POST /api/podcasts/generate` - Trigger podcast generation
- `GET /api/podcasts/:id` - Get podcast details
- `DELETE /api/podcasts/:id` - Delete a podcast

## Next Steps

1. Implement basic dashboard UI with "Generate Podcast" button
2. Set up Gmail label access and email fetching
3. Create podcast generation endpoint
4. Implement OpenAI integration for script generation
5. Add audio generation functionality 