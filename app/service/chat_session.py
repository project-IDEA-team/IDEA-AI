from typing import Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["kead_db"]
chat_sessions = db["chat_sessions"]

class ChatSession:
    def __init__(self, session_id: str, user_type: str):
        self.session_id = session_id
        self.user_type = user_type
        self.created_at = datetime.now()
        self.messages: List[Dict] = []
        self.context: Dict = {}

    def add_message(self, role: str, content: str, intent: Optional[str] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "intent": intent
        }
        self.messages.append(message)
        self._save_to_db()

    def _save_to_db(self):
        try:
            chat_sessions.update_one(
                {"session_id": self.session_id},
                {
                    "$set": {
                        "user_type": self.user_type,
                        "created_at": self.created_at,
                        "messages": self.messages,
                        "context": self.context,
                        "updated_at": datetime.now()
                    }
                },
                upsert=True
            )
        except Exception as e:
            print("==== [chat_session.py] 세션 저장 에러 ====")
            print(e)
            traceback.print_exc()

    @classmethod
    def load_session(cls, session_id: str) -> Optional["ChatSession"]:
        session_data = chat_sessions.find_one({"session_id": session_id})
        if not session_data:
            return None

        session = cls(session_data["session_id"], session_data["user_type"])
        session.created_at = session_data["created_at"]
        session.messages = session_data["messages"]
        session.context = session_data.get("context", {})
        return session

    def get_recent_messages(self, limit: int = 5) -> List[Dict]:
        return self.messages[-limit:]

    def clear_context(self):
        self.context = {}
        self._save_to_db() 