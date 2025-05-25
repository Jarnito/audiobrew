# AudioBrew Backend Deployment on Render

This guide will walk you through deploying your AudioBrew FastAPI backend to Render.com.

## Prerequisites

✅ Your backend code is ready in the `api/` directory
✅ All dependencies are listed in `api/requirements.txt`
✅ `api/Procfile` is configured for Render
✅ Your code is pushed to GitHub

## Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account (recommended for easy repo access)
3. Verify your email if required

## Step 2: Create a New Web Service

1. **Click "New +"** in the top right corner
2. **Select "Web Service"**
3. **Connect your GitHub repository:**
   - If first time: Click "Connect account" and authorize Render to access your GitHub
   - Select your `audiobrew` repository
   - Click "Connect"

## Step 3: Configure the Web Service

Fill in the following settings:

### Basic Settings
- **Name**: `audiobrew-backend` (or any name you prefer)
- **Region**: Choose closest to your users (e.g., `Oregon (US West)`)
- **Branch**: `main` (or your default branch)
- **Root Directory**: `api`
- **Runtime**: `Python 3`

### Build & Deploy Settings
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Instance Type
- **Free** (for testing) or **Starter** ($7/month for production)

## Step 4: Environment Variables

Click "Advanced" and add these environment variables:

### Required Variables
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
OPENAI_API_KEY=your_openai_api_key
```

### Google OAuth Variables
```
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_REDIRECT_URI=https://your-render-app.onrender.com/api/auth/gmail/callback
```

### Optional Variables
```
ENVIRONMENT=production
```

## Step 5: Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (usually 2-5 minutes)
3. **Check the logs** for any errors during deployment

## Step 6: Get Your Backend URL

Once deployed successfully:
1. Your backend will be available at: `https://your-service-name.onrender.com`
2. Copy this URL - you'll need it for frontend configuration

## Step 7: Update Frontend Configuration

Update your frontend to use the new backend URL:

1. Open `src/lib/config.ts`
2. Update the production API URL:
```typescript
const API_BASE_URL = 'https://your-service-name.onrender.com';
```

## Step 8: Update Google OAuth Redirect URI

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to APIs & Services > Credentials
3. Edit your OAuth 2.0 Client ID
4. Add to "Authorized redirect URIs":
   ```
   https://your-service-name.onrender.com/api/auth/gmail/callback
   ```

## Step 9: Test Your Deployment

1. Visit `https://your-service-name.onrender.com/docs` to see the API documentation
2. Test a simple endpoint to ensure it's working
3. Test the full flow from your frontend

## Troubleshooting

### Common Issues:

**Build Fails:**
- Check that `requirements.txt` is in the `api/` directory
- Ensure all dependencies have compatible versions

**App Crashes on Start:**
- Check the logs in Render dashboard
- Verify environment variables are set correctly
- Ensure `main.py` has the correct FastAPI app instance

**CORS Errors:**
- Verify your frontend URL is in the CORS origins in `main.py`
- Check that the API URL in frontend config is correct

**OAuth Issues:**
- Verify Google OAuth redirect URI matches exactly
- Check that Google credentials are set in environment variables

## Free Tier Limitations

Render's free tier:
- ✅ 750 hours/month (enough for testing)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold starts can take 30+ seconds
- 💡 Consider upgrading to Starter ($7/month) for production

## Next Steps

After successful deployment:
1. Update your frontend's API configuration
2. Test all functionality end-to-end
3. Consider setting up monitoring and logging
4. Plan for production scaling if needed

---

**Need Help?** Check Render's documentation or the deployment logs for specific error messages. 