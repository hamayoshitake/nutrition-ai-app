from firebase_functions import https_fn
import json

# Import the ChatService from repositories instead of using Firestore client directly
from repositories.chat_repository import ChatService

chat_service = ChatService()

@https_fn.on_request()
def saveChatMessage(request):
    if request.method != "POST":
        return https_fn.Response(json.dumps({"error": "Method not allowed, use POST"}), status=405)
    body = request.get_json(silent=True) or {}
    session_id = body.get("session_id")
    user_id = body.get("user_id")
    role = body.get("role")
    message_text = body.get("message_text")
    if not session_id or not user_id or not role or not message_text:
        return https_fn.Response(json.dumps({"error": "session_id, user_id, role, message_text are required"}), status=400)
    
    # Use ChatService to save the message
    # The save_message method returns the document reference, but we don't assume a specific structure.
    doc_ref = chat_service.save_message(session_id, user_id, role, message_text)
    # Attempt to get the document ID if available
    doc_id = ""
    try:
        # Firestore returns a tuple (write_result, doc_ref), adjust accordingly
        doc_id = doc_ref[1].id
    except Exception as e:
        pass
    
    return https_fn.Response(json.dumps({"message": "Chat message saved", "doc_id": doc_id}), status=200)

@https_fn.on_request()
def getChatMessages(request):
    if request.method != "GET":
        return https_fn.Response(json.dumps({"error": "Method not allowed, use GET"}), status=405)
    session_id = request.args.get("session_id")
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    if not session_id:
        return https_fn.Response(json.dumps({"error": "session_id is required"}), status=400)
    try:
        limit = int(limit) if limit is not None else 10
        offset = int(offset) if offset is not None else 0
    except ValueError:
        return https_fn.Response(json.dumps({"error": "Invalid limit/offset"}), status=400)
    
    # Use ChatService to retrieve messages
    messages = chat_service.get_messages(session_id, limit, offset)
    return https_fn.Response(json.dumps({"messages": messages}), status=200) 