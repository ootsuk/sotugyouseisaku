"""
API統合管理
全APIブループリントを登録してFlaskアプリに統合
"""

from flask import Flask
import logging

# 各APIブループリントをインポート
from src.api.sensors_api import sensors_bp
from src.api.watering_api import watering_bp
from src.api.camera_api import camera_bp
from src.api.notifications_api import notifications_bp
from src.api.settings_api import settings_bp


def register_api_blueprints(app: Flask):
    """APIブループリントをFlaskアプリに登録"""
    
    logger = logging.getLogger('api')
    
    try:
        # センサーAPI
        app.register_blueprint(sensors_bp)
        logger.info("センサーAPI登録完了")
        
        # 給水API
        app.register_blueprint(watering_bp)
        logger.info("給水API登録完了")
        
        # カメラAPI
        app.register_blueprint(camera_bp)
        logger.info("カメラAPI登録完了")
        
        # 通知API
        app.register_blueprint(notifications_bp)
        logger.info("通知API登録完了")
        
        # 設定API
        app.register_blueprint(settings_bp)
        logger.info("設定API登録完了")
        
        logger.info("✅ 全APIブループリント登録完了")
        
    except Exception as e:
        logger.error(f"❌ APIブループリント登録エラー: {str(e)}")
        raise


def get_api_info() -> dict:
    """登録されているAPI情報を取得"""
    return {
        'apis': [
            {
                'name': 'Sensors API',
                'prefix': '/api/sensors',
                'endpoints': ['/', '/history', '/water-level']
            },
            {
                'name': 'Watering API',
                'prefix': '/api/watering',
                'endpoints': ['/', '/history', '/stop']
            },
            {
                'name': 'Camera API',
                'prefix': '/api/camera',
                'endpoints': ['/capture', '/images']
            },
            {
                'name': 'Notifications API',
                'prefix': '/api/notifications',
                'endpoints': ['/test', '/alert', '/history']
            },
            {
                'name': 'Settings API',
                'prefix': '/api/settings',
                'endpoints': ['/', '/reset']
            }
        ],
        'total_apis': 5,
        'total_endpoints': 14
    }

