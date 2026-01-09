import os
import pymupdf4llm
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Global Vector Store
vector_store = None
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index_v3")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "extracted_images")

def initialize_vector_store():
    global vector_store
    
    # Check if index already exists to avoid re-computing
    if os.path.exists(INDEX_PATH):
        try:
            print("Loading existing FAISS index...")
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            vector_store = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            print("Loaded existing FAISS index successfully.")
            return
        except Exception as e:
            print(f"Error loading index: {e}")

    # Load PDFs with PyMuPDF4LLM (Markdown ONLY - Faster)
    documents = []
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        
    print("Scanning for PDFs and extracting rich content (Tables only, No Images)...")
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".pdf"):
            # CRITICAL: Filter out leftover Finance/Tax files that might be locked
            if "Finance" in filename or "budget" in filename:
                print(f"Skipping excluded file: {filename}")
                continue
                
            filepath = os.path.join(DATA_DIR, filename)
            print(f"Processing PDF: {filename} (Fast Mode)...")
            
            # Convert to markdown (Tables preserved, Images skipped)
            md_text = pymupdf4llm.to_markdown(
                filepath, 
                write_images=False  # Disabled for speed
            )
            
            documents.append(Document(page_content=md_text, metadata={"source": filename}))
            
    if not documents:
        print("No PDF documents found to index.")
        return

    print(f"Loaded {len(documents)} docs (full markdown).")

    # Split Text (Markdown friendly)
    print("Splitting markdown text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, # Larger chunks for markdown tables
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    # Create Embeddings & Index
    print("Generating embeddings and building index. This may take 1-2 minutes...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Save Index
    vector_store.save_local(INDEX_PATH)
    print(f"Index built and saved! Ready to query.")

def query_pdfs(query):
    """
    Query the PDF knowledge base.
    """
    global vector_store
    if vector_store is None:
        initialize_vector_store()
    
    if vector_store is None:
        return "No documents available to answer this query."

    # Retrieve top 3 relevant chunks
    docs = vector_store.similarity_search(query, k=3)
    
    context = "\n\n".join([doc.page_content for doc in docs])
    return context

