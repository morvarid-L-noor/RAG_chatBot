# Deployment Checklist

Use this checklist to ensure a smooth deployment.

## ✅ Pre-Deployment

- [ ] Code is pushed to GitHub
- [ ] All environment variables are documented
- [ ] `.env` file is in `.gitignore` (should not be committed)
- [ ] Backend dependencies are in `requirements.txt`
- [ ] Frontend dependencies are in `package.json`

## 🚂 Railway (Backend) Setup

- [ ] Created Railway account
- [ ] Connected GitHub repository
- [ ] Set Root Directory to `backend`
- [ ] Set Start Command to `python main.py`
- [ ] Added environment variables:
  - [ ] `GROQ_API_KEY`
  - [ ] `USE_GROQ=true`
  - [ ] `CHROMA_DB_PATH=/data/chroma_db`
  - [ ] `ALLOWED_ORIGINS` (add after getting Vercel URL)
- [ ] Deployment successful
- [ ] Backend URL obtained: `https://________________.up.railway.app`
- [ ] Health check works: `/health` endpoint returns `{"status":"healthy"}`

## 🎨 Vercel (Frontend) Setup

- [ ] Created Vercel account
- [ ] Connected GitHub repository
- [ ] Set Root Directory to `frontend`
- [ ] Added environment variable:
  - [ ] `NEXT_PUBLIC_API_URL` = your Railway backend URL
- [ ] Deployment successful
- [ ] Frontend URL obtained: `https://________________.vercel.app`

## 🔗 Connect Frontend to Backend

- [ ] Updated Railway `ALLOWED_ORIGINS` with Vercel URL
- [ ] Redeployed Railway backend (to apply CORS changes)
- [ ] Tested frontend can communicate with backend

## 🧪 Testing

- [ ] Upload a PDF from frontend
- [ ] Add a URL from frontend
- [ ] Ask a question about uploaded content
- [ ] Verify responses include sources
- [ ] Check that both PDF and URL content are accessible

## 📝 Post-Deployment

- [ ] Bookmarked Railway dashboard
- [ ] Bookmarked Vercel dashboard
- [ ] Documented your deployment URLs
- [ ] Shared your app URL with users (optional)

## 🆘 If Something Goes Wrong

1. **Check Logs:**
   - Railway: Service → Logs tab
   - Vercel: Deployment → View Function Logs

2. **Common Issues:**
   - CORS errors → Check `ALLOWED_ORIGINS` in Railway
   - 404 errors → Verify `NEXT_PUBLIC_API_URL` in Vercel
   - API key errors → Check `GROQ_API_KEY` in Railway

3. **Redeploy:**
   - Railway: Automatic on git push
   - Vercel: Automatic on git push

