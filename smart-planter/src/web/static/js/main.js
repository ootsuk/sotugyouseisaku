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