# ログ設定ユーティリティ

"""
ログ設定とログ管理のユーティリティ関数
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logging():
    """ログ設定を初期化"""
    
    # ログディレクトリの作成
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # ログファイル名（日付付き）
    log_file = log_dir / f"smart-planter-{datetime.now().strftime('%Y%m%d')}.log"
    
    # ログレベル設定
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # ログフォーマット
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # アプリケーション固有のロガー
    app_logger = logging.getLogger('smart_planter')
    app_logger.setLevel(logging.INFO)
    
    return app_logger

def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得"""
    return logging.getLogger(f'smart_planter.{name}')
