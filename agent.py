import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Global Resource Cache
_vector_store = None
_embeddings = None

def get_vector_store():
    global _vector_store, _embeddings
    if _vector_store:
        return _vector_store
    
    index_path = os.path.join(os.path.dirname(__file__), "faiss_index")
    if os.path.exists(index_path):
        try:
            print("Loading FAISS Index...")
            _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            _vector_store = FAISS.load_local(index_path, _embeddings, allow_dangerous_deserialization=True)
            print("FAISS Index Loaded.")
            return _vector_store
        except Exception as e:
            print(f"Failed to load FAISS: {e}")
            return None
    return None

def agent(user_message, chat_history):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not found.", "System Error"

    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=api_key)
        
        # 1. Router Logic (Simple Heuristic or Mini-LLM)
        # For speed, we will use a "technical keyword" heuristic + simple intent check
        technical_keywords = ["process", "thread", "schedule", "deadlock", "memory", "paging", "kernel", "semaphore", "disk", "fcfs", "sjf", "round robin"]
        is_technical = any(kw in user_message.lower() for kw in technical_keywords) or len(user_message.split()) > 3
        
        context_text = ""
        mode = "Direct LLM"

        # 2. Retrieval (RAG)
        if is_technical:
            vector_store = get_vector_store()
            if vector_store:
                print(f"Searching knowledge base for: {user_message}")
                docs = vector_store.similarity_search(user_message, k=3)
                context_chunks = [doc.page_content for doc in docs]
                context_text = "\n\n---\n\n".join(context_chunks)
                mode = "Router -> RAG (Textbook)"
        
        # 3. Construct Prompt
        history_text = ""
        recent_history = chat_history[-6:] if chat_history else []
        for msg in recent_history:
            role = "User" if msg.get("role") == "user" else "Assistant"
            history_text += f"{role}: {msg.get('content', '')}\n"

        system_prompt = f"""You are OS Buddy, an expert Operating Systems Tutor based on the Silberschatz textbook.

        CONTEXT FROM TEXTBOOK:
        {context_text if context_text else "No textbook context available. Answer effectively using your general knowledge."}

        INSTRUCTIONS:
        1. If Context is present, USE IT. It contains the exact definitions and steps.
        2. If the user asks for a diagram (or if the concept *needs* one, e.g., Scheduling, Lifecycle), generate Mermaid.js code.
        3. Explain strictly but friendly.
        
        DIAGRAMMING RULES (CRITICAL):
        - Use `graph TD` or `sequenceDiagram`.
        - Node IDs: NO spaces (e.g., `id["Label"]`).
        - Strings: ALWAYS double quotes.
        - NO special chars in IDs.
        
        Conversation:
        {history_text}
        
        User: {user_message}
        """

        response = llm.invoke(system_prompt)
        return response.content, mode

    except Exception as e:
        print(f"Agent Error: {e}")
        return f"I encountered an error: {str(e)}", "System Crash"
