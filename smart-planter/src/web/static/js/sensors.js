/**
 * センサーデータ管理モジュール
 * すくすくミントちゃん - スマートプランターシステム
 * 
 * 機能:
 * - センサーデータの取得と管理
 * - データのキャッシング
 * - リアルタイム更新
 * - 異常値の検出
 * - センサーステータスの監視
 */

// センサー管理クラス
class SensorManager {
    constructor() {
        // センサーデータのキャッシュ
        this.sensorData = {
            temperature: null,
            humidity: null,
            soilMoisture: null,
            waterVolume: null,
            waterPercentage: null,
            pressure: null,
            timestamp: null
        };
        
        // センサーステータス
        this.sensorStatus = {
            temperature_humidity: 'unknown',  // unknown, ok, warning, error
            soil_moisture: 'unknown',
            water_level: 'unknown',
            pressure: 'unknown'
        };
        
        // 設定値
        this.config = {
            updateInterval: 30000,  // 30秒
            maxRetries: 3,
            timeout: 5000,
            
            // アラート閾値
            temperatureMin: 5,
            temperatureMax: 35,
            humidityMin: 30,
            humidityMax: 80,
            soilMoistureThreshold: 159,
            waterLevelMin: 20  // パーセント
        };
        
        // データ履歴（最大100件）
        this.history = {
            temperature: [],
            humidity: [],
            soilMoisture: [],
            timestamps: []
        };
        
        this.maxHistoryLength = 100;
        
        // 更新タイマー
        this.updateTimer = null;
        
        // イベントリスナー
        this.listeners = {
            dataUpdate: [],
            statusChange: [],
            alert: []
        };
    }
    
    /**
     * センサーマネージャーを初期化
     */
    async initialize() {
        console.log('センサーマネージャーを初期化中...');
        
        try {
            // 初回データ取得
            await this.fetchSensorData();
            
            // 自動更新を開始
            this.startAutoUpdate();
            
            console.log('センサーマネージャーの初期化完了');
            return true;
        } catch (error) {
            console.error('センサーマネージャーの初期化エラー:', error);
            return false;
        }
    }
    
    /**
     * センサーデータを取得
     */
    async fetchSensorData() {
        try {
            const response = await fetch('/api/sensors/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                timeout: this.config.timeout
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'success' && result.data) {
                this.updateSensorData(result.data);
                return result.data;
            } else {
                throw new Error(result.message || 'データの取得に失敗しました');
            }
        } catch (error) {
            console.error('センサーデータ取得エラー:', error);
            this.handleSensorError('fetch', error);
            throw error;
        }
    }
    
    /**
     * センサーデータを更新
     */
    updateSensorData(data) {
        // データを更新
        this.sensorData = {
            temperature: data.temperature ?? null,
            humidity: data.humidity ?? null,
            soilMoisture: data.soil_moisture ?? null,
            waterVolume: data.water_volume ?? null,
            waterPercentage: data.water_percentage ?? null,
            pressure: data.pressure ?? null,
            timestamp: data.timestamp || new Date().toISOString()
        };
        
        // 履歴に追加
        this.addToHistory(this.sensorData);
        
        // ステータスをチェック
        this.checkSensorStatus();
        
        // アラートをチェック
        this.checkAlerts();
        
        // リスナーに通知
        this.notifyListeners('dataUpdate', this.sensorData);
    }
    
    /**
     * データを履歴に追加
     */
    addToHistory(data) {
        if (data.temperature !== null) {
            this.history.temperature.push(data.temperature);
        }
        if (data.humidity !== null) {
            this.history.humidity.push(data.humidity);
        }
        if (data.soilMoisture !== null) {
            this.history.soilMoisture.push(data.soilMoisture);
        }
        this.history.timestamps.push(data.timestamp);
        
        // 最大長を超えたら古いデータを削除
        if (this.history.temperature.length > this.maxHistoryLength) {
            this.history.temperature.shift();
            this.history.humidity.shift();
            this.history.soilMoisture.shift();
            this.history.timestamps.shift();
        }
    }
    
    /**
     * センサーステータスをチェック
     */
    checkSensorStatus() {
        const data = this.sensorData;
        const oldStatus = {...this.sensorStatus};
        
        // 温湿度センサー
        if (data.temperature !== null && data.humidity !== null) {
            this.sensorStatus.temperature_humidity = 'ok';
        } else {
            this.sensorStatus.temperature_humidity = 'error';
        }
        
        // 土壌水分センサー
        if (data.soilMoisture !== null) {
            if (data.soilMoisture <= this.config.soilMoistureThreshold) {
                this.sensorStatus.soil_moisture = 'warning';
            } else {
                this.sensorStatus.soil_moisture = 'ok';
            }
        } else {
            this.sensorStatus.soil_moisture = 'error';
        }
        
        // 水位センサー
        if (data.waterPercentage !== null) {
            if (data.waterPercentage <= this.config.waterLevelMin) {
                this.sensorStatus.water_level = 'warning';
            } else {
                this.sensorStatus.water_level = 'ok';
            }
        } else {
            this.sensorStatus.water_level = 'error';
        }
        
        // 圧力センサー
        if (data.pressure !== null) {
            this.sensorStatus.pressure = 'ok';
        } else {
            this.sensorStatus.pressure = 'unknown';
        }
        
        // ステータスが変更された場合は通知
        if (JSON.stringify(oldStatus) !== JSON.stringify(this.sensorStatus)) {
            this.notifyListeners('statusChange', this.sensorStatus);
        }
    }
    
    /**
     * アラートをチェック
     */
    checkAlerts() {
        const data = this.sensorData;
        const alerts = [];
        
        // 温度アラート
        if (data.temperature !== null) {
            if (data.temperature < this.config.temperatureMin) {
                alerts.push({
                    type: 'temperature',
                    severity: 'warning',
                    message: `温度が低すぎます: ${data.temperature.toFixed(1)}°C`
                });
            } else if (data.temperature > this.config.temperatureMax) {
                alerts.push({
                    type: 'temperature',
                    severity: 'warning',
                    message: `温度が高すぎます: ${data.temperature.toFixed(1)}°C`
                });
            }
        }
        
        // 湿度アラート
        if (data.humidity !== null) {
            if (data.humidity < this.config.humidityMin) {
                alerts.push({
                    type: 'humidity',
                    severity: 'warning',
                    message: `湿度が低すぎます: ${data.humidity.toFixed(1)}%`
                });
            } else if (data.humidity > this.config.humidityMax) {
                alerts.push({
                    type: 'humidity',
                    severity: 'warning',
                    message: `湿度が高すぎます: ${data.humidity.toFixed(1)}%`
                });
            }
        }
        
        // 土壌水分アラート
        if (data.soilMoisture !== null && data.soilMoisture <= this.config.soilMoistureThreshold) {
            alerts.push({
                type: 'soil_moisture',
                severity: 'info',
                message: `土壌水分が低下しています: ${data.soilMoisture}`
            });
        }
        
        // 水位アラート
        if (data.waterPercentage !== null && data.waterPercentage <= this.config.waterLevelMin) {
            alerts.push({
                type: 'water_level',
                severity: 'warning',
                message: `水の残量が少なくなっています: ${data.waterPercentage.toFixed(0)}%`
            });
        }
        
        // アラートを通知
        alerts.forEach(alert => {
            this.notifyListeners('alert', alert);
        });
    }
    
    /**
     * センサーエラーを処理
     */
    handleSensorError(sensorType, error) {
        console.error(`センサーエラー [${sensorType}]:`, error);
        
        // ステータスを更新
        if (sensorType === 'temperature_humidity') {
            this.sensorStatus.temperature_humidity = 'error';
        } else if (sensorType === 'soil_moisture') {
            this.sensorStatus.soil_moisture = 'error';
        } else if (sensorType === 'water_level') {
            this.sensorStatus.water_level = 'error';
        }
        
        // エラーアラートを通知
        this.notifyListeners('alert', {
            type: 'sensor_error',
            severity: 'error',
            message: `センサーエラー: ${error.message}`
        });
    }
    
    /**
     * 自動更新を開始
     */
    startAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }
        
        this.updateTimer = setInterval(async () => {
            try {
                await this.fetchSensorData();
            } catch (error) {
                console.error('自動更新エラー:', error);
            }
        }, this.config.updateInterval);
        
        console.log(`自動更新を開始しました (${this.config.updateInterval}ms間隔)`);
    }
    
    /**
     * 自動更新を停止
     */
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
            console.log('自動更新を停止しました');
        }
    }
    
    /**
     * イベントリスナーを追加
     */
    addEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }
    
    /**
     * イベントリスナーを削除
     */
    removeEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }
    
    /**
     * リスナーに通知
     */
    notifyListeners(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`リスナーエラー [${event}]:`, error);
                }
            });
        }
    }
    
    /**
     * 現在のセンサーデータを取得
     */
    getCurrentData() {
        return {...this.sensorData};
    }
    
    /**
     * センサーステータスを取得
     */
    getStatus() {
        return {...this.sensorStatus};
    }
    
    /**
     * データ履歴を取得
     */
    getHistory(sensor = null, limit = null) {
        if (sensor && this.history[sensor]) {
            const data = this.history[sensor];
            return limit ? data.slice(-limit) : data;
        }
        
        const history = {...this.history};
        if (limit) {
            Object.keys(history).forEach(key => {
                history[key] = history[key].slice(-limit);
            });
        }
        return history;
    }
    
    /**
     * 設定を更新
     */
    updateConfig(newConfig) {
        this.config = {...this.config, ...newConfig};
        console.log('センサー設定を更新しました:', this.config);
        
        // 更新間隔が変更された場合は自動更新を再起動
        if (newConfig.updateInterval && this.updateTimer) {
            this.startAutoUpdate();
        }
    }
    
    /**
     * 統計情報を取得
     */
    getStatistics(sensor, period = 'all') {
        const data = this.history[sensor];
        if (!data || data.length === 0) {
            return null;
        }
        
        // 期間によるフィルタリング
        let filteredData = data;
        if (period !== 'all') {
            const now = new Date();
            const timestamps = this.history.timestamps;
            
            filteredData = data.filter((value, index) => {
                const timestamp = new Date(timestamps[index]);
                const diff = now - timestamp;
                
                switch (period) {
                    case 'hour':
                        return diff <= 3600000;  // 1時間
                    case 'day':
                        return diff <= 86400000;  // 24時間
                    case 'week':
                        return diff <= 604800000;  // 7日間
                    default:
                        return true;
                }
            });
        }
        
        if (filteredData.length === 0) {
            return null;
        }
        
        // 統計計算
        const sum = filteredData.reduce((a, b) => a + b, 0);
        const avg = sum / filteredData.length;
        const min = Math.min(...filteredData);
        const max = Math.max(...filteredData);
        
        return {
            count: filteredData.length,
            average: avg,
            min: min,
            max: max,
            current: filteredData[filteredData.length - 1]
        };
    }
    
    /**
     * センサーデータをエクスポート
     */
    exportData(format = 'json') {
        const exportData = {
            current: this.sensorData,
            history: this.history,
            status: this.sensorStatus,
            exported_at: new Date().toISOString()
        };
        
        if (format === 'json') {
            return JSON.stringify(exportData, null, 2);
        } else if (format === 'csv') {
            // CSV形式に変換
            let csv = 'Timestamp,Temperature,Humidity,Soil Moisture\n';
            
            for (let i = 0; i < this.history.timestamps.length; i++) {
                csv += `${this.history.timestamps[i]},`;
                csv += `${this.history.temperature[i] ?? ''},`;
                csv += `${this.history.humidity[i] ?? ''},`;
                csv += `${this.history.soilMoisture[i] ?? ''}\n`;
            }
            
            return csv;
        }
        
        return null;
    }
    
    /**
     * センサーをリセット
     */
    reset() {
        this.sensorData = {
            temperature: null,
            humidity: null,
            soilMoisture: null,
            waterVolume: null,
            waterPercentage: null,
            pressure: null,
            timestamp: null
        };
        
        this.sensorStatus = {
            temperature_humidity: 'unknown',
            soil_moisture: 'unknown',
            water_level: 'unknown',
            pressure: 'unknown'
        };
        
        this.history = {
            temperature: [],
            humidity: [],
            soilMoisture: [],
            timestamps: []
        };
        
        console.log('センサーマネージャーをリセットしました');
    }
}

// グローバルインスタンス
let sensorManager = null;

/**
 * センサーマネージャーを取得または初期化
 */
function getSensorManager() {
    if (!sensorManager) {
        sensorManager = new SensorManager();
    }
    return sensorManager;
}

/**
 * センサーデータを取得（簡易版）
 */
async function getSensorData() {
    const manager = getSensorManager();
    try {
        return await manager.fetchSensorData();
    } catch (error) {
        console.error('センサーデータ取得エラー:', error);
        return null;
    }
}

/**
 * 現在のセンサー値を取得（キャッシュから）
 */
function getCurrentSensorData() {
    const manager = getSensorManager();
    return manager.getCurrentData();
}

/**
 * センサーステータスを取得
 */
function getSensorStatus() {
    const manager = getSensorManager();
    return manager.getStatus();
}

// モジュールのエクスポート（ES6モジュールとして使用する場合）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SensorManager,
        getSensorManager,
        getSensorData,
        getCurrentSensorData,
        getSensorStatus
    };
}

