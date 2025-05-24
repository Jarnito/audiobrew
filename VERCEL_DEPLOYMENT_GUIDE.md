# Vercel Deployment Guide for AudioBrew

## Overview
This guide will help you deploy your AudioBrew application to Vercel's hobby plan. The app consists of a SvelteKit frontend and a FastAPI backend running as serverless functions.

## Prerequisites
- Vercel account (free hobby plan)
- GitHub repository with your code
- Environment variables from your current setup

## Step 1: Environment Variables Setup

You'll need to configure these environment variables in Vercel:

### Required Environment Variables
1. **SUPABASE_URL** - Your Supabase project URL
2. **SUPABASE_SERVICE_KEY** - Your Supabase service role key
3. **GOOGLE_CLIENT_ID** - Google OAuth client ID
4. **GOOGLE_CLIENT_SECRET** - Google OAuth client secret

### Setting Environment Variables in Vercel
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable with the appropriate values

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect it's a SvelteKit project
5. Click "Deploy"

### Option B: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from your project directory
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name: audiobrew (or your preferred name)
# - In which directory is your code located? ./
```

## Step 3: Configure Domain and Environment

### Production Environment Variables
After deployment, update these environment variables:

1. **CORS Origins**: Update the CORS settings in `api/index.py` to use your actual domain
2. **OAuth Redirect URIs**: Update Google OAuth settings to use your Vercel domain

### Google OAuth Configuration
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services → Credentials
3. Edit your OAuth 2.0 Client ID
4. Add your Vercel domain to Authorized redirect URIs:
   - `https://your-app-name.vercel.app/auth/callback`

## Step 4: Test Deployment

### Frontend Tests
- ✅ Homepage loads correctly
- ✅ Login/signup flows work
- ✅ Dashboard is accessible after login

### Backend API Tests
- ✅ `https://your-app.vercel.app/api` returns API status
- ✅ Gmail connection flow works
- ✅ Podcast generation functions properly

## File Structure for Vercel

```
audiobrew/
├── src/                    # SvelteKit frontend
├── api/                    # Python serverless functions
│   ├── index.py           # Main API handler
│   ├── requirements.txt   # Python dependencies
│   └── routers/           # API route modules
├── vercel.json            # Vercel configuration
├── svelte.config.js       # SvelteKit config with Vercel adapter
└── package.json          # Node.js dependencies
```

## Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/sveltekit"
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

### svelte.config.js
```javascript
import adapter from '@sveltejs/adapter-vercel';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      runtime: 'nodejs18.x'
    })
  }
};

export default config;
```

## Common Issues and Solutions

### Issue 1: API Routes Not Working
**Problem**: API endpoints return 404 errors
**Solution**: Ensure `api/index.py` exists and all routes are properly configured

### Issue 2: Environment Variables Not Loading
**Problem**: App can't connect to Supabase or Google OAuth
**Solution**: Double-check environment variables are set in Vercel dashboard

### Issue 3: CORS Errors
**Problem**: Frontend can't access API
**Solution**: Update CORS origins in `api/index.py` to include your Vercel domain

### Issue 4: Function Timeout
**Problem**: API functions timeout on complex operations
**Solution**: The `maxDuration` is set to 30 seconds in `vercel.json`

## Monitoring and Logs

### View Function Logs
1. Go to Vercel dashboard
2. Select your project
3. Click on "Functions" tab
4. View logs for individual function calls

### Performance Monitoring
- Monitor function execution time
- Check for cold start issues
- Monitor error rates

## Cost Considerations (Hobby Plan)

### Included in Hobby Plan
- ✅ 100GB bandwidth per month
- ✅ 100GB-hours of function execution
- ✅ Custom domains
- ✅ SSL certificates

### Potential Overage Costs
- Function execution time (if exceeding 100GB-hours)
- Bandwidth (if exceeding 100GB)

## Security Best Practices

1. **Environment Variables**: Never commit secrets to code
2. **CORS Configuration**: Restrict to your actual domains in production
3. **API Keys**: Use least-privilege principles for Supabase keys
4. **OAuth Scopes**: Only request necessary Google OAuth scopes

## Updating Your Deployment

### Automatic Deployments
- Every push to your main branch will trigger a new deployment
- Pull requests create preview deployments

### Manual Deployments
```bash
# Deploy specific branch
vercel --prod

# Deploy with specific environment
vercel --env production
```

## Support and Troubleshooting

If you encounter issues:
1. Check Vercel function logs
2. Verify environment variables
3. Test API endpoints individually
4. Check Google OAuth configuration
5. Review Supabase connection settings

## Next Steps After Deployment

1. ✅ Test all functionality thoroughly
2. ✅ Set up monitoring and alerts
3. ✅ Configure custom domain (optional)
4. ✅ Set up analytics (optional)
5. ✅ Configure backup procedures 