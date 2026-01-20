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
        
        # 1. Router Logic (Strict)
        # Check against technical keywords. If no match, treat as "General Chat" unless context implies OS.
        technical_keywords = [
            "process", "thread", "schedule", "deadlock", "memory", "paging", "kernel", "semaphore", "disk", 
            "fcfs", "sjf", "round robin", "os", "operating system", "linux", "windows", "cpu", "cache", 
            "virtual", "file system", "interrupt", "system call", "mutex", "hardware", "software", "code", 
            "programming", "computer", "server", "client", "network", "boot", "algorithm", "concurrency",
            "synchronization", "banker", "page", "frame", "segmentation", "io", "driver", "monitor"
        ]
        
        is_technical = any(kw in user_message.lower() for kw in technical_keywords)
        
        # GUARDRAIL: Hard Block for non-technical queries that aren't greetings
        if not is_technical:
            greetings = ["hi", "hello", "hey", "greetings", "good morning", "start", "help", "who are you"]
            is_greeting = any(g == user_message.lower().strip() or user_message.lower().startswith(g + " ") for g in greetings)
            
            if not is_greeting:
                return "🚫 **Out of Scope**: I am strictly programmed to answer questions about **Operating Systems** only (e.g., Paging, Scheduling, Deadlocks). I cannot assist with Geography, General Knowledge, or other topics.", "Blocked by Keyword Guardrail"

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
        
        SCOPE:
        You are a SPECIALIZED Operating Systems Tutor.
        You MUST ONLY answer questions directly related to Operating Systems (Concepts, Algorithms, Kernels, Memory, Concurrency, etc.).
        
        STRICT REFUSAL POLICY:
        If the user asks about ANYTHING else (including General Python, Web Development, Geography, Biology, Sports, Politics, or General Knowledge), you must politely but FIRMLY REFUSE.
        
        Refusal Template: "I am strictly programmed to help with Operating Systems only. I cannot answer questions about [topic]. Please ask me about topics like Paging, Scheduling, or Deadlocks."

        CONTEXT FROM TEXTBOOK:
        {context_text if context_text else "No specific textbook context found."}

        INSTRUCTIONS:
        1. If Context is present, USE IT. It contains the exact definitions and steps.
        2. If the user asks for a diagram (or if the concept *needs* one, e.g., Scheduling, Lifecycle), generate Mermaid.js code.
        3. Explain strictly but friendly.
        
        DIAGRAMMING RULES (CRITICAL):
        - **FOR FLOWCHARTS (`graph TD`)**:
            - Use `-->|Label|` for arrows.
            - IDs must be alphanumeric.
        - **FOR SEQUENCE DIAGRAMS (`sequenceDiagram`)**:
            - Use `A->>B: Message` (Colon syntax).
            - **NEVER** use `-->|Label|` in sequence diagrams.
            - **NEVER** use `Note over A,B,C` (Max 2 participants like `Note over A,B`).
        - **GENERAL**:
            - Strings: ALWAYS double quotes.
            - No `|>` at end of arrows.
        
        Conversation:
        {history_text}
        
        User: {user_message}
        """

        response = llm.invoke(system_prompt)
        return response.content, mode

    except Exception as e:
        print(f"Agent Error: {e}")
        return f"I encountered an error: {str(e)}", "System Crash"
