# API機能 統合実装ガイド

## 📋 概要
REST APIエンドポイントの実装手順書。センサー、給水、カメラ、通知の各機能へのAPIアクセスを提供

## 🎯 実装目標
- センサーデータ取得API
- 給水制御API
- カメラ制御API
- 通知管理API
- API認証・エラーハンドリング
- API仕様書の自動生成

## 🛠️ 必要な環境

### ソフトウェア
- Python 3.11.x
- Flask 2.3.3
- Flask-RESTful
- Flask-CORS
- marshmallow (データシリアライゼーション)

## 📁 ファイル作成手順

### Step 1: APIディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# APIディレクトリの確認
ls -la src/api/
```

### Step 2: 各ファイルの作成順序
1. `src/api/sensors_api.py` - センサーAPI
2. `src/api/watering_api.py` - 給水API
3. `src/api/camera_api.py` - カメラAPI
4. `src/api/notifications_api.py` - 通知API
5. `src/api/api_blueprint.py` - API統合

### Step 3: ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/api/sensors_api.py
touch src/api/watering_api.py
touch src/api/camera_api.py
touch src/api/notifications_api.py
touch src/api/api_blueprint.py
```

### Step 4: 依存関係の追加
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# 必要なライブラリをインストール
pip install Flask-RESTful
pip install Flask-CORS
pip install marshmallow

# requirements.txtを更新
pip freeze > requirements.txt
```

## 📄 実装コード

### 📄 src/api/sensors_api.py
センサーデータ取得API

```python
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any

# センサー制御モジュールをインポート（実装後）
# from src.sensors.sensor_manager import SensorManager

sensors_bp = Blueprint('sensors', __name__, url_prefix='/api/sensors')
api = Api(sensors_bp)

class SensorsResource(Resource):
    """センサーデータ取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.sensors')
        # self.sensor_manager = SensorManager()  # 実装後に有効化
    
    def get(self):
        """全センサーデータを取得"""
        try:
            # TODO: 実際のセンサーデータを取得
            mock_data = {
                'temperature': 25.5,
                'humidity': 60.0,
                'soil_moisture': 180,
                'water_level': 'normal',
                'pressure': 1013.25,
                'water_volume': 500.0,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("センサーデータ取得API呼び出し")
            return jsonify({
                'status': 'success',
                'data': mock_data
            }), 200
            
        except Exception as e:
            self.logger.error(f"センサーデータ取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'センサーデータの取得に失敗しました'
            }), 500

class SensorHistoryResource(Resource):
    """センサーデータ履歴取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.sensors.history')
    
    def get(self):
        """指定期間のセンサーデータ履歴を取得"""
        try:
            # クエリパラメータから期間を取得
            hours = request.args.get('hours', 24, type=int)
            sensor_name = request.args.get('sensor', 'all')
            
            # TODO: 実際の履歴データを取得
            mock_history = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'temperature': 25.5,
                    'humidity': 60.0,
                    'soil_moisture': 180,
                    'sensor': sensor_name
                }
            ]
            
            self.logger.info(f"センサーデータ履歴取得API呼び出し (期間: {hours}時間)")
            return jsonify({
                'status': 'success',
                'data': mock_history,
                'period_hours': hours,
                'sensor': sensor_name
            }), 200
            
        except Exception as e:
            self.logger.error(f"センサーデータ履歴取得エラー: {str(e)}")
            return jsonify({
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
                'pressure': 1013.25,
                'water_height': 25.0,
                'water_volume': 500.0,
                'water_percentage': 83.3,
                'status': 'normal',
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("水の残量取得API呼び出し")
            return jsonify({
                'status': 'success',
                'data': mock_water_data
            }), 200
            
        except Exception as e:
            self.logger.error(f"水の残量取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '水の残量データの取得に失敗しました'
            }), 500

# APIリソースを登録
api.add_resource(SensorsResource, '/')
api.add_resource(SensorHistoryResource, '/history')
api.add_resource(WaterLevelResource, '/water-level')
```

### 📄 src/api/watering_api.py
給水制御API

```python
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any

# 給水制御モジュールをインポート（実装後）
# from src.watering.watering_scheduler import WateringScheduler

watering_bp = Blueprint('watering', __name__, url_prefix='/api/watering')
api = Api(watering_bp)

class WateringResource(Resource):
    """給水制御API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.watering')
        # self.watering_scheduler = WateringScheduler()  # 実装後に有効化
    
    def post(self):
        """手動給水を実行"""
        try:
            # リクエストデータを取得
            data = request.get_json() or {}
            duration = data.get('duration', 5)  # デフォルト5秒
            
            # TODO: 実際の給水制御を実行
            self.logger.info(f"手動給水実行API呼び出し (時間: {duration}秒)")
            
            # 給水実行のシミュレーション
            result = {
                'status': 'success',
                'message': f'給水が完了しました (時間: {duration}秒)',
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(result), 200
            
        except Exception as e:
            self.logger.error(f"給水実行エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '給水の実行に失敗しました'
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
            
            # TODO: 実際の給水履歴を取得
            mock_history = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'manual',
                    'duration': 5,
                    'soil_moisture_before': 150,
                    'soil_moisture_after': 200,
                    'success': True
                }
            ]
            
            self.logger.info("給水履歴取得API呼び出し")
            return jsonify({
                'status': 'success',
                'data': mock_history,
                'period_days': days
            }), 200
            
        except Exception as e:
            self.logger.error(f"給水履歴取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '給水履歴の取得に失敗しました'
            }), 500

class WateringStatusResource(Resource):
    """給水ステータス取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.watering.status')
    
    def get(self):
        """給水システムのステータスを取得"""
        try:
            # TODO: 実際のステータスを取得
            mock_status = {
                'system_running': True,
                'pump_running': False,
                'last_watering': datetime.now().isoformat(),
                'next_check': datetime.now().isoformat(),
                'auto_mode': True
            }
            
            self.logger.info("給水ステータス取得API呼び出し")
            return jsonify({
                'status': 'success',
                'data': mock_status
            }), 200
            
        except Exception as e:
            self.logger.error(f"給水ステータス取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '給水ステータスの取得に失敗しました'
            }), 500

# APIリソースを登録
api.add_resource(WateringResource, '/')
api.add_resource(WateringHistoryResource, '/history')
api.add_resource(WateringStatusResource, '/status')
```

### 📄 src/api/camera_api.py
カメラ制御API

```python
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any
import base64

# カメラ制御モジュールをインポート（実装後）
# from src.camera.camera_control import CameraController

camera_bp = Blueprint('camera', __name__, url_prefix='/api/camera')
api = Api(camera_bp)

class CameraCaptureResource(Resource):
    """カメラ撮影API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.camera.capture')
        # self.camera_controller = CameraController()  # 実装後に有効化
    
    def post(self):
        """写真を撮影"""
        try:
            # リクエストデータを取得
            data = request.get_json() or {}
            save_image = data.get('save', True)
            
            # TODO: 実際のカメラ撮影を実行
            self.logger.info("カメラ撮影API呼び出し")
            
            # 撮影のシミュレーション
            result = {
                'status': 'success',
                'message': '写真を撮影しました',
                'filename': f"plant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                'timestamp': datetime.now().isoformat()
            }
            
            if save_image:
                result['saved'] = True
                result['path'] = f"/data/images/{result['filename']}"
            
            return jsonify(result), 200
            
        except Exception as e:
            self.logger.error(f"カメラ撮影エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '写真の撮影に失敗しました'
            }), 500

class ImageListResource(Resource):
    """画像リスト取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.camera.images')
    
    def get(self):
        """画像リストを取得"""
        try:
            # クエリパラメータから期間を取得
            days = request.args.get('days', 30, type=int)
            
            # TODO: 実際の画像リストを取得
            mock_images = [
                {
                    'filename': 'plant_20250101_120000.jpg',
                    'timestamp': datetime.now().isoformat(),
                    'size_bytes': 1024000,
                    'width': 1920,
                    'height': 1080
                }
            ]
            
            self.logger.info("画像リスト取得API呼び出し")
            return jsonify({
                'status': 'success',
                'data': mock_images,
                'period_days': days
            }), 200
            
        except Exception as e:
            self.logger.error(f"画像リスト取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '画像リストの取得に失敗しました'
            }), 500

class TimelapseResource(Resource):
    """タイムラプス作成API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.camera.timelapse')
    
    def post(self):
        """タイムラプスを作成"""
        try:
            # リクエストデータを取得
            data = request.get_json() or {}
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            fps = data.get('fps', 10)
            
            # TODO: 実際のタイムラプス作成を実行
            self.logger.info("タイムラプス作成API呼び出し")
            
            result = {
                'status': 'success',
                'message': 'タイムラプスを作成しました',
                'filename': f"timelapse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                'fps': fps,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(result), 200
            
        except Exception as e:
            self.logger.error(f"タイムラプス作成エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'タイムラプスの作成に失敗しました'
            }), 500

# APIリソースを登録
api.add_resource(CameraCaptureResource, '/capture')
api.add_resource(ImageListResource, '/images')
api.add_resource(TimelapseResource, '/timelapse')
```

### 📄 src/api/notifications_api.py
通知管理API

```python
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any

# 通知管理モジュールをインポート（実装後）
# from src.notifications.line_notify import LineNotifier

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')
api = Api(notifications_bp)

class NotificationResource(Resource):
    """通知送信API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.notifications')
        # self.line_notifier = LineNotifier()  # 実装後に有効化
    
    def post(self):
        """通知を送信"""
        try:
            # リクエストデータを取得
            data = request.get_json() or {}
            message = data.get('message', '')
            notification_type = data.get('type', 'info')
            
            if not message:
                return jsonify({
                    'status': 'error',
                    'message': 'メッセージが指定されていません'
                }), 400
            
            # TODO: 実際の通知送信を実行
            self.logger.info(f"通知送信API呼び出し: {message}")
            
            result = {
                'status': 'success',
                'message': '通知を送信しました',
                'notification_type': notification_type,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(result), 200
            
        except Exception as e:
            self.logger.error(f"通知送信エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '通知の送信に失敗しました'
            }), 500

class NotificationHistoryResource(Resource):
    """通知履歴取得API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.notifications.history')
    
    def get(self):
        """通知履歴を取得"""
        try:
            # クエリパラメータから期間を取得
            days = request.args.get('days', 7, type=int)
            
            # TODO: 実際の通知履歴を取得
            mock_history = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'message': '🌧️ 自動給水が完了しました',
                    'type': 'watering',
                    'success': True
                }
            ]
            
            self.logger.info("通知履歴取得API呼び出し")
            return jsonify({
                'status': 'success',
                'data': mock_history,
                'period_days': days
            }), 200
            
        except Exception as e:
            self.logger.error(f"通知履歴取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '通知履歴の取得に失敗しました'
            }), 500

class NotificationSettingsResource(Resource):
    """通知設定API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.notifications.settings')
    
    def get(self):
        """通知設定を取得"""
        try:
            # TODO: 実際の通知設定を取得
            mock_settings = {
                'line_notify_enabled': True,
                'watering_notifications': True,
                'sensor_alerts': True,
                'daily_reports': True,
                'notification_time': '09:00'
            }
            
            self.logger.info("通知設定取得API呼び出し")
            return jsonify({
                'status': 'success',
                'data': mock_settings
            }), 200
            
        except Exception as e:
            self.logger.error(f"通知設定取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '通知設定の取得に失敗しました'
            }), 500
    
    def put(self):
        """通知設定を更新"""
        try:
            # リクエストデータを取得
            data = request.get_json() or {}
            
            # TODO: 実際の通知設定を更新
            self.logger.info("通知設定更新API呼び出し")
            
            result = {
                'status': 'success',
                'message': '通知設定を更新しました',
                'settings': data,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(result), 200
            
        except Exception as e:
            self.logger.error(f"通知設定更新エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '通知設定の更新に失敗しました'
            }), 500

# APIリソースを登録
api.add_resource(NotificationResource, '/')
api.add_resource(NotificationHistoryResource, '/history')
api.add_resource(NotificationSettingsResource, '/settings')
```

### 📄 src/api/api_blueprint.py
API統合管理

```python
from flask import Flask
from src.api.sensors_api import sensors_bp
from src.api.watering_api import watering_bp
from src.api.camera_api import camera_bp
from src.api.notifications_api import notifications_bp

def register_api_blueprints(app: Flask):
    """APIブループリントをFlaskアプリに登録"""
    
    # センサーAPI
    app.register_blueprint(sensors_bp)
    
    # 給水API
    app.register_blueprint(watering_bp)
    
    # カメラAPI
    app.register_blueprint(camera_bp)
    
    # 通知API
    app.register_blueprint(notifications_bp)
    
    # CORS設定（必要に応じて）
    from flask_cors import CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
```

## 🔧 Flaskアプリケーションへの統合

### main.pyの更新
```python
# main.pyに以下を追加
from src.api.api_blueprint import register_api_blueprints

def main():
    """メイン実行関数"""
    # ログ設定
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🌱 すくすくミントちゃん起動中...")
        
        # Flaskアプリケーション作成
        app = create_app()
        
        # APIブループリントを登録
        register_api_blueprints(app)
        
        # アプリケーション実行
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ アプリケーション停止")
    except Exception as e:
        logger.error(f"❌ アプリケーションエラー: {str(e)}")
        sys.exit(1)
```

## 🧪 APIテスト方法

### 1. センサーデータ取得テスト
```bash
# センサーデータ取得
curl -X GET http://localhost:5000/api/sensors/

# センサーデータ履歴取得
curl -X GET http://localhost:5000/api/sensors/history?hours=48

# 水の残量取得
curl -X GET http://localhost:5000/api/sensors/water-level
```

### 2. 給水制御テスト
```bash
# 手動給水実行
curl -X POST http://localhost:5000/api/watering/ \
  -H "Content-Type: application/json" \
  -d '{"duration": 10}'

# 給水履歴取得
curl -X GET http://localhost:5000/api/watering/history

# 給水ステータス取得
curl -X GET http://localhost:5000/api/watering/status
```

### 3. カメラ制御テスト
```bash
# 写真撮影
curl -X POST http://localhost:5000/api/camera/capture \
  -H "Content-Type: application/json" \
  -d '{"save": true}'

# 画像リスト取得
curl -X GET http://localhost:5000/api/camera/images?days=7

# タイムラプス作成
curl -X POST http://localhost:5000/api/camera/timelapse \
  -H "Content-Type: application/json" \
  -d '{"fps": 15}'
```

### 4. 通知管理テスト
```bash
# 通知送信
curl -X POST http://localhost:5000/api/notifications/ \
  -H "Content-Type: application/json" \
  -d '{"message": "テスト通知です", "type": "info"}'

# 通知履歴取得
curl -X GET http://localhost:5000/api/notifications/history

# 通知設定取得
curl -X GET http://localhost:5000/api/notifications/settings

# 通知設定更新
curl -X PUT http://localhost:5000/api/notifications/settings \
  -H "Content-Type: application/json" \
  -d '{"watering_notifications": true}'
```

## 📚 API仕様書

### エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/sensors/` | 全センサーデータ取得 |
| GET | `/api/sensors/history` | センサーデータ履歴取得 |
| GET | `/api/sensors/water-level` | 水の残量取得 |
| POST | `/api/watering/` | 手動給水実行 |
| GET | `/api/watering/history` | 給水履歴取得 |
| GET | `/api/watering/status` | 給水ステータス取得 |
| POST | `/api/camera/capture` | 写真撮影 |
| GET | `/api/camera/images` | 画像リスト取得 |
| POST | `/api/camera/timelapse` | タイムラプス作成 |
| POST | `/api/notifications/` | 通知送信 |
| GET | `/api/notifications/history` | 通知履歴取得 |
| GET | `/api/notifications/settings` | 通知設定取得 |
| PUT | `/api/notifications/settings` | 通知設定更新 |

### レスポンス形式
```json
{
  "status": "success|error",
  "data": {},
  "message": "メッセージ",
  "timestamp": "2025-01-01T00:00:00"
}
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

