#!/usr/bin/env python3
# test_chat_service.py
# ChatService クラスのテスト

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# 親ディレクトリをパスに追加（backend/functions 直下をモジュール検索パスに）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# テスト対象のクラスをインポート
from services.chat_service import ChatService
from repositories.chats_repository import ChatsRepository


class TestChatService:

    def setup_method(self):
        """各テスト実行前の準備"""
        # テスト用のパラメータ
        self.user_id = "test_user_123"
        self.session_id = "test_session_456"
        self.limit = 5
        self.offset = 0

        # テスト用のモックメッセージデータ
        self.mock_messages = [
            {
                "id": "msg1",
                "doc_id": "doc1",
                "role": "user",
                "message_text": "こんにちは",
                "created_at": "2023-07-01T12:30:45.123Z",
                "user_id": self.user_id,
                "session_id": self.session_id
            },
            {
                "id": "msg2",
                "doc_id": "doc2",
                "role": "agent",
                "message_text": "いかがお手伝いしましょうか？",
                "created_at": "2023-07-01T12:31:00.456Z",
                "user_id": self.user_id,
                "session_id": self.session_id
            }
        ]

        # ChatsRepositoryをモック化
        self.mock_repository = MagicMock(spec=ChatsRepository)
        self.patcher = patch('services.chat_service.ChatsRepository', return_value=self.mock_repository)
        self.patcher.start()
        
        # テスト対象のインスタンスを作成
        self.chat_service = ChatService()

    def teardown_method(self):
        """各テスト実行後のクリーンアップ"""
        self.patcher.stop()

    def test_get_messages_success(self):
        """正常系: メッセージが存在する場合のテスト"""
        # get_messages メソッドのモック設定
        self.mock_repository.get_messages.return_value = self.mock_messages

        # サービスメソッドを実行
        result = self.chat_service.get_messages(
            user_id=self.user_id,
            session_id=self.session_id,
            limit=self.limit,
            offset=self.offset
        )

        # モックが正しく呼び出されたか検証
        self.mock_repository.get_messages.assert_called_once_with(
            self.user_id, self.session_id, self.limit, self.offset
        )

        # 戻り値の検証
        assert "messages" in result
        assert "count" in result
        assert result["count"] == 2
        assert len(result["messages"]) == 2

        # 整形されたメッセージの検証
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"] == "こんにちは"
        assert result["messages"][0]["timestamp"] == "2023-07-01T12:30:45.123Z"
        
        assert result["messages"][1]["role"] == "agent"
        assert result["messages"][1]["content"] == "いかがお手伝いしましょうか？"

    def test_get_messages_empty(self):
        """正常系: メッセージが存在しない場合のテスト"""
        # 空のリストを返すようにモック設定
        self.mock_repository.get_messages.return_value = []

        # サービスメソッドを実行
        result = self.chat_service.get_messages(
            user_id=self.user_id,
            session_id=self.session_id
        )

        # 戻り値の検証
        assert "messages" in result
        assert "count" in result
        assert result["count"] == 0
        assert len(result["messages"]) == 0

    def test_get_messages_invalid_limit(self):
        """異常系: 不正な limit 値を指定した場合のテスト"""
        # サービスメソッドを実行
        result = self.chat_service.get_messages(
            user_id=self.user_id,
            session_id=self.session_id,
            limit=-1  # 不正な値
        )

        # デフォルト値の 10 で呼び出されることを検証
        self.mock_repository.get_messages.assert_called_once_with(self.user_id, self.session_id, 10, 0)

    def test_get_messages_invalid_offset(self):
        """異常系: 不正な offset 値を指定した場合のテスト"""
        # サービスメソッドを実行
        result = self.chat_service.get_messages(
            user_id=self.user_id,
            session_id=self.session_id,
            offset=-5  # 不正な値
        )

        # デフォルト値の 0 で呼び出されることを検証
        self.mock_repository.get_messages.assert_called_once_with(self.user_id, self.session_id, 10, 0)

    def test_get_messages_exception(self):
        """異常系: 例外が発生した場合のテスト"""
        # 例外を発生させるようにモック設定
        self.mock_repository.get_messages.side_effect = Exception("データベース接続エラー")

        # サービスメソッドを実行
        result = self.chat_service.get_messages(
            user_id=self.user_id,
            session_id=self.session_id
        )

        # 戻り値の検証
        assert "messages" in result
        assert "error" in result
        assert len(result["messages"]) == 0
        assert "データベース接続エラー" in result["error"]

    def test_create_message_success(self):
        """正常系: メッセージ作成成功のテスト"""
        # create_message メソッドのモック設定
        doc_ref_mock = (None, MagicMock())
        doc_ref_mock[1].id = "new_message_id"
        self.mock_repository.create_message.return_value = doc_ref_mock

        # サービスメソッドを実行
        result = self.chat_service.create_message(
            user_id=self.user_id,
            session_id=self.session_id,
            role="user",
            message_text="テストメッセージ"
        )

        # モックが正しく呼び出されたか検証
        self.mock_repository.create_message.assert_called_once_with(
            self.user_id, self.session_id, "user", "テストメッセージ"
        )

        # 戻り値の検証
        assert "success" in result
        assert result["success"] is True
        assert "doc_id" in result
        assert result["doc_id"] == "new_message_id"
        assert "message" in result

    def test_create_message_exception(self):
        """異常系: メッセージ作成時に例外発生のテスト"""
        # 例外を発生させるようにモック設定
        self.mock_repository.create_message.side_effect = Exception("保存エラー")

        # サービスメソッドを実行
        result = self.chat_service.create_message(
            user_id=self.user_id,
            session_id=self.session_id,
            role="user",
            message_text="テストメッセージ"
        )

        # 戻り値の検証
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "保存エラー" in result["error"]


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 