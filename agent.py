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
        history_text = ""
        if chat_history:
            for msg in chat_history:
                # msg is usually {"role": "user", "content": "..."}
                role = "User" if msg.get("role") == "user" else "AI"
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"

        # 2. Construct Prompt
        prompt = f"""You are a strict but helpful Tutor for Operating Systems.
        
        Your Goal: Answer the user's question about Operating Systems.
        
        Constraints:
        1. Answer comprehensively using your internal knowledge (Llama 3).
        2. Refuse to answer non-OS topics.
        3. Use the Conversation History to understand context.
        
        Conversation History:
        {history_text}
        
        Current User Question:
        {user_message}
        """
        
        # Generate Response
        response = llm.invoke(prompt)
        return response.content, "Internal Knowledge (Llama 3 70B)"
        
    except Exception as e:
        return f"Error contacting Groq API: {str(e)}", "API Call Failed"
