# 開発ロードマップ - すくすくミントちゃん

## 📋 概要
新人エンジニア向けの段階的実装手順書。各機能を優先順位に従って実装していく詳細なガイド

## 🎯 実装戦略
1. **高優先度**: 基本機能（センサー、給水、データ保存）
2. **中優先度**: 拡張機能（カメラ、通知、Web UI）
3. **低優先度**: 高度機能（AI、高度スケジューリング）

---

## 🚀 Phase 1: 高優先度機能（基本機能）

### 1.1 センサー制御機能
**ファイル**: `src/sensors/INTEGRATED_GUIDE.md`

#### 実装順序
1. `src/sensors/base_sensor.py` - 基底クラス
2. `src/sensors/temperature_humidity.py` - 温湿度センサー
3. `src/sensors/soil_moisture.py` - 土壌水分センサー
4. `src/sensors/float_switch.py` - フロートスイッチ
5. `src/sensors/sensor_manager.py` - 統合管理

#### 実装手順
```bash
# プロジェクトルートから実行
cd smart-planter

# 1. ファイル作成
touch src/sensors/base_sensor.py
touch src/sensors/temperature_humidity.py
touch src/sensors/soil_moisture.py
touch src/sensors/float_switch.py
touch src/sensors/sensor_manager.py

# 2. 依存関係インストール
source venv/bin/activate
pip install RPi.GPIO smbus2 spidev numpy

# 3. 実装（各ファイルにコードを記述）
# 4. テスト実行
python -m pytest tests/test_sensors.py
```

### 1.2 給水制御機能
**ファイル**: `src/watering/INTEGRATED_GUIDE.md`

#### 実装順序
1. `src/watering/pump_control.py` - ポンプ制御
2. `src/watering/watering_logic.py` - 給水判定ロジック
3. `src/watering/watering_scheduler.py` - スケジューラー

#### 実装手順
```bash
# 1. ファイル作成
touch src/watering/pump_control.py
touch src/watering/watering_logic.py
touch src/watering/watering_scheduler.py

# 2. 実装（各ファイルにコードを記述）
# 3. テスト実行
python -m pytest tests/test_watering.py
```

### 1.3 データ保存機能
**ファイル**: `src/data/INTEGRATED_GUIDE.md`

#### 実装順序
1. `src/data/csv_handler.py` - CSVファイル操作
2. `src/data/data_manager.py` - データ統合管理

#### 実装手順
```bash
# 1. ファイル作成
touch src/data/csv_handler.py
touch src/data/data_manager.py

# 2. 依存関係インストール
pip install pandas Pillow

# 3. 実装（各ファイルにコードを記述）
```

---

## 🔧 Phase 2: 中優先度機能（拡張機能）

### 2.1 API機能
**ファイル**: `src/api/INTEGRATED_GUIDE.md`

#### 実装順序
1. `src/api/sensors_api.py` - センサーAPI
2. `src/api/watering_api.py` - 給水API
3. `src/api/api_blueprint.py` - API統合

#### 実装手順
```bash
# 1. ファイル作成
touch src/api/sensors_api.py
touch src/api/watering_api.py
touch src/api/api_blueprint.py

# 2. 依存関係インストール
pip install Flask-RESTful Flask-CORS marshmallow

# 3. 実装（各ファイルにコードを記述）
# 4. Flaskアプリに統合
```

### 2.2 Web UI機能
**ファイル**: `src/web/INTEGRATED_GUIDE.md`

#### 実装順序
1. `src/web/templates/base.html` - ベーステンプレート
2. `src/web/templates/dashboard.html` - ダッシュボード
3. `src/web/static/css/main.css` - スタイル
4. `src/web/static/js/main.js` - JavaScript

#### 実装手順
```bash
# 1. ファイル作成
touch src/web/templates/base.html
touch src/web/templates/dashboard.html
touch src/web/static/css/main.css
touch src/web/static/js/main.js

# 2. 依存関係インストール
pip install Flask-SocketIO python-socketio

# 3. 実装（各ファイルにコードを記述）
```

### 2.3 カメラ機能
**ファイル**: `src/camera/INTEGRATED_GUIDE.md`

#### 実装順序
1. `src/camera/camera_control.py` - カメラ制御
2. `src/camera/image_processing.py` - 画像処理
3. `src/camera/timelapse.py` - タイムラプス

### 2.4 LINE通知機能
**ファイル**: `src/notifications/INTEGRATED_GUIDE.md`

#### 実装順序
1. `src/notifications/line_notify.py` - LINE通知
2. `src/notifications/alert_manager.py` - アラート管理
3. `src/notifications/notification_scheduler.py` - スケジューラー

---

## 🧪 Phase 3: テスト・統合

### 3.1 単体テスト
```bash
# テストファイル作成
touch tests/test_sensors.py
touch tests/test_watering.py
touch tests/test_integration.py

# テスト実行
python -m pytest tests/
```

### 3.2 統合テスト
```bash
# 全体システムテスト
python main.py
# ブラウザで http://localhost:5000 にアクセス
# 各機能の動作確認
```

---

## 📅 実装スケジュール

### Week 1-2: 基本機能
- [ ] センサー制御機能
- [ ] 給水制御機能
- [ ] データ保存機能

### Week 3-4: 拡張機能
- [ ] API機能
- [ ] Web UI機能
- [ ] カメラ機能
- [ ] LINE通知機能

### Week 5-6: テスト・統合
- [ ] 単体テスト
- [ ] 統合テスト
- [ ] バグ修正
- [ ] ドキュメント整備

---

## 🔍 各機能の詳細実装手順

### センサー制御機能
1. **ハードウェア接続確認**
   - AHT25温湿度センサー（I2C）
   - SEN0193土壌水分センサー（ADC）
   - フロートスイッチ（GPIO）

2. **ソフトウェア実装**
   - 基底クラス設計
   - 各センサー制御クラス
   - エラーハンドリング
   - データフィルタリング

3. **テスト**
   - 個別センサーテスト
   - 統合テスト
   - エラーケーステスト

### 給水制御機能
1. **ハードウェア接続確認**
   - リレーモジュール接続
   - 水中ポンプ接続
   - 安全回路確認

2. **ソフトウェア実装**
   - ポンプ制御クラス
   - 給水判定ロジック
   - スケジューラー

3. **テスト**
   - 手動給水テスト
   - 自動給水テスト
   - 安全機能テスト

---

## 🛠️ 開発環境セットアップ

### 1. 仮想環境アクティベート
```bash
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter
source venv/bin/activate
```

### 2. 依存関係インストール
```bash
pip install -r requirements.txt
```

### 3. 開発サーバー起動
```bash
python main.py
```

### 4. アクセス確認
```
http://localhost:5000
```

---

## 📚 参考資料

### 実装ガイド
- `src/sensors/INTEGRATED_GUIDE.md` - センサー制御
- `src/watering/INTEGRATED_GUIDE.md` - 給水制御
- `src/data/INTEGRATED_GUIDE.md` - データ管理
- `src/api/INTEGRATED_GUIDE.md` - API機能
- `src/web/INTEGRATED_GUIDE.md` - Web UI
- `src/camera/INTEGRATED_GUIDE.md` - カメラ機能
- `src/notifications/INTEGRATED_GUIDE.md` - 通知機能

### プロジェクト資料
- `README.md` - プロジェクト概要
- `SETUP_GUIDE.md` - 環境構築手順
- `開発環境構築手順書.md` - 詳細セットアップ

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS
