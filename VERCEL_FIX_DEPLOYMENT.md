# Vercel Deployment Fix Guide

## Problem Analysis

The AudioBrew app was deployed to Vercel but the backend API endpoints were returning 404 errors, and after fixing the routing, 500 errors due to missing dependencies.

### Symptoms
- Frontend loads correctly at `https://audiobrew.vercel.app`
- All API calls to `/api/*` initially returned 404 errors
- After routing fix: 500 errors with "ModuleNotFoundError: No module named 'openai'"
- Console errors show: "Failed to load resource: the server responded with a status of 500"
- Cannot fetch podcasts, connect Gmail, or use any backend functionality

### Root Causes
1. **Missing Routing**: The `vercel.json` configuration was missing **rewrites** to route API requests to the Python serverless function at `api/index.py`.
2. **Missing Dependencies**: The `api/requirements.txt` was missing the `openai` dependency required by the podcast router.

## The Fix

### 1. Updated vercel.json (Routing Fix)
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

### 2. Updated api/requirements.txt (Dependency Fix)
```txt
fastapi==0.104.1
uvicorn==0.24.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-api-python-client==2.108.0
python-dotenv==1.0.0
pydantic==2.4.2
supabase==2.0.3
httpx==0.24.1
ruff==0.11.8
mangum==0.17.0
openai==1.78.1
```

The key addition is the `openai==1.78.1` dependency which is required by the podcast generation functionality.

### 3. How It Works

1. **Frontend Request**: Frontend makes request to `/api/podcast/list`
2. **Vercel Routing**: Vercel matches the pattern `/api/(.*)` and routes to `/api/index.py`
3. **FastAPI Handling**: The `api/index.py` serverless function receives the request
4. **Dependency Loading**: All required dependencies (including openai) are available
5. **Router Processing**: FastAPI routes the request to the appropriate router (podcast, gmail, user)
6. **Response**: The response is sent back to the frontend

### 4. Serverless Function Structure

The `api/index.py` file correctly:
- Creates a FastAPI app with all routers
- Includes CORS middleware for the production domain
- Uses Mangum to wrap FastAPI for serverless execution
- Exports `handler` for Vercel to invoke
- Now has all required dependencies available

## Deployment Steps

### 1. Local Testing (Already Working)
- ✅ Backend runs on `http://localhost:8000`
- ✅ Frontend runs on `http://localhost:5173`
- ✅ All API endpoints work locally
- ✅ All dependencies installed locally

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
- `/api/gmail/status` → Error response (not 404 or 500 due to missing modules)

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
- `podcast.router` → `/api/podcast/*` (requires openai dependency)
- `user.router` → `/api/user/*`

### Vercel Serverless Functions
- Python function: `api/index.py` (FastAPI with Mangum)
- Handles all API routes via rewrites
- 30-second timeout configured
- All dependencies from requirements.txt installed automatically

## Troubleshooting

### Common Issues
1. **Still getting 404s**: Clear browser cache and check Network tab for actual URLs being called
2. **500 errors with ModuleNotFoundError**: Check that all required dependencies are in `api/requirements.txt`
3. **CORS errors**: Verify the production domain is in the CORS allow_origins list
4. **Environment variables**: Double-check all required env vars are set in Vercel
5. **Function timeout**: Increase maxDuration if needed (max 60s on hobby plan)

### Debugging
1. Check Vercel function logs in the dashboard for specific error messages
2. Test API endpoints directly with curl
3. Verify the build output includes the Python function
4. Check that dependencies are properly installed during build
5. Look for import errors in the function logs

### Recent Fixes Applied
- ✅ Added routing rewrites to `vercel.json`
- ✅ Added missing `openai==1.78.1` dependency to `api/requirements.txt`
- ✅ Build tested locally and passes successfully

## Success Criteria
- ✅ `/api` endpoint returns success message
- ✅ Frontend can fetch user's podcasts (no 500 errors)
- ✅ Gmail connection status works
- ✅ Can generate new podcasts
- ✅ No 404 or 500 errors in browser console 