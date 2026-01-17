import os
import time
from pymongo import MongoClient
import dns.resolver
import pymongo
import certifi
import json

# Fix for Windows/Network DNS issues: Force Google DNS
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

class MongoDBManager:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI")
        self.client = None
        self.db = None
        self.use_local = False
        self.local_file = "chat_history.json"
        
        try:
            if not self.uri:
                raise ValueError("MONGO_URI not found")
            
            self.client = MongoClient(
                self.uri, 
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=3000,
                socketTimeoutMS=3000,
                tlsCAFile=certifi.where()
            )
            # Test Connection
            self.client.admin.command('ping')
            self.db = self.client["chat_db"]
            print("Connected to MongoDB Atlas!")
            self._ensure_indexes()
        except Exception as e:
            print(f"\n[WARNING] MongoDB Connection Failed: {e}")
            print(f"[ACTION] Switching to Local File Storage ({self.local_file})\n")
            print(f"[ACTION] Switching to Local File Storage ({self.local_file})\n")
            self.use_local = True

    def _ensure_indexes(self):
        try:
            # Create TTL index for 1 year (31,536,000 seconds) on 'last_active'
            # Note: MongoDB requires a Date field for TTL to work accurately.
            self.db.sessions.create_index("last_active", expireAfterSeconds=31536000)
            print("Ensured MongoDB TTL Index for 1-year retention.")
        except Exception as e:
            print(f"Warning: Could not create TTL index: {e}")

    def _load_local(self):
        if not os.path.exists(self.local_file):
            return {}
        try:
            with open(self.local_file, "r") as f:
                return json.load(f)
        except:
            return {}

    def _save_local(self, data):
        try:
            with open(self.local_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save local history: {e}")

    def get_sessions(self, user_id=None):
        if self.use_local:
            history = self._load_local()
            # Convert dict to list format expected by app
            sessions = []
            for sid, data in history.items():
                # Filter by user_id if provided
                if user_id and data.get("user_id") != user_id:
                    continue
                    
                sessions.append({
                    "id": sid,
                    "title": data.get("title", "New Chat"),
                    "timestamp": data.get("timestamp", 0)
                })
            return sessions 
        
        try:
            # MongoDB
            query = {}
            if user_id:
                query["user_id"] = user_id
                
            cursors = self.db.sessions.find(query, {"id": 1, "title": 1, "timestamp": 1, "_id": 0})
            return list(cursors)
        except Exception as e:
            print(f"MongoDB Read Failed: {e}. Switching to Local.")
            self.use_local = True
            return self.get_sessions(user_id)

    def get_session(self, session_id):
        if self.use_local:
            history = self._load_local()
            return history.get(session_id, {"messages": []})
        
        try:
            data = self.db.sessions.find_one({"id": session_id}, {"_id": 0})
            return data if data else {"messages": []}
        except Exception as e:
            print(f"MongoDB Read Session Failed: {e}. Switching to Local.")
            self.use_local = True
            return self.get_session(session_id)

    def save_session(self, session_id, session_data, user_id=None):
        # Ensure ID is in data
        session_data["id"] = session_id
        if user_id:
            session_data["user_id"] = user_id

        
        if self.use_local:
            history = self._load_local()
            history[session_id] = session_data
            self._save_local(history)
            return

        try:
            self.db.sessions.update_one(
                {"id": session_id},
                {"$set": session_data},
                upsert=True
            )
        except Exception as e:
            print(f"MongoDB Write Failed: {e}. Switching to Local.")
            self.use_local = True
            self.save_session(session_id, session_data, user_id)

    def delete_session(self, session_id, user_id=None):
        if self.use_local:
            history = self._load_local()
            if session_id in history:
                # Optional: Check ownership
                if user_id and history[session_id].get("user_id") != user_id:
                    return False
                del history[session_id]
                self._save_local(history)
            return True
        
        try:
            query = {"id": session_id}
            if user_id:
                query["user_id"] = user_id
                
            result = self.db.sessions.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            print(f"MongoDB Delete Failed: {e}")
            return False


