# Render.com FastAPI Deployment Guide

## 🚀 Quick Deploy (30 minutes total)

### **Step 1: Prepare for Render (5 minutes)**

Your code is **already compatible**! I've just updated:
- ✅ CORS to include Render URLs
- ✅ Entry point for production
- ✅ Health check endpoint

### **Step 2: Deploy to Render (10 minutes)**

1. **Sign up for Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (free)

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub repo: `audiobrew`

3. **Configure Service**
   ```
   Name: audiobrew-api
   Region: Oregon (US West) or closest to you
   Branch: main (or your current branch)
   Root Directory: api
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Choose Plan**
   - Select **"Free"** (Perfect for testing!)
   - Note: Free tier sleeps after 15 min of inactivity (normal for free plans)

### **Step 3: Environment Variables (5 minutes)**

In Render dashboard, add these environment variables:

```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key  
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OPENAI_API_KEY=your_openai_api_key
REDIRECT_URI=https://your-app-name.onrender.com/api/gmail/callback
```

**Important**: Replace `your-app-name` with your actual Render service name!

### **Step 4: Deploy & Test (5 minutes)**

1. **Click "Create Web Service"**
   - Render will automatically build and deploy
   - Takes ~3-5 minutes for first deployment
   - Watch the logs for any issues

2. **Test Your API**
   ```bash
   # Replace with your actual Render URL
   curl https://your-app-name.onrender.com/health
   curl https://your-app-name.onrender.com/
   ```

### **Step 5: Update Frontend (5 minutes)**

Update your frontend to use the new Render API:

1. **Create API config** in `src/lib/config.ts`:
   ```typescript
   export const API_CONFIG = {
     baseUrl: import.meta.env.PROD 
       ? 'https://your-app-name.onrender.com'  // Replace with actual URL
       : 'http://localhost:8000',
     timeout: 30000
   };
   ```

2. **Update environment in Vercel**:
   ```
   PUBLIC_API_BASE_URL=https://your-app-name.onrender.com
   ```

3. **Update Google OAuth**:
   - Go to Google Cloud Console
   - Update redirect URI to: `https://your-app-name.onrender.com/api/gmail/callback`

## 🎯 Benefits of Render

✅ **Free tier** - Perfect for testing and small projects  
✅ **Zero config** - Automatically detects FastAPI  
✅ **Git integration** - Auto-deploy on push  
✅ **Better logs** - Real-time debugging  
✅ **No serverless limits** - Full Python environment  
✅ **Easy scaling** - Upgrade to paid when needed ($7/month)  

## 🔍 Troubleshooting

### **Common Issues:**

1. **"Service Unavailable"**
   - Free tier sleeps after 15 min inactivity
   - First request takes ~30 seconds to wake up
   - This is normal for free tier!

2. **CORS Errors**
   - Make sure your Render URL is in CORS origins
   - Check the exact URL (should be `.onrender.com`)

3. **Environment Variables**
   - Double-check all env vars are set in Render dashboard
   - Make sure REDIRECT_URI matches your Render URL

4. **Build Failures**
   - Check build logs in Render dashboard
   - Usually means missing dependencies

### **Check Deployment:**
- Render dashboard shows real-time logs
- Much easier to debug than Vercel serverless!

## 🚀 What's Next?

Once deployed successfully:

1. **Test everything**: Login, Gmail connection, podcast generation
2. **Monitor usage**: Render dashboard shows metrics
3. **Consider upgrading**: If you need always-on service ($7/month)
4. **Scale up**: Easy to upgrade resources as you grow

## 💡 Why This Setup is Perfect

- **Frontend**: Vercel (excellent for SvelteKit)
- **Backend**: Render (excellent for FastAPI)  
- **Best of both worlds**: Each platform does what it's best at
- **Cost effective**: Free for testing, cheap for production
- **Scalable**: Easy to upgrade both services independently

You now have a **production-ready, scalable architecture**! 🎉 