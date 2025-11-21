# Deployment Guide

This guide will help you deploy your RAG Chatbot to production using **Vercel** (frontend) and **Railway** (backend).

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free)
3. **Railway Account** - Sign up at [railway.app](https://railway.app) (free tier available)
4. **Groq API Key** - Get one at [console.groq.com](https://console.groq.com)

## 🚀 Step 1: Push Code to GitHub

1. Initialize git repository (if not already done):

```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create a new repository on GitHub and push:

```bash
git remote add origin https://github.com/yourusername/rag-chatbot.git
git branch -M main
git push -u origin main
```

## 🔧 Step 2: Deploy Backend to Railway

### 2.1 Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will detect it's a Python project

### 2.2 Configure Backend Settings

1. In Railway dashboard, click on your service
2. Go to **Settings** tab
3. Set the **Root Directory** to `backend`
4. Set the **Start Command** to: `python main.py`

### 2.3 Add Environment Variables

Go to **Variables** tab and add:

```env
GROQ_API_KEY=your_groq_api_key_here
USE_GROQ=true
CHROMA_DB_PATH=/data/chroma_db
PORT=8000
```

**Important Notes:**

- Replace `your_groq_api_key_here` with your actual Groq API key
- Railway provides persistent storage at `/data` - use this for ChromaDB
- Railway automatically sets `PORT` but you can specify it

### 2.4 Deploy

1. Railway will automatically start building and deploying
2. Wait for deployment to complete (usually 2-5 minutes)
3. Once deployed, Railway will provide a URL like: `https://your-app-name.up.railway.app`
4. **Copy this URL** - you'll need it for the frontend

### 2.5 Test Backend

Visit: `https://your-app-name.up.railway.app/health`

You should see: `{"status":"healthy"}`

## 🎨 Step 3: Deploy Frontend to Vercel

### 3.1 Import Project to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Vercel will auto-detect Next.js

### 3.2 Configure Frontend Settings

1. **Root Directory**: Set to `frontend`
2. **Framework Preset**: Next.js (auto-detected)
3. **Build Command**: `npm run build` (default)
4. **Output Directory**: `.next` (default)

### 3.3 Add Environment Variables

Go to **Settings** → **Environment Variables** and add:

```env
NEXT_PUBLIC_API_URL=https://your-app-name.up.railway.app
```

**Important:** Replace `your-app-name.up.railway.app` with your actual Railway backend URL (from Step 2.4)

### 3.4 Deploy

1. Click **"Deploy"**
2. Wait for build to complete (usually 1-2 minutes)
3. Vercel will provide a URL like: `https://your-app-name.vercel.app`

### 3.5 Test Frontend

Visit your Vercel URL and test:

1. Upload a PDF
2. Add a URL
3. Ask questions

## 🔒 Step 4: Update CORS Settings (Important!)

Your backend needs to allow requests from your Vercel frontend.

1. Go back to Railway dashboard
2. Open your backend service
3. Go to **Variables** tab
4. Add a new variable:

```env
ALLOWED_ORIGINS=https://your-app-name.vercel.app
```

5. Update `backend/main.py` to use this environment variable (see below)

## 📝 Step 5: Update Backend CORS Configuration

Update your backend to allow your Vercel domain:

```python
# In backend/main.py, update the CORS middleware:
import os

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy to Railway.

## ✅ Step 6: Verify Deployment

1. **Backend Health Check:**

   - Visit: `https://your-railway-url/health`
   - Should return: `{"status":"healthy"}`

2. **Frontend:**

   - Visit your Vercel URL
   - Try uploading a PDF
   - Try adding a URL
   - Ask a question

3. **Check Logs:**
   - Railway: View logs in Railway dashboard
   - Vercel: View logs in Vercel dashboard

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Backend not starting

- Check Railway logs
- Verify all environment variables are set
- Ensure `CHROMA_DB_PATH` points to `/data/chroma_db`

**Problem:** 404 errors

- Verify Railway URL is correct
- Check that backend is running (view logs)

**Problem:** CORS errors

- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Check CORS middleware configuration

### Frontend Issues

**Problem:** Can't connect to backend

- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check that backend URL is accessible
- Ensure CORS is configured properly

**Problem:** Build fails

- Check Vercel build logs
- Ensure all dependencies are in `package.json`
- Verify Node.js version compatibility

## 🔄 Updating Your Deployment

### Backend Updates

1. Push changes to GitHub
2. Railway will automatically redeploy
3. Monitor logs in Railway dashboard

### Frontend Updates

1. Push changes to GitHub
2. Vercel will automatically redeploy
3. Monitor build logs in Vercel dashboard

## 💰 Cost Considerations

### Free Tier Limits

**Railway:**

- $5 free credit per month
- Sufficient for small to medium usage
- ChromaDB storage is included

**Vercel:**

- Unlimited deployments
- 100GB bandwidth/month
- Perfect for frontend hosting

**Groq:**

- Free tier with generous limits
- Fast inference
- No credit card required

## 📊 Monitoring

### Railway Monitoring

- View logs in Railway dashboard
- Monitor resource usage
- Set up alerts if needed

### Vercel Monitoring

- View analytics in Vercel dashboard
- Monitor build times
- Check deployment status

## 🎉 You're Done!

Your RAG Chatbot is now live! Share your Vercel URL with others to use your application.

## 🔗 Quick Reference

- **Backend URL:** `https://your-app-name.up.railway.app`
- **Frontend URL:** `https://your-app-name.vercel.app`
- **Railway Dashboard:** [railway.app](https://railway.app)
- **Vercel Dashboard:** [vercel.com](https://vercel.com)
