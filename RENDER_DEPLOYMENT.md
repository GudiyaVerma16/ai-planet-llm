# Render Deployment Guide - Step by Step

## Prerequisites
- GitHub account with your `ai-planet-llm` repository
- Google Gemini API key (or OpenAI API key)
- SerpAPI key (optional, for web search)

---

## Step 1: Create Render Account

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (recommended)
4. Authorize Render to access your GitHub account

---

## Step 2: Create PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Fill in the details:
   - **Name**: `ai-planet-db`
   - **Database**: `aiplanet`
   - **User**: `aiplanet_user`
   - **Region**: Choose closest to you (e.g., `Oregon`)
   - **PostgreSQL Version**: `16` (or latest)
   - **Plan**: **Free**
3. Click **"Create Database"**
4. Wait 2-3 minutes for database to be ready
5. Once ready, go to **"Connections"** tab
6. Copy the **"Internal Database URL"** - you'll need this later
   - Format: `postgresql://aiplanet_user:password@dpg-xxxxx-a/aiplanet`

---

## Step 3: Deploy Backend

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. **Connect Repository**:
   - Click **"Connect account"** if not already connected
   - Select your repository: `GudiyaVerma16/ai-planet-llm`
   - Click **"Connect"**
3. **Configure Service**:
   - **Name**: `ai-planet-backend`
   - **Region**: Same as database (e.g., `Oregon`)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
4. **Add Environment Variables**:
   Click **"Advanced"** → **"Add Environment Variable"** and add:
   
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | Paste the Internal Database URL from Step 2 |
   | `GOOGLE_API_KEY` | Your Google Gemini API key |
   | `OPENAI_API_KEY` | Your OpenAI API key (optional) |
   | `SERPAPI_KEY` | Your SerpAPI key (optional) |
   | `UPLOAD_DIR` | `/opt/render/project/src/uploads` |
   | `ALLOWED_ORIGINS` | Leave empty for now (we'll update after frontend is deployed) |
5. **Plan**: Select **Free**
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for build to complete
8. Once deployed, copy the **Service URL** (e.g., `https://ai-planet-backend.onrender.com`)

---

## Step 4: Update Backend CORS (After Frontend URL is Known)

1. Go to your backend service in Render
2. Click **"Environment"** tab
3. Add/Update `ALLOWED_ORIGINS`:
   - Value: `https://your-frontend-url.onrender.com,http://localhost:3000`
   - (Replace `your-frontend-url` with actual frontend URL after Step 5)
4. Click **"Save Changes"**
5. Service will automatically redeploy

---

## Step 5: Deploy Frontend

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. **Connect Repository**:
   - Select your repository: `GudiyaVerma16/ai-planet-llm`
3. **Configure Service**:
   - **Name**: `ai-planet-frontend`
   - **Region**: Same as backend
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Runtime**: `Node`
   - **Build Command**: 
     ```bash
     npm install && npm run build
     ```
   - **Start Command**:
     ```bash
     npm run preview
     ```
4. **Add Environment Variables**:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: Your backend URL from Step 3 (e.g., `https://ai-planet-backend.onrender.com/api`)
5. **Plan**: Select **Free**
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for build to complete
8. Copy the **Frontend URL** (e.g., `https://ai-planet-frontend.onrender.com`)

---

## Step 6: Update Backend CORS with Frontend URL

1. Go back to backend service → **Environment** tab
2. Update `ALLOWED_ORIGINS`:
   ```
   https://ai-planet-frontend.onrender.com,http://localhost:3000
   ```
   (Replace with your actual frontend URL)
3. Save and wait for redeploy

---

## Step 7: Test Your Deployment

1. Open your frontend URL in browser
2. Try creating a workflow
3. Upload a PDF
4. Test chat functionality

---

## Important Notes

### Free Tier Limitations:
- **Spinning down**: Free services spin down after 15 minutes of inactivity
- **First request**: May take 30-60 seconds to wake up
- **Database**: Free tier has 90-day retention limit

### File Storage:
- Uploaded files are stored in `/opt/render/project/src/uploads`
- Files persist only during service runtime
- For production, consider using cloud storage (AWS S3, Cloudinary)

### Environment Variables:
- Never commit `.env` files to Git
- All secrets should be in Render's Environment Variables

### Database Migrations:
- Tables are auto-created on first startup
- If you need to reset, delete and recreate the database

---

## Troubleshooting

### Backend won't start:
- Check logs in Render Dashboard
- Verify `DATABASE_URL` is correct
- Ensure all environment variables are set

### Frontend can't connect to backend:
- Check `VITE_API_BASE_URL` is correct
- Verify CORS settings in backend
- Check browser console for errors

### Database connection errors:
- Verify `DATABASE_URL` uses Internal Database URL
- Check database is running (Status should be "Available")
- Ensure database and backend are in same region

### Build fails:
- Check build logs for specific errors
- Verify all dependencies in `requirements.txt` and `package.json`
- Ensure Python/Node versions are compatible

---

## Production Recommendations

1. **Upgrade to Paid Plan**: For always-on services
2. **Use External File Storage**: AWS S3 or Cloudinary for uploads
3. **Add Monitoring**: Set up health checks and alerts
4. **Enable HTTPS**: Render provides free SSL certificates
5. **Database Backups**: Configure automatic backups

---

## Quick Reference URLs

After deployment, you'll have:
- **Frontend**: `https://ai-planet-frontend.onrender.com`
- **Backend API**: `https://ai-planet-backend.onrender.com`
- **API Docs**: `https://ai-planet-backend.onrender.com/docs`
- **Health Check**: `https://ai-planet-backend.onrender.com/health`

---

*Your application is now live on Render! 🚀*
