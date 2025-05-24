# AudioBrew Vercel Deployment Checklist

## Pre-Deployment Checklist ✅

- [x] **Code Built Successfully** - `npm run build` completed without errors
- [x] **SvelteKit Vercel Adapter** - Installed and configured 
- [x] **Vercel Configuration** - `vercel.json` properly set up
- [x] **Python API Handler** - `api/index.py` created with Mangum
- [x] **Dependencies Updated** - `requirements.txt` includes `mangum`

## Deployment Steps

### Step 1: Push to GitHub
Ensure your latest code is pushed to your GitHub repository:
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

### Step 2: Deploy via Vercel Dashboard

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign in** to your Vercel account
3. **Click "New Project"**
4. **Select "Import Git Repository"**
5. **Choose your AudioBrew repository**
6. **Configure Project Settings:**
   - Project Name: `audiobrew` (or your preferred name)
   - Framework Preset: Vercel should auto-detect "SvelteKit"
   - Root Directory: `./` (default)
   - Build Command: `npm run build` (default)
   - Output Directory: `.svelte-kit/output` (default)

### Step 3: Environment Variables ⚠️ IMPORTANT

Before clicking "Deploy", you MUST add these environment variables:

**Click "Environment Variables" section and add:**

#### **Backend API Variables:**
1. **SUPABASE_URL**
   - Value: Your Supabase project URL
   - Environment: Production, Preview, Development

2. **SUPABASE_SERVICE_KEY** 
   - Value: Your Supabase service role key
   - Environment: Production, Preview, Development

3. **GOOGLE_CLIENT_ID**
   - Value: Your Google OAuth client ID
   - Environment: Production, Preview, Development

4. **GOOGLE_CLIENT_SECRET**
   - Value: Your Google OAuth client secret
   - Environment: Production, Preview, Development

5. **OPENAI_API_KEY**
   - Value: Your OpenAI API key (for script generation)
   - Environment: Production, Preview, Development

6. **REDIRECT_URI**
   - Value: `https://your-app-name.vercel.app/api/auth/gmail/callback`
   - Environment: Production, Preview, Development
   - ⚠️ **IMPORTANT:** Replace `your-app-name` with your actual Vercel domain

#### **Frontend Variables:**
7. **PUBLIC_SUPABASE_URL**
   - Value: Your Supabase project URL (same as SUPABASE_URL)
   - Environment: Production, Preview, Development

8. **PUBLIC_SUPABASE_ANON_KEY**
   - Value: Your Supabase anonymous/public key
   - Environment: Production, Preview, Development

### Step 4: Deploy
Click **"Deploy"** and wait for the build to complete.

## Post-Deployment Configuration

### Update Google OAuth Settings

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Navigate to:** APIs & Services → Credentials
3. **Select your OAuth 2.0 Client ID**
4. **Add to Authorized redirect URIs:**
   ```
   https://your-app-name.vercel.app/auth/callback
   ```
   (Replace `your-app-name` with your actual Vercel domain)

### Update CORS Settings (Optional but Recommended)

After deployment, update the CORS origins in `api/index.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app-name.vercel.app",  # Your production domain
        "http://localhost:5173",             # Local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

## Testing Your Deployment

### 1. Frontend Tests
- [ ] Homepage loads at `https://your-app-name.vercel.app`
- [ ] Login/signup pages work
- [ ] Google OAuth flow works
- [ ] Dashboard is accessible after login

### 2. API Tests
- [ ] API status: `https://your-app-name.vercel.app/api`
- [ ] Gmail connection works in profile
- [ ] Podcast generation functions

### 3. Full User Flow
- [ ] Sign up with Google
- [ ] Connect Gmail account
- [ ] Create AudioBrew label and add emails
- [ ] Generate a podcast
- [ ] Download and share podcasts work

## Troubleshooting

### If Deployment Fails:
1. **Check build logs** in Vercel dashboard
2. **Verify environment variables** are set correctly
3. **Check for missing dependencies**

### If API doesn't work:
1. **Check Function logs** in Vercel dashboard
2. **Verify Python dependencies** in `requirements.txt`
3. **Check CORS settings**

### If OAuth doesn't work:
1. **Verify redirect URIs** in Google Cloud Console
2. **Check environment variables** `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
3. **Ensure HTTPS** is used (Vercel provides this automatically)

## Expected Results

After successful deployment:
- ✅ **Frontend URL:** `https://your-app-name.vercel.app`
- ✅ **API URL:** `https://your-app-name.vercel.app/api`
- ✅ **Function Logs:** Available in Vercel dashboard
- ✅ **Auto-deployments:** Set up for future Git pushes

## Custom Domain (Optional)

If you want a custom domain:
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed
4. Update Google OAuth redirect URIs with new domain

---

## Need Help?

If you encounter any issues:
1. Check the detailed logs in Vercel dashboard
2. Review the `VERCEL_DEPLOYMENT_GUIDE.md` for more details
3. Test API endpoints individually to isolate issues 