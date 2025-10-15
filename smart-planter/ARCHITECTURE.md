# すくすくミントちゃん - システムアーキテクチャ説明書

## 📋 概要
このドキュメントでは、各ファイルの役割、連携方法、主要な関数について説明します。

---

## 🏗️ 全体アーキテクチャ

```
┌─────────────────────────────────────────────────┐
│  ユーザー（ブラウザ）                            │
└─────────────────────────────────────────────────┘
                    ↓ HTTP
┌─────────────────────────────────────────────────┐
│  main.py                                        │
│  - アプリケーションのエントリーポイント          │
│  - サーバー起動                                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  src/app/app.py                                 │
│  - Flaskアプリ作成                              │
│  - 画面表示ルート定義（HTML返す）               │
└─────────────────────────────────────────────────┘
                    ↓
        ┌──────────┴──────────┐
        ↓                     ↓
┌──────────────┐      ┌──────────────────┐
│ 画面表示     │      │ API (JSON返す)    │
│ templates/   │      │ src/api/         │
└──────────────┘      └──────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ センサー     │      │ カメラ       │      │ 給水制御     │
│ src/sensors/ │      │ src/camera/  │      │ src/watering/│
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## 📁 ファイル別の役割と連携

### 🔹 **1. main.py**（エントリーポイント）

**役割:**
- アプリケーションの起動
- ログシステムの初期化
- Flaskアプリの作成と実行

**主要な関数:**
```python
def main():
    """メイン実行関数"""
    # 1. ログ設定
    setup_logging()  # src/utils/logger.py から
    
    # 2. Flaskアプリ作成
    app = create_app()  # src/app/app.py から
    
    # 3. APIブループリント登録
    register_api_blueprints(app)  # src/api/api_blueprint.py から
    
    # 4. サーバー起動
    app.run(host='0.0.0.0', port=8080)
```

**連携先:**
- `src/app/app.py` - Flaskアプリ作成
- `src/api/api_blueprint.py` - API登録
- `src/utils/logger.py` - ログ設定

---

### 🔹 **2. src/app/app.py**（Flaskアプリケーション）

**役割:**
- Flaskアプリのインスタンス作成
- 画面表示ルートの定義のみ（シンプル）
- エラーハンドリング

**主要な関数:**
```python
def create_app():
    """Flaskアプリケーションを作成"""
    app = Flask(__name__)
    
    # ルート定義（画面表示のみ）
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/settings')
    def settings():
        return render_template('settings.html')
    
    return app
```

**連携先:**
- `src/web/templates/` - HTMLテンプレート
- `src/web/static/` - CSS/JavaScript

**重要:** APIエンドポイントは定義しない（src/api/に分離）

---

### 🔹 **3. src/api/api_blueprint.py**（API統合管理）

**役割:**
- 全てのAPIブループリントを統合
- Flaskアプリに一括登録

**主要な関数:**
```python
def register_api_blueprints(app: Flask):
    """APIブループリントをFlaskアプリに登録"""
    
    # 各APIを登録
    app.register_blueprint(sensors_bp)      # センサーAPI
    app.register_blueprint(watering_bp)     # 給水API
    app.register_blueprint(camera_bp)       # カメラAPI
    app.register_blueprint(notifications_bp) # 通知API
    app.register_blueprint(settings_bp)     # 設定API
```

**連携先:**
- `src/api/sensors_api.py`
- `src/api/watering_api.py`
- `src/api/camera_api.py`
- `src/api/notifications_api.py`
- `src/api/settings_api.py`

---

### 🔹 **4. src/api/sensors_api.py**（センサーAPI）

**役割:**
- センサーデータのRESTful API提供
- sensor_managerとの連携

**APIエンドポイント:**
```
GET /api/sensors/           - 全センサーデータ取得
GET /api/sensors/history    - センサー履歴取得
GET /api/sensors/water-level - 水位データ取得
```

**主要なクラス:**
```python
class SensorsResource(Resource):
    def get(self):
        """全センサーデータを取得"""
        # sensor_managerから最新データ取得
        latest_data = sensor_manager.get_latest_data()
        
        return {
            'status': 'success',
            'data': {
                'temperature': latest_data.get('temperature'),
                'humidity': latest_data.get('humidity'),
                'soil_moisture': latest_data.get('soil_moisture'),
                ...
            }
        }
```

**連携先:**
- `src/sensors/sensor_manager.py` - センサーデータ取得

---

### 🔹 **5. src/sensors/sensor_manager.py**（センサー統合管理）

**役割:**
- 全てのセンサーを統合管理
- バックグラウンドでの定期監視
- データキャッシング

**主要なクラスと関数:**
```python
class SensorManager:
    def __init__(self):
        """初期化"""
        # 各センサーのインスタンス作成
        self.sensors['temperature_humidity'] = AHT25Sensor()
        self.sensors['soil_moisture'] = SEN0193Sensor()
        self.sensors['water_level'] = FloatSwitch()
    
    def start_monitoring(self):
        """センサー監視開始"""
        # バックグラウンドスレッドで定期的にデータ取得
        # 60秒ごとに全センサーを読み取り
    
    def read_all_sensors(self):
        """全センサーのデータを読み取る"""
        # 各センサーのread_data()を呼び出し
        # 結果をキャッシュに保存
    
    def get_latest_data(self):
        """最新のセンサーデータを統合して取得"""
        # キャッシュから最新データを返す
        return {
            'temperature': ...,
            'humidity': ...,
            'soil_moisture': ...,
            'water_present': ...,
        }
```

**連携先:**
- `src/sensors/temperature_humidity.py` - 温湿度センサー
- `src/sensors/soil_moisture.py` - 土壌水分センサー
- `src/sensors/float_switch.py` - フロートスイッチ

---

### 🔹 **6. src/sensors/temperature_humidity.py**（AHT25センサー）

**役割:**
- AHT25温湿度センサーからI2C通信でデータ取得

**主要なクラス:**
```python
class AHT25Sensor(BaseSensor):
    def initialize(self):
        """センサー初期化"""
        # I2Cバスに接続
        # リセットコマンド送信
    
    def read_data(self):
        """温湿度データ読み取り"""
        # 1. 測定開始コマンド送信
        # 2. データ読み取り（6バイト）
        # 3. 温度・湿度に変換
        
        return {
            'temperature': 25.5,  # 摂氏
            'humidity': 60.0,     # %
            'timestamp': ...
        }
```

**エラーハンドリング:**
- Raspberry Pi以外 → ダミーデータ返す
- センサー未接続 → ダミーデータ返す
- 読み取りエラー → エラーカウント増加

---

### 🔹 **7. src/sensors/soil_moisture.py**（SEN0193センサー）

**役割:**
- SEN0193土壌水分センサーからADC経由でデータ取得

**主要なクラス:**
```python
class SEN0193Sensor(BaseSensor):
    def read_data(self):
        """土壌水分データ読み取り"""
        # 1. MCP3002 ADCから値取得（0.0-1.0）
        # 2. 生の値（0-255）に変換
        # 3. 電圧に変換
        # 4. 水分状態を判定
        
        return {
            'raw_value': 180,            # 生の値
            'voltage': 2.1,              # 電圧
            'moisture_percentage': 45.0, # 水分率
            'status': 'Optimal',         # Dry/Optimal/VeryWet
        }
    
    def _get_moisture_status(self, raw_value):
        """水分状態判定"""
        if raw_value > 200: return "Dry"
        elif raw_value > 150: return "Optimal"
        else: return "VeryWet"
```

**連携:**
- `record_soil_moisture.py` とは別（こちらはリアルタイム、recordはログ用）

---

### 🔹 **8. src/sensors/float_switch.py**（フロートスイッチ）

**役割:**
- 水タンクの水位をGPIOで検知

**主要なクラス:**
```python
class FloatSwitch(BaseSensor):
    def read_data(self):
        """水位データ読み取り"""
        # GPIOピンの状態を読み取り
        # LOW = 水あり、HIGH = 水なし
        
        return {
            'water_present': True/False,
            'level': 'normal'/'low',
        }
```

---

### 🔹 **9. src/api/camera_api.py**（カメラAPI）

**役割:**
- カメラ撮影のAPIエンドポイント提供

**APIエンドポイント:**
```
POST /api/camera/capture - 写真撮影
GET  /api/camera/images  - 画像リスト取得
```

**主要なクラス:**
```python
# モジュールレベルでカメラマネージャー作成
camera_manager = PlantCaptureManager()  # src/camera/camera.py から

class CaptureResource(Resource):
    def post(self):
        """写真撮影"""
        # camera.pyのcapture_and_save()を呼び出し
        camera_manager.capture_and_save()
        
        return {'status': 'success', 'message': '写真を撮影しました'}
```

**連携先:**
- `src/camera/camera.py` - 実際の撮影処理

---

### 🔹 **10. src/camera/camera.py**（カメラ撮影）

**役割:**
- OpenCVでカメラから画像取得
- JPEG保存
- 古い画像の自動削除

**主要なクラスと関数:**
```python
class PlantCaptureManager:
    def capture_and_save(self):
        """カメラから画像をキャプチャして保存"""
        # 1. カメラを開く
        cap = cv2.VideoCapture(0)
        
        # 2. 解像度設定（1280x720）
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # 3. 画像取得
        ret, frame = cap.read()
        
        # 4. ファイル名生成（YYYYMMDD_HHMMSS.jpg）
        file_name = get_file_name()
        
        # 5. 画像保存
        save_image(frame, file_path)
        
        # 6. カメラ解放
        cap.release()
        
        # 7. 古い画像削除（90日以上前）
        delete_old_images()

def get_file_name():
    """ファイル名生成"""
    return datetime.now().strftime("%Y%m%d_%H%M%S.jpg")

def delete_old_images():
    """90日より古い画像を削除"""
    # plant_images/ 内のJPEGファイルを検索
    # 作成日時をチェックして削除
```

**保存先:** `plant_images/`

---

### 🔹 **11. src/api/watering_api.py**（給水API）

**役割:**
- 給水制御のAPIエンドポイント提供

**APIエンドポイント:**
```
POST /api/watering/       - 手動給水
GET  /api/watering/history - 給水履歴
POST /api/watering/stop   - 緊急停止
```

**主要なクラス:**
```python
class WateringResource(Resource):
    def post(self):
        """手動給水実行"""
        data = request.get_json(silent=True) or {}
        duration = data.get('duration', 5)  # デフォルト5秒
        
        # TODO: 実際の給水制御
        # watering_controller.manual_water(duration)
        
        return {
            'status': 'success',
            'message': f'給水が完了しました ({duration}秒)'
        }
```

**将来の連携先:**
- `src/watering/watering_controller.py` - 給水制御（未実装）

---

### 🔹 **12. src/api/settings_api.py**（設定API）

**役割:**
- システム設定の取得・保存
- JSON形式で永続化

**APIエンドポイント:**
```
GET/POST /api/settings/      - 設定取得・保存
POST     /api/settings/reset - デフォルトに戻す
```

**主要なクラスと関数:**
```python
class SettingsResource(Resource):
    def get(self):
        """設定取得"""
        settings = self._load_settings()  # config/settings.json から読み込み
        return {'status': 'success', 'data': settings}
    
    def post(self):
        """設定保存"""
        new_settings = request.get_json(silent=True)
        self._save_settings(new_settings)  # config/settings.json に保存
        return {'status': 'success', 'message': '設定を保存しました'}
    
    def _load_settings(self):
        """JSONファイルから設定読み込み"""
        # config/settings.json が存在すれば読み込み
        # なければデフォルト設定を返す
    
    def _save_settings(self, settings):
        """JSONファイルに設定保存"""
        # config/settings.json に書き込み
```

**保存先:** `config/settings.json`

---

### 🔹 **13. src/web/static/js/sensors.js**（フロントエンドセンサー管理）

**役割:**
- フロントエンドでのセンサーデータ管理
- APIとの通信
- データキャッシング・履歴管理

**主要なクラスと関数:**
```python
class SensorManager {
    async fetchSensorData() {
        """センサーデータをAPIから取得"""
        // GET /api/sensors/ を呼び出し
        const response = await fetch('/api/sensors/');
        const result = await response.json();
        
        // データを更新
        this.updateSensorData(result.data);
    }
    
    startAutoUpdate() {
        """自動更新開始"""
        // 30秒ごとにfetchSensorData()を実行
        setInterval(() => this.fetchSensorData(), 30000);
    }
    
    getStatistics(sensor, period) {
        """統計情報取得"""
        // 履歴データから平均・最小・最大を計算
        return {
            average: ...,
            min: ...,
            max: ...,
        };
    }
}

// グローバル関数
function getSensorManager() {
    """センサーマネージャー取得"""
    return new SensorManager();
}

function getSensorData() {
    """センサーデータ取得（APIコール）"""
    // fetchSensorData()のラッパー
}
```

**連携先:**
- バックエンド: `/api/sensors/` エンドポイント
- フロントエンド: `main.js`, `dashboard.js`

---

### 🔹 **14. src/web/static/js/dashboard.js**（ダッシュボードJS）

**役割:**
- ダッシュボードページ専用の機能
- グラフ表示（Chart.js使用）

**主要な関数:**
```javascript
function initializeChart() {
    """Chart.jsでグラフ初期化"""
    // 温度、湿度、土壌水分のラインチャート作成
}

function updateChart(data) {
    """グラフデータ更新"""
    // 最新20件のデータポイントを表示
    // 古いデータは削除
}
```

**連携先:**
- `sensors.js` - センサーデータ取得

---

### 🔹 **15. src/web/static/js/main.js**（メインJS）

**役割:**
- 全ページ共通の機能
- WebSocket通信（将来実装）
- UI更新関数

**主要な関数:**
```javascript
function refreshData() {
    """データ更新"""
    // センサーデータ取得
    // 給水履歴取得
    // UIに反映
}

function manualWatering() {
    """手動給水"""
    // POST /api/watering/ を呼び出し
}

function capturePhoto() {
    """写真撮影"""
    // POST /api/camera/capture を呼び出し
}

function emergencyStop() {
    """緊急停止"""
    // POST /api/watering/stop を呼び出し
}

function showAlert(message, type) {
    """アラート表示"""
    // Bootstrap alertを動的に表示
}
```

---

## 🔄 **データフロー例**

### **例1: センサーデータの表示**

```
1. ブラウザ（dashboard.html）
   ↓ ページ読み込み
   
2. sensors.js
   ├── getSensorManager().initialize()
   └── startAutoUpdate()  # 30秒ごと
   ↓ fetch('/api/sensors/')

3. Flask (main.py)
   ↓ ルーティング
   
4. src/api/sensors_api.py
   ├── SensorsResource.get()
   └── sensor_manager.get_latest_data()
   ↓

5. src/sensors/sensor_manager.py
   ├── data_cache から取得
   └── または read_all_sensors()
   ↓

6. 各センサークラス
   ├── AHT25Sensor.read_data()    # I2C通信
   ├── SEN0193Sensor.read_data()  # ADC読み取り
   └── FloatSwitch.read_data()    # GPIO読み取り
   ↓ データ返却

7. ブラウザに表示
   └── sensors.js が受信
       └── updateSensorDisplay() でUI更新
```

---

### **例2: 写真撮影**

```
1. ブラウザ（dashboard.html）
   ↓ ボタンクリック
   
2. main.js
   └── capturePhoto()
   ↓ POST /api/camera/capture

3. src/api/camera_api.py
   ├── CaptureResource.post()
   └── camera_manager.capture_and_save()
   ↓

4. src/camera/camera.py
   ├── PlantCaptureManager.capture_and_save()
   ├── cv2.VideoCapture(0)  # カメラ開く
   ├── frame取得
   ├── JPEGで保存
   └── 古い画像削除
   ↓

5. ブラウザに成功メッセージ
```

---

### **例3: 設定変更**

```
1. ブラウザ（settings.html）
   ↓ フォーム送信
   
2. settings.html (JavaScript)
   └── saveAllSettings()
   ↓ POST /api/settings/

3. src/api/settings_api.py
   ├── SettingsResource.post()
   ├── _load_settings()      # 現在の設定読み込み
   ├── 設定をマージ
   └── _save_settings()      # JSON保存
   ↓

4. config/settings.json
   └── 設定をファイルに保存
   ↓

5. ブラウザに成功メッセージ
```

---

## 📊 **モジュール間の依存関係**

```
main.py
  ├─ depends on: src/app/app.py
  ├─ depends on: src/api/api_blueprint.py
  └─ depends on: src/utils/logger.py

src/api/api_blueprint.py
  ├─ depends on: src/api/sensors_api.py
  ├─ depends on: src/api/watering_api.py
  ├─ depends on: src/api/camera_api.py
  ├─ depends on: src/api/notifications_api.py
  └─ depends on: src/api/settings_api.py

src/api/sensors_api.py
  └─ depends on: src/sensors/sensor_manager.py

src/sensors/sensor_manager.py
  ├─ depends on: src/sensors/temperature_humidity.py
  ├─ depends on: src/sensors/soil_moisture.py
  └─ depends on: src/sensors/float_switch.py

src/api/camera_api.py
  └─ depends on: src/camera/camera.py
```

---

## 🎯 **重要なポイント**

### **1. レイヤー分離:**
- **プレゼンテーション層:** app.py（画面）
- **API層:** src/api/（JSONレスポンス）
- **ビジネスロジック層:** src/sensors/, src/camera/など
- **データ層:** config/settings.json, CSVファイル

### **2. エラーハンドリング:**
- 全てのモジュールでRaspberry Pi以外の環境に対応
- ハードウェア未接続でもダミーデータで動作
- エラー時も適切なレスポンス返却

### **3. 拡張性:**
- 新しいセンサー追加: BaseSensorを継承
- 新しいAPI追加: Blueprintで登録
- 新しい画面追加: app.pyにルート追加

---

**作成日**: 2025年10月15日  
**バージョン**: 1.0  
**ブランチ**: integration/test-all-features

