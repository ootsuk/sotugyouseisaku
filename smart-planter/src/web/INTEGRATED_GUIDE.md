# Web UI機能 統合実装ガイド

## 📋 概要
スマートプランターのWebダッシュボード、成長記録、AI園芸アドバイザーの実装手順書

## 🎯 実装目標
- リアルタイムセンサーデータ表示
- 植物の成長記録とタイムラプス
- AI園芸アドバイザー機能
- レスポンシブデザイン対応
- 手動操作機能（撮影、給水）

## 🛠️ 必要な環境

### フロントエンド
- HTML5, CSS3, JavaScript
- Chart.js (グラフ表示)
- Bootstrap 5 (レスポンシブデザイン)
- WebSocket (リアルタイム通信)

### バックエンド
- Flask 2.3.3
- Flask-SocketIO (WebSocket)
- 既存のセンサー・給水システム

---

## 📄 実装コード

### 📄 templates/base.html
ベーステンプレート

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">                <!-- 文字エンコーディングをUTF-8に設定 -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  <!-- レスポンシブ対応のビューポート設定 -->
    <title>{% block title %}すくすくミントちゃん{% endblock %}</title>  <!-- ページタイトル（ブロックで上書き可能） -->
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">  <!-- Bootstrap CSSを読み込み -->
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>  <!-- Chart.jsライブラリを読み込み -->
    <!-- Socket.IO -->
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>  <!-- Socket.IOライブラリを読み込み -->
    <!-- カスタムCSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">  <!-- カスタムスタイルを読み込み -->
    
    {% block extra_head %}{% endblock %}  <!-- 追加のhead要素（ブロックで上書き可能） -->
</head>
<body>
    <!-- ナビゲーションバー -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">  <!-- Bootstrapのナビゲーションバー -->
        <div class="container">            <!-- コンテナで幅を制限 -->
            <a class="navbar-brand" href="/">  <!-- ブランドロゴリンク -->
                🌱 すくすくミントちゃん    <!-- ブランド名 -->
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">  <!-- モバイル用トグルボタン -->
                <span class="navbar-toggler-icon"></span>  <!-- ハンバーガーメニューアイコン -->
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">  <!-- ナビゲーションメニュー -->
                <ul class="navbar-nav ms-auto">  <!-- ナビゲーションリスト（右寄せ） -->
                    <li class="nav-item">        <!-- ナビゲーションアイテム -->
                        <a class="nav-link" href="/">ダッシュボード</a>  <!-- ダッシュボードリンク -->
                    </li>
                    <li class="nav-item">        <!-- ナビゲーションアイテム -->
                        <a class="nav-link" href="/history">成長記録</a>  <!-- 成長記録リンク -->
                    </li>
                    <li class="nav-item">        <!-- ナビゲーションアイテム -->
                        <a class="nav-link" href="/advisor">AI園芸アドバイザー</a>  <!-- AIアドバイザーリンク -->
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- メインコンテンツ -->
    <main class="container mt-4">         <!-- メインコンテンツエリア（上マージン4） -->
        {% block content %}{% endblock %}  <!-- メインコンテンツ（ブロックで上書き可能） -->
    </main>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>  <!-- Bootstrap JavaScriptを読み込み -->
    <!-- カスタムJS -->
    {% block extra_scripts %}{% endblock %}  <!-- 追加のスクリプト（ブロックで上書き可能） -->
</body>
</html>
```

### 📄 templates/dashboard.html
ダッシュボード画面

```html
{% extends "base.html" %}                <!-- ベーステンプレートを継承 -->

{% block title %}ダッシュボード - すくすくミントちゃん{% endblock %}  <!-- ページタイトルを設定 -->

{% block content %}
<div class="row">                         <!-- Bootstrapの行レイアウト -->
    <!-- センサーデータ表示 -->
    <div class="col-lg-8">                <!-- 左側8カラム -->
        <div class="card mb-4">           <!-- Bootstrapカード（下マージン4） -->
            <div class="card-header">     <!-- カードヘッダー -->
                <h5 class="card-title mb-0">🌡️ 現在の状態</h5>  <!-- カードタイトル -->
            </div>
            <div class="card-body">       <!-- カードボディ -->
                <div class="row">         <!-- センサーデータ表示用の行 -->
                    <div class="col-md-3">  <!-- 温度表示用3カラム -->
                        <div class="text-center">  <!-- 中央寄せ -->
                            <div class="display-6 text-primary" id="temperature">--</div>  <!-- 温度表示（プライマリカラー） -->
                            <div class="text-muted">温度 (°C)</div>  <!-- 温度ラベル -->
                        </div>
                    </div>
                    <div class="col-md-3">  <!-- 湿度表示用3カラム -->
                        <div class="text-center">  <!-- 中央寄せ -->
                            <div class="display-6 text-info" id="humidity">--</div>  <!-- 湿度表示（インフォカラー） -->
                            <div class="text-muted">湿度 (%)</div>  <!-- 湿度ラベル -->
                        </div>
                    </div>
                    <div class="col-md-3">  <!-- 土壌水分表示用3カラム -->
                        <div class="text-center">  <!-- 中央寄せ -->
                            <div class="display-6 text-success" id="soil-moisture">--</div>  <!-- 土壌水分表示（サクセスカラー） -->
                            <div class="text-muted">土壌水分 (%)</div>  <!-- 土壌水分ラベル -->
                        </div>
                    </div>
                    <div class="col-md-3">  <!-- 水位表示用3カラム -->
                        <div class="text-center">  <!-- 中央寄せ -->
                            <div class="display-6" id="water-level">--</div>  <!-- 水位表示 -->
                            <div class="text-muted">水位</div>  <!-- 水位ラベル -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 最新画像 -->
        <div class="card mb-4">           <!-- Bootstrapカード（下マージン4） -->
            <div class="card-header d-flex justify-content-between align-items-center">  <!-- ヘッダー（フレックス、両端寄せ） -->
                <h5 class="card-title mb-0">📸 最新の画像</h5>  <!-- カードタイトル -->
                <button class="btn btn-primary btn-sm" onclick="takePhoto()">  <!-- 撮影ボタン -->
                    📷 撮影
                </button>
            </div>
            <div class="card-body text-center">  <!-- カードボディ（中央寄せ） -->
                <img id="latest-image" src="/api/camera/latest"   <!-- 最新画像表示 -->
                     class="img-fluid rounded" style="max-height: 400px;"  <!-- レスポンシブ、角丸、最大高さ制限 -->
                     onerror="this.src='/static/images/placeholder.jpg'">  <!-- エラー時の代替画像 -->
                <div class="mt-2 text-muted" id="image-timestamp">--</div>  <!-- 画像タイムスタンプ -->
            </div>
        </div>
    </div>

    <!-- 操作パネル -->
    <div class="col-lg-4">                <!-- 右側4カラム -->
        <div class="card mb-4">           <!-- Bootstrapカード（下マージン4） -->
            <div class="card-header">     <!-- カードヘッダー -->
                <h5 class="card-title mb-0">🎮 操作</h5>  <!-- カードタイトル -->
            </div>
            <div class="card-body">       <!-- カードボディ -->
                <div class="d-grid gap-2">  <!-- グリッドレイアウト（縦並び、間隔2） -->
                    <button class="btn btn-success" onclick="manualWatering()">  <!-- 手動給水ボタン -->
                        💧 手動給水
                    </button>
                    <button class="btn btn-warning" onclick="emergencyStop()">  <!-- 緊急停止ボタン -->
                        🛑 緊急停止
                    </button>
                    <button class="btn btn-info" onclick="refreshData()">  <!-- データ更新ボタン -->
                        🔄 データ更新
                    </button>
                </div>
            </div>
        </div>

        <!-- 給水設定 -->
        <div class="card mb-4">           <!-- Bootstrapカード（下マージン4） -->
            <div class="card-header">     <!-- カードヘッダー -->
                <h5 class="card-title mb-0">⚙️ 給水設定</h5>  <!-- カードタイトル -->
            </div>
            <div class="card-body">       <!-- カードボディ -->
                <div class="mb-3">        <!-- フォームグループ（下マージン3） -->
                    <label class="form-label">土壌水分閾値</label>  <!-- ラベル -->
                    <input type="number" class="form-control" id="moisture-threshold" value="159">  <!-- 数値入力フィールド -->
                </div>
                <div class="mb-3">        <!-- フォームグループ（下マージン3） -->
                    <label class="form-label">給水間隔 (時間)</label>  <!-- ラベル -->
                    <input type="number" class="form-control" id="watering-interval" value="12">  <!-- 数値入力フィールド -->
                </div>
                <button class="btn btn-primary w-100" onclick="updateSettings()">  <!-- 設定更新ボタン（全幅） -->
                    設定更新
                </button>
            </div>
        </div>

        <!-- システム状態 -->
        <div class="card">                <!-- Bootstrapカード -->
            <div class="card-header">     <!-- カードヘッダー -->
                <h5 class="card-title mb-0">📊 システム状態</h5>  <!-- カードタイトル -->
            </div>
            <div class="card-body">       <!-- カードボディ -->
                <div class="mb-2">        <!-- 状態表示（下マージン2） -->
                    <span class="badge bg-success" id="sensor-status">センサー: 正常</span>  <!-- センサー状態バッジ -->
                </div>
                <div class="mb-2">        <!-- 状態表示（下マージン2） -->
                    <span class="badge bg-info" id="watering-status">給水: 待機中</span>  <!-- 給水状態バッジ -->
                </div>
                <div class="mb-2">        <!-- 状態表示（下マージン2） -->
                    <span class="badge bg-primary" id="connection-status">接続: オンライン</span>  <!-- 接続状態バッジ -->
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}                <!-- 追加スクリプトブロック -->
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>  <!-- ダッシュボードJavaScriptを読み込み -->
{% endblock %}
```

### 📄 static/css/style.css
カスタムスタイル

```css
:root {                                   /* CSS変数を定義 */
    --primary-color: #28a745;            /* プライマリカラー（緑） */
    --secondary-color: #6c757d;          /* セカンダリカラー（グレー） */
    --success-color: #28a745;            /* サクセスカラー（緑） */
    --info-color: #17a2b8;               /* インフォカラー（青） */
    --warning-color: #ffc107;            /* ワーニングカラー（黄） */
    --danger-color: #dc3545;              /* デンジャーカラー（赤） */
}

body {                                    /* ボディスタイル */
    background-color: #f8f9fa;           /* 背景色を薄いグレーに設定 */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;  /* フォントファミリーを設定 */
}

.navbar-brand {                           /* ナビゲーションブランドスタイル */
    font-weight: bold;                    /* フォントウェイトを太字に */
    font-size: 1.5rem;                   /* フォントサイズを1.5remに */
}

.card {                                   /* カードスタイル */
    border: none;                         /* ボーダーを削除 */
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);  /* 影を追加 */
    border-radius: 0.5rem;                /* 角丸を設定 */
}

.card-header {                            /* カードヘッダースタイル */
    background-color: #fff;              /* 背景色を白に */
    border-bottom: 1px solid #dee2e6;    /* 下ボーダーを追加 */
    font-weight: 600;                    /* フォントウェイトを設定 */
}

.display-6 {                              /* 大きな表示用スタイル */
    font-weight: 700;                    /* フォントウェイトを太字に */
    margin-bottom: 0.5rem;               /* 下マージンを設定 */
}

.btn {                                    /* ボタンスタイル */
    border-radius: 0.375rem;             /* 角丸を設定 */
    font-weight: 500;                    /* フォントウェイトを設定 */
}

.badge {                                  /* バッジスタイル */
    font-size: 0.875rem;                  /* フォントサイズを設定 */
}

/* センサーデータ表示 */
.sensor-value {                           /* センサー値表示スタイル */
    font-size: 2rem;                     /* フォントサイズを2remに */
    font-weight: bold;                   /* フォントウェイトを太字に */
    margin-bottom: 0.5rem;               /* 下マージンを設定 */
}

.sensor-label {                           /* センサーラベルスタイル */
    color: #6c757d;                      /* 色をグレーに */
    font-size: 0.875rem;                 /* フォントサイズを小さく */
    text-transform: uppercase;           /* 大文字に変換 */
    letter-spacing: 0.5px;               /* 文字間隔を設定 */
}

/* 画像表示 */
.plant-image {                            /* 植物画像スタイル */
    max-height: 400px;                   /* 最大高さを制限 */
    border-radius: 0.5rem;               /* 角丸を設定 */
    box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1);  /* 影を追加 */
}

/* レスポンシブ対応 */
@media (max-width: 768px) {               /* モバイル用メディアクエリ */
    .display-6 {                         /* 大きな表示の調整 */
        font-size: 1.5rem;               /* フォントサイズを小さく */
    }
    
    .card-body {                         /* カードボディの調整 */
        padding: 1rem;                   /* パディングを調整 */
    }
    
    .btn {                               /* ボタンの調整 */
        font-size: 0.875rem;             /* フォントサイズを小さく */
    }
}

/* アニメーション */
.fade-in {                               /* フェードインアニメーション */
    animation: fadeIn 0.5s ease-in;      /* アニメーションを適用 */
}

@keyframes fadeIn {                      /* フェードインキーフレーム */
    from { opacity: 0; transform: translateY(10px); }  /* 開始状態 */
    to { opacity: 1; transform: translateY(0); }      /* 終了状態 */
}

/* ステータス表示 */
.status-online {                         /* オンライン状態スタイル */
    color: var(--success-color);         /* サクセスカラーを使用 */
}

.status-offline {                        /* オフライン状態スタイル */
    color: var(--danger-color);          /* デンジャーカラーを使用 */
}

.status-warning {                        /* 警告状態スタイル */
    color: var(--warning-color);         /* ワーニングカラーを使用 */
}

/* チャット機能 */
.chat-message {                          /* チャットメッセージスタイル */
    margin-bottom: 10px;                 /* 下マージンを設定 */
    padding: 10px;                       /* パディングを設定 */
    border-radius: 10px;                 /* 角丸を設定 */
}

.bot-message {                           /* ボットメッセージスタイル */
    background-color: #e9ecef;           /* 背景色を薄いグレーに */
    margin-right: 20%;                   /* 右マージンを設定 */
}

.user-message {                          /* ユーザーメッセージスタイル */
    background-color: #007bff;           /* 背景色を青に */
    color: white;                        /* 文字色を白に */
    margin-left: 20%;                    /* 左マージンを設定 */
    text-align: right;                   /* 右寄せ */
}

.message-content {                       /* メッセージ内容スタイル */
    word-wrap: break-word;               /* 単語の折り返しを有効 */
}
```

### 📄 static/js/dashboard.js
ダッシュボードJavaScript

```javascript
class Dashboard {                         /* ダッシュボードクラスを定義 */
    constructor() {                      /* コンストラクタ */
        this.socket = io();               /* Socket.IOクライアントを初期化 */
        this.init();                      /* 初期化メソッドを呼び出し */
    }

    init() {                             /* 初期化メソッド */
        this.setupSocketListeners();      /* Socket.IOリスナーを設定 */
        this.loadInitialData();          /* 初期データを読み込み */
        this.startPeriodicUpdates();     /* 定期更新を開始 */
    }

    setupSocketListeners() {             /* Socket.IOリスナー設定 */
        // センサーデータ受信
        this.socket.on('sensor_data', (data) => {  /* センサーデータ受信イベント */
            this.updateSensorDisplay(data);        /* センサー表示を更新 */
        });

        // 接続状態
        this.socket.on('connect', () => {          /* 接続イベント */
            this.updateConnectionStatus(true);     /* 接続状態を更新 */
        });

        this.socket.on('disconnect', () => {       /* 切断イベント */
            this.updateConnectionStatus(false);    /* 接続状態を更新 */
        });
    }

    updateSensorDisplay(data) {          /* センサー表示更新 */
        // 温湿度データ
        if (data.temperature_humidity && !data.temperature_humidity.error) {  /* 温湿度データが存在し、エラーがない場合 */
            document.getElementById('temperature').textContent =   /* 温度表示を更新 */
                data.temperature_humidity.temperature;
            document.getElementById('humidity').textContent =      /* 湿度表示を更新 */
                data.temperature_humidity.humidity;
        }

        // 土壌水分データ
        if (data.soil_moisture && !data.soil_moisture.error) {     /* 土壌水分データが存在し、エラーがない場合 */
            document.getElementById('soil-moisture').textContent = /* 土壌水分表示を更新 */
                data.soil_moisture.moisture_percentage;
        }

        // 水位データ
        if (data.water_level && !data.water_level.error) {         /* 水位データが存在し、エラーがない場合 */
            const waterLevel = data.water_level.is_water_available ? '💧 満水' : '🚨 空';  /* 水位状態を判定 */
            document.getElementById('water-level').innerHTML = waterLevel;  /* 水位表示を更新 */
        }
    }

    updateConnectionStatus(connected) {   /* 接続状態更新 */
        const statusElement = document.getElementById('connection-status');  /* 接続状態要素を取得 */
        if (connected) {                 /* 接続中の場合 */
            statusElement.textContent = '接続: オンライン';  /* テキストを更新 */
            statusElement.className = 'badge bg-success';   /* クラスを成功バッジに変更 */
        } else {                         /* 切断中の場合 */
            statusElement.textContent = '接続: オフライン'; /* テキストを更新 */
            statusElement.className = 'badge bg-danger';    /* クラスを危険バッジに変更 */
        }
    }

    async loadInitialData() {            /* 初期データ読み込み */
        try {
            // 給水設定読み込み
            const settingsResponse = await fetch('/api/watering/settings');  /* 給水設定APIを呼び出し */
            const settings = await settingsResponse.json();                 /* JSONレスポンスを解析 */
            
            document.getElementById('moisture-threshold').value = settings.soil_moisture_threshold;  /* 土壌水分閾値を設定 */
            document.getElementById('watering-interval').value = settings.watering_interval_hours;  /* 給水間隔を設定 */

            // システム状態読み込み
            const statusResponse = await fetch('/api/watering/status');     /* 給水状態APIを呼び出し */
            const status = await statusResponse.json();                     /* JSONレスポンスを解析 */
            
            this.updateSystemStatus(status);                               /* システム状態を更新 */
        } catch (error) {
            console.error('初期データ読み込みエラー:', error);              /* エラーログ出力 */
        }
    }

    updateSystemStatus(status) {         /* システム状態更新 */
        // センサー状態
        const sensorStatus = document.getElementById('sensor-status');      /* センサー状態要素を取得 */
        if (status.watering_controller_status) {                           /* 給水制御状態が存在する場合 */
            sensorStatus.textContent = 'センサー: 正常';                    /* テキストを更新 */
            sensorStatus.className = 'badge bg-success';                   /* クラスを成功バッジに変更 */
        }

        // 給水状態
        const wateringStatus = document.getElementById('watering-status');  /* 給水状態要素を取得 */
        if (status.auto_watering_running) {                                 /* 自動給水が実行中の場合 */
            wateringStatus.textContent = '給水: 自動実行中';                /* テキストを更新 */
            wateringStatus.className = 'badge bg-info';                     /* クラスを情報バッジに変更 */
        } else {                          /* 自動給水が停止中の場合 */
            wateringStatus.textContent = '給水: 待機中';                    /* テキストを更新 */
            wateringStatus.className = 'badge bg-secondary';                /* クラスをセカンダリバッジに変更 */
        }
    }

    startPeriodicUpdates() {             /* 定期更新開始 */
        // 5秒間隔でデータ更新
        setInterval(() => {              /* 5秒間隔で実行 */
            this.refreshData();           /* データを更新 */
        }, 5000);
    }

    async refreshData() {                /* データ更新 */
        try {
            const response = await fetch('/api/sensors/latest');           /* 最新センサーデータAPIを呼び出し */
            const data = await response.json();                           /* JSONレスポンスを解析 */
            this.updateSensorDisplay(data);                               /* センサー表示を更新 */
        } catch (error) {
            console.error('データ更新エラー:', error);                     /* エラーログ出力 */
        }
    }

    async manualWatering() {             /* 手動給水 */
        try {
            const response = await fetch('/api/watering/manual', {         /* 手動給水APIを呼び出し */
                method: 'POST'            /* POSTメソッドを使用 */
            });
            const result = await response.json();                         /* JSONレスポンスを解析 */
            
            if (result.success) {         /* 成功の場合 */
                this.showAlert('給水完了', 'success');                     /* 成功アラートを表示 */
            } else {                      /* 失敗の場合 */
                this.showAlert(`給水失敗: ${result.message}`, 'danger');  /* 失敗アラートを表示 */
            }
        } catch (error) {
            this.showAlert('給水エラー', 'danger');                        /* エラーアラートを表示 */
        }
    }

    async emergencyStop() {              /* 緊急停止 */
        if (confirm('緊急停止を実行しますか？')) {                         /* 確認ダイアログを表示 */
            try {
                const response = await fetch('/api/watering/emergency_stop', {  /* 緊急停止APIを呼び出し */
                    method: 'POST'        /* POSTメソッドを使用 */
                });
                const result = await response.json();                     /* JSONレスポンスを解析 */
                
                if (result.success) {     /* 成功の場合 */
                    this.showAlert('緊急停止完了', 'warning');            /* 警告アラートを表示 */
                } else {                  /* 失敗の場合 */
                    this.showAlert(`停止失敗: ${result.message}`, 'danger');  /* 失敗アラートを表示 */
                }
            } catch (error) {
                this.showAlert('停止エラー', 'danger');                    /* エラーアラートを表示 */
            }
        }
    }

    async takePhoto() {                  /* 撮影 */
        try {
            const response = await fetch('/api/camera/capture', {          /* 撮影APIを呼び出し */
                method: 'POST'            /* POSTメソッドを使用 */
            });
            const result = await response.json();                         /* JSONレスポンスを解析 */
            
            if (result.success) {         /* 成功の場合 */
                // 画像更新
                const img = document.getElementById('latest-image');        /* 画像要素を取得 */
                img.src = `/api/camera/latest?t=${Date.now()}`;           /* 画像URLを更新（キャッシュ回避） */
                this.showAlert('撮影完了', 'success');                     /* 成功アラートを表示 */
            } else {                      /* 失敗の場合 */
                this.showAlert(`撮影失敗: ${result.message}`, 'danger');  /* 失敗アラートを表示 */
            }
        } catch (error) {
            this.showAlert('撮影エラー', 'danger');                        /* エラーアラートを表示 */
        }
    }

    async updateSettings() {             /* 設定更新 */
        const settings = {               /* 設定オブジェクトを構築 */
            soil_moisture_threshold: parseInt(document.getElementById('moisture-threshold').value),  /* 土壌水分閾値を取得 */
            watering_interval_hours: parseInt(document.getElementById('watering-interval').value)   /* 給水間隔を取得 */
        };

        try {
            const response = await fetch('/api/watering/settings', {       /* 設定更新APIを呼び出し */
                method: 'POST',           /* POSTメソッドを使用 */
                headers: {                /* ヘッダーを設定 */
                    'Content-Type': 'application/json'  /* JSONコンテンツタイプ */
                },
                body: JSON.stringify(settings)         /* 設定をJSON文字列化 */
            });
            const result = await response.json();                         /* JSONレスポンスを解析 */
            
            if (result.success) {         /* 成功の場合 */
                this.showAlert('設定更新完了', 'success');                /* 成功アラートを表示 */
            } else {                      /* 失敗の場合 */
                this.showAlert(`設定更新失敗: ${result.message}`, 'danger');  /* 失敗アラートを表示 */
            }
        } catch (error) {
            this.showAlert('設定更新エラー', 'danger');                    /* エラーアラートを表示 */
        }
    }

    showAlert(message, type) {           /* アラート表示 */
        // Bootstrap アラート表示
        const alertDiv = document.createElement('div');                  /* アラート要素を作成 */
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;  /* クラスを設定 */
        alertDiv.innerHTML = `                                           /* HTMLを設定 */
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.insertBefore(alertDiv, document.body.firstChild);  /* ボディの最初に挿入 */
        
        // 3秒後に自動削除
        setTimeout(() => {               /* 3秒後に実行 */
            if (alertDiv.parentNode) {   /* 親要素が存在する場合 */
                alertDiv.parentNode.removeChild(alertDiv);              /* アラート要素を削除 */
            }
        }, 3000);
    }
}

// グローバル関数
function manualWatering() {              /* 手動給水グローバル関数 */
    dashboard.manualWatering();
}

function emergencyStop() {               /* 緊急停止グローバル関数 */
    dashboard.emergencyStop();
}

function takePhoto() {                   /* 撮影グローバル関数 */
    dashboard.takePhoto();
}

function refreshData() {                 /* データ更新グローバル関数 */
    dashboard.refreshData();
}

function updateSettings() {              /* 設定更新グローバル関数 */
    dashboard.updateSettings();
}

// ダッシュボード初期化
let dashboard;                           /* ダッシュボードインスタンス変数 */
document.addEventListener('DOMContentLoaded', () => {  /* DOM読み込み完了イベント */
    dashboard = new Dashboard();         /* ダッシュボードインスタンスを作成 */
});
```

---

## 📊 実装完了チェックリスト

- [ ] Flask Webアプリケーション構造作成
- [ ] HTMLテンプレート実装完了
- [ ] JavaScript機能実装完了
- [ ] WebSocket通信実装完了
- [ ] API実装完了
- [ ] CSSスタイル実装完了
- [ ] レスポンシブデザイン確認完了
- [ ] リアルタイム更新確認完了
- [ ] 手動操作機能確認完了
- [ ] エラーハンドリング確認完了

## 🎯 次のステップ

1. **成長記録画面実装**: グラフ表示とタイムラプス
2. **AI園芸アドバイザー実装**: LLM連携
3. **カメラ機能実装**: 撮影と画像管理
4. **統合テスト**: 全機能の動作確認

---

## 🏗️ クラス全体の流れと意味

### **Dashboardクラス**
**意味**: Webダッシュボードの核となるJavaScriptクラス
**役割**:
- Socket.IOによるリアルタイム通信
- センサーデータの動的表示更新
- 手動操作（給水、撮影、緊急停止）の提供
- 設定変更の管理
- ユーザーフレンドリーなアラート表示

**全体の流れ**:
1. **初期化**: Socket.IO接続、初期データ読み込み、定期更新開始
2. **リアルタイム通信**: WebSocketでセンサーデータを受信
3. **データ表示**: 受信したデータをHTML要素に反映
4. **ユーザー操作**: ボタンクリックでAPI呼び出し
5. **状態管理**: 接続状態、システム状態の表示
6. **エラーハンドリング**: 通信エラー時の適切な処理
7. **UI更新**: 成功/失敗時のアラート表示

**主要機能**:
- **センサー監視**: 温湿度、土壌水分、水位のリアルタイム表示
- **手動制御**: 給水、撮影、緊急停止の実行
- **設定管理**: 給水パラメータの動的変更
- **状態表示**: システムの健全性を視覚的に表示
- **レスポンシブ**: モバイル・デスクトップ両対応

**技術的特徴**:
- **非同期処理**: async/awaitによるAPI呼び出し
- **イベント駆動**: Socket.IOイベントによるリアルタイム更新
- **エラー処理**: try-catchによる堅牢なエラーハンドリング
- **UI/UX**: Bootstrapによる美しいインターフェース

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

