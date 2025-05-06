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
    chats_repository = ChatsRepository()
    doc_ref = chats_repository.create_message(session_id, user_id, role, message_text)
    doc_id = ""
    try:
        # Firestore returns a tuple (write_result, doc_ref), extract doc_id if available
        doc_id = doc_ref[1].id
    except Exception as e:
        pass
    return {"message": "Chat message saved", "doc_id": doc_id}


@function_tool
def get_chat_messages_tool(session_id: str, limit: int = 10, offset: int = 0) -> dict:
    """
    Retrieve chat messages for a specified session using ChatsRepository.
    
    Parameters:
      - session_id: The session identifier
      - limit: Number of messages to retrieve (default 10)
      - offset: Pagination offset (default 0)
    
    Returns:
      A dictionary containing a list of chat messages.
    """
    chats_repository = ChatsRepository()
    messages = chats_repository.get_messages(session_id, limit, offset)
    return {"messages": messages}