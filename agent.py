import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def agent(user_message, chat_history):
    # Retrieve GROQ_API_KEY
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not found in .env file.", "Configuration Check Failed"

    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            groq_api_key=api_key
        )
        
        # Pure LLM Mode
        
        # 1. Format History
        # Format History
        history_text = ""
        # Limit history to last 10 messages to avoid token limits
        recent_history = chat_history[-10:] if chat_history else []
        for msg in recent_history:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

        prompt = f"""You are a strict but helpful Tutor for Operating Systems (based on Silberschatz OS Concepts).

        Your Goal: Answer the user's question about Operating Systems.
        
        STRICT RULES:
        1. Answer ONLY questions related to Operating Systems, Computer Science, or Coding.
        2. If the user asks about anything else (e.g., General Knowledge, Sports, Movies, Geography), politely REFUSE.
           - Example Refusal: "I am an OS Tutor. I can only answer questions about Operating Systems."
        3. Use the Conversation History to understand context (e.g. "What about threads?" refers to previous topic).
        
        DIAGRAM GENERATION RULES:
        1. If the user asks for a diagram, YOU MUST generate a Mermaid.js diagram.
        2. STRICT SYNTAX RULES:
           - Use `graph TD` or `graph LR` for flowcharts.
           - Use `sequenceDiagram` for interaction flows.
           - Use `gantt` ONLY for scheduling.
           - DO NOT use `block-beta` or other experimental features.
           - DO NOT add comments (%%) inside the code block.
        3. EXAMPLES:
           - Scheduling (Gantt):
             ```mermaid
             gantt
             title FCFS
             dateFormat s
             axisFormat %s
             Process P1 : 0, 5
             Process P2 : 5, 3
             ```
           - Paging (Flowchart):
             ```mermaid
             graph LR
             CPU[CPU] -->|Logical Addr| MMU{{MMU}}
             MMU -->|Physical Addr| RAM[Memory]
             ```
        4. Keep diagrams SIMPLE. No complex styling.
        5. DO NOT generate diagrams for non-OS topics.
        
        Conversation History:
        {history_text}
        
        Current Question:
        {user_message}
        """
        
        # Generate Response
        response = llm.invoke(prompt)
        return response.content, "Internal Knowledge (Llama 3 70B)"
        
    except Exception as e:
        return f"Error contacting Groq API: {str(e)}", "API Call Failed"
