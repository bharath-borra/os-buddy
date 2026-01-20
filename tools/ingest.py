import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "tools", "data")
PDF_PATH = os.path.join(DATA_DIR, "Abraham-Silberschatz-Operating-System-Concepts-10th-2018.pdf")
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")

def ingest():
    print(f"Loading PDF from {PDF_PATH}...")
    if not os.path.exists(PDF_PATH):
        print("Error: PDF not found!")
        return

    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages.")

    print("Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print("Creating embeddings (this may take a minute)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Building Vector Store...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    print(f"Saving index to {INDEX_PATH}...")
    vector_store.save_local(INDEX_PATH)
    print("Done!")

if __name__ == "__main__":
    ingest()
