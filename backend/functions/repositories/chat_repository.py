from firebase_admin import firestore
from datetime import datetime
import uuid


class ChatService:
    def __init__(self):
        # Initialize the Firestore client
        self.db = firestore.client()

    def save_message(self, session_id, user_id, role, message_text):
        # Save a single chat message with additional user_id field
        data = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "message_text": message_text,
            "created_at": datetime.now().isoformat()
        }
        return self.db.collection("chat_messages").add(data)

    def get_messages(self, session_id, limit=10, offset=0):
        # Retrieve messages for a given session_id
        query = (
            self.db.collection("chat_messages")
            .where("session_id", "==", session_id)
            .order_by("created_at")
            .offset(offset)
            .limit(limit)
            .get()
        )
        messages = []
        for doc in query:
            msg = doc.to_dict()
            msg["doc_id"] = doc.id
            messages.append(msg)
        return messages