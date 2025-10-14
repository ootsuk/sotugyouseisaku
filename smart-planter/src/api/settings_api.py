"""
設定管理API
システム設定の取得・保存エンドポイント
"""

from flask import Blueprint, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any
import json
import os

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')
api = Api(settings_bp)

# 設定ファイルのパス
SETTINGS_FILE = 'config/settings.json'


class SettingsResource(Resource):
    """設定管理API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.settings')
        self.default_settings = {
            'temperatureHumidityInterval': 1800,
            'soilMoistureInterval': 300,
            'sensorCheckInterval': 60,
            'soilMoistureThreshold': 159,
            'wateringIntervalHours': 12,
            'wateringDurationSeconds': 5,
            'waterAmountMl': 100,
            'cameraResolutionWidth': 1280,
            'cameraResolutionHeight': 720,
            'autoCaptureTime': '06:00',
            'imageRetentionDays': 90,
            'lineNotifyToken': '',
            'notifyWatering': True,
            'notifyError': True,
            'notifyWaterLow': True,
            'notifyDaily': False,
            'dataBasePath': '/mnt/usb-storage',
            'logLevel': 'INFO',
            'debugMode': False,
            'autoRestart': True,
            'tempAlertMin': 5,
            'tempAlertMax': 35,
            'humidityAlertMin': 30,
            'humidityAlertMax': 80,
            'sensorErrorThreshold': 3
        }
    
    def get(self):
        """設定を取得"""
        try:
            # 設定ファイルから読み込み
            settings = self._load_settings()
            
            self.logger.info("設定取得API呼び出し")
            return ({
                'status': 'success',
                'data': settings
            }), 200
            
        except Exception as e:
            self.logger.error(f"設定取得エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': '設定の取得に失敗しました'
            }), 500
    
    def post(self):
        """設定を保存"""
        try:
            # リクエストデータを取得
            new_settings = request.get_json(silent=True) or {}
            
            # 現在の設定を読み込み
            current_settings = self._load_settings()
            
            # 設定を更新
            current_settings.update(new_settings)
            
            # ファイルに保存
            self._save_settings(current_settings)
            
            self.logger.info(f"設定保存API呼び出し: {len(new_settings)}項目更新")
            return ({
                'status': 'success',
                'message': '設定を保存しました',
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            self.logger.error(f"設定保存エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': f'設定の保存に失敗しました: {str(e)}'
            }), 500
    
    def _load_settings(self) -> Dict[str, Any]:
        """設定ファイルから設定を読み込み"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.default_settings.copy()
        except Exception as e:
            self.logger.warning(f"設定ファイル読み込みエラー: {e}")
            return self.default_settings.copy()
    
    def _save_settings(self, settings: Dict[str, Any]):
        """設定をファイルに保存"""
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)


class SettingsResetResource(Resource):
    """設定リセットAPI"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.settings.reset')
    
    def post(self):
        """設定をデフォルトに戻す"""
        try:
            settings_resource = SettingsResource()
            
            # デフォルト設定を保存
            settings_resource._save_settings(settings_resource.default_settings)
            
            self.logger.info("設定リセットAPI呼び出し")
            return ({
                'status': 'success',
                'message': '設定をデフォルトに戻しました',
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            self.logger.error(f"設定リセットエラー: {str(e)}")
            return ({
                'status': 'error',
                'message': '設定のリセットに失敗しました'
            }), 500


# APIリソースを登録
api.add_resource(SettingsResource, '/')
api.add_resource(SettingsResetResource, '/reset')

