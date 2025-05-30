from agents import function_tool
from services.chat_service import ChatService


@function_tool(strict_mode=False)
def save_chat_message_tool(session_id: str, user_id: str, role: str, message_text: str) -> dict:
    """
    Chats メッセージを保存するツール（サービス呼び出し版）

    パラメータ:
      - session_id: セッションID
      - user_id: ユーザーID
      - role: 送信者の役割（例: 'user' または 'agent'）
      - message_text: メッセージの内容

    戻り値:
      dict: サービスの create_message の戻り値
    """
    service = ChatService()
    return service.create_message(user_id, session_id, role, message_text)


@function_tool(strict_mode=False)
def get_chat_messages_tool(user_id: str, session_id: str, limit: int = 10, offset: int = 0) -> dict:
    """
    チャットメッセージを取得するツール（サービス呼び出し版）

    パラメータ:
      - user_id: ユーザーID
      - session_id: セッションID
      - limit: 取得するメッセージ数（デフォルト: 10）
      - offset: ページネーションのオフセット（デフォルト: 0）

    戻り値:
      dict: サービスの get_messages の戻り値
    """
    service = ChatService()
    return service.get_messages(user_id, session_id, limit, offset)