# 🎓 OS Tutor Buddy

**OS Tutor Buddy** is an intelligent, AI-powered teaching assistant aimed at helping students master **Operating Systems concepts**. Built with **Llama 3 (via Groq)** and **LangChain**, it acts as a strict but helpful tutor, answering questions, generating diagrams, and referencing course materials via RAG (Retrieval-Augmented Generation).

---

## 🚀 Key Features

*   **🧠 Advanced AI Tutor**: Powered by **Llama 3.3 70B** for high-quality, accurate explanations of complex implementation details (concurrency, scheduling, memory management).
*   **📚 RAG (Retrieval-Augmented Generation)**: Automatically scans, indexes, and retrieves knowledge from PDF textbooks found in the `tools/data/` folder, ensuring answers are grounded in your specific curriculum.
*   **💾 Hybrid Storage System**: unique **Dual-Layer Persistence** architecture:
    *   **Primary**: Saves chat history to **MongoDB Atlas**.
    *   **Fallback**: Automatically switches to **Local File Storage** (`chat_history.json`) if the database connection drops, ensuring no data is ever lost.
*   **📊 Dynamic Visualizations**: Automatically generates **Mermaid.js** diagrams (Flowcharts, Sequence diagrams) to visualize algorithms like Process Scheduling or Deadlocks.
*   **⚡ High Performance**: Uses **Groq's LPU** for near-instant inference speeds.

---

## 🛠️ Tech Stack

*   **Framework**: Flask (Python)
*   **LLM Engine**: Groq API (Llama 3.3 70B Versatile)
*   **Orchestration**: LangChain
*   **Vector Database**: FAISS (Facebook AI Similarity Search)
*   **Primary Database**: MongoDB Atlas
*   **Embeddings**: HuggingFace (`sentence-transformers/all-mpnet-base-v2`)
*   **PDF Processing**: PyMuPDF4LLM

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/os-tutor-buddy.git
    cd os-tutor-buddy
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    MONGO_URI=your_mongodb_connection_string
    ```

4.  **Add Knowledge Base**
    Place your Operating System textbooks (.pdf) in the `tools/data/` folder. The system will automatically index them on the first run.

5.  **Run the Application**
    ```bash
    python app.py
    ```
    Visit `http://localhost:5000` in your browser.

---

## 📂 Project Structure

```text
├── app.py                 # Main Flask Application & Routes
├── agent.py               # AI Tutor Logic (System Prompts, Guardrails)
├── tools/
│   ├── db.py             # Hybrid Storage Manager (Mongo + Local Fallback)
│   ├── pdf_query_tools.py # RAG Implementation (FAISS + PDF Indexing)
│   └── data/             # Folder for PDF Textbooks
├── static/                # CSS, JS, Images
└── templates/             # HTML Templates
```

---

## 🛡️ License
This project is open-source and available under the **MIT License**.
