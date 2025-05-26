"""
アプリケーション設定ファイル
日本時間（JST）設定とその他の設定を管理
"""
import os
from datetime import timezone, timedelta
from typing import Optional

# 日本時間（JST）の設定
JST = timezone(timedelta(hours=9))

# 環境設定
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Firebase設定
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'nutrition-ai-app')
FIRESTORE_EMULATOR_HOST = os.getenv('FIRESTORE_EMULATOR_HOST')

# OpenAI設定
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')

# タイムゾーン設定
DEFAULT_TIMEZONE = JST
TIMEZONE_NAME = 'Asia/Tokyo'

# 日付フォーマット設定
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT = '%H:%M:%S'

# ログ設定
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# API設定
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '120'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# 栄養データ設定
NUTRITION_API_BASE_URL = os.getenv('NUTRITION_API_BASE_URL', 'https://api.example.com')
NUTRITION_CACHE_TTL = int(os.getenv('NUTRITION_CACHE_TTL', '3600'))  # 1時間

class Config:
    """設定クラス"""
    
    # 基本設定
    ENVIRONMENT = ENVIRONMENT
    DEBUG = DEBUG
    
    # タイムゾーン設定
    TIMEZONE = JST
    TIMEZONE_NAME = TIMEZONE_NAME
    
    # 日付フォーマット
    DATE_FORMAT = DATE_FORMAT
    DATETIME_FORMAT = DATETIME_FORMAT
    TIME_FORMAT = TIME_FORMAT
    
    # Firebase設定
    FIREBASE_PROJECT_ID = FIREBASE_PROJECT_ID
    FIRESTORE_EMULATOR_HOST = FIRESTORE_EMULATOR_HOST
    
    # OpenAI設定
    OPENAI_API_KEY = OPENAI_API_KEY
    OPENAI_MODEL = OPENAI_MODEL
    
    # API設定
    API_TIMEOUT = API_TIMEOUT
    MAX_RETRIES = MAX_RETRIES
    
    # ログ設定
    LOG_LEVEL = LOG_LEVEL
    LOG_FORMAT = LOG_FORMAT
    
    # 栄養データ設定
    NUTRITION_API_BASE_URL = NUTRITION_API_BASE_URL
    NUTRITION_CACHE_TTL = NUTRITION_CACHE_TTL
    
    @classmethod
    def get_timezone(cls) -> timezone:
        """タイムゾーンを取得"""
        return cls.TIMEZONE
    
    @classmethod
    def is_development(cls) -> bool:
        """開発環境かどうかを判定"""
        return cls.ENVIRONMENT == 'development'
    
    @classmethod
    def is_production(cls) -> bool:
        """本番環境かどうかを判定"""
        return cls.ENVIRONMENT == 'production'

# 設定インスタンス
config = Config() 