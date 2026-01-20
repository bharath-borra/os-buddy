# 🎓 OS Tutor Buddy

[![Live Demo](https://img.shields.io/badge/Live_Demo-FF4F00?style=for-the-badge&logo=render&logoColor=white)](https://os-buddy.onrender.com/)

**OS Tutor Buddy** is an intelligent, AI-powered teaching assistant aimed at helping students master **Operating Systems concepts**. Built with **Llama 3 (via Groq)** and **LangChain**, it acts as a strict but helpful tutor, answering questions, generating diagrams, and referencing course materials via RAG (Retrieval-Augmented Generation).

---

## 🚀 Key Features

*   **🧠 Advanced AI Tutor**: Powered by **Llama 3.3 70B** for high-quality, accurate explanations of complex implementation details (concurrency, scheduling, memory management).
*   **�️ Strict Domain Focus**: The AI is **strictly scoped** to Operating Systems topics. It actively **rejects unrelated queries** (like sports, movies, or general knowledge) to ensure the study session remains focused.
*   **�📚 RAG (Retrieval-Augmented Generation)**: Automatically scans, indexes, and retrieves knowledge from PDF textbooks found in the `tools/data/` folder, ensuring answers are grounded in your specific curriculum.
*   **💾 Hybrid Storage System**: unique **Dual-Layer Persistence** architecture:
    *   **Primary**: Saves chat history to **MongoDB Atlas**.
    *   **Fallback**: Automatically switches to **Local File Storage** (`chat_history.json`) if the database connection drops, ensuring no data is ever lost.
*   **🤝 Llama + RAG Handshake**: Seamlessly orchestrates general reasoning (Llama 3) with specific Textbook knowledge (FAISS Vector Store). if the query is technical (e.g., "Page Tables"), it retrieves context chunks and feeds them into the system prompt, ensuring the AI answers *from the book*.
*   **📊 Diagram Generation (Mermaid.js)**: Turns complex processes into visual flowcharts on the fly. The AI generates Mermaid syntax, which the frontend sanitizes and renders instantly. (Previously referred to as "Migrane" image generation). 
*   **💾 Smart Session Management**: 
    *   **New Chat**: Instantly spawn fresh contexts.
    *   **Deletion Options**: Easily manage your workspace by deleting old or irrelevant chat sessions.
*   **⚡ High Performance**: Uses **Groq's LPU** for near-instant inference speeds.
*   **🛡️ Robust Error Handling**: Includes self-healing sanitizers for diagram syntax to ensure visuals always render correctly.

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

## 💻 For Developers: Installation & Setup

If you want to run this project locally for development:

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
