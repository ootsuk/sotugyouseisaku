"""
センサーデータ取得API
温湿度、土壌水分、水位センサーのデータ取得エンドポイント
"""

from flask import Blueprint, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any

# センサー制御モジュールをインポート
try:
    from gpiozero import MCP3002
    SENSOR_AVAILABLE = True
except ImportError:
    SENSOR_AVAILABLE = False
    # Raspberry Pi以外の環境ではダミーデータを使用

sensors_bp = Blueprint('sensors', __name__, url_prefix='/api/sensors')
api = Api(sensors_bp)


class SensorsResource(Resource):
    """全センサーデータ取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.sensors')
    
    def get(self):
        """全センサーデータを取得"""
        try:
            # 土壌水分センサーデータ取得
            soil_moisture = self._get_soil_moisture()
            
            # TODO: 温湿度センサー実装後に取得
            temperature = 25.5
            humidity = 60.0
            
            # TODO: 水位センサー実装後に取得
            water_volume = 1500
            water_percentage = 75
            
            sensor_data = {
                'temperature': temperature,
                'humidity': humidity,
                'soil_moisture': soil_moisture,
                'water_volume': water_volume,
                'water_percentage': water_percentage,
                'pressure': None,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("センサーデータ取得API呼び出し")
            return {
                'status': 'success',
                'data': sensor_data
            }, 200
            
        except Exception as e:
            self.logger.error(f"センサーデータ取得エラー: {str(e)}")
            return {
                'status': 'error',
                'message': 'センサーデータの取得に失敗しました'
            }, 500
    
    def _get_soil_moisture(self) -> int:
        """土壌水分センサーから値を取得"""
        if not SENSOR_AVAILABLE:
            return 180  # ダミー値
        
        try:
            sen0193 = MCP3002(channel=0)
            raw_value = int(sen0193.value * 255)
            return raw_value
        except Exception as e:
            self.logger.warning(f"土壌水分センサー読み取りエラー: {e}")
            return 180  # エラー時はダミー値


class SensorHistoryResource(Resource):
    """センサーデータ履歴取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.sensors.history')
    
    def get(self):
        """センサーデータの履歴を取得"""
        try:
            # クエリパラメータから期間を取得
            hours = request.args.get('hours', 24, type=int)
            sensor_name = request.args.get('sensor', 'all', type=str)
            
            # TODO: 実際のセンサーデータ履歴を取得
            # CSVファイルやデータベースから読み込む
            mock_history = []
            
            self.logger.info(f"センサーデータ履歴取得API呼び出し (期間: {hours}時間)")
            return ({
                'status': 'success',
                'data': mock_history,
                'period_hours': hours,
                'sensor': sensor_name
            }), 200
            
        except Exception as e:
            self.logger.error(f"センサーデータ履歴取得エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': 'センサーデータ履歴の取得に失敗しました'
            }), 500


class WaterLevelResource(Resource):
    """水の残量取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.sensors.water_level')
    
    def get(self):
        """水の残量データを取得"""
        try:
            # TODO: 実際の圧力センサーデータを取得
            mock_water_data = {
                'pressure': None,
                'water_height': 25.0,
                'water_volume': 1500,
                'water_percentage': 75,
                'status': 'normal',
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("水の残量取得API呼び出し")
            return ({
                'status': 'success',
                'data': mock_water_data
            }), 200
            
        except Exception as e:
            self.logger.error(f"水の残量取得エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': '水の残量データの取得に失敗しました'
            }), 500


# APIリソースを登録（末尾スラッシュあり・なし両方対応）
api.add_resource(SensorsResource, '/', '//') 
api.add_resource(SensorHistoryResource, '/history', '/history/')
api.add_resource(WaterLevelResource, '/water-level', '/water-level/')

