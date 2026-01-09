import os
import time
from pymongo import MongoClient
import dns.resolver

# Fix for Windows/Network DNS issues: Force Google DNS
try:
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']
except:
    pass

class MongoDBManager:
    def __init__(self):
        uri = os.environ.get("MONGO_URI")
        self.db = None
        
        if not uri:
            print("Warning: MONGO_URI not found in .env. Using in-memory fallback.")
        else:
            try:
                # serverSelectionTimeoutMS=5000: Fail fast if no connection (5s)
                client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                self.db = client['os_buddy']
                # Trigger a command to verify connection immediately (optional, catches error now)
                # self.db.command('ping') 
                print("Connected to MongoDB Atlas!")
            except Exception as e:
                print(f"Failed to connect to MongoDB: {e}")
                print("Falling back to local session handling (non-persistent).")

    def get_sessions(self):
        """Fetch all sessions ordered by timestamp desc."""
        if self.db is None: return []
        
        try:
            sessions = list(self.db.sessions.find({}, {"_id": 0}).sort("timestamp", -1))
            return sessions
        except Exception as e:
            print(f"Error fetching sessions: {e}")
            return []

    def get_session(self, session_id):
        if self.db is None: return {"messages": []}
        try:
            return self.db.sessions.find_one({"id": session_id}, {"_id": 0}) or {"messages": []}
        except Exception as e:
            print(f"Error getting session: {e}")
            return {"messages": []}

    def save_session(self, session_id, session_data):
        if self.db is None: return
        try:
            # Upsert (Insert or Update)
            session_data["id"] = session_id  # Ensure ID is in the doc
            self.db.sessions.update_one(
                {"id": session_id},
                {"$set": session_data},
                upsert=True
            )
        except Exception as e:
            print(f"Error saving session: {e}")
