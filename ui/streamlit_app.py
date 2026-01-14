"""
Streamlit frontend for the Multi-Modal RAG application.
Enhanced with improved UI/UX, error handling, chat history, and performance optimizations.
"""

import base64
import io
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
import requests
import streamlit as st
from PIL import Image
import json

# =============================================================================
# Configuration
# =============================================================================

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="📄 Multi-Modal RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/multi-modal-rag-app',
        'Report a bug': 'https://github.com/your-repo/multi-modal-rag-app/issues',
        'About': """
        ## Multi-Modal RAG Assistant
        
        A powerful document Q&A system powered by:
        - 🤖 OpenAI GPT-4o-mini & GPT-4o
        - 🔍 ChromaDB Vector Search
        - ⚡ LangChain Orchestration
        
        Upload documents and ask questions with optional image context.
        """
    }
)

# API Configuration
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env and .env.example
load_dotenv()
if not Path('.env').exists():
    load_dotenv('.env.example')

# Auto-detect API URL based on environment
# Priority: Environment Variable > Docker > Local
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000") + "/api/v1" 
    if os.getenv("RENDER_EXTERNAL_URL") 
    else "http://backend:8000/api/v1" if os.getenv("DOCKER_ENV") 
    else "http://localhost:8000/api/v1"
)

# Request timeout configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))  # seconds
HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))  # seconds

# =============================================================================
# Custom CSS Styling
# =============================================================================

def apply_custom_styles():
    """
    Apply modern conversational AI styling inspired by ChatGPT/Gemini.
    Clean, minimal chat-focused design with smooth animations.
    """
    st.markdown("""
    <style>
        /* ===== ROOT VARIABLES ===== */
        :root {
            /* Colors - Professional Blue theme */
            --primary-500: #2563eb;      /* Primary blue */
            --primary-600: #1d4ed8;
            --primary-700: #1e40af;
            
            /* Neutral palette */
            --neutral-50: #f9fafb;
            --neutral-100: #f3f4f6;
            --neutral-200: #e5e7eb;
            --neutral-300: #d1d5db;
            --neutral-400: #9ca3af;
            --neutral-500: #6b7280;
            --neutral-600: #4b5563;
            --neutral-700: #374151;
            --neutral-800: #1f2937;
            --neutral-900: #111827;
            
            /* Functional colors */
            --text-primary: #111827;
            --text-secondary: #6b7280;
            --border-color: #e5e7eb;
            --bg-surface: #ffffff;
            --bg-elevated: #f9fafb;
            
            /* User message colors */
            --user-bg: #2563eb;
            --user-text: #ffffff;
            
            /* Assistant message colors */
            --assistant-bg: #f3f4f6;
            --assistant-text: #111827;
        }
        
        /* ===== DARK MODE ===== */
        @media (prefers-color-scheme: dark) {
            :root {
                --text-primary: #e5e7eb;
                --text-secondary: #9ca3af;
                --border-color: #374151;
                --bg-surface: #1f2937;
                --bg-elevated: #111827;
                --assistant-bg: #374151;
                --assistant-text: #e5e7eb;
            }
        }
        
        /* ===== GLOBAL STYLES ===== */
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background-color: var(--bg-surface);
        }
        
        /* ===== MAIN CONTAINER ===== */
        .main .block-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        /* ===== HEADER STYLING ===== */
        .header-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.5rem 0 1rem 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .header-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .header-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .status-healthy {
            color: #10b981;
        }
        
        .status-error {
            color: #ef4444;
        }
        
        /* ===== WELCOME SECTION ===== */
        .welcome-container {
            max-width: 900px;
            margin: 3rem auto;
        }
        
        .welcome-header {
            text-align: center;;
        }
        
        .welcome-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }
        
        .welcome-subtitle {
            font-size: 1.125rem;
            color: var(--text-secondary);
            margin-bottom: 0;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .feature-card {
            background-color: var(--bg-elevated);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            border-color: var(--primary-500);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.75rem;
        }
        
        .feature-title {
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }
        
        .feature-description {
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        /* ===== CHAT CONTAINER ===== */
        .chat-wrapper {
            display: flex;
            flex-direction: column;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1;
        }
        
        .chat-messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem 0;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-width: 900px;
            margin: 4rem auto 0;
            width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        /* ===== CHAT MESSAGES ===== */
        .message-group {
            display: flex;
            margin-bottom: 1rem;
            animation: slideIn 0.3s ease-out;
        }
        
        .message-group.user {
            justify-content: flex-end;
        }
        
        .message-group.assistant {
            justify-content: flex-start;
        }
        
        .message-bubble {
            max-width: 70%;
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            word-wrap: break-word;
            line-height: 1.5;
            font-size: 0.95rem;
        }
        
        .message-bubble.user {
            background-color: var(--primary-500);
            color: white;
            border-bottom-right-radius: 0.25rem;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        }
        
        .message-bubble.assistant {
            background-color: var(--assistant-bg);
            color: var(--assistant-text);
            border-bottom-left-radius: 0.25rem;
            border: 1px solid var(--border-color);
        }
        
        .message-content {
            margin: 0;
            word-break: break-word;
            white-space: pre-wrap;
            overflow-wrap: break-word;
        }
        
        .message-timestamp {
            font-size: 0.75rem;
            opacity: 0.6;
            margin-top: 0.25rem;
            padding: 0 0.25rem;
        }
        
        /* Loading state */
        .loading-dots {
            display: inline-flex;
            gap: 0.3rem;
        }
        
        .loading-dot {
            width: 0.4rem;
            height: 0.4rem;
            border-radius: 50%;
            background-color: var(--assistant-text);
            animation: bounce 1.4s infinite;
        }
        
        .loading-dot:nth-child(1) {
            animation-delay: 0s;
        }
        
        .loading-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .loading-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes bounce {
            0%, 80%, 100% {
                transform: translateY(0);
                opacity: 0.6;
            }
            40% {
                transform: translateY(-0.8rem);
                opacity: 1;
            }
        }
        
        /* ===== INPUT AREA ===== */
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: var(--bg-surface);
            border-top: 1px solid var(--border-color);
            padding: 1.5rem;
            max-width: 900px;
            margin: 0 auto;
            width: 100%;
            z-index: 999;
        }
        
        .input-form {
            display: flex;
            gap: 0.75rem;
            align-items: flex-end;
        }
        
        .input-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .stTextArea > div > div > textarea {
            border: 1px solid var(--border-color) !important;
            border-radius: 0.75rem !important;
            background-color: var(--bg-elevated) !important;
            color: var(--text-primary) !important;
            font-size: 0.95rem !important;
            resize: vertical !important;
            max-height: 120px !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-500) !important;
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1) !important;
        }
        
        .input-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
        }
        
        .stButton > button {
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            height: 2.5rem;
        }
        
        .stButton > button[type="primary"] {
            background-color: var(--primary-500) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        }
                
        .st-emotion-cache-t1wise {
            padding: 0rem 3rem 0rem;
        }
        
        /* ===== SOURCES & CONTEXT ===== */
        .sources-section {
            margin-top: 1rem;
            background-color: var(--bg-elevated);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1rem;
        }
        
        .source-item {
            padding: 0.75rem;
            background-color: var(--bg-surface);
            border-radius: 0.5rem;
            border-left: 3px solid var(--primary-500);
            margin-bottom: 0.75rem;
            font-size: 0.875rem;
        }
        
        .source-filename {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        
        .source-preview {
            color: var(--text-secondary);
            line-height: 1.4;
        }
        
        /* ===== SIDEBAR STYLING ===== */
        .stSidebar {
            background-color: var(--bg-elevated);
        }
        
        .stSidebar [data-testid="stSidebarNav"] {
            padding-top: 0;
        }
        
        /* ===== ALERTS & MESSAGES ===== */
        .stAlert {
            border-radius: 0.75rem !important;
            font-size: 0.95rem !important;
        }
        
        .stInfo {
            background-color: rgba(59, 130, 246, 0.1) !important;
            border-color: var(--primary-500) !important;
            border-left: 4px solid var(--primary-500) !important;
        }
        
        .stSuccess {
            background-color: rgba(16, 185, 129, 0.1) !important;
            border-color: #10b981 !important;
            border-left: 4px solid #10b981 !important;
        }
        
        .stError {
            background-color: rgba(239, 68, 68, 0.1) !important;
            border-color: #ef4444 !important;
            border-left: 4px solid #ef4444 !important;
        }
        
        .stWarning {
            background-color: rgba(245, 158, 11, 0.1) !important;
            border-color: #f59e0b !important;
            border-left: 4px solid #f59e0b !important;
        }
        
        /* ===== EXPANDER ===== */
        .streamlit-expanderHeader {
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            color: var(--text-primary) !important;
        }
        
        /* ===== FILE UPLOADER ===== */
        .stFileUploader {
            border: 2px dashed var(--border-color) !important;
            border-radius: 0.75rem !important;
            background-color: var(--bg-elevated) !important;
            padding: 1.5rem !important;
        }
        
        .stFileUploader [data-testid="stFileUploadDropzone"] {
            padding: 1rem !important;
        }
        
        /* ===== METRIC CARDS ===== */
        .stMetric {
            background-color: var(--bg-elevated) !important;
            padding: 1rem !important;
            border-radius: 0.75rem !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* ===== DIVIDERS ===== */
        hr {
            border: none !important;
            border-top: 1px solid var(--border-color) !important;
            margin: 1rem 0 !important;
        }
        
        /* ===== FOOTER ===== */
        .footer {
            text-align: center;
            color: var(--text-secondary);
            padding: 2rem 1rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.875rem;
        }
        
        /* ===== ANIMATIONS ===== */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        /* ===== HIDE DEFAULTS ===== */
        #MainMenu {
            visibility: hidden;
        }
        
        footer {
            visibility: hidden;
        }
        
        /* ===== RESPONSIVE DESIGN ===== */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 0 0.5rem;
            }
            
            .message-bubble {
                max-width: 85%;
                font-size: 0.9rem;
                padding: 0.65rem 0.85rem;
            }
            
            .welcome-title {
                font-size: 2rem;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .input-container {
                padding: 1rem;
            }
            
            .st-emotion-cache-t1wise {
                padding: 0rem 0.5rem 0rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# Session State Initialization
# =============================================================================

def init_session_state():
    """Initialize all session state variables with defaults."""
    defaults = {
        "file_id": None,
        "uploaded_filename": None,
        "chat_history": [],
        "api_healthy": None,
        "last_health_check": None,
        "total_documents": 0,
        "upload_progress": 0,
        "theme": "light",
        "show_sources": True,
        "show_context": False,
        "max_sources": 5,
    }
    
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

# =============================================================================
# API Helper Functions
# =============================================================================

class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: int = None, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

def make_api_request(
    method: str,
    endpoint: str,
    timeout: int = REQUEST_TIMEOUT,
    **kwargs
) -> Dict[str, Any]:
    """
    Make an API request with proper error handling and retry logic.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        timeout: Request timeout in seconds
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        Response JSON data
        
    Raises:
        APIError: If the request fails
    """
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = "Unknown error"
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", str(error_data))
            except:
                error_detail = response.text or f"HTTP {response.status_code}"
            
            raise APIError(
                message=f"API request failed",
                status_code=response.status_code,
                detail=error_detail
            )
            
    except requests.exceptions.Timeout:
        raise APIError(
            message="Request timed out",
            detail="The server is taking too long to respond. Please try again."
        )
    except requests.exceptions.ConnectionError:
        raise APIError(
            message="Connection failed",
            detail="Cannot connect to the backend API. Please ensure the server is running."
        )
    except APIError:
        raise
    except Exception as e:
        raise APIError(
            message="Unexpected error",
            detail=str(e)
        )

def check_api_health() -> Dict[str, Any]:
    """
    Check if the backend API is healthy with caching.
    
    Returns:
        Health status dictionary with stats
    """
    # Use cached result if recent (within 30 seconds)
    if (st.session_state.last_health_check and 
        time.time() - st.session_state.last_health_check < 30 and
        st.session_state.api_healthy is not None):
        return {
            "healthy": st.session_state.api_healthy,
            "total_documents": st.session_state.total_documents
        }
    
    try:
        result = make_api_request("GET", "/health", timeout=HEALTH_CHECK_TIMEOUT)
        st.session_state.api_healthy = True
        st.session_state.total_documents = result.get("vectorstore", {}).get("total_documents", 0)
        st.session_state.last_health_check = time.time()
        return {"healthy": True, "total_documents": st.session_state.total_documents, "data": result}
    except APIError:
        st.session_state.api_healthy = False
        st.session_state.last_health_check = time.time()
        return {"healthy": False, "total_documents": 0}

def encode_image_to_base64(image_file) -> Optional[str]:
    """
    Convert uploaded image to base64 string with optimization.
    
    Args:
        image_file: Uploaded file object
        
    Returns:
        Base64 encoded string or None if failed
    """
    try:
        image = Image.open(image_file)
        
        # Optimize image size for API (max 1024px on longest side)
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Save to buffer with optimization
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85, optimize=True)
        return base64.b64encode(buffered.getvalue()).decode()
        
    except Exception as e:
        st.error(f"❌ Error encoding image: {str(e)}")
        return None

def upload_document(uploaded_file) -> bool:
    """
    Upload document to the backend API with progress tracking.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_data = uploaded_file.getvalue()
        files = {
            "file": (
                uploaded_file.name,
                file_data,
                uploaded_file.type or "application/octet-stream"
            )
        }
        
        progress_bar = st.progress(0, text="Uploading file...")
        progress_bar.progress(30, text="Processing document...")
        
        result = make_api_request("POST", "/upload", files=files)
        
        progress_bar.progress(100, text="Complete!")
        time.sleep(0.5)  # Brief pause to show completion
        progress_bar.empty()
        
        st.session_state.file_id = result["file_id"]
        st.session_state.uploaded_filename = result["filename"]
        st.session_state.chat_history = []  # Clear chat history for new document
        
        st.success(f"✅ {result['message']}")
        return True
        
    except APIError as e:
        st.error(f"❌ Upload failed: {e.detail}")
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return False

def query_document(question: str, image_base64: Optional[str] = None) -> Optional[Dict]:
    """
    Query the document using the backend API.
    
    Args:
        question: User's question
        image_base64: Optional base64 encoded image
        
    Returns:
        Query response dictionary or None if failed
    """
    if not st.session_state.file_id:
        st.error("❌ No document uploaded. Please upload a document first.")
        return None
    
    try:
        payload = {
            "question": question,
            "file_id": st.session_state.file_id,
            "image_base64": image_base64
        }
        
        result = make_api_request(
            "POST",
            "/query",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        return result
        
    except APIError as e:
        st.error(f"❌ Query failed: {e.detail}")
        return None

def get_uploaded_files() -> List[Dict]:
    """
    Get list of all uploaded files from the API.
    
    Returns:
        List of file dictionaries
    """
    try:
        return make_api_request("GET", "/files")
    except APIError:
        return []

# =============================================================================
# UI Components
# =============================================================================

def render_header():
    """Render the modern header with document status."""
    st.markdown(
        f"""
        <div class="header-container">
            <h1 class="header-title">💬 Chat with your Document</h1>
            <div class="header-status">
                {('🟢 <span class="status-healthy">Connected</span>' if check_api_health()["healthy"] else '🔴 <span class="status-error">Disconnected</span>')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    """Render the sidebar with document upload and settings."""
    with st.sidebar:
        st.header("📁 Document Management")
        
        # File uploader with clear instructions
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=["pdf", "docx", "txt", "csv", "png", "jpg", "jpeg", "db"],
            help="""
            **Supported formats:**
            - 📄 PDF - Portable Document Format
            - 📝 DOCX - Microsoft Word
            - 📃 TXT - Plain text files
            - 📊 CSV - Comma-separated values
            - 🖼️ PNG/JPG/JPEG - Images (OCR extracted)
            - 🗄️ DB - SQLite databases
            """,
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            # Show file preview info
            file_size = len(uploaded_file.getvalue())
            st.info(f"📎 **{uploaded_file.name}**\n\nSize: {file_size / 1024:.1f} KB")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Upload", type="primary", use_container_width=True):
                    if upload_document(uploaded_file):
                        st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.rerun()
        
        st.divider()
        
        # Current document info
        if st.session_state.file_id:
            st.markdown(
                f"""
                <div class="file-info-card">
                    <strong>📄 Active Document</strong><br>
                    {st.session_state.uploaded_filename}<br>
                    <small>ID: {st.session_state.file_id[:8]}...</small>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear", use_container_width=True, help="Remove current document"):
                    st.session_state.file_id = None
                    st.session_state.uploaded_filename = None
                    st.session_state.chat_history = []
                    st.rerun()
            with col2:
                if st.button("🔄 Refresh", use_container_width=True, help="Refresh API connection"):
                    st.session_state.last_health_check = None
                    st.rerun()
        
        st.divider()
        
        # Settings section
        with st.expander("⚙️ Settings", expanded=False):
            st.session_state.show_sources = st.toggle(
                "Show Sources",
                value=st.session_state.show_sources,
                help="Display source documents for answers"
            )
            
            st.session_state.show_context = st.toggle(
                "Show Context",
                value=st.session_state.show_context,
                help="Display retrieved context used for answers"
            )
            
            st.session_state.max_sources = st.slider(
                "Max Sources to Display",
                min_value=1,
                max_value=10,
                value=st.session_state.max_sources,
                help="Maximum number of source documents to show"
            )
        
        # Previously uploaded files
        with st.expander("📚 All Uploaded Files", expanded=False):
            files = get_uploaded_files()
            if files:
                for file_info in files:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"📄 {file_info['filename'][:20]}...")
                    with col2:
                        if st.button("Use", key=f"use_{file_info['file_id']}", help="Select this document"):
                            st.session_state.file_id = file_info['file_id']
                            st.session_state.uploaded_filename = file_info['filename']
                            st.session_state.chat_history = []
                            st.rerun()
            else:
                st.info("No files uploaded yet")
        
        # Help section
        st.divider()
        with st.expander("❓ Help", expanded=False):
            st.markdown("""
            **How to use:**
            1. Upload a document using the file uploader
            2. Wait for processing to complete
            3. Ask questions in the chat interface
            4. Optionally add images for visual queries
            
            **Tips:**
            - Be specific in your questions
            - Use quotes for exact phrases
            - Try different phrasings if needed
            
            **Keyboard shortcuts:**
            - `Enter` - Submit question
            - `Ctrl+K` - Focus search
            """)

def render_chat_message(role: str, content: str, timestamp: str = None, sources: List = None):
    """
    Render a modern chat message bubble.
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        timestamp: Optional timestamp string
        sources: Optional list of source documents
    """
    bubble_class = "user" if role == "user" else "assistant"
    
    # Render message bubble
    st.markdown(
        f"""
        <div class="message-group {bubble_class}">
            <div class="message-bubble {bubble_class}">
                <p class="message-content">{content}</p>
                {f'<div class="message-timestamp">{timestamp}</div>' if timestamp else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render sources if available and assistant message
    if role == "assistant" and sources and st.session_state.show_sources:
        with st.expander(f"📚 {len(sources)} Source(s)", expanded=False):
            for i, source in enumerate(sources[:st.session_state.max_sources], 1):
                st.markdown(
                    f"""
                    <div class="source-item">
                        <div class="source-filename">📄 {source.get('filename', 'Unknown')}</div>
                        {f'<div class="source-preview"><strong>Page:</strong> {source.get("page_number")}</div>' if source.get('page_number') else ''}
                        <div class="source-preview">{source.get('content', 'No preview available')[:150]}...</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

def render_chat_interface():
    """Render the main chat interface with fixed input at bottom."""
    # Chat messages container (scrollable)
    if not st.session_state.chat_history:
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 1rem; color: var(--text-secondary);">
                <p style="font-size: 1.125rem;">No messages yet. Start a conversation! 💬</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for message in st.session_state.chat_history:
            render_chat_message(
                role=message["role"],
                content=message["content"],
                timestamp=message.get("timestamp"),
                sources=message.get("sources") if message["role"] == "assistant" else None
            )
    
    st.divider()
    
    col1, col2 = st.columns([4, 1], gap="small")
    
    with col1:
        question = st.text_area(
            "Message",
            placeholder="Ask anything about your document...",
            height=80,
            key="question_input",
            label_visibility="collapsed",
            max_chars=5000
        )
    
    with col2:
        uploaded_image = st.file_uploader(
            "Add image",
            type=["png", "jpg", "jpeg"],
            help="Optional image for visual context",
            key="image_input",
            label_visibility="collapsed"
        )
        
        if uploaded_image:
            # Show thumbnail
            image = Image.open(uploaded_image)
            st.image(image, caption="Attached", use_container_width=True, width=80)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    st.markdown('<div style="display: flex; gap: 0.5rem; margin-top: 1rem;">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1], gap="small")
    
    with col1:
        submit_disabled = not question.strip() or not st.session_state.file_id
        if st.button(
            "🚀 Send",
            type="primary",
            disabled=submit_disabled,
            use_container_width=True,
            key="submit_btn"
        ):
            if question.strip() and st.session_state.file_id:
                process_question(question, uploaded_image)
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True, help="Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("📥 Export", use_container_width=True, help="Export chat"):
            export_chat_history()
    
    st.markdown('</div>', unsafe_allow_html=True)

def process_question(question: str, uploaded_image=None):
    """
    Process a user question and get AI response.
    
    Args:
        question: User's question text
        uploaded_image: Optional uploaded image file
    """
    timestamp = datetime.now().strftime("%H:%M")
    
    # Add user message to history
    user_message = {
        "role": "user",
        "content": question,
        "timestamp": timestamp
    }
    st.session_state.chat_history.append(user_message)
    
    # Encode image if provided
    image_base64 = None
    if uploaded_image:
        image_base64 = encode_image_to_base64(uploaded_image)
    
    # Get AI response
    with st.spinner("🤔 Thinking..."):
        result = query_document(question, image_base64)
    
    if result:
        # Add assistant message to history
        assistant_message = {
            "role": "assistant",
            "content": result["answer"],
            "timestamp": datetime.now().strftime("%H:%M"),
            "sources": result.get("sources", []),
            "context": result.get("context", "")
        }
        st.session_state.chat_history.append(assistant_message)
        
        # Show context if enabled
        if st.session_state.show_context and result.get("context"):
            with st.expander("📄 Retrieved Context", expanded=False):
                st.text_area(
                    "Context",
                    result["context"],
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
    
    st.rerun()

def export_chat_history():
    """Export chat history as a downloadable file."""
    if not st.session_state.chat_history:
        st.warning("No chat history to export")
        return
    
    # Format chat history for export
    export_data = {
        "document": st.session_state.uploaded_filename,
        "exported_at": datetime.now().isoformat(),
        "messages": st.session_state.chat_history
    }
    
    json_str = json.dumps(export_data, indent=2)
    
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def render_welcome_screen():
    """Render a clean, modern welcome screen."""
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-header">
                <h1 class="welcome-title">Welcome to your AI Assistant</h1>
                <p class="welcome-subtitle">Upload a document and start asking questions</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Features grid
    st.markdown(
        """
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Multi-Format</div>
                <div class="feature-description">PDF, Word, Text, CSV, Images, SQLite</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Smart Search</div>
                <div class="feature-description">Understand context, not just keywords</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI Powered</div>
                <div class="feature-description">GPT-4o for accurate answers</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">👁️</div>
                <div class="feature-title">Vision</div>
                <div class="feature-description">Analyze images in documents</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📚</div>
                <div class="feature-title">Sources</div>
                <div class="feature-description">Trace answers back to documents</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Fast</div>
                <div class="feature-description">Instant results with OCR support</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.info("📁 **Start by uploading a document in the sidebar**")
    
    st.divider()
    
    # API health check
    health = check_api_health()
    if health["healthy"]:
        st.success(f"🟢 **System Ready** • {health['total_documents']} documents indexed")
    else:
        st.error("🔴 **Backend not available** - Please start the API server")

def render_footer():
    """Render the application footer."""
    st.markdown(
        """
        <div class="footer">
            <strong>Multi-Modal RAG Assistant</strong><br>
            Powered by LangChain • ChromaDB • OpenAI<br>
            <small>© 2026 - Abdullah Al Raiyan</small>
        </div>
        """,
        unsafe_allow_html=True
    )

# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    # Initialize
    init_session_state()
    apply_custom_styles()
    
    # Check API health
    health = check_api_health()
    
    if not health["healthy"]:
        st.error("""
        🔴 **Backend API is not accessible**
        
        Please ensure the backend service is running:
        - For Docker: `docker-compose up --build`
        - For local: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
        """)
        
        if st.button("🔄 Retry Connection"):
            st.session_state.last_health_check = None
            st.rerun()
        
        st.stop()
    
    # Render UI
    render_header()
    render_sidebar()
    
    # Main content area
    if st.session_state.file_id:
        render_chat_interface()
    else:
        render_welcome_screen()
    
    render_footer()

# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()
