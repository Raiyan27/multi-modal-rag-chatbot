"""
Streamlit frontend for the Multi-Modal RAG application.
"""

import base64
import io
import requests
import streamlit as st
from PIL import Image
import json

st.set_page_config(
    page_title="📄 Document & Image Q&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1" # uncomment when running locally via uvicorn
# API_BASE_URL = "http://backend:8000/api/v1" # comment out when running locally via uvicorn

if "file_id" not in st.session_state:
    st.session_state.file_id = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None


def encode_image_to_base64(image_file):
    """Convert uploaded image to base64 string."""
    try:
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except Exception as e:
        st.error(f"Error encoding image: {str(e)}")
        return None


def upload_document(uploaded_file):
    """Upload document to the backend API."""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        with st.spinner("Uploading and processing document..."):
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.file_id = result["file_id"]
            st.session_state.uploaded_filename = result["filename"]
            st.success(f"✅ {result['message']}")
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"❌ Upload failed: {error_detail}")
            return False
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend API. Please ensure the backend is running.")
        return False
    except Exception as e:
        st.error(f"❌ Error uploading file: {str(e)}")
        return False


def query_document(question, image_base64=None):
    """Query the document using the backend API."""
    try:
        payload = {
            "question": question,
            "file_id": st.session_state.file_id,
            "image_base64": image_base64
        }
        
        with st.spinner("Generating answer..."):
            response = requests.post(
                f"{API_BASE_URL}/query",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"❌ Query failed: {error_detail}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend API. Please ensure the backend is running.")
        return None
    except Exception as e:
        st.error(f"❌ Error querying document: {str(e)}")
        return None


def check_api_health():
    """Check if the backend API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# Main application
def main():
    st.title("📄Multi-modal RAG chatbot")
    
    # Check API health
    if not check_api_health():
        st.error("🔴 Backend API is not accessible. Please start the backend service.")
        st.stop()
    else:
        st.success("🟢 Backend API is running")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Document Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "docx", "txt", "csv", "png", "jpg", "jpeg", "db"],
            help="Supported formats: PDF, DOCX, TXT, CSV, PNG, JPG, JPEG, SQLite DB"
        )
        
        if uploaded_file is not None:
            if st.button("📤 Upload & Process", type="primary"):
                if upload_document(uploaded_file):
                    st.rerun()
        
        # Display current file info
        if st.session_state.file_id:
            st.success(f"✅ **Current Document:** {st.session_state.uploaded_filename}")
            st.info(f"**File ID:** `{st.session_state.file_id}`")
            
            if st.button("🗑️ Clear Document"):
                st.session_state.file_id = None
                st.session_state.uploaded_filename = None
                st.rerun()
    
    # Main content area
    if st.session_state.file_id:
        st.header("💬 Ask Questions")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            question = st.text_area(
                "Enter your question:",
                placeholder="What is this document about?",
                height=100
            )
        
        with col2:
            st.subheader("🖼️ Optional Image")
            uploaded_image = st.file_uploader(
                "Upload an image (optional)",
                type=["png", "jpg", "jpeg"],
                help="Upload an image for multi-modal queries"
            )
            
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        # Query button
        if st.button("🚀 Ask Question", type="primary", disabled=not question.strip()):
            if question.strip():
                image_base64 = None
                if uploaded_image:
                    image_base64 = encode_image_to_base64(uploaded_image)
                
                result = query_document(question, image_base64)
                
                if result:
                    st.header("💡 Answer")
                    st.write(result["answer"])
                    
                    with st.expander("📄 Context Used", expanded=False):
                        st.text_area("Context", result["context"], height=200, disabled=True)
                    
                    with st.expander("📚 Sources", expanded=False):
                        for i, source in enumerate(result["sources"], 1):
                            st.subheader(f"Source {i}")
                            st.write(f"**Filename:** {source['filename']}")
                            if source["page_number"]:
                                st.write(f"**Page:** {source['page_number']}")
                            st.write(f"**Content Preview:** {source['content']}")
                            st.divider()
            else:
                st.warning("Please enter a question.")
    
    else:
        st.header("👋 Welcome!")
        st.markdown("""
        **Get started by uploading a document:**
        
        1. 📁 Use the sidebar to upload a document (PDF, DOCX, TXT, CSV, PNG, JPG, JPEG, or SQLite DB)
        2. ⏳ Wait for the document to be processed and indexed
        3. 💬 Ask questions about your document
        4. 🖼️ Optionally include images for multi-modal queries
        
        **Supported Features:**
        - 📄 Multi-format document processing
        - 🔍 Semantic search and retrieval
        - 🤖 AI-powered question answering
        - 👁️ Vision-based image analysis
        - 📊 Database content analysis
        """)
        
        st.subheader("💡 Example Questions")
        example_questions = [
            "What is the main topic of this document?",
            "Summarize the key points in bullet format",
            "What are the conclusions or recommendations?",
            "Extract any numerical data or statistics",
            "What is shown in the uploaded image?",
            "How does the image relate to the document content?"
        ]
        
        for i, question in enumerate(example_questions, 1):
            st.write(f"{i}. {question}")
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Multi-Modal RAG System • Powered by LangChain, ChromaDB & OpenAI"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
