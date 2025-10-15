# すくすくミントちゃん - 関数リファレンス

## 📋 主要な関数・メソッド一覧

このドキュメントでは、各モジュールの主要な関数について詳しく説明します。

---

## 🔹 **main.py**

### `main()`
**説明:** アプリケーションのメインエントリーポイント  
**引数:** なし  
**戻り値:** なし  
**処理フロー:**
```python
1. setup_logging()でログシステム初期化
2. create_app()でFlaskアプリ作成
3. register_api_blueprints(app)でAPI登録
4. app.run()でサーバー起動
```

---

## 🔹 **src/app/app.py**

### `create_app()`
**説明:** Flaskアプリケーションを作成して返す  
**引数:** なし  
**戻り値:** `Flask` - Flaskアプリインスタンス  
**処理:**
```python
- テンプレートとスタティックディレクトリを指定
- SECRET_KEYを環境変数から取得
- ルート定義（/, /dashboard, /settings, /logs）
- エラーハンドラー定義（404, 500）
```

---

## 🔹 **src/api/api_blueprint.py**

### `register_api_blueprints(app: Flask)`
**説明:** 全てのAPIブループリントをFlaskアプリに登録  
**引数:**
- `app` (Flask): Flaskアプリインスタンス
**戻り値:** なし  
**登録するAPI:**
```python
- sensors_bp      → /api/sensors/*
- watering_bp     → /api/watering/*
- camera_bp       → /api/camera/*
- notifications_bp → /api/notifications/*
- settings_bp     → /api/settings/*
```

---

## 🔹 **src/api/sensors_api.py**

### `SensorsResource.get()`
**説明:** 全センサーの現在のデータを取得  
**HTTPメソッド:** GET  
**エンドポイント:** `/api/sensors/`  
**引数:** なし  
**戻り値:**
```json
{
  "status": "success",
  "data": {
    "temperature": 25.5,
    "humidity": 60.0,
    "soil_moisture": 180,
    "soil_moisture_percentage": 45.0,
    "water_volume": 1500,
    "water_percentage": 75,
    "water_level": "normal",
    "pressure": null,
    "timestamp": "2025-10-15T09:30:00"
  }
}
```

### `SensorHistoryResource.get()`
**説明:** センサーデータ履歴を取得  
**HTTPメソッド:** GET  
**エンドポイント:** `/api/sensors/history`  
**クエリパラメータ:**
- `limit` (int, optional): 取得件数（デフォルト: 100）
- `sensor_type` (str, optional): センサータイプ（temperature, humidity, soil_moisture）
**戻り値:**
```json
{
  "status": "success",
  "data": {
    "history": [...],
    "count": 100
  }
}
```

---

## 🔹 **src/sensors/sensor_manager.py**

### `SensorManager.__init__()`
**説明:** センサーマネージャーの初期化  
**処理:**
```python
1. ロガー取得
2. センサー辞書初期化
3. データキャッシュ辞書初期化
4. _initialize_sensors()で各センサー作成
```

### `SensorManager.start_monitoring()`
**説明:** バックグラウンドでセンサー監視を開始  
**引数:** なし  
**戻り値:** なし  
**処理:**
```python
1. running フラグをTrueに設定
2. 監視スレッドを作成・起動
3. _monitoring_loop()を実行
```

### `SensorManager._monitoring_loop()`
**説明:** 監視ループ（バックグラウンドスレッド）  
**処理:**
```python
while running:
    1. read_all_sensors()で全データ取得
    2. 60秒待機
    3. 繰り返し
```

### `SensorManager.read_all_sensors()`
**説明:** 全センサーのデータを一括読み取り  
**引数:** なし  
**戻り値:** `Dict[str, Any]` - 各センサーのデータ辞書  
**処理:**
```python
for sensor_name, sensor in sensors.items():
    if sensor.is_enabled:
        data = sensor.read_data()  # センサーから読み取り
        results[sensor_name] = data
        data_cache[sensor_name] = {'data': data, 'timestamp': time.time()}
```

### `SensorManager.get_latest_data()`
**説明:** 最新のセンサーデータを統合形式で取得  
**引数:** なし  
**戻り値:** `Dict[str, Any]` - 統合されたセンサーデータ  
**形式:**
```python
{
    'temperature': 25.5,
    'humidity': 60.0,
    'soil_moisture': 180,
    'soil_moisture_percentage': 45.0,
    'water_present': True,
    'water_level': 'normal',
    'timestamp': 1234567890.0
}
```

### `SensorManager.force_read(sensor_name: str)`
**説明:** 指定センサーの強制読み取り（キャッシュ無視）  
**引数:**
- `sensor_name` (str): センサー名
**戻り値:** `Dict[str, Any]` - センサーデータ

---

## 🔹 **src/sensors/temperature_humidity.py**

### `AHT25Sensor.__init__()`
**説明:** AHT25センサーの初期化  
**処理:**
```python
1. BaseSensor.__init__("AHT25", 0)呼び出し
2. I2Cアドレス0x38設定
3. smbus2.SMBus(1)でI2Cバス作成（Raspberry Piの場合）
4. initialized フラグをFalseに設定
```

### `AHT25Sensor.initialize()`
**説明:** センサーハードウェアの初期化  
**引数:** なし  
**戻り値:** `bool` - 成功/失敗  
**処理:**
```python
1. リセットコマンド送信（0xBA）
2. 100ms待機
3. 初期化コマンド送信（0xBE, 0x08, 0x00）
4. 100ms待機
5. initialized = True
```

### `AHT25Sensor.read_data()`
**説明:** 温湿度データを読み取る  
**引数:** なし  
**戻り値:** `Dict[str, Any]`
```python
# 成功時
{
    'temperature': 25.5,  # 摂氏
    'humidity': 60.0,     # %
    'timestamp': 1234567890.0,
    'mode': 'real' または 'dummy'
}

# エラー時
{
    'error': 'エラーメッセージ'
}
```
**処理:**
```python
1. 測定開始コマンド送信（0xAC, 0x33, 0x00）
2. 100ms待機
3. 6バイトのデータ読み取り
4. ビット演算で湿度・温度を抽出
5. 値の範囲チェック（湿度: 0-100%, 温度: -40～85℃）
6. 結果を返す
```

---

## 🔹 **src/sensors/soil_moisture.py**

### `SEN0193Sensor.__init__(channel=0, vref=3.3)`
**説明:** 土壌水分センサーの初期化  
**引数:**
- `channel` (int): ADCチャンネル番号（デフォルト: 0）
- `vref` (float): 基準電圧（デフォルト: 3.3V）

### `SEN0193Sensor.read_data()`
**説明:** 土壌水分データを読み取る  
**引数:** なし  
**戻り値:** `Dict[str, Any]`
```python
{
    'raw_value': 180,               # 0-255
    'voltage': 2.1,                 # V
    'moisture_percentage': 45.0,    # %
    'status': 'Optimal',            # Dry/Optimal/VeryWet
    'timestamp': 1234567890.0,
    'mode': 'real' または 'dummy'
}
```
**処理:**
```python
1. MCP3002.valueで値取得（0.0-1.0）
2. 255倍して生の値に変換（0-255）
3. vref倍して電圧に変換
4. _get_moisture_status()で状態判定
5. パーセンテージ計算: (255 - raw_value) / 255 * 100
6. 結果を返す
```

### `SEN0193Sensor._get_moisture_status(raw_value: int)`
**説明:** 生の水分値から状態文字列を返す  
**引数:**
- `raw_value` (int): 生の値（0-255）
**戻り値:** `str` - "Dry"/"Optimal"/"VeryWet"  
**判定基準:**
```python
if raw_value > 200:
    return "Dry"        # 乾燥
elif raw_value > 150:
    return "Optimal"    # 最適
else:
    return "VeryWet"    # 過湿
```

---

## 🔹 **src/sensors/float_switch.py**

### `FloatSwitch.__init__(pin=18)`
**説明:** フロートスイッチの初期化  
**引数:**
- `pin` (int): GPIOピン番号（デフォルト: 18）

### `FloatSwitch.initialize()`
**説明:** GPIOの初期化  
**処理:**
```python
1. GPIO.setmode(GPIO.BCM)
2. GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
```

### `FloatSwitch.read_data()`
**説明:** 水位データを読み取る  
**戻り値:** `Dict[str, Any]`
```python
{
    'water_present': True/False,
    'level': 'normal'/'low',
    'raw_value': 0 or 1,  # GPIO state
    'timestamp': 1234567890.0,
    'mode': 'real' または 'dummy'
}
```
**処理:**
```python
1. GPIO.input(pin)でGPIO状態取得
2. LOW = 水あり、HIGH = 水なし
3. 水位レベル判定
```

### `FloatSwitch.cleanup()`
**説明:** GPIOクリーンアップ  
**処理:**
```python
GPIO.cleanup(pin)  # 使用したピンを解放
```

---

## 🔹 **src/sensors/base_sensor.py**

### `BaseSensor.__init__(name: str, pin: int)`
**説明:** 基底クラスの初期化  
**引数:**
- `name` (str): センサー名
- `pin` (int): GPIOピン番号

### `BaseSensor.is_healthy()`
**説明:** センサーの健全性をチェック  
**戻り値:** `bool`  
**判定:**
```python
return error_count < max_errors and is_enabled
```

### `BaseSensor.increment_error_count()`
**説明:** エラーカウントを増加  
**処理:**
```python
1. error_count += 1
2. if error_count >= max_errors:
    - is_enabled = False  # センサー無効化
    - エラーログ出力
```

### `BaseSensor.reset_error_count()`
**説明:** エラーカウントをリセット  
**処理:**
```python
error_count = 0
```

### `BaseSensor.get_status()`
**説明:** センサー状態を取得  
**戻り値:** `Dict[str, Any]`
```python
{
    'name': 'センサー名',
    'enabled': True/False,
    'healthy': True/False,
    'error_count': 0,
    'pin': 18
}
```

---

## 🔹 **src/camera/camera.py**

### `PlantCaptureManager.__init__()`
**説明:** カメラマネージャーの初期化  
**処理:**
```python
1. camera_index = 0（デフォルトカメラ）
2. 画像保存ディレクトリ設定
3. ディレクトリ存在確認・作成
```

### `PlantCaptureManager.capture_and_save()`
**説明:** カメラから画像をキャプチャして保存  
**引数:** なし  
**戻り値:** なし（例外をraise）  
**処理:**
```python
1. cv2.VideoCapture(0)でカメラ開く
2. 解像度設定（1280x720）
3. フレーム取得
4. ファイル名生成（YYYYMMDD_HHMMSS.jpg）
5. JPEG形式で保存（品質95%）
6. カメラ解放
7. delete_old_images()で古い画像削除
```

### `get_file_name()`
**説明:** タイムスタンプ付きファイル名を生成  
**引数:** なし  
**戻り値:** `str` - "20251015_093000.jpg" 形式  
**処理:**
```python
return datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
```

### `save_image(image, file_path)`
**説明:** 画像をJPEGで保存  
**引数:**
- `image` (numpy.ndarray): OpenCV画像
- `file_path` (str): 保存先パス
**戻り値:** なし  
**処理:**
```python
cv2.imwrite(file_path, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
```

### `delete_old_images(directory, days=90)`
**説明:** 指定日数より古い画像を削除  
**引数:**
- `directory` (str): ディレクトリパス
- `days` (int): 削除する日数（デフォルト: 90）
**戻り値:** なし  
**処理:**
```python
1. ディレクトリ内の*.jpgファイルを取得
2. 各ファイルの作成日時をチェック
3. 作成日時 > days日 の場合、削除
```

---

## 🔹 **src/api/camera_api.py**

### `CaptureResource.post()`
**説明:** 写真撮影API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/camera/capture`  
**リクエストボディ:**
```json
{
  "save": true  // オプション
}
```
**レスポンス（成功時）:**
```json
{
  "status": "success",
  "message": "写真を撮影しました",
  "camera_error": null,
  "timestamp": "2025-10-15T09:30:00"
}
```
**レスポンス（カメラ未接続時）:**
```json
{
  "status": "warning",
  "message": "カメラが接続されていません（開発環境）",
  "camera_error": "エラーメッセージ",
  "timestamp": "2025-10-15T09:30:00"
}
```

### `CameraImagesResource.get()`
**説明:** 画像リスト取得API  
**HTTPメソッド:** GET  
**エンドポイント:** `/api/camera/images`  
**レスポンス:**
```json
{
  "status": "success",
  "images": [
    {
      "filename": "20251015_093000.jpg",
      "path": "/path/to/image",
      "timestamp": "2025-10-15T09:30:00"
    }
  ],
  "count": 10
}
```

---

## 🔹 **src/api/watering_api.py**

### `WateringResource.post()`
**説明:** 手動給水実行API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/watering/`  
**リクエストボディ:**
```json
{
  "duration": 5  // 秒数（オプション、デフォルト: 5）
}
```
**レスポンス:**
```json
{
  "status": "success",
  "message": "給水が完了しました (5秒)",
  "duration": 5,
  "timestamp": "2025-10-15T09:30:00"
}
```

### `WateringStopResource.post()`
**説明:** 給水緊急停止API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/watering/stop`  
**レスポンス:**
```json
{
  "status": "success",
  "message": "給水を緊急停止しました"
}
```

---

## 🔹 **src/api/settings_api.py**

### `SettingsResource.get()`
**説明:** 設定取得API  
**HTTPメソッド:** GET  
**エンドポイント:** `/api/settings/`  
**レスポンス:**
```json
{
  "status": "success",
  "data": {
    "sensor_interval": 60,
    "watering_duration": 5,
    "soil_threshold_low": 150,
    "soil_threshold_high": 200,
    "camera_enabled": true,
    "line_notifications": true,
    ...
  }
}
```

### `SettingsResource.post()`
**説明:** 設定保存API  
**HTTPメソッド:** POST  
**エンドポイント:** `/api/settings/`  
**リクエストボディ:** 設定オブジェクト（JSON）  
**レスポンス:**
```json
{
  "status": "success",
  "message": "設定を保存しました"
}
```

### `SettingsResource._load_settings()`
**説明:** JSONファイルから設定読み込み  
**戻り値:** `Dict[str, Any]` - 設定辞書  
**処理:**
```python
1. config/settings.json が存在するかチェック
2. 存在する場合: JSONを読み込んで返す
3. 存在しない場合: _get_default_settings()を返す
```

### `SettingsResource._save_settings(settings: Dict)`
**説明:** JSONファイルに設定保存  
**引数:**
- `settings` (Dict): 設定辞書
**処理:**
```python
1. config/ディレクトリ作成（存在しない場合）
2. settings を JSON形式で config/settings.json に書き込み
3. インデント付き（indent=2）
```

---

## 🔹 **src/web/static/js/sensors.js**

### `SensorManager.initialize()`
**説明:** センサーマネージャーの初期化（フロントエンド）  
**引数:** なし  
**戻り値:** なし  
**処理:**
```javascript
1. データキャッシュ初期化
2. 履歴配列初期化
3. fetchSensorData()で初回データ取得
```

### `SensorManager.fetchSensorData()`
**説明:** APIからセンサーデータ取得  
**引数:** なし  
**戻り値:** `Promise<Object>`  
**処理:**
```javascript
1. fetch('/api/sensors/')でGETリクエスト
2. JSONレスポンス解析
3. updateSensorData()でキャッシュ更新
4. データを返す
```

### `SensorManager.startAutoUpdate(interval=30000)`
**説明:** 自動更新を開始  
**引数:**
- `interval` (number): 更新間隔（ミリ秒、デフォルト: 30秒）
**処理:**
```javascript
setInterval(() => {
    this.fetchSensorData();
}, interval);
```

### `SensorManager.getStatistics(sensor, period)`
**説明:** 統計情報を取得  
**引数:**
- `sensor` (string): センサー名
- `period` (string): 期間（'hour', 'day', 'week'）
**戻り値:** `Object`
```javascript
{
    average: 25.5,
    min: 20.0,
    max: 30.0,
    count: 120
}
```

---

## 🔹 **src/web/static/js/main.js**

### `refreshData()`
**説明:** 全データを更新  
**処理:**
```javascript
1. センサーデータ取得
2. 給水履歴取得
3. UI更新
```

### `manualWatering(duration=5)`
**説明:** 手動給水実行  
**引数:**
- `duration` (number): 給水時間（秒）
**処理:**
```javascript
1. POST /api/watering/ を呼び出し
2. 結果表示
```

### `capturePhoto()`
**説明:** 写真撮影実行  
**処理:**
```javascript
1. POST /api/camera/capture を呼び出し
2. 結果表示
```

### `emergencyStop()`
**説明:** 緊急停止実行  
**処理:**
```javascript
1. 確認ダイアログ表示
2. POST /api/watering/stop を呼び出し
```

### `showAlert(message, type='info')`
**説明:** アラート表示  
**引数:**
- `message` (string): メッセージ
- `type` (string): タイプ（'success', 'warning', 'danger', 'info'）
**処理:**
```javascript
1. Bootstrap alertをHTML生成
2. ページに挿入
3. 5秒後に自動削除
```

---

**作成日**: 2025年10月15日  
**バージョン**: 1.0  
**ブランチ**: integration/test-all-features

