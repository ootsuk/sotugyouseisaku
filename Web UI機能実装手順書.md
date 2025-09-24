# Web UI機能 詳細実装手順書
## すくすくミントちゃん - Webユーザーインターフェース

---

## 📋 概要
スマートプランターのWebダッシュボード、成長記録、AI園芸アドバイザーの実装手順書

## 🎯 実装目標
- リアルタイムセンサーデータ表示
- 植物の成長記録とタイムラプス
- AI園芸アドバイザー機能
- レスポンシブデザイン対応
- 手動操作機能（撮影、給水）

---

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

## 🔧 実装手順

### Step 1: Flask Webアプリケーション構造

#### 1.1 プロジェクト構造
```
src/
├── app.py                 # メインアプリケーション
├── api/
│   ├── __init__.py
│   ├── sensor_api.py      # センサーAPI
│   ├── watering_api.py    # 給水API
│   └── camera_api.py      # カメラAPI
├── templates/
│   ├── base.html         # ベーステンプレート
│   ├── dashboard.html    # ダッシュボード
│   ├── history.html      # 成長記録
│   └── advisor.html      # AI園芸アドバイザー
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── history.js
│   │   └── advisor.js
│   └── images/
└── utils/
    ├── __init__.py
    └── helpers.py
```

#### 1.2 メインアプリケーション
```python
# src/app.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import threading
import time

# 既存システムのインポート
from sensors.sensor_manager import SensorManager
from watering.auto_watering_manager import AutoWateringManager
from notifications.line_notify import LineNotify
from camera.camera_controller import CameraController

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-planter-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# グローバル変数
sensor_manager = None
auto_watering_manager = None
line_notify = None
camera_controller = None

def init_systems():
    """システム初期化"""
    global sensor_manager, auto_watering_manager, line_notify, camera_controller
    
    # システム初期化
    sensor_manager = SensorManager()
    line_notify = LineNotify()
    auto_watering_manager = AutoWateringManager(sensor_manager, line_notify)
    camera_controller = CameraController()
    
    # センサー監視開始
    sensor_manager.start_monitoring()
    
    # 自動給水開始
    auto_watering_manager.start_auto_watering()
    
    print("🌱 すくすくミントちゃんシステム起動完了")

@app.route('/')
def dashboard():
    """ダッシュボード"""
    return render_template('dashboard.html')

@app.route('/history')
def history():
    """成長記録"""
    return render_template('history.html')

@app.route('/advisor')
def advisor():
    """AI園芸アドバイザー"""
    return render_template('advisor.html')

@socketio.on('connect')
def handle_connect():
    """WebSocket接続"""
    print('クライアント接続')
    emit('status', {'message': '接続完了'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket切断"""
    print('クライアント切断')

def send_sensor_data():
    """センサーデータをWebSocketで送信"""
    while True:
        try:
            if sensor_manager:
                data = sensor_manager.get_latest_data()
                socketio.emit('sensor_data', data)
            time.sleep(5)  # 5秒間隔
        except Exception as e:
            print(f"センサーデータ送信エラー: {e}")
            time.sleep(10)

if __name__ == '__main__':
    # システム初期化
    init_systems()
    
    # センサーデータ送信スレッド開始
    data_thread = threading.Thread(target=send_sensor_data, daemon=True)
    data_thread.start()
    
    print("🌱 すくすくミントちゃん起動中...")
    print("🌐 Web UI: http://192.168.1.100:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

### Step 2: HTMLテンプレート実装

#### 2.1 ベーステンプレート
```html
<!-- templates/base.html -->
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
    <!-- カスタムCSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    <!-- ナビゲーションバー -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">
        <div class="container">
            <a class="navbar-brand" href="/">
                🌱 すくすくミントちゃん
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">ダッシュボード</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/history">成長記録</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/advisor">AI園芸アドバイザー</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- メインコンテンツ -->
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- カスタムJS -->
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

#### 2.2 ダッシュボード
```html
<!-- templates/dashboard.html -->
{% extends "base.html" %}

{% block title %}ダッシュボード - すくすくミントちゃん{% endblock %}

{% block content %}
<div class="row">
    <!-- センサーデータ表示 -->
    <div class="col-lg-8">
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="card-title mb-0">🌡️ 現在の状態</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <div class="text-center">
                            <div class="display-6 text-primary" id="temperature">--</div>
                            <div class="text-muted">温度 (°C)</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <div class="display-6 text-info" id="humidity">--</div>
                            <div class="text-muted">湿度 (%)</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <div class="display-6 text-success" id="soil-moisture">--</div>
                            <div class="text-muted">土壌水分 (%)</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <div class="display-6" id="water-level">--</div>
                            <div class="text-muted">水位</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 最新画像 -->
        <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0">📸 最新の画像</h5>
                <button class="btn btn-primary btn-sm" onclick="takePhoto()">
                    📷 撮影
                </button>
            </div>
            <div class="card-body text-center">
                <img id="latest-image" src="/api/camera/latest" 
                     class="img-fluid rounded" style="max-height: 400px;"
                     onerror="this.src='/static/images/placeholder.jpg'">
                <div class="mt-2 text-muted" id="image-timestamp">--</div>
            </div>
        </div>
    </div>

    <!-- 操作パネル -->
    <div class="col-lg-4">
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="card-title mb-0">🎮 操作</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <button class="btn btn-success" onclick="manualWatering()">
                        💧 手動給水
                    </button>
                    <button class="btn btn-warning" onclick="emergencyStop()">
                        🛑 緊急停止
                    </button>
                    <button class="btn btn-info" onclick="refreshData()">
                        🔄 データ更新
                    </button>
                </div>
            </div>
        </div>

        <!-- 給水設定 -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="card-title mb-0">⚙️ 給水設定</h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <label class="form-label">土壌水分閾値</label>
                    <input type="number" class="form-control" id="moisture-threshold" value="159">
                </div>
                <div class="mb-3">
                    <label class="form-label">給水間隔 (時間)</label>
                    <input type="number" class="form-control" id="watering-interval" value="12">
                </div>
                <button class="btn btn-primary w-100" onclick="updateSettings()">
                    設定更新
                </button>
            </div>
        </div>

        <!-- システム状態 -->
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">📊 システム状態</h5>
            </div>
            <div class="card-body">
                <div class="mb-2">
                    <span class="badge bg-success" id="sensor-status">センサー: 正常</span>
                </div>
                <div class="mb-2">
                    <span class="badge bg-info" id="watering-status">給水: 待機中</span>
                </div>
                <div class="mb-2">
                    <span class="badge bg-primary" id="connection-status">接続: オンライン</span>
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

### Step 3: JavaScript実装

#### 3.1 ダッシュボードJavaScript
```javascript
// static/js/dashboard.js
class Dashboard {
    constructor() {
        this.socket = io();
        this.init();
    }

    init() {
        this.setupSocketListeners();
        this.loadInitialData();
        this.startPeriodicUpdates();
    }

    setupSocketListeners() {
        // センサーデータ受信
        this.socket.on('sensor_data', (data) => {
            this.updateSensorDisplay(data);
        });

        // 接続状態
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
        });
    }

    updateSensorDisplay(data) {
        // 温湿度データ
        if (data.temperature_humidity && !data.temperature_humidity.error) {
            document.getElementById('temperature').textContent = 
                data.temperature_humidity.temperature;
            document.getElementById('humidity').textContent = 
                data.temperature_humidity.humidity;
        }

        // 土壌水分データ
        if (data.soil_moisture && !data.soil_moisture.error) {
            document.getElementById('soil-moisture').textContent = 
                data.soil_moisture.moisture_percentage;
        }

        // 水位データ
        if (data.water_level && !data.water_level.error) {
            const waterLevel = data.water_level.is_water_available ? '💧 満水' : '🚨 空';
            document.getElementById('water-level').innerHTML = waterLevel;
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (connected) {
            statusElement.textContent = '接続: オンライン';
            statusElement.className = 'badge bg-success';
        } else {
            statusElement.textContent = '接続: オフライン';
            statusElement.className = 'badge bg-danger';
        }
    }

    async loadInitialData() {
        try {
            // 給水設定読み込み
            const settingsResponse = await fetch('/api/watering/settings');
            const settings = await settingsResponse.json();
            
            document.getElementById('moisture-threshold').value = settings.soil_moisture_threshold;
            document.getElementById('watering-interval').value = settings.watering_interval_hours;

            // システム状態読み込み
            const statusResponse = await fetch('/api/watering/status');
            const status = await statusResponse.json();
            
            this.updateSystemStatus(status);
        } catch (error) {
            console.error('初期データ読み込みエラー:', error);
        }
    }

    updateSystemStatus(status) {
        // センサー状態
        const sensorStatus = document.getElementById('sensor-status');
        if (status.watering_controller_status) {
            sensorStatus.textContent = 'センサー: 正常';
            sensorStatus.className = 'badge bg-success';
        }

        // 給水状態
        const wateringStatus = document.getElementById('watering-status');
        if (status.auto_watering_running) {
            wateringStatus.textContent = '給水: 自動実行中';
            wateringStatus.className = 'badge bg-info';
        } else {
            wateringStatus.textContent = '給水: 待機中';
            wateringStatus.className = 'badge bg-secondary';
        }
    }

    startPeriodicUpdates() {
        // 5秒間隔でデータ更新
        setInterval(() => {
            this.refreshData();
        }, 5000);
    }

    async refreshData() {
        try {
            const response = await fetch('/api/sensors/latest');
            const data = await response.json();
            this.updateSensorDisplay(data);
        } catch (error) {
            console.error('データ更新エラー:', error);
        }
    }

    async manualWatering() {
        try {
            const response = await fetch('/api/watering/manual', {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('給水完了', 'success');
            } else {
                this.showAlert(`給水失敗: ${result.message}`, 'danger');
            }
        } catch (error) {
            this.showAlert('給水エラー', 'danger');
        }
    }

    async emergencyStop() {
        if (confirm('緊急停止を実行しますか？')) {
            try {
                const response = await fetch('/api/watering/emergency_stop', {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.success) {
                    this.showAlert('緊急停止完了', 'warning');
                } else {
                    this.showAlert(`停止失敗: ${result.message}`, 'danger');
                }
            } catch (error) {
                this.showAlert('停止エラー', 'danger');
            }
        }
    }

    async takePhoto() {
        try {
            const response = await fetch('/api/camera/capture', {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                // 画像更新
                const img = document.getElementById('latest-image');
                img.src = `/api/camera/latest?t=${Date.now()}`;
                this.showAlert('撮影完了', 'success');
            } else {
                this.showAlert(`撮影失敗: ${result.message}`, 'danger');
            }
        } catch (error) {
            this.showAlert('撮影エラー', 'danger');
        }
    }

    async updateSettings() {
        const settings = {
            soil_moisture_threshold: parseInt(document.getElementById('moisture-threshold').value),
            watering_interval_hours: parseInt(document.getElementById('watering-interval').value)
        };

        try {
            const response = await fetch('/api/watering/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('設定更新完了', 'success');
            } else {
                this.showAlert(`設定更新失敗: ${result.message}`, 'danger');
            }
        } catch (error) {
            this.showAlert('設定更新エラー', 'danger');
        }
    }

    showAlert(message, type) {
        // Bootstrap アラート表示
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.insertBefore(alertDiv, document.body.firstChild);
        
        // 3秒後に自動削除
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 3000);
    }
}

// グローバル関数
function manualWatering() {
    dashboard.manualWatering();
}

function emergencyStop() {
    dashboard.emergencyStop();
}

function takePhoto() {
    dashboard.takePhoto();
}

function refreshData() {
    dashboard.refreshData();
}

function updateSettings() {
    dashboard.updateSettings();
}

// ダッシュボード初期化
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new Dashboard();
});
```

### Step 4: API実装

#### 4.1 センサーAPI
```python
# src/api/sensor_api.py
from flask import Blueprint, jsonify
import logging

sensor_bp = Blueprint('sensor', __name__)
logger = logging.getLogger("sensor_api")

@sensor_bp.route('/sensors/latest', methods=['GET'])
def get_latest_sensor_data():
    """最新のセンサーデータ取得"""
    try:
        from ..app import sensor_manager
        if not sensor_manager:
            return jsonify({'error': 'センサーマネージャーが初期化されていません'}), 500
        
        data = sensor_manager.get_latest_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"センサーデータ取得エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/sensors/status', methods=['GET'])
def get_sensor_status():
    """センサー状態取得"""
    try:
        from ..app import sensor_manager
        if not sensor_manager:
            return jsonify({'error': 'センサーマネージャーが初期化されていません'}), 500
        
        status = sensor_manager.get_sensor_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"センサー状態取得エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

### Step 5: CSS実装

#### 5.1 カスタムスタイル
```css
/* static/css/style.css */
:root {
    --primary-color: #28a745;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --info-color: #17a2b8;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
}

body {
    background-color: #f8f9fa;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.navbar-brand {
    font-weight: bold;
    font-size: 1.5rem;
}

.card {
    border: none;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border-radius: 0.5rem;
}

.card-header {
    background-color: #fff;
    border-bottom: 1px solid #dee2e6;
    font-weight: 600;
}

.display-6 {
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.btn {
    border-radius: 0.375rem;
    font-weight: 500;
}

.badge {
    font-size: 0.875rem;
}

/* センサーデータ表示 */
.sensor-value {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.sensor-label {
    color: #6c757d;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* 画像表示 */
.plant-image {
    max-height: 400px;
    border-radius: 0.5rem;
    box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1);
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
    .display-6 {
        font-size: 1.5rem;
    }
    
    .card-body {
        padding: 1rem;
    }
    
    .btn {
        font-size: 0.875rem;
    }
}

/* アニメーション */
.fade-in {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ステータス表示 */
.status-online {
    color: var(--success-color);
}

.status-offline {
    color: var(--danger-color);
}

.status-warning {
    color: var(--warning-color);
}
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

---

## 🎯 次のステップ

1. **成長記録画面実装**: グラフ表示とタイムラプス
2. **AI園芸アドバイザー実装**: LLM連携
3. **カメラ機能実装**: 撮影と画像管理
4. **統合テスト**: 全機能の動作確認

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

