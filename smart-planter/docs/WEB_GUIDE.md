# Web UI機能 統合実装ガイド

## 📋 概要
スマートプランターのWebダッシュボード、成長記録、設定画面の実装手順書

## 🎯 実装目標
- リアルタイムセンサーデータ表示
- 植物の成長記録とタイムラプス
- 手動操作機能（撮影、給水）
- レスポンシブデザイン対応
- 設定画面

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

## 📁 ファイル作成手順

### Step 1: Web UIディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# Web UIディレクトリの確認
ls -la src/web/
ls -la src/web/templates/
ls -la src/web/static/
```

### Step 2: 各ファイルの作成順序
1. `src/web/templates/base.html` - ベーステンプレート
2. `src/web/templates/dashboard.html` - ダッシュボード
3. `src/web/templates/settings.html` - 設定ページ
4. `src/web/static/css/main.css` - メインスタイル
5. `src/web/static/js/main.js` - メインJavaScript

### Step 3: ファイル作成コマンド
```bash
# テンプレートファイルを作成
touch src/web/templates/base.html
touch src/web/templates/dashboard.html
touch src/web/templates/settings.html

# 静的ファイルを作成
touch src/web/static/css/main.css
touch src/web/static/js/main.js
touch src/web/static/js/sensors.js
touch src/web/static/js/dashboard.js

# ディレクトリが存在しない場合は作成
mkdir -p src/web/static/css
mkdir -p src/web/static/js
mkdir -p src/web/static/images
```

### Step 4: 依存関係の追加
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# WebSocket関連ライブラリをインストール
pip install Flask-SocketIO
pip install python-socketio

# requirements.txtを更新
pip freeze > requirements.txt
```

## 📄 実装コード

### 📄 src/web/templates/base.html
ベーステンプレート

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}すくすくミントちゃん{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Socket.IO -->
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- カスタムCSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    <!-- ナビゲーションバー -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-seedling"></i> すくすくミントちゃん
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('index') }}">
                            <i class="fas fa-home"></i> ダッシュボード
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('settings') }}">
                            <i class="fas fa-cog"></i> 設定
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('logs') }}">
                            <i class="fas fa-file-alt"></i> ログ
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- メインコンテンツ -->
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>

    <!-- フッター -->
    <footer class="bg-light mt-5 py-4">
        <div class="container text-center">
            <p class="text-muted mb-0">
                &copy; 2025 すくすくミントちゃん - チームKEBABS
            </p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- カスタムJS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

### 📄 src/web/templates/dashboard.html
ダッシュボードページ

```html
{% extends "base.html" %}

{% block title %}ダッシュボード - すくすくミントちゃん{% endblock %}

{% block content %}
<div class="row">
    <!-- システムステータス -->
    <div class="col-12 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-info-circle"></i> システムステータス</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <div class="text-center">
                            <h6>システム状態</h6>
                            <span id="system-status" class="badge bg-success">稼働中</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h6>最終更新</h6>
                            <span id="last-update">-</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h6>稼働時間</h6>
                            <span id="uptime">-</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h6>バージョン</h6>
                            <span id="version">1.0.0</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- センサーデータ -->
    <div class="col-lg-8 mb-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-thermometer-half"></i> センサーデータ</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <!-- 温度 -->
                    <div class="col-md-4 mb-3">
                        <div class="sensor-card">
                            <div class="sensor-icon">
                                <i class="fas fa-thermometer-half"></i>
                            </div>
                            <div class="sensor-info">
                                <h6>温度</h6>
                                <div class="sensor-value" id="temperature">-</div>
                                <div class="sensor-unit">°C</div>
                            </div>
                        </div>
                    </div>

                    <!-- 湿度 -->
                    <div class="col-md-4 mb-3">
                        <div class="sensor-card">
                            <div class="sensor-icon">
                                <i class="fas fa-tint"></i>
                            </div>
                            <div class="sensor-info">
                                <h6>湿度</h6>
                                <div class="sensor-value" id="humidity">-</div>
                                <div class="sensor-unit">%</div>
                            </div>
                        </div>
                    </div>

                    <!-- 土壌水分 -->
                    <div class="col-md-4 mb-3">
                        <div class="sensor-card">
                            <div class="sensor-icon">
                                <i class="fas fa-seedling"></i>
                            </div>
                            <div class="sensor-info">
                                <h6>土壌水分</h6>
                                <div class="sensor-value" id="soil-moisture">-</div>
                                <div class="sensor-unit">-</div>
                            </div>
                        </div>
                    </div>

                    <!-- 水の残量 -->
                    <div class="col-md-6 mb-3">
                        <div class="sensor-card">
                            <div class="sensor-icon">
                                <i class="fas fa-tint"></i>
                            </div>
                            <div class="sensor-info">
                                <h6>水の残量</h6>
                                <div class="sensor-value" id="water-volume">-</div>
                                <div class="sensor-unit">ml</div>
                                <div class="progress mt-2">
                                    <div class="progress-bar" id="water-progress" role="progressbar"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 水の残量パーセンテージ -->
                    <div class="col-md-6 mb-3">
                        <div class="sensor-card">
                            <div class="sensor-icon">
                                <i class="fas fa-percentage"></i>
                            </div>
                            <div class="sensor-info">
                                <h6>残量</h6>
                                <div class="sensor-value" id="water-percentage">-</div>
                                <div class="sensor-unit">%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 操作パネル -->
    <div class="col-lg-4 mb-4">
        <div class="card">
            <div class="card-header bg-warning text-dark">
                <h5 class="mb-0"><i class="fas fa-tools"></i> 操作パネル</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <button class="btn btn-primary" onclick="manualWatering()">
                        <i class="fas fa-tint"></i> 手動給水
                    </button>
                    <button class="btn btn-info" onclick="capturePhoto()">
                        <i class="fas fa-camera"></i> 写真撮影
                    </button>
                    <button class="btn btn-secondary" onclick="refreshData()">
                        <i class="fas fa-sync-alt"></i> データ更新
                    </button>
                    <button class="btn btn-danger" onclick="emergencyStop()">
                        <i class="fas fa-stop"></i> 緊急停止
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- グラフ -->
    <div class="col-12 mb-4">
        <div class="card">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0"><i class="fas fa-chart-line"></i> センサーデータグラフ</h5>
            </div>
            <div class="card-body">
                <canvas id="sensorChart" width="400" height="200"></canvas>
            </div>
        </div>
    </div>

    <!-- 給水履歴 -->
    <div class="col-12 mb-4">
        <div class="card">
            <div class="card-header bg-secondary text-white">
                <h5 class="mb-0"><i class="fas fa-history"></i> 給水履歴</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>日時</th>
                                <th>種類</th>
                                <th>時間</th>
                                <th>土壌水分（前）</th>
                                <th>土壌水分（後）</th>
                                <th>状態</th>
                            </tr>
                        </thead>
                        <tbody id="watering-history">
                            <tr>
                                <td colspan="6" class="text-center">データを読み込み中...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
{% endblock %}
```

### 📄 src/web/static/css/main.css
メインスタイル

```css
/* カスタムスタイル */
:root {
    --primary-color: #28a745;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #17a2b8;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
}

/* センサーカード */
.sensor-card {
    display: flex;
    align-items: center;
    padding: 1rem;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    background-color: white;
    transition: box-shadow 0.15s ease-in-out;
}

.sensor-card:hover {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.sensor-icon {
    font-size: 2rem;
    color: var(--primary-color);
    margin-right: 1rem;
}

.sensor-info h6 {
    margin-bottom: 0.25rem;
    color: var(--secondary-color);
    font-size: 0.875rem;
    font-weight: 600;
}

.sensor-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
    line-height: 1;
}

.sensor-unit {
    font-size: 0.75rem;
    color: var(--secondary-color);
    margin-top: 0.25rem;
}

/* ナビゲーションバー */
.navbar-brand {
    font-weight: bold;
}

.navbar-brand i {
    margin-right: 0.5rem;
}

/* カード */
.card {
    border: none;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border-radius: 0.5rem;
}

.card-header {
    border-radius: 0.5rem 0.5rem 0 0 !important;
    border-bottom: none;
    font-weight: 600;
}

/* ボタン */
.btn {
    border-radius: 0.375rem;
    font-weight: 500;
}

.btn i {
    margin-right: 0.5rem;
}

/* プログレスバー */
.progress {
    height: 0.5rem;
    border-radius: 0.25rem;
}

.progress-bar {
    border-radius: 0.25rem;
}

/* テーブル */
.table {
    margin-bottom: 0;
}

.table th {
    border-top: none;
    font-weight: 600;
    color: var(--secondary-color);
    font-size: 0.875rem;
}

/* アラート */
.alert {
    border: none;
    border-radius: 0.5rem;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
    .sensor-card {
        flex-direction: column;
        text-align: center;
    }
    
    .sensor-icon {
        margin-right: 0;
        margin-bottom: 0.5rem;
    }
    
    .sensor-value {
        font-size: 1.25rem;
    }
}

/* アニメーション */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-in-out;
}

/* ステータスバッジ */
.status-badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
}

.status-normal {
    background-color: var(--success-color);
    color: white;
}

.status-warning {
    background-color: var(--warning-color);
    color: black;
}

.status-danger {
    background-color: var(--danger-color);
    color: white;
}

/* ローディング */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ダークモード対応 */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #212529;
        color: #f8f9fa;
    }
    
    .card {
        background-color: #343a40;
        border-color: #495057;
    }
    
    .sensor-card {
        background-color: #343a40;
        border-color: #495057;
    }
    
    .table {
        color: #f8f9fa;
    }
    
    .table th {
        color: #adb5bd;
    }
}
```

### 📄 src/web/static/js/main.js
メインJavaScript

```javascript
// グローバル変数
let socket;
let sensorChart;
let isConnected = false;

// DOM読み込み完了後に実行
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    initializeEventListeners();
    startDataRefresh();
});

// WebSocket初期化
function initializeWebSocket() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            isConnected = true;
            updateConnectionStatus(true);
            console.log('WebSocket接続が確立されました');
        });
        
        socket.on('disconnect', function() {
            isConnected = false;
            updateConnectionStatus(false);
            console.log('WebSocket接続が切断されました');
        });
        
        socket.on('sensor_data', function(data) {
            updateSensorDisplay(data);
        });
        
        socket.on('watering_status', function(data) {
            updateWateringStatus(data);
        });
        
    } catch (error) {
        console.error('WebSocket初期化エラー:', error);
        updateConnectionStatus(false);
    }
}

// イベントリスナー初期化
function initializeEventListeners() {
    // データ更新ボタン
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }
    
    // 手動給水ボタン
    const wateringBtn = document.getElementById('watering-btn');
    if (wateringBtn) {
        wateringBtn.addEventListener('click', manualWatering);
    }
    
    // 写真撮影ボタン
    const photoBtn = document.getElementById('photo-btn');
    if (photoBtn) {
        photoBtn.addEventListener('click', capturePhoto);
    }
}

// データ更新開始
function startDataRefresh() {
    // 初回データ取得
    refreshData();
    
    // 30秒ごとにデータ更新
    setInterval(refreshData, 30000);
}

// センサーデータ取得
async function refreshData() {
    try {
        showLoading(true);
        
        // センサーデータを取得
        const sensorResponse = await fetch('/api/sensors/');
        const sensorData = await sensorResponse.json();
        
        if (sensorData.status === 'success') {
            updateSensorDisplay(sensorData.data);
        }
        
        // 給水履歴を取得
        await loadWateringHistory();
        
        // システムステータスを更新
        updateSystemStatus();
        
    } catch (error) {
        console.error('データ更新エラー:', error);
        showAlert('データの更新に失敗しました', 'danger');
    } finally {
        showLoading(false);
    }
}

// センサー表示更新
function updateSensorDisplay(data) {
    // 温度
    updateSensorValue('temperature', data.temperature, '°C');
    
    // 湿度
    updateSensorValue('humidity', data.humidity, '%');
    
    // 土壌水分
    updateSensorValue('soil-moisture', data.soil_moisture, '');
    
    // 水の残量
    updateSensorValue('water-volume', data.water_volume, 'ml');
    updateSensorValue('water-percentage', data.water_percentage, '%');
    
    // 水の残量プログレスバー
    updateWaterProgress(data.water_percentage);
    
    // 最終更新時刻
    updateLastUpdateTime();
}

// センサー値更新
function updateSensorValue(elementId, value, unit) {
    const element = document.getElementById(elementId);
    if (element) {
        if (value !== null && value !== undefined) {
            element.textContent = value.toFixed(1);
            element.parentElement.classList.add('fade-in');
            
            // アニメーション後にクラスを削除
            setTimeout(() => {
                element.parentElement.classList.remove('fade-in');
            }, 500);
        } else {
            element.textContent = '-';
        }
    }
}

// 水の残量プログレスバー更新
function updateWaterProgress(percentage) {
    const progressBar = document.getElementById('water-progress');
    if (progressBar && percentage !== null) {
        progressBar.style.width = percentage + '%';
        
        // 色を変更
        progressBar.className = 'progress-bar';
        if (percentage > 50) {
            progressBar.classList.add('bg-success');
        } else if (percentage > 20) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-danger');
        }
    }
}

// 手動給水実行
async function manualWatering() {
    try {
        const duration = prompt('給水時間（秒）を入力してください:', '5');
        if (!duration || isNaN(duration)) {
            return;
        }
        
        showLoading(true);
        
        const response = await fetch('/api/watering/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                duration: parseInt(duration)
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('給水が完了しました', 'success');
            await loadWateringHistory(); // 履歴を更新
        } else {
            showAlert('給水に失敗しました: ' + result.message, 'danger');
        }
        
    } catch (error) {
        console.error('給水エラー:', error);
        showAlert('給水の実行に失敗しました', 'danger');
    } finally {
        showLoading(false);
    }
}

// 写真撮影
async function capturePhoto() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/camera/capture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                save: true
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('写真を撮影しました', 'success');
        } else {
            showAlert('写真撮影に失敗しました: ' + result.message, 'danger');
        }
        
    } catch (error) {
        console.error('写真撮影エラー:', error);
        showAlert('写真撮影に失敗しました', 'danger');
    } finally {
        showLoading(false);
    }
}

// 給水履歴読み込み
async function loadWateringHistory() {
    try {
        const response = await fetch('/api/watering/history?days=7');
        const result = await response.json();
        
        if (result.status === 'success') {
            updateWateringHistoryTable(result.data);
        }
        
    } catch (error) {
        console.error('給水履歴読み込みエラー:', error);
    }
}

// 給水履歴テーブル更新
function updateWateringHistoryTable(history) {
    const tbody = document.getElementById('watering-history');
    if (!tbody) return;
    
    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">給水履歴がありません</td></tr>';
        return;
    }
    
    tbody.innerHTML = history.map(record => `
        <tr>
            <td>${formatDateTime(record.timestamp)}</td>
            <td>
                <span class="badge ${record.manual ? 'bg-warning' : 'bg-info'}">
                    ${record.manual ? '手動' : '自動'}
                </span>
            </td>
            <td>${record.duration}秒</td>
            <td>${record.soil_moisture_before || '-'}</td>
            <td>${record.soil_moisture_after || '-'}</td>
            <td>
                <span class="badge ${record.success ? 'bg-success' : 'bg-danger'}">
                    ${record.success ? '成功' : '失敗'}
                </span>
            </td>
        </tr>
    `).join('');
}

// システムステータス更新
function updateSystemStatus() {
    const statusElement = document.getElementById('system-status');
    if (statusElement) {
        statusElement.textContent = isConnected ? '稼働中' : '接続エラー';
        statusElement.className = `badge ${isConnected ? 'bg-success' : 'bg-danger'}`;
    }
}

// 接続ステータス更新
function updateConnectionStatus(connected) {
    isConnected = connected;
    updateSystemStatus();
    
    // 接続状態に応じてUIを更新
    const elements = document.querySelectorAll('[data-requires-connection]');
    elements.forEach(element => {
        element.disabled = !connected;
    });
}

// 最終更新時刻更新
function updateLastUpdateTime() {
    const element = document.getElementById('last-update');
    if (element) {
        element.textContent = new Date().toLocaleString();
    }
}

// ローディング表示
function showLoading(show) {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(element => {
        element.style.display = show ? 'inline-block' : 'none';
    });
}

// アラート表示
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alertId = 'alert-' + Date.now();
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // 5秒後に自動で削除
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// アラートコンテナ作成
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// 日時フォーマット
function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('ja-JP');
}

// 緊急停止
async function emergencyStop() {
    if (!confirm('緊急停止を実行しますか？')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/watering/stop', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert('緊急停止を実行しました', 'warning');
        } else {
            showAlert('緊急停止に失敗しました: ' + result.message, 'danger');
        }
        
    } catch (error) {
        console.error('緊急停止エラー:', error);
        showAlert('緊急停止に失敗しました', 'danger');
    } finally {
        showLoading(false);
    }
}
```

### 📄 src/web/static/js/dashboard.js
ダッシュボード専用JavaScript

```javascript
// チャート初期化
function initializeChart() {
    const ctx = document.getElementById('sensorChart');
    if (!ctx) return;
    
    sensorChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: '温度 (°C)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                },
                {
                    label: '湿度 (%)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1
                },
                {
                    label: '土壌水分',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

// チャートデータ更新
function updateChart(data) {
    if (!sensorChart) return;
    
    const now = new Date().toLocaleTimeString();
    
    // データを追加
    sensorChart.data.labels.push(now);
    sensorChart.data.datasets[0].data.push(data.temperature);
    sensorChart.data.datasets[1].data.push(data.humidity);
    sensorChart.data.datasets[2].data.push(data.soil_moisture);
    
    // 最大20個のデータポイントを保持
    if (sensorChart.data.labels.length > 20) {
        sensorChart.data.labels.shift();
        sensorChart.data.datasets.forEach(dataset => {
            dataset.data.shift();
        });
    }
    
    sensorChart.update();
}

// ダッシュボード初期化
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    
    // チャート更新をメインのデータ更新に統合
    const originalUpdateSensorDisplay = window.updateSensorDisplay;
    window.updateSensorDisplay = function(data) {
        originalUpdateSensorDisplay(data);
        updateChart(data);
    };
});
```

## 🧪 テスト方法

### 1. テンプレートテスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# Flaskアプリケーション起動
python main.py

# ブラウザでアクセス
# http://localhost:5000
```

### 2. レスポンシブテスト
- デスクトップブラウザで表示確認
- モバイルブラウザで表示確認
- タブレットブラウザで表示確認

### 3. 機能テスト
- センサーデータの表示確認
- 手動給水ボタンの動作確認
- 写真撮影ボタンの動作確認
- データ更新ボタンの動作確認

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

