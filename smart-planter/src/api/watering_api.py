"""
給水制御API
手動給水、緊急停止、給水履歴のAPIエンドポイント
"""

from flask import Blueprint, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any

# 給水制御モジュールをインポート（実装後に有効化）
# from src.watering.watering_controller import WateringController

watering_bp = Blueprint('watering', __name__, url_prefix='/api/watering')
api = Api(watering_bp)


class WateringResource(Resource):
    """給水制御API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.watering')
        # self.watering_controller = WateringController()  # 実装後に有効化
    
    def post(self):
        """手動給水を実行"""
        try:
            # リクエストデータを取得
            data = request.get_json(silent=True) or {}
            duration = data.get('duration', 5)  # デフォルト5秒
            
            # TODO: 実際の給水制御を実行
            # result = self.watering_controller.manual_water(duration)
            
            self.logger.info(f"手動給水実行API呼び出し (時間: {duration}秒)")
            
            # 給水実行のシミュレーション
            result = {
                'status': 'success',
                'message': f'給水が完了しました (時間: {duration}秒)',
                'duration': duration,
                'soil_moisture_before': 150,
                'soil_moisture_after': None,  # 給水後に測定
                'timestamp': datetime.now().isoformat()
            }
            
            return (result), 200
            
        except Exception as e:
            self.logger.error(f"給水実行エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': f'給水の実行に失敗しました: {str(e)}'
            }), 500


class WateringHistoryResource(Resource):
    """給水履歴取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.watering.history')
    
    def get(self):
        """給水履歴を取得"""
        try:
            # クエリパラメータから期間を取得
            days = request.args.get('days', 7, type=int)
            
            # TODO: 実際の給水履歴をCSVまたはデータベースから取得
            # from src.data.data_manager import DataManager
            # data_manager = DataManager()
            # history = data_manager.get_watering_history(days)
            
            # モックデータ（実装例）
            mock_history = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'manual': False,
                    'duration': 5,
                    'soil_moisture_before': 150,
                    'soil_moisture_after': 200,
                    'success': True
                }
            ]
            
            self.logger.info(f"給水履歴取得API呼び出し (期間: {days}日)")
            return ({
                'status': 'success',
                'data': mock_history,
                'days': days,
                'count': len(mock_history)
            }), 200
            
        except Exception as e:
            self.logger.error(f"給水履歴取得エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': '給水履歴の取得に失敗しました'
            }), 500


class WateringStopResource(Resource):
    """給水緊急停止API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.watering.stop')
    
    def post(self):
        """給水を緊急停止"""
        try:
            # TODO: 実際の給水停止処理
            # self.watering_controller.emergency_stop()
            
            self.logger.warning("給水緊急停止API呼び出し")
            
            result = {
                'status': 'success',
                'message': '給水を緊急停止しました',
                'timestamp': datetime.now().isoformat()
            }
            
            return (result), 200
            
        except Exception as e:
            self.logger.error(f"給水停止エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': '給水停止に失敗しました'
            }), 500


# APIリソースを登録（末尾スラッシュあり・なし両方対応）
api.add_resource(WateringResource, '/', '//')
api.add_resource(WateringHistoryResource, '/history', '/history/')
api.add_resource(WateringStopResource, '/stop', '/stop/')

