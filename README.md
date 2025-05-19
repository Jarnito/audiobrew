# AudioBrew

AudioBrew is an application that converts newsletter emails into podcasts, allowing you to listen to your favorite newsletters on the go.

## Features

- **Gmail Integration**: Connect your Gmail account and use the "AudioBrew" label to mark newsletters for conversion
- **Podcast Generation**: Convert your newsletter emails into audio podcasts using OpenAI's TTS API
- **Podcast Management**: View, play, download, share, and delete your generated podcasts

## Getting Started

### Prerequisites

- Node.js (v16 or later)
- Python (v3.9 or later)
- Supabase account for database and storage
- OpenAI API key for text-to-speech

### Installation

1. Clone the repository
2. Install frontend dependencies:

```bash
npm install
```

3. Install backend dependencies:

```bash
cd api
pip install -r requirements.txt
```

4. Set up environment variables:

Create a `.env` file in the root directory with the following variables:

```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=http://localhost:5173/api/auth/gmail/callback
OPENAI_API_KEY=your_openai_api_key
```

5. Set up Supabase:
   - Run database migrations:
   ```bash
   psql -h your_supabase_host -U postgres -d postgres -f migrations/gmail_connections.sql
   psql -h your_supabase_host -U postgres -d postgres -f migrations/podcasts.sql
   ```
   - Set up storage bucket by following the instructions in `docs/supabase_setup.md`

## Development

Start the frontend development server:

```bash
npm run dev
```

Start the backend API server:

```bash
python run_api.py
```

## How It Works

1. Connect your Gmail account in the Profile section
2. Create a label called "AudioBrew" in your Gmail account
3. Add newsletters to this label
4. Go to the Dashboard and click "Generate" to create a podcast from your labeled emails
5. The system will:
   - Fetch the emails from your Gmail account
   - Generate a podcast script using OpenAI's GPT-4o
   - Convert the script to audio using OpenAI's TTS API
   - Store the audio in Supabase storage
   - Save the podcast metadata in the database
6. Listen to, download, or share your generated podcasts

## API Endpoints

### Gmail API

- `GET /api/gmail/auth`: Start the Gmail OAuth flow
- `GET /api/gmail/status`: Check Gmail connection status
- `GET /api/gmail/labels`: Check if the AudioBrew label exists
- `GET /api/gmail/emails`: Get emails with the AudioBrew label

### Podcast API

- `POST /api/podcast/generate`: Generate a podcast from emails
- `GET /api/podcast/list`: List all podcasts for a user
- `GET /api/podcast/{podcast_id}`: Get a specific podcast
- `DELETE /api/podcast/{podcast_id}`: Delete a podcast

## License

MIT
