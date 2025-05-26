"""
日時ユーティリティモジュール
日本時間（JST）での日時操作を提供
"""
from datetime import datetime, date, time, timezone, timedelta
from typing import Optional, Union
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import JST, DATE_FORMAT, DATETIME_FORMAT, TIME_FORMAT

def now_jst() -> datetime:
    """
    現在の日本時間を取得
    
    Returns:
        datetime: 現在の日本時間
    """
    return datetime.now(JST)

def jst_date() -> str:
    """
    現在の日本時間の日付を文字列で取得
    
    Returns:
        str: YYYY-MM-DD形式の日付文字列
    """
    return now_jst().strftime(DATE_FORMAT)

def jst_datetime() -> str:
    """
    現在の日本時間の日時を文字列で取得
    
    Returns:
        str: YYYY-MM-DD HH:MM:SS形式の日時文字列
    """
    return now_jst().strftime(DATETIME_FORMAT)

def jst_time() -> str:
    """
    現在の日本時間の時刻を文字列で取得
    
    Returns:
        str: HH:MM:SS形式の時刻文字列
    """
    return now_jst().strftime(TIME_FORMAT)

def to_jst(dt: datetime) -> datetime:
    """
    任意のdatetimeオブジェクトを日本時間に変換
    
    Args:
        dt (datetime): 変換対象のdatetimeオブジェクト
        
    Returns:
        datetime: 日本時間に変換されたdatetimeオブジェクト
    """
    if dt.tzinfo is None:
        # タイムゾーン情報がない場合はUTCとして扱う
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(JST)

def format_jst_date(dt: Optional[datetime] = None, format_str: str = DATE_FORMAT) -> str:
    """
    日本時間の日付を指定フォーマットで文字列化
    
    Args:
        dt (Optional[datetime]): 対象のdatetimeオブジェクト（Noneの場合は現在時刻）
        format_str (str): フォーマット文字列
        
    Returns:
        str: フォーマットされた日付文字列
    """
    if dt is None:
        dt = now_jst()
    else:
        dt = to_jst(dt)
    return dt.strftime(format_str)

def format_jst_datetime(dt: Optional[datetime] = None, format_str: str = DATETIME_FORMAT) -> str:
    """
    日本時間の日時を指定フォーマットで文字列化
    
    Args:
        dt (Optional[datetime]): 対象のdatetimeオブジェクト（Noneの場合は現在時刻）
        format_str (str): フォーマット文字列
        
    Returns:
        str: フォーマットされた日時文字列
    """
    if dt is None:
        dt = now_jst()
    else:
        dt = to_jst(dt)
    return dt.strftime(format_str)

def parse_date_jst(date_str: str, format_str: str = DATE_FORMAT) -> datetime:
    """
    日付文字列を日本時間のdatetimeオブジェクトに変換
    
    Args:
        date_str (str): 日付文字列
        format_str (str): フォーマット文字列
        
    Returns:
        datetime: 日本時間のdatetimeオブジェクト
    """
    dt = datetime.strptime(date_str, format_str)
    return dt.replace(tzinfo=JST)

def is_today_jst(target_date: Union[str, datetime, date]) -> bool:
    """
    指定された日付が日本時間の今日かどうかを判定
    
    Args:
        target_date (Union[str, datetime, date]): 判定対象の日付
        
    Returns:
        bool: 今日の場合True
    """
    today = now_jst().date()
    
    if isinstance(target_date, str):
        target_dt = datetime.strptime(target_date, DATE_FORMAT).date()
    elif isinstance(target_date, datetime):
        target_dt = to_jst(target_date).date()
    elif isinstance(target_date, date):
        target_dt = target_date
    else:
        raise ValueError("Unsupported date type")
    
    return target_dt == today

def get_week_start_jst() -> str:
    """
    日本時間の今週の開始日（月曜日）を取得
    
    Returns:
        str: YYYY-MM-DD形式の日付文字列
    """
    today = now_jst()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    return week_start.strftime(DATE_FORMAT)

def get_month_start_jst() -> str:
    """
    日本時間の今月の開始日を取得
    
    Returns:
        str: YYYY-MM-DD形式の日付文字列
    """
    today = now_jst()
    month_start = today.replace(day=1)
    return month_start.strftime(DATE_FORMAT)

def get_system_datetime_info() -> dict:
    """
    システムメッセージ用の現在日時情報を取得
    
    Returns:
        dict: 現在の日時情報
    """
    current_jst = now_jst()
    
    return {
        "current_datetime": format_jst_datetime(current_jst),
        "current_date": format_jst_date(current_jst),
        "current_time": jst_time(),
        "timezone": "Asia/Tokyo (JST, UTC+9)",
        "weekday": current_jst.strftime("%A"),
        "weekday_jp": ["月", "火", "水", "木", "金", "土", "日"][current_jst.weekday()],
        "week_start": get_week_start_jst(),
        "month_start": get_month_start_jst()
    }

# 便利な定数
WEEKDAYS_JP = ["月", "火", "水", "木", "金", "土", "日"]
MONTHS_JP = ["1月", "2月", "3月", "4月", "5月", "6月", 
             "7月", "8月", "9月", "10月", "11月", "12月"] 