"""
カメラ制御API
写真撮影、画像取得、タイムラプス生成のAPIエンドポイント
"""

from flask import Blueprint, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any

# カメラ制御モジュールをインポート
from src.camera.camera import PlantCaptureManager

camera_bp = Blueprint('camera', __name__, url_prefix='/api/camera')
api = Api(camera_bp)

# カメラマネージャーのインスタンスを作成
camera_manager = PlantCaptureManager()


class CaptureResource(Resource):
    """写真撮影API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.camera.capture')
    
    def post(self):
        """写真を撮影して保存"""
        try:
            # リクエストデータを取得（オプション）
            data = request.get_json(silent=True) or {}
            save = data.get('save', True)
            
            self.logger.info("写真撮影API呼び出し")
            
            # 実際にカメラで撮影
            camera_error_msg = None
            try:
                camera_manager.capture_and_save()
                message = '写真を撮影しました'
                status = 'success'
            except Exception as camera_error:
                # カメラエラー（接続されていない等）の場合
                self.logger.warning(f"カメラ未接続またはエラー: {str(camera_error)}")
                message = 'カメラが接続されていません（開発環境）'
                status = 'warning'
                camera_error_msg = str(camera_error)
            
            result = {
                'status': status,
                'message': message,
                'camera_error': camera_error_msg,
                'timestamp': datetime.now().isoformat()
            }
            
            return result, 200
            
        except Exception as e:
            self.logger.error(f"写真撮影エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': f'写真撮影に失敗しました: {str(e)}'
            }), 500


class ImageListResource(Resource):
    """画像リスト取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.camera.images')
    
    def get(self):
        """保存された画像のリストを取得"""
        try:
            import glob
            import os
            
            # 画像ディレクトリから画像ファイルを取得
            image_dir = "plant_images"
            if not os.path.exists(image_dir):
                return ({
                    'status': 'success',
                    'data': [],
                    'count': 0
                }), 200
            
            image_files = glob.glob(os.path.join(image_dir, "*.jp*g"))
            image_files.sort(reverse=True)  # 新しい順
            
            # ファイル名のリストを作成
            images = []
            for file_path in image_files[:50]:  # 最新50件
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_time = os.path.getctime(file_path)
                
                images.append({
                    'filename': file_name,
                    'path': file_path,
                    'size': file_size,
                    'created_at': datetime.fromtimestamp(file_time).isoformat()
                })
            
            self.logger.info(f"画像リスト取得: {len(images)}件")
            return ({
                'status': 'success',
                'data': images,
                'count': len(images)
            }), 200
            
        except Exception as e:
            self.logger.error(f"画像リスト取得エラー: {str(e)}")
            return ({
                'status': 'error',
                'message': '画像リストの取得に失敗しました'
            }), 500


# APIリソースを登録
api.add_resource(CaptureResource, '/capture')
api.add_resource(ImageListResource, '/images')

