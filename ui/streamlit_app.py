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
        - 🤖 OpenAI GPT-4 & GPT-4 Vision
        - 🔍 ChromaDB Vector Search
        - ⚡ LangChain Orchestration
        
        Upload documents and ask questions with optional image context.
        """
    }
)

# API Configuration
import os

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
REQUEST_TIMEOUT = 60  # seconds
HEALTH_CHECK_TIMEOUT = 5  # seconds

# =============================================================================
# Custom CSS Styling
# =============================================================================

def apply_custom_styles():
    """
    Apply modern, accessible CSS styling with solid colors.
    Color scheme is optimized for both light and dark mode readability.
    """
    st.markdown("""
    <style>
        /* ===== ROOT VARIABLES - Modern Professional Palette ===== */
        :root {
            /* Primary brand colors - Deep Blue theme */
            --primary-500: #2563eb;      /* Primary blue - accessible on white */
            --primary-600: #1d4ed8;      /* Darker blue for hover states */
            --primary-700: #1e40af;      /* Even darker for active states */
            --primary-100: #dbeafe;      /* Light blue for backgrounds */
            --primary-50: #eff6ff;       /* Very light blue */
            
            /* Secondary colors - Professional Green */
            --success-500: #10b981;      /* Success green */
            --success-600: #059669;      /* Darker green */
            --success-100: #d1fae5;      /* Light green bg */
            
            /* Alert colors */
            --error-500: #ef4444;        /* Error red */
            --error-600: #dc2626;        /* Darker red */
            --error-100: #fee2e2;        /* Light red bg */
            
            --warning-500: #f59e0b;      /* Warning amber */
            --warning-100: #fef3c7;      /* Light amber bg */
            
            /* Neutral palette - Works in both modes */
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
            --text-secondary: #4b5563;
            --text-tertiary: #6b7280;
            --border-color: #e5e7eb;
            --bg-surface: #ffffff;
            --bg-elevated: #f9fafb;
            
            /* Spacing system */
            --spacing-xs: 0.25rem;
            --spacing-sm: 0.5rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 2rem;
            
            /* Border radius */
            --radius-sm: 0.375rem;
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            
            /* Shadows */
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        /* ===== DARK MODE SUPPORT ===== */
        @media (prefers-color-scheme: dark) {
            :root {
                --text-primary: #d1d5db;
                --text-secondary: #9ca3af;
                --text-tertiary: #6b7280;
                --border-color: #374151;
                --bg-surface: #1f2937;
                --bg-elevated: #111827;
                
                /* Adjust primary colors for dark mode */
                --primary-500: #3b82f6;
                --primary-100: #1e3a8a;
            }
        }
        
        /* ===== TYPOGRAPHY ===== */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: var(--spacing-md);
        }
        
        /* ===== MAIN CONTAINER ===== */
        .main .block-container {
            padding: var(--spacing-xl) var(--spacing-lg);
            max-width: 1280px;
            margin: 0 auto;
        }
        
        /* ===== HEADER STYLING ===== */
        .main-header {
            color: var(--primary-600);
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: var(--spacing-sm);
            letter-spacing: -0.025em;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1rem;
            font-weight: 400;
        }
        
        /* ===== CARD COMPONENTS ===== */
        .card {
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-md);
            box-shadow: var(--shadow-sm);
            transition: box-shadow 0.2s ease;
        }
        
        .card:hover {
            box-shadow: var(--shadow-md);
        }
        
        /* ===== CHAT MESSAGE STYLING ===== */
        .chat-message {
            padding: var(--spacing-lg);
            border-radius: var(--radius-lg);
            margin-bottom: var(--spacing-md);
            border: 1px solid var(--border-color);
            animation: fadeIn 0.3s ease-out;
            background-color: var(--bg-surface);
        }
        
        .user-message {
            border-left: 4px solid var(--primary-500);
            background-color: var(--primary-50);
        }
        
        @media (prefers-color-scheme: dark) {
            .user-message {
                background-color: rgba(37, 99, 235, 0.1);
            }
            
            .assistant-message {
                background-color: rgba(16, 185, 129, 0.5);
            }
            
            .assistant-message .message-content {
                color: #36363b;
            }
            .message-header {
                color: #36363b;
            }
        }
        
        .assistant-message {
            border-left: 4px solid var(--success-500);
            background-color: var(--success-100);
        }
        
        .message-header {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: var(--spacing-sm);
            font-size: 0.95rem;
        }
        
        .message-content {
            color: var(--text-primary);
            font-size: 1rem;
            line-height: 1.7;
        }
        
        .message-timestamp {
            color: var(--text-tertiary);
            font-size: 0.8rem;
            float: right;
        }
        
        /* ===== STATUS INDICATORS ===== */
        .status-healthy {
            color: var(--success-600);
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .status-error {
            color: var(--error-500);
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        /* ===== BUTTONS ===== */
        .stButton > button {
            border-radius: var(--radius-md);
            font-weight: 500;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* ===== SOURCE CARD ===== */
        .source-card {
            background-color: var(--bg-elevated);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-sm);
        }
        
        .source-card strong {
            color: var(--text-primary);
            font-size: 0.95rem;
        }
        
        .source-card em {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        
        .source-card small {
            color: var(--text-tertiary);
            font-size: 0.85rem;
            line-height: 1.5;
        }
        
        /* ===== FILE INFO CARD ===== */
        .file-info-card {
            background-color: var(--primary-500);
            color: white;
            padding: var(--spacing-lg);
            border-radius: var(--radius-lg);
            margin-bottom: var(--spacing-md);
            box-shadow: var(--shadow-md);
        }
        
        .file-info-card strong {
            font-size: 1rem;
            display: block;
            margin-bottom: var(--spacing-xs);
        }
        
        .file-info-card small {
            opacity: 0.9;
            font-size: 0.85rem;
        }
        
        /* ===== METRIC STYLING ===== */
        .metric-container {
            background-color: var(--bg-elevated);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            text-align: center;
        }
        
        /* ===== FOOTER ===== */
        .footer {
            text-align: center;
            color: var(--text-tertiary);
            padding: var(--spacing-xl) var(--spacing-md);
            margin-top: var(--spacing-xl);
            border-top: 1px solid var(--border-color);
            font-size: 0.9rem;
        }
        
        .footer strong {
            color: var(--text-secondary);
        }
        
        /* ===== STREAMLIT OVERRIDES ===== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 1rem;
            color: var(--text-primary);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-color: var(--border-color);
            border-radius: var(--radius-md);
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-500);
            box-shadow: 0 0 0 1px var(--primary-500);
        }
        
        /* File uploader */
        .stFileUploader {
            border: 2px dashed var(--border-color);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            background-color: var(--bg-elevated);
        }
        
        /* Dividers */
        hr {
            border-color: var(--border-color);
            margin: var(--spacing-lg) 0;
        }
        
        /* ===== ANIMATIONS ===== */
        @keyframes fadeIn {
            from { 
                opacity: 0; 
                transform: translateY(10px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }
        
        @keyframes slideIn {
            from { 
                transform: translateX(100%); 
                opacity: 0; 
            }
            to { 
                transform: translateX(0); 
                opacity: 1; 
            }
        }
        
        /* ===== ACCESSIBILITY ===== */
        /* Focus indicators */
        button:focus,
        input:focus,
        textarea:focus,
        select:focus {
            outline: 2px solid var(--primary-500);
            outline-offset: 2px;
        }
        
        /* High contrast for readability */
        ::selection {
            background-color: var(--primary-500);
            color: white;
        }
        
        /* ===== RESPONSIVE DESIGN ===== */
        @media (max-width: 768px) {
            .main .block-container {
                padding: var(--spacing-md);
            }
            
            .main-header {
                font-size: 1.875rem;
            }
            
            .chat-message {
                padding: var(--spacing-md);
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
    """Render the main application header with modern styling."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            '<h1 class="main-header">📄 Multi-Modal RAG Assistant</h1>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="subtitle">Intelligent document Q&A powered by AI</p>',
            unsafe_allow_html=True
        )
    
    with col2:
        health = check_api_health()
        if health["healthy"]:
            st.markdown(
                '<div style="text-align: right;"><p class="status-healthy">🟢 API Connected</p></div>',
                unsafe_allow_html=True
            )
            st.metric("Documents Indexed", health["total_documents"])
        else:
            st.markdown(
                '<p class="status-error">🔴 API Disconnected</p>',
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
    Render a single chat message with modern, accessible styling.
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        timestamp: Optional timestamp string
        sources: Optional list of source documents
    """
    icon = "👤" if role == "user" else "🤖"
    css_class = "user-message" if role == "user" else "assistant-message"
    
    st.markdown(
        f"""
        <div class="chat-message {css_class}">
            <div class="message-header">
                {icon} {role.capitalize()}
                {f'<span class="message-timestamp">{timestamp}</span>' if timestamp else ''}
            </div>
            <div class="message-content">{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render sources if available
    if sources and st.session_state.show_sources:
        with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
            for i, source in enumerate(sources[:st.session_state.max_sources], 1):
                st.markdown(
                    f"""
                    <div class="source-card">
                        <strong>Source {i}: {source.get('filename', 'Unknown')}</strong>
                        {f"<br><em>Page {source.get('page_number')}</em>" if source.get('page_number') else ""}
                        <br><small>{source.get('content', 'No preview available')[:200]}...</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

def render_chat_interface():
    """Render the main chat interface."""
    st.header("💬 Chat with Your Document")
    
    # Chat history display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Start a conversation by asking a question about your document!")
        else:
            for message in st.session_state.chat_history:
                render_chat_message(
                    role=message["role"],
                    content=message["content"],
                    timestamp=message.get("timestamp"),
                    sources=message.get("sources")
                )
    
    st.divider()
    
    # Input section
    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_area(
            "Your question",
            placeholder="Ask anything about your document...",
            height=100,
            key="question_input",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**🖼️ Add Image**")
        uploaded_image = st.file_uploader(
            "Optional image",
            type=["png", "jpg", "jpeg"],
            help="Add an image for visual queries",
            key="image_input",
            label_visibility="collapsed"
        )
        
        if uploaded_image:
            st.image(uploaded_image, caption="Attached", use_container_width=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        submit_disabled = not question.strip() or not st.session_state.file_id
        if st.button(
            "🚀 Ask Question",
            type="primary",
            disabled=submit_disabled,
            use_container_width=True
        ):
            if question.strip():
                process_question(question, uploaded_image)
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("📋 Export", use_container_width=True, help="Export chat history"):
            export_chat_history()

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
    """Render a clean, modern welcome screen when no document is loaded."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 👋 Welcome to Multi-Modal RAG Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 Get Started
        
        **1. 📁 Upload a Document**  
        Use the sidebar to upload your document (PDF, DOCX, TXT, CSV, images, or SQLite DB)
        
        **2. ⏳ Wait for Processing**  
        The system will extract text, create embeddings, and index your document
        
        **3. 💬 Ask Questions**  
        Start a conversation about your document content
        
        **4. 🖼️ Add Images (Optional)**  
        Include images for visual context in your queries
        """)
    
    with col2:
        st.markdown("""
        ### ✨ Features
        
        - **📄 Multi-Format Support** - PDF, Word, Text, CSV, Images, SQLite
        - **🔍 Semantic Search** - Find relevant information intelligently
        - **🤖 AI-Powered Answers** - GPT-4 generates accurate responses
        - **👁️ Vision Analysis** - GPT-4 Vision for image understanding
        - **💾 Persistent Storage** - Your documents are securely stored
        - **📊 Source Attribution** - See where answers come from
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Example questions section
    st.markdown("### 💡 Example Questions You Can Ask")
    
    example_cols = st.columns(3)
    
    examples = [
        ["What is the main topic?", "Summarize the key points", "What are the conclusions?"],
        ["Extract numerical data", "List all people mentioned", "What dates are referenced?"],
        ["Compare sections A and B", "What is shown in the image?", "Explain the relationship"]
    ]
    
    for col, example_list in zip(example_cols, examples):
        with col:
            for example in example_list:
                st.markdown(f"• *{example}*")
    
    st.divider()
    
    # Quick stats
    health = check_api_health()
    if health["healthy"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Documents Indexed", health["total_documents"])
        with col2:
            st.metric("🤖 AI Model", "GPT-4")
        with col3:
            st.metric("🔍 Vector DB", "ChromaDB")

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
    
    # Render UI components
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
