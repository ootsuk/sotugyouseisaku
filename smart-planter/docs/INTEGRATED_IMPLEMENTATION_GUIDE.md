# 統合実装ガイド - すくすくミントちゃん

## 📋 概要
スマートプランターシステムの全機能を統合した実装ガイド。新人エンジニア向けの詳細な手順書

## 🎯 実装目標
- 温湿度センサー（AHT25）制御
- 土壌水分センサー（SEN0193）制御
- 圧力センサー（MS583730BA01-50）による水の残量測定
- 自動給水制御システム
- データ管理・保存機能
- REST API機能
- Web UIダッシュボード
- LINE通知機能

## 🛠️ 必要な環境

### ハードウェア
- Raspberry Pi 5 (4GB以上推奨)
- 温湿度センサー AHT25
- 土壌水分センサー SEN0193
- 圧力センサー MS583730BA01-50
- リレーモジュール AE-G5V-DRV
- 水中ポンプ（12V DC）
- ADC MCP3002
- 水タンク
- ジャンパーワイヤー
- ブレッドボード

### ソフトウェア
- Raspberry Pi OS (64-bit) - Bookworm
- Python 3.11.x
- Flask 2.3.3
- RPi.GPIO
- smbus2 (I2C通信用)
- spidev (SPI通信用)
- numpy (データ処理用)

## 📁 ファイル作成手順

### Step 1: プロジェクト構造の確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# プロジェクト構造の確認
tree -I 'venv|__pycache__|*.pyc' .
```

### Step 2: 各機能ディレクトリの作成
```bash
# センサー機能
mkdir -p src/sensors
touch src/sensors/__init__.py
touch src/sensors/base_sensor.py
touch src/sensors/temperature_humidity.py
touch src/sensors/soil_moisture.py
touch src/sensors/pressure_sensor.py
touch src/sensors/float_switch.py
touch src/sensors/sensor_manager.py

# 給水機能
mkdir -p src/watering
touch src/watering/__init__.py
touch src/watering/pump_control.py
touch src/watering/watering_logic.py
touch src/watering/watering_scheduler.py

# データ管理機能
mkdir -p src/data
touch src/data/__init__.py
touch src/data/csv_handler.py
touch src/data/data_manager.py
touch src/data/database.py

# API機能
mkdir -p src/api
touch src/api/__init__.py
touch src/api/sensors_api.py
touch src/api/watering_api.py
touch src/api/camera_api.py
touch src/api/notifications_api.py
touch src/api/api_blueprint.py

# Web UI機能
mkdir -p src/web/templates
mkdir -p src/web/static/css
mkdir -p src/web/static/js
mkdir -p src/web/static/images
touch src/web/templates/base.html
touch src/web/templates/dashboard.html
touch src/web/templates/settings.html
touch src/web/static/css/main.css
touch src/web/static/js/main.js
touch src/web/static/js/dashboard.js

# テスト機能
mkdir -p tests
touch tests/__init__.py
touch tests/test_sensors.py
touch tests/test_watering.py
touch tests/test_integration.py
```

### Step 3: 依存関係のインストール
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# 必要なライブラリをインストール
pip install Flask==2.3.3
pip install Flask-RESTful
pip install Flask-CORS
pip install Flask-SocketIO
pip install RPi.GPIO
pip install smbus2
pip install spidev
pip install numpy
pip install pandas
pip install Pillow
pip install marshmallow
pip install python-socketio

# requirements.txtを更新
pip freeze > requirements.txt
```

## 📄 実装順序

### Phase 1: 基本機能（高優先度）

#### 1.1 センサー制御機能
**実装ファイル**: `src/sensors/`
**手順書**: `docs/SENSOR_CONTROL_GUIDE.md`

```bash
# 1. 基底クラス実装
vim src/sensors/base_sensor.py

# 2. 温湿度センサー実装
vim src/sensors/temperature_humidity.py

# 3. 土壌水分センサー実装
vim src/sensors/soil_moisture.py

# 4. 圧力センサー実装（水の残量測定）
vim src/sensors/pressure_sensor.py

# 5. センサー統合管理実装
vim src/sensors/sensor_manager.py

# 6. テスト実行
python -m pytest tests/test_sensors.py
```

#### 1.2 給水制御機能
**実装ファイル**: `src/watering/`
**手順書**: `docs/WATERING_CONTROL_GUIDE.md`

```bash
# 1. ポンプ制御実装
vim src/watering/pump_control.py

# 2. 給水判定ロジック実装
vim src/watering/watering_logic.py

# 3. 給水スケジューラー実装
vim src/watering/watering_scheduler.py

# 4. テスト実行
python -m pytest tests/test_watering.py
```

#### 1.3 データ管理機能
**実装ファイル**: `src/data/`
**手順書**: `docs/DATA_MANAGEMENT_GUIDE.md`

```bash
# 1. CSVハンドラー実装
vim src/data/csv_handler.py

# 2. データマネージャー実装
vim src/data/data_manager.py

# 3. テスト実行
python -c "from src.data.data_manager import DataManager; print('DataManager test passed')"
```

### Phase 2: 拡張機能（中優先度）

#### 2.1 API機能
**実装ファイル**: `src/api/`
**手順書**: `docs/API_IMPLEMENTATION_GUIDE.md`

```bash
# 1. センサーAPI実装
vim src/api/sensors_api.py

# 2. 給水API実装
vim src/api/watering_api.py

# 3. カメラAPI実装
vim src/api/camera_api.py

# 4. 通知API実装
vim src/api/notifications_api.py

# 5. API統合実装
vim src/api/api_blueprint.py

# 6. Flaskアプリに統合
vim src/app/app.py
```

#### 2.2 Web UI機能
**実装ファイル**: `src/web/`
**手順書**: `docs/WEB_UI_GUIDE.md`

```bash
# 1. ベーステンプレート実装
vim src/web/templates/base.html

# 2. ダッシュボード実装
vim src/web/templates/dashboard.html

# 3. 設定ページ実装
vim src/web/templates/settings.html

# 4. CSS実装
vim src/web/static/css/main.css

# 5. JavaScript実装
vim src/web/static/js/main.js
vim src/web/static/js/dashboard.js
```

### Phase 3: 統合・テスト

#### 3.1 統合テスト
```bash
# 1. 統合テスト実装
vim tests/test_integration.py

# 2. 統合テスト実行
python -m pytest tests/test_integration.py

# 3. 全体システムテスト
python main.py
```

#### 3.2 動作確認
```bash
# 1. アプリケーション起動
python main.py

# 2. ブラウザでアクセス
# http://localhost:5000

# 3. APIテスト
curl -X GET http://localhost:5000/api/sensors/
curl -X POST http://localhost:5000/api/watering/ -H "Content-Type: application/json" -d '{"duration": 5}'
```

## 🔧 各機能の詳細実装

### センサー制御機能
- **AHT25温湿度センサー**: I2C通信で温度・湿度を取得
- **SEN0193土壌水分センサー**: ADC経由で土壌水分を測定
- **MS583730BA01-50圧力センサー**: I2C通信で水の残量を測定
- **フロートスイッチ**: GPIO経由で水タンクの水位を監視

### 給水制御機能
- **土壌水分値159以下**: 自動給水判定
- **前回給水から12時間経過**: 給水間隔制御
- **リレーモジュール制御**: 水ポンプのON/OFF制御
- **安全機能**: 連続給水防止、水タンク空検知

### データ管理機能
- **CSV形式**: センサーデータの保存
- **JSON形式**: 給水履歴の保存
- **JPEG形式**: 画像データの保存
- **90日間**: 自動削除機能

### API機能
- **REST API**: センサー、給水、カメラ、通知の各機能
- **JSON形式**: リクエスト・レスポンス
- **エラーハンドリング**: 適切なエラーレスポンス

### Web UI機能
- **ダッシュボード**: リアルタイムセンサーデータ表示
- **操作パネル**: 手動給水、写真撮影
- **グラフ表示**: センサーデータの時系列グラフ
- **レスポンシブデザイン**: モバイル対応

## 🧪 テスト方法

### 1. 単体テスト
```bash
# センサーテスト
python -m pytest tests/test_sensors.py -v

# 給水テスト
python -m pytest tests/test_watering.py -v

# データ管理テスト
python -c "from src.data.data_manager import DataManager; manager = DataManager(); print('DataManager test passed')"
```

### 2. 統合テスト
```bash
# 統合テスト実行
python -m pytest tests/test_integration.py -v

# 全体システムテスト
python main.py &
curl -X GET http://localhost:5000/api/sensors/
```

### 3. 動作確認
```bash
# アプリケーション起動
python main.py

# ブラウザでアクセス
# http://localhost:5000

# 各機能の動作確認
# - センサーデータの表示
# - 手動給水の実行
# - 写真撮影の実行
# - データ更新の確認
```

## 📚 参考資料

### 実装ガイド
- `docs/SENSOR_CONTROL_GUIDE.md` - センサー制御
- `docs/WATERING_CONTROL_GUIDE.md` - 給水制御
- `docs/DATA_MANAGEMENT_GUIDE.md` - データ管理
- `docs/API_IMPLEMENTATION_GUIDE.md` - API機能
- `docs/WEB_UI_GUIDE.md` - Web UI

### プロジェクト資料
- `README.md` - プロジェクト概要
- `SETUP_GUIDE.md` - 環境構築手順
- `開発環境構築手順書.md` - 詳細セットアップ

## 🚀 デプロイ手順

### 1. 開発環境でのテスト
```bash
# 仮想環境でテスト
source venv/bin/activate
python main.py
```

### 2. 本番環境へのデプロイ
```bash
# ラズパイ上で実行
cd /home/pi/smart-planter
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 3. 自動起動設定
```bash
# systemdサービス作成
sudo cp scripts/smart-planter.service /etc/systemd/system/
sudo systemctl enable smart-planter.service
sudo systemctl start smart-planter.service
```

## ⚠️ 注意事項

### 1. ハードウェア接続
- GPIOピンの接続を正確に行う
- 電源電圧を確認する（3.3V、5V）
- アース（GND）の接続を忘れない

### 2. ソフトウェア設定
- I2C・SPIを有効化する
- 仮想環境を正しく設定する
- 環境変数を適切に設定する

### 3. セキュリティ
- ローカルネットワーク内でのみアクセス
- ファイアウォールの設定
- 定期的なバックアップ

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

