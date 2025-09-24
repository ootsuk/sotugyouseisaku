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
- Web UI: http://192.168.1.100:5000
- mDNS: http://smart-planter.local:5000

## 📚 ドキュメント
- [開発環境構築手順書](../開発環境構築手順書.md)
- [センサー制御機能実装手順書](../センサー制御機能実装手順書.md)
- [自動給水機能実装手順書](../自動給水機能実装手順書.md)
- [Web UI機能実装手順書](../Web UI機能実装手順書.md)
- [データ管理機能実装手順書](../データ管理機能実装手順書.md)
- [LINE通知サービス実装手順書](../LINE通知サービス実装手順書.md)
- [統合テスト手順書](../統合テスト手順書.md)

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

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

