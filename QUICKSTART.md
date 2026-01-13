# Quick Start Guide - Deploy to Render (Free Tier)

## Prerequisites

- GitHub account
- Render account (free tier)
- OpenAI API key

---

## 🚀 Deploy to Render (5 Minutes)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Deploy Backend

- Go to https://dashboard.render.com/
- Click "New +" → "Web Service"
- Connect your repository
- **Configure**:
  - Name: `multimodal-rag-backend`
  - Build: `pip install -r requirements.txt`
  - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - Instance: Free
- **Environment Variables**:
  - `OPENAI_API_KEY` = your key
  - `PYTHONPATH` = `/opt/render/project/src`
- Click "Create Web Service"
- **Copy the URL** (e.g., `https://multimodal-rag-backend-xyz.onrender.com`)

### 3. Deploy Frontend

- Click "New +" → "Web Service"
- Connect same repository
- **Configure**:
  - Name: `multimodal-rag-frontend`
  - Build: `pip install streamlit requests Pillow`
  - Start: `streamlit run ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
  - Instance: Free
- **Environment Variables**:
  - `API_BASE_URL` = `https://YOUR-BACKEND-URL/api/v1`
    (Replace with URL from step 2)
- Click "Create Web Service"

### 4. Access Your App

- Frontend: Your frontend Render URL
- Backend API: Your backend URL + `/docs`

**Done! 🎉**

---

## 💻 Local Testing (Before Deploying)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_VISION_MODEL=gpt-4o
OPENAI_MINI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 3. Run Backend (Terminal 1)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run Frontend (Terminal 2)

```bash
streamlit run ui/streamlit_app.py
```

### 5. Test the Application

- Backend API docs: http://localhost:8000/docs
- Frontend UI: http://localhost:8501
- Upload a document and test queries

---

## Deploy to Render

Once local testing is successful:

### Quick Deploy Steps:

1. **Initialize Git (if not done)**

   ```bash
   git init
   git add .
   git commit -m "Initial commit for Render deployment"
   ```

2. **Push to GitHub**

   ```bash
   # Create a new repo on GitHub first, then:
   git remote add origin https://github.com/yourusername/your-repo.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy on Render**

   - Go to https://dashboard.render.com/
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click "Apply"

4. **Configure Environment Variables**

   - Wait for services to be created
   - Go to Backend service → Environment
   - Add `OPENAI_API_KEY` = `your-key`
   - Service will auto-redeploy

5. **Update Frontend URL**

   - Copy backend URL (e.g., `https://multimodal-rag-backend.onrender.com`)
   - Go to Frontend service → Environment
   - Add `API_BASE_URL` = `https://your-backend-url/api/v1`
   - Save

6. **Access Your Live App**
   - Frontend: `https://multimodal-rag-frontend.onrender.com`
   - Backend API: `https://multimodal-rag-backend.onrender.com/docs`

---

## Troubleshooting

**Backend won't start:**

- Check logs in Render dashboard
- Verify OPENAI_API_KEY is set
- Ensure all dependencies are in requirements.txt

**Frontend can't connect:**

- Verify API_BASE_URL environment variable
- Check CORS settings in backend
- Ensure backend is showing "healthy" status

**First request is slow:**

- Normal on free tier (cold start ~30-60s)
- Subsequent requests will be faster
- Consider paid plan for instant responses

---

For detailed instructions, see [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
