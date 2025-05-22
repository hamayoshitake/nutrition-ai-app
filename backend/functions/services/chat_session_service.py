from repositories.chat_sessions_repository import ChatSessionsRepository


class ChatSessionService:
    def __init__(self):
        self.repo = ChatSessionsRepository()

    def create_session(self, user_id: str) -> str:
        """指定されたユーザーIDのための新しいチャットセッションを作成し、セッションIDを返します。"""
        return self.repo.create_session(user_id)