from repositories.chats_repository import ChatsRepository


class ChatMessageService:
    def __init__(self):
        self.repo = ChatsRepository()

    def save_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        message_text: str
    ) -> bool:
        """
        チャットメッセージを保存します。
        """
        return self.repo.create_message(user_id, session_id, role, message_text)

    def get_messages(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> list[dict]:
        """
        チャットメッセージを取得します。
        """
        return self.repo.get_messages(user_id, session_id, limit, offset)
