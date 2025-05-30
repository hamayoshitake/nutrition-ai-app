"""
チャット関連のビジネスロジックを提供するサービスモジュール
"""

from repositories.chats_repository import ChatsRepository


class ChatService:
    """
    チャット機能に関するビジネスロジックを実装するサービスクラス
    """

    def __init__(self):
        self.chats_repository = ChatsRepository()

    def create_message(self, user_id: str, session_id: str, role: str, message_text: str) -> dict:
        """
        チャットメッセージを保存し、結果を辞書で返却します。

        Args:
            user_id: ユーザーID
            session_id: セッションID
            role: 送信者の役割（'user'または'agent'など）
            message_text: メッセージの内容

        Returns:
            辞書: {"success": bool, "doc_id"?: str, "message"?: str, "error"?: str}
        """
        try:
            doc_ref = self.chats_repository.create_message(user_id, session_id, role, message_text)
            doc_id = ""
            try:
                # Firestore returns a tuple (write_result, doc_ref), extract doc_id if available
                doc_id = doc_ref[1].id
            except Exception:
                pass
            return {"success": True, "doc_id": doc_id, "message": "チャットメッセージを保存しました"}
        except Exception as e:
            return {"success": False, "error": f"チャットメッセージの保存エラー: {str(e)}"}

    def get_messages(self, user_id: str, session_id: str, limit: int = 10, offset: int = 0) -> dict:
        """
        指定されたユーザー・セッションからチャットメッセージを取得し、結果を辞書で返却します。

        Args:
            user_id: ユーザーID
            session_id: セッションID
            limit: 取得するメッセージ数（デフォルト: 10）
            offset: ページネーションのオフセット（デフォルト: 0）

        Returns:
            辞書: {"messages": [...], "count": int, "error"?: str}
        """
        try:
            # パラメータのバリデーション
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

            # リポジトリからメッセージを取得
            messages = self.chats_repository.get_messages(user_id, session_id, limit_val, offset_val)

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
            # 例外が発生した場合は空のメッセージリストを返却
            return {"messages": [], "error": str(e)} 