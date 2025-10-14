# 統合テスト手順書

## 📋 概要
すくすくミントちゃんの全機能統合テストの実施手順

## 🎯 テスト目的
- 全機能が正常に動作することを確認
- APIエンドポイントの動作確認
- エラーハンドリングの確認
- パフォーマンスの確認

## 🛠️ 事前準備

### 1. ブランチの確認
```bash
git branch --show-current
# integration/test-all-features であることを確認
```

### 2. 依存関係のインストール
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# pytestをインストール（まだの場合）
pip install pytest pytest-cov
```

## 🧪 テスト実行手順

### 1. 全テストを実行
```bash
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# 全テスト実行
pytest tests/test_integration.py -v
```

### 2. カバレッジ付きでテスト実行
```bash
# カバレッジレポート付きでテスト
pytest tests/test_integration.py -v --cov=src --cov-report=html
```

### 3. 特定のテストクラスのみ実行
```bash
# Webアプリケーションのテストのみ
pytest tests/test_integration.py::TestWebApplication -v

# APIのテストのみ
pytest tests/test_integration.py::TestAPI -v

# パフォーマンステストのみ
pytest tests/test_integration.py::TestPerformance -v
```

### 4. 詳細出力で実行
```bash
# より詳細な出力
pytest tests/test_integration.py -vv --tb=long
```

## 📊 テスト項目

### ✅ Webアプリケーションテスト
- [x] アプリケーション初期化
- [x] メインページ表示
- [x] ダッシュボードページ表示
- [x] 設定ページ表示
- [x] ログページ表示

### ✅ APIエンドポイントテスト
- [x] システムステータスAPI (GET /api/status)
- [x] センサーデータAPI (GET /api/sensors)
- [x] 手動給水API (POST /api/watering)
- [x] 設定取得API (GET /api/settings)
- [x] 設定保存API (POST /api/settings)
- [x] カメラ撮影API (POST /api/camera/capture)
- [x] 給水履歴API (GET /api/watering/history)
- [x] 緊急停止API (POST /api/watering/stop)
- [x] テスト通知API (POST /api/notifications/test)

### ✅ エラーハンドリングテスト
- [x] 404エラー処理
- [x] API 404エラー処理

### ✅ データ検証テスト
- [x] センサーデータ形式検証
- [x] データ範囲検証
- [x] タイムスタンプ形式検証

### ✅ パフォーマンステスト
- [x] APIレスポンスタイム（1秒以内）
- [x] ページロード時間（1秒以内）

## 📈 期待される結果

### 成功時の出力例
```
tests/test_integration.py::TestWebApplication::test_app_initialization PASSED
tests/test_integration.py::TestWebApplication::test_index_page PASSED
tests/test_integration.py::TestWebApplication::test_dashboard_page PASSED
tests/test_integration.py::TestAPI::test_api_status PASSED
tests/test_integration.py::TestAPI::test_api_sensors PASSED
...

======================== XX passed in X.XXs ========================
```

### テストカバレッジ
- 目標: 80%以上
- レポート: `htmlcov/index.html` で確認可能

## 🔍 手動テスト項目

### 1. Webブラウザテスト
```bash
# サーバーを起動
python main.py
```

**テスト項目:**
1. `http://localhost:8080/` - メインページ
   - [ ] ページが表示される
   - [ ] センサーデータが表示される
   - [ ] 手動給水ボタンが動作する

2. `http://localhost:8080/dashboard` - ダッシュボード
   - [ ] ページが表示される
   - [ ] センサーカードが表示される
   - [ ] グラフが表示される
   - [ ] 操作パネルが動作する

3. `http://localhost:8080/settings` - 設定ページ
   - [ ] ページが表示される
   - [ ] 全設定項目が表示される
   - [ ] 保存ボタンが動作する

4. `http://localhost:8080/logs` - ログページ
   - [ ] ページが表示される

### 2. JavaScript機能テスト

**ブラウザのコンソールで確認:**
```javascript
// センサーマネージャーの初期化
const manager = getSensorManager();
await manager.initialize();

// 現在のデータを取得
const data = manager.getCurrentData();
console.log(data);

// 統計情報を取得
const stats = manager.getStatistics('temperature', 'all');
console.log(stats);
```

### 3. API手動テスト

**curlコマンドでテスト:**
```bash
# システムステータス
curl http://localhost:8080/api/status

# センサーデータ
curl http://localhost:8080/api/sensors

# 手動給水
curl -X POST http://localhost:8080/api/watering

# 設定取得
curl http://localhost:8080/api/settings

# 設定保存
curl -X POST http://localhost:8080/api/settings \
  -H "Content-Type: application/json" \
  -d '{"soilMoistureThreshold": 150}'
```

## 🐛 トラブルシューティング

### テストが失敗する場合

1. **ImportError が発生**
   ```bash
   # パスの確認
   echo $PYTHONPATH
   
   # プロジェクトルートから実行
   cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter
   pytest tests/test_integration.py
   ```

2. **アサーションエラー**
   ```bash
   # 詳細なトレースバックを表示
   pytest tests/test_integration.py -vv --tb=long
   ```

3. **タイムアウトエラー**
   ```bash
   # タイムアウト時間を延長
   pytest tests/test_integration.py --timeout=10
   ```

## 📝 テスト結果の記録

### テスト実行日: ____________________

### テスト結果:
- [ ] 全テスト成功
- [ ] 一部テスト失敗（詳細を記載）
- [ ] テスト失敗（詳細を記載）

### カバレッジ: _____%

### 問題点:
```
（問題があれば記載）
```

### 修正事項:
```
（修正が必要な項目を記載）
```

## 🎯 次のステップ

テスト成功後:
1. 結果をドキュメント化
2. mainブランチにマージ
3. リモートリポジトリにプッシュ
4. 本番環境へのデプロイ準備

---

**作成日**: 2025年10月10日  
**バージョン**: 1.0  
**チーム**: KEBABS

