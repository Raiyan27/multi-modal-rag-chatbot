# Deploying Multi-Modal RAG App to Render

This guide will help you deploy the Multi-Modal RAG application to Render.com.

## Prerequisites

1. A [Render](https://render.com) account (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. An OpenAI API key

## Deployment Options

### Option 1: Blueprint Deployment (Recommended)

This deploys both backend and frontend services automatically using `render.yaml`.

#### Steps:

1. **Push your code to GitHub/GitLab/Bitbucket**

   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create a New Blueprint in Render**

   - Go to https://dashboard.render.com/
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically detect `render.yaml` and create both services

3. **Set Environment Variables**
   After deployment starts, go to each service:

   - **Backend Service**:
     - Navigate to "Environment" tab
     - Add: `OPENAI_API_KEY` = `your-api-key-here`
     - Save changes (service will auto-redeploy)

4. **Update Frontend API URL**

   - After backend deploys, copy its URL (e.g., `https://multimodal-rag-backend.onrender.com`)
   - Go to Frontend service → "Environment" tab
   - Add: `API_BASE_URL` = `https://your-backend-url.onrender.com/api/v1`
   - Save changes

5. **Access Your App**
   - Frontend URL: `https://multimodal-rag-frontend.onrender.com`
   - Backend API: `https://multimodal-rag-backend.onrender.com/docs`

---

### Option 2: Manual Service Creation

If you prefer to create services individually:

#### Backend Service:

1. **Create Web Service**

   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - **Name**: `multimodal-rag-backend`
     - **Region**: Choose nearest
     - **Branch**: `main`
     - **Root Directory**: Leave empty
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Starter (or higher)

2. **Add Disk Storage**

   - In service settings, go to "Disks"
   - Click "Add Disk"
   - **Name**: `rag-data`
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: 10 GB

3. **Environment Variables**
   Add these in the "Environment" tab:

   ```
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4o
   OPENAI_VISION_MODEL=gpt-4o
   OPENAI_MINI_MODEL=gpt-4o-mini
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   PYTHONPATH=/opt/render/project/src
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   MAX_FILE_SIZE_MB=50
   DEBUG_MODE=false
   ```

4. **Health Check**
   - **Path**: `/api/v1/health`

#### Frontend Service:

1. **Create Web Service**

   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - **Name**: `multimodal-rag-frontend`
     - **Region**: Same as backend
     - **Branch**: `main`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install streamlit requests Pillow`
     - **Start Command**: `streamlit run ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
     - **Plan**: Starter

2. **Environment Variables**
   ```
   API_BASE_URL=https://your-backend-url.onrender.com/api/v1
   ```
   Replace `your-backend-url` with your actual backend service URL.

---

## Important Configuration Notes

### 1. CORS Settings

Update CORS origins in backend to allow frontend access:

- In `app/main.py`, update `CORS_ORIGINS` environment variable
- Or modify the CORS middleware to include your frontend URL

### 2. Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down will be slower (cold start ~30-60 seconds)
- 750 hours/month free compute per service
- Consider upgrading to paid plan for production use

### 3. Storage Persistence

- Disk storage persists across deployments
- Uploaded files and vector database are preserved
- Free tier includes limited disk space

### 4. Environment Variables Security

- Never commit `.env` file to Git
- Always set `OPENAI_API_KEY` through Render dashboard
- Use "Secret Files" feature for sensitive configurations

---

## Deployment Checklist

- [ ] Code pushed to Git repository
- [ ] `render.yaml` file in root directory
- [ ] `.gitignore` includes `.env` and sensitive files
- [ ] OpenAI API key ready
- [ ] Backend service deployed and healthy
- [ ] Frontend service configured with backend URL
- [ ] Test health endpoint: `https://your-backend/api/v1/health`
- [ ] Test frontend upload and query functionality

---

## Monitoring and Debugging

### View Logs

- Go to your service in Render dashboard
- Click "Logs" tab to see real-time logs
- Look for startup errors or API issues

### Common Issues

**Backend not starting:**

- Check logs for missing dependencies
- Verify `OPENAI_API_KEY` is set
- Ensure all required environment variables are present

**Frontend can't connect to backend:**

- Verify `API_BASE_URL` points to correct backend URL
- Check CORS settings in backend
- Ensure backend is healthy (green status)

**File upload failures:**

- Check disk storage is attached and mounted
- Verify `MAX_FILE_SIZE_MB` setting
- Check logs for permission errors

**Slow first request:**

- Normal on free tier (cold start)
- Consider upgrading to paid plan to keep service always on

---

## Updating Your Deployment

When you push changes to your repository:

1. Render automatically detects the changes
2. Services rebuild and redeploy
3. Health checks ensure successful deployment
4. Old version serves traffic until new version is ready

### Manual Redeploy

- Go to service dashboard
- Click "Manual Deploy" → "Deploy latest commit"

---

## Cost Optimization

**Free Tier:**

- 2 services = 2 × 750 hours/month
- Sufficient for development and light production use

**Recommendations:**

- Start with Starter plan ($7/month per service)
- Add disk storage as needed ($0.25/GB/month)
- Monitor usage in Render dashboard
- Upgrade to Standard plan for production traffic

---

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Render Blueprints Guide](https://render.com/docs/infrastructure-as-code)
- [Python on Render](https://render.com/docs/deploy-python)
- [FastAPI Deployment](https://render.com/docs/deploy-fastapi)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)

---

## Support

For issues specific to:

- **Render Platform**: https://community.render.com/
- **This Application**: Check logs and review configuration above

---

## Security Best Practices

1. **Never expose API keys in code or logs**
2. **Use environment variables for all secrets**
3. **Enable HTTPS** (automatic on Render)
4. **Set proper CORS origins** in production
5. **Regularly update dependencies**: `pip list --outdated`
6. **Monitor API usage** to prevent unexpected charges
7. **Set rate limits** in your FastAPI backend

---

**You're all set! 🚀**

Your Multi-Modal RAG application should now be live on Render.
