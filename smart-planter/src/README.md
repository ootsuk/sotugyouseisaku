# src/ フォルダー説明書

## 📁 概要
ソースコードのメインディレクトリ。プロジェクトの核となる機能を実装するコードを格納。

## 📂 サブディレクトリ

### 📁 app/
**Flaskアプリケーション**
- `app.py`: Flaskアプリケーションのメインコード
- `routes.py`: ルート定義
- `__init__.py`: パッケージ初期化

### 📁 sensors/
**センサー制御システム**
- `base_sensor.py`: センサーの基底クラス
- `aht25_sensor.py`: AHT25温湿度センサー制御
- `sen0193_sensor.py`: SEN0193土壌水分センサー制御
- `float_switch.py`: フロートスイッチ制御
- `sensor_manager.py`: センサー管理システム

### 📁 watering/
**給水制御システム**
- `watering_controller.py`: 給水制御クラス
- `auto_watering_manager.py`: 自動給水管理システム

### 📁 camera/
**カメラ制御システム**
- `camera_controller.py`: カメラ制御クラス
- `image_processor.py`: 画像処理機能

### 📁 notifications/
**通知機能システム**
- `line_notify.py`: LINE通知クラス
- `notification_manager.py`: 通知管理システム

### 📁 data/
**データ管理システム**
- `data_manager.py`: データ管理クラス
- `data_manager_service.py`: データ管理サービス

### 📁 api/
**REST API**
- `sensor_api.py`: センサー関連API
- `watering_api.py`: 給水関連API
- `camera_api.py`: カメラ関連API
- `data_api.py`: データ関連API
- `notification_api.py`: 通知関連API

### 📁 utils/
**ユーティリティ**
- `helpers.py`: 共通ヘルパー関数
- `config_manager.py`: 設定管理
- `logger.py`: ログ設定

### 📁 web/
**Webフロントエンド**
- `templates/`: HTMLテンプレート
- `static/`: 静的ファイル（CSS, JS, 画像）

## 🔧 開発ガイドライン

### コーディング規約
- PEP 8 に準拠
- 型ヒントを使用
- ドキュメント文字列を記述

### インポート順序
1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルアプリケーション

### エラーハンドリング
- 適切な例外処理
- ログ出力
- ユーザーフレンドリーなエラーメッセージ

## 📝 ファイル命名規則
- **Pythonファイル**: snake_case
- **クラス名**: PascalCase
- **関数名**: snake_case
- **定数**: UPPER_CASE

## 🧪 テスト
各モジュールに対応するテストファイルを `tests/` ディレクトリに配置

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

