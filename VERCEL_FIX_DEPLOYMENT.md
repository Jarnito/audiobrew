# Vercel Deployment Fix Guide

## Problem Analysis

The AudioBrew app was deployed to Vercel but the backend API endpoints were returning 404 errors. The issue was with the Vercel configuration not properly routing API requests to the Python serverless function.

### Symptoms
- Frontend loads correctly at `https://audiobrew.vercel.app`
- All API calls to `/api/*` return 404 errors
- Console errors show: "Failed to load resource: the server responded with a status of 404"
- Cannot fetch podcasts, connect Gmail, or use any backend functionality

### Root Cause
The `vercel.json` configuration was missing **rewrites** to route API requests to the Python serverless function at `api/index.py`.

## The Fix

### 1. Updated vercel.json
```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  },
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

The key addition is the `rewrites` section that tells Vercel:
- Any request to `/api/*` should be routed to the Python serverless function
- The function at `api/index.py` will handle all API endpoints

### 2. How It Works

1. **Frontend Request**: Frontend makes request to `/api/podcast/list`
2. **Vercel Routing**: Vercel matches the pattern `/api/(.*)` and routes to `/api/index.py`
3. **FastAPI Handling**: The `api/index.py` serverless function receives the request
4. **Router Processing**: FastAPI routes the request to the appropriate router (podcast, gmail, user)
5. **Response**: The response is sent back to the frontend

### 3. Serverless Function Structure

The `api/index.py` file correctly:
- Creates a FastAPI app with all routers
- Includes CORS middleware for the production domain
- Uses Mangum to wrap FastAPI for serverless execution
- Exports `handler` for Vercel to invoke

## Deployment Steps

### 1. Local Testing (Already Working)
- ✅ Backend runs on `http://localhost:8000`
- ✅ Frontend runs on `http://localhost:5173`
- ✅ All API endpoints work locally

### 2. Deploy to Vercel
```bash
# Option 1: Using Vercel CLI
npx vercel --prod

# Option 2: Via Vercel Dashboard
# Push to GitHub and deploy via Vercel dashboard
```

### 3. Required Environment Variables
Ensure these are set in Vercel dashboard:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `OPENAI_API_KEY`
- `REDIRECT_URI=https://audiobrew.vercel.app/api/auth/gmail/callback`

### 4. Verification
After deployment, test these endpoints:
```bash
# Root API endpoint
curl https://audiobrew.vercel.app/api

# Podcast list (should return validation error for invalid user ID)
curl "https://audiobrew.vercel.app/api/podcast/list?user_id=test"

# Gmail status (should return error for missing user)
curl "https://audiobrew.vercel.app/api/gmail/status?user_id=test"
```

Expected responses:
- `/api` → `{"message": "AudioBrew API is running"}`
- `/api/podcast/list` → `{"detail": "Invalid user ID format"}`
- `/api/gmail/status` → Error response (not 404)

## Technical Details

### Frontend API Calls
The frontend makes requests to these patterns:
- `/api/podcast/list`
- `/api/podcast/generate`
- `/api/gmail/status`
- `/api/gmail/auth`
- `/api/gmail/emails`
- `/api/user/{userId}`

### Backend Routing
The FastAPI app in `api/index.py` includes routers with prefix `/api`:
- `gmail.router` → `/api/gmail/*`
- `podcast.router` → `/api/podcast/*`
- `user.router` → `/api/user/*`

### Vercel Serverless Functions
- Python function: `api/index.py` (FastAPI with Mangum)
- Handles all API routes via rewrites
- 30-second timeout configured

## Troubleshooting

### Common Issues
1. **Still getting 404s**: Clear browser cache and check Network tab for actual URLs being called
2. **CORS errors**: Verify the production domain is in the CORS allow_origins list
3. **Environment variables**: Double-check all required env vars are set in Vercel
4. **Function timeout**: Increase maxDuration if needed (max 60s on hobby plan)

### Debugging
1. Check Vercel function logs in the dashboard
2. Test API endpoints directly with curl
3. Verify the build output includes the Python function
4. Check that dependencies are properly installed

## Success Criteria
- ✅ `/api` endpoint returns success message
- ✅ Frontend can fetch user's podcasts
- ✅ Gmail connection status works
- ✅ Can generate new podcasts
- ✅ No 404 errors in browser console 