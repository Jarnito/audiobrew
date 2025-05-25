# FastAPI Railway Deployment Guide

## Step 1: Prepare Your Code (5 minutes)

### 1. Restore Full FastAPI Code
```bash
# Restore the full FastAPI code (undo the simplified version)
mv api/index_full.py api/index.py  # If you have this backup
# OR revert the git changes to get the full routers back
```

### 2. Ensure requirements.txt is complete
Your `api/requirements.txt` should include:
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

### 3. Create Procfile (for Railway)
Create `api/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Update api/main.py for production
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.append(str(parent_directory))

# Import the routers
from api.routers import gmail, podcast, user

app = FastAPI(title="AudioBrew API")

# Add CORS middleware - Updated for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://audiobrew.vercel.app",  # Your frontend
        "http://localhost:5173",         # Local development
        "http://localhost:3000",         # Alternative local
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(gmail.router, prefix="/api")
app.include_router(podcast.router, prefix="/api")
app.include_router(user.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "AudioBrew API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "audiobrew-api"}
```

## Step 2: Deploy to Railway (10 minutes)

### 1. Sign up for Railway
- Go to [railway.app](https://railway.app)
- Sign up with GitHub
- Connect your GitHub account

### 2. Create New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your audiobrew repository
- Select the `api` folder as the root directory

### 3. Configure Environment Variables
In Railway dashboard, add these environment variables:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OPENAI_API_KEY=your_openai_api_key
REDIRECT_URI=https://audiobrew.vercel.app/api/auth/gmail/callback
```

### 4. Deploy
- Railway will automatically detect FastAPI
- Click "Deploy"
- Wait for deployment to complete
- You'll get a URL like: `https://audiobrew-api.railway.app`

## Step 3: Update Frontend (10 minutes)

### 1. Create API config file
Create `src/lib/config.ts`:
```typescript
export const API_CONFIG = {
  baseUrl: import.meta.env.PROD 
    ? 'https://your-railway-url.railway.app'  // Replace with your Railway URL
    : 'http://localhost:8000',
  timeout: 30000
};
```

### 2. Update environment variables in Vercel
Add to Vercel environment variables:
```
PUBLIC_API_BASE_URL=https://your-railway-url.railway.app
```

### 3. Update all API calls
Find and replace in your frontend:
```typescript
// Old (internal Vercel API)
const response = await fetch('/api/podcast/list');

// New (external Railway API)
import { API_CONFIG } from '$lib/config';
const response = await fetch(`${API_CONFIG.baseUrl}/api/podcast/list`);
```

## Step 4: Test Everything (10 minutes)

### 1. Test API directly
```bash
# Test Railway API
curl https://your-railway-url.railway.app/api
curl https://your-railway-url.railway.app/health
```

### 2. Test with frontend
- Deploy updated frontend to Vercel
- Test login/signup
- Test Gmail connection
- Test podcast generation

## Step 5: Update OAuth Redirect (5 minutes)

### 1. Update Google Cloud Console
- Go to Google Cloud Console
- Update OAuth redirect URI to: `https://your-railway-url.railway.app/api/gmail/callback`

### 2. Update environment variable
Update REDIRECT_URI in Railway:
```
REDIRECT_URI=https://your-railway-url.railway.app/api/gmail/callback
```

## Troubleshooting

### Common Issues:
1. **CORS errors**: Make sure Railway URL is in CORS origins
2. **Environment variables**: Double-check all env vars are set in Railway
3. **OAuth issues**: Verify redirect URI in Google Console matches Railway URL

### Check logs:
- Railway dashboard has real-time logs
- Much better than Vercel's limited serverless logs

## Benefits of This Approach

✅ **Keeps existing code** - no rewriting needed
✅ **Solves deployment issues** - Railway handles FastAPI perfectly
✅ **Better performance** - dedicated container vs serverless
✅ **Easier debugging** - proper logs and error tracking
✅ **Cost effective** - ~$5-10/month vs Vercel issues
✅ **Scalable** - can handle more complex features later

## Next Steps

Once deployed successfully:
1. Test all functionality thoroughly
2. Monitor performance and costs
3. Consider adding monitoring (Railway has built-in metrics)
4. Document the new architecture for team 