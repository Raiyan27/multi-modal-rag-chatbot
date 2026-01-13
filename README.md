# 📄🧠 Multi-Modal RAG Application

An intelligent document Q&A system that processes multiple document types, stores vector embeddings, and answers questions using both text and image inputs. Built with modern AI/ML technologies and optimized for both local development and cloud deployment.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## 🚀 Features

- **Multi-Format Document Processing**: Support for PDF, DOCX, TXT, CSV, PNG, JPG, JPEG, and SQLite databases
- **Vector Storage**: Persistent ChromaDB for efficient similarity search
- **Multi-Modal Queries**: Text and image-based question answering using GPT-4 Vision
- **Production Ready**: Full Docker containerization with docker-compose orchestration
- **Modern UI**: Clean, accessible Streamlit interface with dark mode support
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation
- **Cloud Ready**: One-click deployment to Render with automatic scaling
- **Performance Optimized**: Singleton patterns, caching, and connection pooling

## 🛠️ Technology Stack

| Component               | Technology                                                 |
| ----------------------- | ---------------------------------------------------------- |
| **API Framework**       | FastAPI                                                    |
| **Orchestration**       | LangChain                                                  |
| **Vector Store**        | ChromaDB (persistent)                                      |
| **LLM & Embeddings**    | OpenAI (GPT-4o-mini, GPT-4 Vision, text-embedding-3-small) |
| **Document Processing** | LangChain loaders + pytesseract + pandas                   |
| **Frontend**            | Streamlit                                                  |
| **Containerization**    | Docker + Docker Compose                                    |
| **Server**              | Uvicorn                                                    |
| **Configuration**       | Pydantic Settings + python-dotenv                          |

## 🔧 Setup and Installation

### 🌐 Deploy to Render (Recommended for Production)

Deploy to Render for free hosting:

1. **Push to GitHub**:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Backend Service**:

   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - **Name**: `multimodal-rag-backend`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable:
     - `OPENAI_API_KEY` = `your-api-key`
   - Deploy!

3. **Create Frontend Service**:

   - Click "New +" → "Web Service"
   - Connect same repository
   - Configure:
     - **Name**: `multimodal-rag-frontend`
     - **Build Command**: `pip install streamlit requests Pillow`
     - **Start Command**: `streamlit run ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - Add environment variable:
     - `API_BASE_URL` = `https://your-backend-url.onrender.com/api/v1`
   - Deploy!

4. **Access Your App**:
   - Frontend: `https://your-frontend.onrender.com`
   - Backend API: `https://your-backend.onrender.com/docs`

📖 **Detailed step-by-step guide**: See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)

---

### 🐳 Docker Deployment (Local or Self-Hosted)

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Quick Start

1. **Clone or create the project directory**:

   ```bash
   mkdir multi-modal-rag-app
   cd multi-modal-rag-app
   ```

2. **Set up environment variables**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:

   ```env
   OPENAI_API_KEY="your_actual_openai_api_key_here"
   ```

3. **Start the application**:

   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - **Streamlit UI**: http://localhost:8501
   - **API Documentation**: http://localhost:8000/docs
   - **API Health Check**: http://localhost:8000/api/v1/health

---

### 💻 Local Development Setup

1. **Set up environment variables**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:

   ```env
   OPENAI_API_KEY="your_actual_openai_api_key_here"
   ```

2. **Create Python virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Backend** (Terminal 1):

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Run Frontend** (Terminal 2):

   ```bash
   streamlit run ui/streamlit_app.py
   ```

6. **Access locally**:
   - Frontend: http://localhost:8501
   - Backend: http://localhost:8000/docs

## 📁 Project Structure

```
multi-modal-rag-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point with CORS & middleware
│   ├── api.py               # API routes (/upload, /query, /files)
│   ├── logic.py             # Business logic for RAG pipeline
│   ├── models.py            # Pydantic models with validation
│   └── config.py            # Configuration management (pydantic-settings)
├── ui/
│   └── streamlit_app.py     # Modern Streamlit frontend with dark mode
├── data/
│   ├── uploads/             # Uploaded files storage
│   └── chroma_db/           # ChromaDB persistent storage
├── sample_docs/             # Sample files for testing
│   ├── sample.txt
│   └── sample.csv
├── Dockerfile               # Backend container configuration
├── docker-compose.yml       # Multi-container orchestration
├── render.yaml              # Render deployment blueprint
├── requirements.txt         # Python dependencies
├── build.sh                 # Render build script
├── start-backend.sh         # Backend startup script
├── start-frontend.sh        # Frontend startup script
├── RENDER_DEPLOYMENT.md     # Detailed Render deployment guide
├── QUICKSTART.md            # Quick reference guide
├── README.md                # This file
└── .env.example             # Environment template
```

## 📊 Supported File Types

| File Type     | Extension               | Description                 |
| ------------- | ----------------------- | --------------------------- |
| PDF           | `.pdf`                  | Portable Document Format    |
| Word Document | `.docx`                 | Microsoft Word documents    |
| Text File     | `.txt`                  | Plain text files            |
| CSV           | `.csv`                  | Comma-separated values      |
| Images        | `.png`, `.jpg`, `.jpeg` | Images (processed with OCR) |
| Database      | `.db`                   | SQLite database files       |

## 🧪 API Endpoints

| Method   | Endpoint             | Description                         |
| -------- | -------------------- | ----------------------------------- |
| `GET`    | `/`                  | Root endpoint with API info         |
| `GET`    | `/api/v1/health`     | Health check with vectorstore stats |
| `POST`   | `/api/v1/upload`     | Upload and process documents        |
| `POST`   | `/api/v1/query`      | Query documents with text/image     |
| `GET`    | `/api/v1/files`      | List uploaded files                 |
| `DELETE` | `/api/v1/files/{id}` | Delete uploaded file                |
| `GET`    | `/docs`              | Interactive API documentation       |

## 🎨 UI Features

- **Modern Design**: Clean, professional interface with accessibility in mind
- **Dark Mode Support**: Automatic theme detection for comfortable viewing
- **Chat History**: Persistent conversation tracking per document
- **Source Attribution**: View which document sections were used for answers
- **Multi-Modal Input**: Upload images alongside text queries
- **File Management**: Easy document switching and management
- **Export Functionality**: Download chat history as JSON
- **Real-time Health Monitoring**: API connection status display

## 🔐 Environment Variables

Create a `.env` file with these variables:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_VISION_MODEL=gpt-4o
OPENAI_MINI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Model Settings
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=50

# Application Settings
CORS_ORIGINS=*
DEBUG_MODE=false
```

## 📚 Documentation

- **[RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)** - Complete guide for deploying to Render
- **[QUICKSTART.md](./QUICKSTART.md)** - Quick reference for deployment
- **[API Documentation](http://localhost:8000/docs)** - Interactive OpenAPI docs (when running locally)

## 🚀 Performance Optimizations

- **Singleton Pattern**: Reuses OpenAI client instances to reduce overhead
- **LRU Caching**: Caches text splitters and frequently accessed data
- **Image Optimization**: Automatically resizes and compresses images before processing
- **Connection Pooling**: Efficient ChromaDB connection management
- **Lazy Loading**: Loads resources only when needed
- **Health Check Caching**: Reduces redundant API calls

## 🔧 Troubleshooting

### Backend Won't Start

- Verify `OPENAI_API_KEY` is set correctly
- Check all required dependencies are installed
- Review logs for specific error messages

### Frontend Can't Connect to Backend

- Ensure backend is running and healthy
- Check `API_BASE_URL` in streamlit_app.py or environment variable
- Verify CORS settings allow your frontend origin

### File Upload Issues

- Check `MAX_FILE_SIZE_MB` setting
- Ensure `data/uploads/` directory exists and is writable
- Verify file format is supported

### Slow Response Times on Render Free Tier

- Normal on first request after inactivity (cold start ~30-60s)
- Consider upgrading to paid plan for always-on instances

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Abdullah Al Raiyan**

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [OpenAI](https://openai.com/)
- Vector storage by [ChromaDB](https://www.trychroma.com/)
- UI framework by [Streamlit](https://streamlit.io/)
- Web framework by [FastAPI](https://fastapi.tiangolo.com/)

---

⭐ If you find this project helpful, please consider giving it a star!
