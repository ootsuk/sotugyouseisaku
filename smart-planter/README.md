# すくすくミントちゃん

## 🌱 プロジェクト概要
園芸初心者・高齢者向けの自動植物育成システム

## 🎯 主な機能
- 温湿度・土壌水分の自動監視
- 土壌水分に基づく自動給水
- 植物の成長記録とタイムラプス
- LINE通知による状況報告
- Web UI による遠隔操作

## 🛠️ 技術スタック
- **ハードウェア**: Raspberry Pi 5
- **センサー**: AHT25 (温湿度), SEN0193 (土壌水分)
- **バックエンド**: Python 3.11, Flask 2.3.3
- **フロントエンド**: HTML5, CSS3, JavaScript
- **通知**: LINE Notify API

## 📁 プロジェクト構成
```
smart-planter/
├── src/                    # ソースコード
│   ├── app/               # Flaskアプリケーション
│   ├── sensors/           # センサー制御
│   ├── watering/          # 給水制御
│   ├── camera/            # カメラ制御
│   ├── notifications/     # 通知機能
│   ├── data/              # データ管理
│   ├── api/               # REST API
│   ├── utils/             # ユーティリティ
│   └── web/               # Webフロントエンド
├── tests/                 # テストコード
├── docs/                  # ドキュメント
├── scripts/               # スクリプト
├── logs/                  # ログファイル
├── data/                  # データファイル
└── config/                # 設定ファイル
```

## 🚀 クイックスタート

### 1. 環境構築
```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. 設定
```bash
# 環境変数設定
cp .env.example .env
# .envファイルを編集してLINE Notifyトークンを設定
```

### 3. 実行
```bash
# アプリケーション起動
python main.py
```

### 4. アクセス
- Web UI: http://localhost:8080
- ダッシュボード: http://localhost:8080/dashboard
- 設定画面: http://localhost:8080/settings

## 🌐 API エンドポイント

### センサーAPI
- `GET /api/sensors/` - 全センサーデータ取得
- `GET /api/sensors/history` - センサー履歴取得
- `GET /api/sensors/water-level` - 水位データ取得

### 給水API
- `POST /api/watering/` - 手動給水実行
- `GET /api/watering/history` - 給水履歴取得
- `POST /api/watering/stop` - 緊急停止

### カメラAPI
- `POST /api/camera/capture` - 写真撮影
- `GET /api/camera/images` - 画像リスト取得

### 設定API
- `GET/POST /api/settings/` - 設定取得・保存
- `POST /api/settings/reset` - 設定リセット

### 通知API
- `POST /api/notifications/test` - テスト通知送信
- `POST /api/notifications/alert` - アラート送信
- `GET /api/notifications/history` - 通知履歴取得

## 📚 ドキュメント

### 📖 システム設計書
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - システム全体のアーキテクチャと連携図
- **[FUNCTION_REFERENCE.md](FUNCTION_REFERENCE.md)** - 全関数・メソッドの詳細リファレンス
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - 環境構築手順
- **[INTEGRATION_TEST.md](INTEGRATION_TEST.md)** - 統合テスト手順

### 📂 モジュール別ガイド
- [センサーモジュール](src/sensors/INTEGRATED_GUIDE.md)
- [給水制御モジュール](src/watering/INTEGRATED_GUIDE.md)
- [カメラモジュール](docs/CAMERA_GUIDE.md)
- [データ管理](src/data/INTEGRATED_GUIDE.md)
- [LINE通知](src/notifications/INTEGRATED_GUIDE.md)
- [Web UI](docs/WEB_GUIDE.md)
- [API](src/api/INTEGRATED_GUIDE.md)

## 🧪 テスト
```bash
# 全テスト実行
python -m pytest tests/

# 個別テスト実行
python tests/test_sensors.py
python tests/test_watering.py
python tests/test_integration.py
```

## 🔧 開発

### コード品質
- PEP 8 に準拠
- 型ヒントを使用
- ドキュメント文字列を記述

### コミット規約
- feat: 新機能
- fix: バグ修正
- docs: ドキュメント更新
- test: テスト追加・修正
- refactor: リファクタリング

## 📞 サポート
- 問題報告: GitHub Issues
- 質問: チーム内Slack

## 📄 ライセンス
MIT License

## 👥 チーム
- **リーダー**: 野下
- **サブリーダー**: 大塚
- **メンバー**: 網中、川渕、檜室

## 🔀 ブランチ戦略

### メインブランチ
- `main` - 本番用（安定版）
- `integration/test-all-features` - 統合テスト用（最新機能）

### 機能ブランチ
- `feature-front` - フロントエンド開発
- `feature-bacend` - バックエンド開発
- `feature/sensors-implementation` - センサーモジュール

### 開発の流れ
```bash
# 統合ブランチを取得
git checkout integration/test-all-features
git pull origin integration/test-all-features

# 機能開発
git checkout -b feature/your-feature
# ... 開発 ...
git commit -m "feat: ..."

# 統合ブランチにマージ
git checkout integration/test-all-features
git merge feature/your-feature

# テスト後、mainにマージ
git checkout main
git merge integration/test-all-features
```

## 📊 実装状況

### ✅ 完成済み
- [x] APIレイヤー（6ファイル、14エンドポイント）
- [x] センサーシステム（5ファイル、3種類のセンサー）
- [x] カメラ撮影機能
- [x] Web UI（ダッシュボード・設定画面）
- [x] 設定の永続化
- [x] 統合テストフレームワーク

### ⏳ 開発中
- [ ] 給水制御モジュール
- [ ] データ管理モジュール（CSV/JSON）
- [ ] LINE通知機能
- [ ] カメラ拡張（タイムラプス）

---

**作成日**: 2025年1月  
**最終更新**: 2025年10月15日  
**バージョン**: 1.1 (integration/test-all-features)  
**チーム**: KEBABS

