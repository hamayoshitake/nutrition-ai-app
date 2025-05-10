from agents import function_tool
from repositories.chats_repository import ChatsRepository


@function_tool
def create_chat_message_tool(session_id: str, user_id: str, role: str, message_text: str) -> dict:
    """
    Save a single chat message using ChatsRepository.
    
    Parameters:
      - session_id: The session identifier
      - user_id: The user identifier
      - role: The role of the sender (e.g., 'user' or 'agent')
      - message_text: The content of the chat message
    
    Returns:
      A dictionary with a success message and the document ID if available.
    """
    try:
        chats_repository = ChatsRepository()
        doc_ref = chats_repository.create_message(user_id, session_id, role, message_text)
        doc_id = ""
        try:
            # Firestore returns a tuple (write_result, doc_ref), extract doc_id if available
            doc_id = doc_ref[1].id
        except Exception:
            pass
        return {"message": "Chat message saved", "doc_id": doc_id}
    except Exception as e:
        return {"message": f"Error saving chat message: {str(e)}"}


@function_tool
def get_chat_messages_tool(session_id: str, limit: int = 10, offset: int = 0) -> dict:
    """
    Retrieve chat messages for a specified session using ChatsRepository.
    
    Parameters:
      - session_id: The session identifier
      - limit: Number of messages to retrieve (default: 10)
      - offset: Pagination offset (default: 0)
    
    Returns:
      A dictionary containing a list of chat messages.
    """
    try:
        # セッションIDのチェック
        if not session_id or not isinstance(session_id, str):
            return {"messages": [], "error": "Invalid session_id"}
            
        # デフォルト値とバリデーション
        limit_val = 10
        offset_val = 0
        
        try:
            if limit is not None:
                limit_val = int(limit)
                if limit_val <= 0:
                    limit_val = 10
            
            if offset is not None:
                offset_val = int(offset)
                if offset_val < 0:
                    offset_val = 0
        except (ValueError, TypeError):
            # 数値に変換できない場合はデフォルト値を使用
            pass
            
        chats_repository = ChatsRepository()
        messages = chats_repository.get_messages(session_id, limit_val, offset_val)
        
        # メッセージが空の場合
        if not messages:
            return {"messages": [], "count": 0}
            
        # メッセージデータを整形
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.get("role", "unknown"),
                "content": msg.get("message_text", ""),
                "timestamp": msg.get("created_at", "")
            })
            
        return {"messages": formatted_messages, "count": len(formatted_messages)}
    except Exception as e:
        # 例外が発生した場合は空のメッセージリストを返す
        return {"messages": [], "error": str(e)}