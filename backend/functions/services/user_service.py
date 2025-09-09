from repositories.users_repository import UsersRepository


class UserService:
    def __init__(self):
        self.repo = UsersRepository()

    def get_user_id_by_session(self, session_id: str) -> str | None:
        """セッションIDからユーザーIDを取得します。"""
        return self.repo.get_user_id_by_session(session_id)