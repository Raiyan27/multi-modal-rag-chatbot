# 📄🧠 Multi-Modal RAG Application

This application can process multiple document types, store vector embeddings, and answer questions using both text and image inputs.

## 🚀 Features

- **Multi-Format Document Processing**: Support for PDF, DOCX, TXT, CSV, PNG, JPG, JPEG, and SQLite databases
- **Vector Storage**: Persistent ChromaDB for efficient similarity search
- **Multi-Modal Queries**: Text and image-based question answering using GPT-4 Vision
- **Production Ready**: Full Docker containerization with docker-compose orchestration
- **Modern UI**: Clean Streamlit interface for document upload and querying
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation

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

## 🔧 Setup and Installation (via Docker)

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
   copy .env.example .env
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

### Local Development Setup

1. **Modify streamlit_app.py file**

   Go to ui/streamlit_app.py file -> `streamlit_app.py`

   ```
   multi-modal-rag-app/
   ├── app/
   ├── ui/
   │   └── streamlit_app.py     # Streamlit frontend
   ```

   uncomment line 43 and comment out line 44.

2. **Set up environment variables**:

   ```bash
   copy .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:

   ```env
   OPENAI_API_KEY="your_actual_openai_api_key_here"
   ```

3. **Create Python virtual environment**

   ```bash
   python -m venv venv
   venv/Scripts/activate
   ```

4. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Run Backend Locally**:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Run Frontend Locally**:
   ```bash
   cd ui
   streamlit run streamlit_app.py --server.port 8501
   ```

## 📁 Project Structure

```
multi-modal-rag-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── api.py               # API routes (/upload, /query)
│   ├── logic.py             # Business logic for RAG pipeline
│   ├── models.py            # Pydantic models
│   └── config.py            # Configuration management
├── ui/
│   └── streamlit_app.py     # Streamlit frontend
├── data/
│   ├── uploads/             # Uploaded files storage
│   └── chroma_db/           # ChromaDB persistent storage
├── sample_docs/             # Sample files for testing
│   ├── sample.txt
│   └── sample.csv
├── Dockerfile               # Backend container
├── docker-compose.yml       # Orchestration
├── requirements.txt         # Python dependencies
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

| Method | Endpoint         | Description                         |
| ------ | ---------------- | ----------------------------------- |
| `GET`  | `/`              | Root endpoint with API info         |
| `GET`  | `/api/v1/health` | Health check with vectorstore stats |
| `POST` | `/api/v1/upload` | Upload and process documents        |
| `POST` | `/api/v1/query`  | Query documents with text/image     |
| `GET`  | `/api/v1/files`  | List uploaded files                 |
| `GET`  | `/docs`          | Interactive API documentation       |
