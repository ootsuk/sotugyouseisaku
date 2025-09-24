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

## 📁 ファイル作成手順（新人エンジニア向け）

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

### 📄 sensors_api.py
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
            
            # TODO: 実際の履歴データを取得
            mock_history = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'temperature': 25.5,
                    'humidity': 60.0,
                    'soil_moisture': 180
                }
            ]
            
            self.logger.info(f"センサーデータ履歴取得API呼び出し (期間: {hours}時間)")
            return jsonify({
                'status': 'success',
                'data': mock_history,
                'period_hours': hours
            }), 200
            
        except Exception as e:
            self.logger.error(f"センサーデータ履歴取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'センサーデータ履歴の取得に失敗しました'
            }), 500

# APIリソースを登録
api.add_resource(SensorsResource, '/')
api.add_resource(SensorHistoryResource, '/history')
```

### 📄 watering_api.py
給水制御API

```python
from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
import logging
from datetime import datetime
from typing import Dict, Any

# 給水制御モジュールをインポート（実装後）
# from src.watering.watering_logic import WateringLogic

watering_bp = Blueprint('watering', __name__, url_prefix='/api/watering')
api = Api(watering_bp)

class WateringResource(Resource):
    """給水制御API"""
    
    def __init__(self):
        self.logger = logging.getLogger('api.watering')
        # self.watering_logic = WateringLogic()  # 実装後に有効化
    
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
            # TODO: 実際の給水履歴を取得
            mock_history = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'manual',
                    'duration': 5,
                    'soil_moisture_before': 150,
                    'soil_moisture_after': 200
                }
            ]
            
            self.logger.info("給水履歴取得API呼び出し")
            return jsonify({
                'status': 'success',
                'data': mock_history
            }), 200
            
        except Exception as e:
            self.logger.error(f"給水履歴取得エラー: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': '給水履歴の取得に失敗しました'
            }), 500

# APIリソースを登録
api.add_resource(WateringResource, '/')
api.add_resource(WateringHistoryResource, '/history')
```

### 📄 api_blueprint.py
API統合管理

```python
from flask import Flask
from src.api.sensors_api import sensors_bp
from src.api.watering_api import watering_bp
# from src.api.camera_api import camera_bp
# from src.api.notifications_api import notifications_bp

def register_api_blueprints(app: Flask):
    """APIブループリントをFlaskアプリに登録"""
    
    # センサーAPI
    app.register_blueprint(sensors_bp)
    
    # 給水API
    app.register_blueprint(watering_bp)
    
    # カメラAPI（実装後）
    # app.register_blueprint(camera_bp)
    
    # 通知API（実装後）
    # app.register_blueprint(notifications_bp)
    
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
```

### 2. 給水制御テスト
```bash
# 手動給水実行
curl -X POST http://localhost:5000/api/watering/ \
  -H "Content-Type: application/json" \
  -d '{"duration": 10}'

# 給水履歴取得
curl -X GET http://localhost:5000/api/watering/history
```

## 📚 API仕様書

### エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/sensors/` | 全センサーデータ取得 |
| GET | `/api/sensors/history` | センサーデータ履歴取得 |
| POST | `/api/watering/` | 手動給水実行 |
| GET | `/api/watering/history` | 給水履歴取得 |

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
