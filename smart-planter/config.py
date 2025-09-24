# すくすくミントちゃん 設定ファイル

"""
設定管理モジュール
環境別の設定を管理
"""

import os
from pathlib import Path

class Config:
    """基本設定クラス"""
    
    # プロジェクト情報
    PROJECT_NAME = "すくすくミントちゃん"
    VERSION = "1.0.0"
    
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    
    # データベース設定
    DATA_BASE_PATH = os.environ.get('DATA_BASE_PATH', '/mnt/usb-storage')
    
    # センサー設定
    SENSOR_CHECK_INTERVAL = int(os.environ.get('SENSOR_CHECK_INTERVAL', 60))
    TEMPERATURE_HUMIDITY_INTERVAL = int(os.environ.get('TEMPERATURE_HUMIDITY_INTERVAL', 1800))
    SOIL_MOISTURE_INTERVAL = int(os.environ.get('SOIL_MOISTURE_INTERVAL', 300))
    
    # 給水設定
    SOIL_MOISTURE_THRESHOLD = int(os.environ.get('SOIL_MOISTURE_THRESHOLD', 159))
    WATERING_INTERVAL_HOURS = int(os.environ.get('WATERING_INTERVAL_HOURS', 12))
    WATERING_DURATION_SECONDS = int(os.environ.get('WATERING_DURATION_SECONDS', 5))
    WATER_AMOUNT_ML = int(os.environ.get('WATER_AMOUNT_ML', 100))
    
    # カメラ設定
    CAMERA_RESOLUTION_WIDTH = int(os.environ.get('CAMERA_RESOLUTION_WIDTH', 1280))
    CAMERA_RESOLUTION_HEIGHT = int(os.environ.get('CAMERA_RESOLUTION_HEIGHT', 720))
    AUTO_CAPTURE_TIME = os.environ.get('AUTO_CAPTURE_TIME', '06:00')
    
    # LINE通知設定
    LINE_NOTIFY_TOKEN = os.environ.get('LINE_NOTIFY_TOKEN')
    LINE_NOTIFY_API_URL = os.environ.get('LINE_NOTIFY_API_URL', 'https://notify-api.line.me/api/notify')
    
    # ログ設定
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH', '/mnt/usb-storage/logs')

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    DATA_BASE_PATH = './data'

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    DATA_BASE_PATH = '/mnt/usb-storage'

class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DEBUG = True
    DATA_BASE_PATH = './test_data'

# 設定辞書
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

