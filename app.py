import json
import uuid
import os
import time
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from agent import agent
from dotenv import load_dotenv
from tools.db import MongoDBManager

load_dotenv()

app = Flask(__name__)

# --- Database ---
db = MongoDBManager()

# --- Routes ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/healthz")
def health_check():
    return jsonify({"status": "ok", "message": "I am awake!"})



@app.route("/sessions", methods=["GET"])
def get_sessions():
    user_id = request.headers.get("X-User-ID")
    sessions = db.get_sessions(user_id)
    # Format for frontend
    formatted = []
    for s in sessions:
        formatted.append({
            "id": s.get("id"),
            "title": s.get("title", "New Chat"),
            "timestamp": s.get("timestamp", 0)
        })
    return jsonify(formatted)

@app.route("/sessions/new", methods=["POST"])
def new_session():
    user_id = request.headers.get("X-User-ID")
    # Create valid empty session
    session_id = str(uuid.uuid4())
    session_data = {
        "title": "New Chat",
        "timestamp": time.time(),
        "last_active": datetime.now(timezone.utc),
        "messages": []
    }
    db.save_session(session_id, session_data, user_id)
    return jsonify({"id": session_id})

@app.route("/sessions/<session_id>", methods=["GET"])
def get_session_chat(session_id):
    session = db.get_session(session_id)
    return jsonify(session)

@app.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session_route(session_id):
    user_id = request.headers.get("X-User-ID")
    success = db.delete_session(session_id, user_id)
    return jsonify({"success": success})

@app.route("/chat", methods=["POST"])
def chat():
    import traceback
    try:
        data = request.json
        user_message = data.get("message", "")
        session_id = data.get("session_id")
        
        if not user_message:
            return jsonify({"response": "Please enter a message.", "thoughts": "Empty input"})
        
        # Generate Session ID if missing
        if not session_id:
            session_id = str(uuid.uuid4())

        # Load Session from DB
        session_data = db.get_session(session_id)
        # Load Session from DB
        session_data = db.get_session(session_id)
        
        # Ensure 'time' is available (imported globally or here)
        # Using global import time is cleaner.
        
        if not session_data.get("messages"):
            session_data = {
                "title": user_message[:30] + "...",
                "timestamp": time.time(),
                "last_active": datetime.now(timezone.utc),
                "messages": []
            }
        
        session_data["timestamp"] = time.time()
        session_data["last_active"] = datetime.now(timezone.utc)
        
        # Append User Msg
        session_data["messages"].append({"role": "user", "content": user_message})
        
        # Generate Response
        response, thought_process = agent(user_message, chat_history=session_data["messages"])
        
        # Append AI Msg
        session_data["messages"].append({"role": "ai", "content": response})
        
        # Update Title if needed
        if session_data.get("title") == "New Chat":
             session_data["title"] = user_message[:30] + "..."

        # Save to MongoDB
        user_id = request.headers.get("X-User-ID")
        db.save_session(session_id, session_data, user_id)
        
        return jsonify({
            "response": response, 
            "thoughts": thought_process,
            "session_id": session_id
        })
    except Exception as e:
        print(f"CRITICAL ERROR in /chat: {e}")
        traceback.print_exc()
        return jsonify({"response": f"System Error: {str(e)}", "thoughts": "Backend Crash"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
