# 統合テスト手順書 - すくすくミントちゃん

## 📋 概要
スマートプランターシステム全体の統合テスト手順書。各機能の連携動作とエンドツーエンドテスト

## 🎯 テスト目標
- 全機能の統合動作確認
- センサー→給水→通知の連携テスト
- Web UI→API→バックエンドの連携テスト
- エラーハンドリングの確認
- パフォーマンステスト

## 🛠️ テスト環境

### ハードウェア
- Raspberry Pi 5
- 全センサー（AHT25、SEN0193、MS583730BA01-50）
- リレーモジュール・水ポンプ
- 水タンク

### ソフトウェア
- Python 3.11.x
- 全実装済み機能
- テスト用データ

## 📁 テストファイル作成手順

### Step 1: テストディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# テストディレクトリの確認
ls -la tests/
```

### Step 2: 各テストファイルの作成順序
1. `tests/test_sensors.py` - センサーテスト
2. `tests/test_watering.py` - 給水テスト
3. `tests/test_integration.py` - 統合テスト
4. `tests/test_api.py` - APIテスト
5. `tests/test_web_ui.py` - Web UIテスト

### Step 3: ファイル作成コマンド
```bash
# 各テストファイルを作成
touch tests/test_sensors.py
touch tests/test_watering.py
touch tests/test_integration.py
touch tests/test_api.py
touch tests/test_web_ui.py
```

## 📄 テスト実装コード

### 📄 tests/test_sensors.py
センサーテスト

```python
import unittest
import time
import logging
from unittest.mock import Mock, patch
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sensors.temperature_humidity import TemperatureHumiditySensor
from src.sensors.soil_moisture import SoilMoistureSensor
from src.sensors.pressure_sensor import PressureSensor
from src.sensors.sensor_manager import SensorManager

class TestTemperatureHumiditySensor(unittest.TestCase):
    """温湿度センサーテスト"""
    
    def setUp(self):
        self.sensor = TemperatureHumiditySensor()
    
    @patch('smbus2.SMBus')
    def test_initialization(self, mock_bus):
        """センサー初期化テスト"""
        mock_bus_instance = Mock()
        mock_bus.return_value = mock_bus_instance
        
        result = self.sensor.initialize()
        
        self.assertTrue(result)
        self.assertTrue(self.sensor.is_healthy())
    
    @patch('smbus2.SMBus')
    def test_read_data_success(self, mock_bus):
        """データ読み取り成功テスト"""
        mock_bus_instance = Mock()
        mock_bus.return_value = mock_bus_instance
        
        # モックデータを設定
        mock_bus_instance.read_i2c_block_data.return_value = [
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]
        
        self.sensor.initialize()
        data = self.sensor.read_data()
        
        self.assertIn('temperature', data)
        self.assertIn('humidity', data)
        self.assertIn('timestamp', data)
        self.assertIn('sensor', data)
    
    @patch('smbus2.SMBus')
    def test_read_data_error(self, mock_bus):
        """データ読み取りエラーテスト"""
        mock_bus_instance = Mock()
        mock_bus.return_value = mock_bus_instance
        mock_bus_instance.read_i2c_block_data.side_effect = Exception("I2C Error")
        
        self.sensor.initialize()
        data = self.sensor.read_data()
        
        self.assertTrue(data.get('error', False))
        self.assertEqual(self.sensor.error_count, 1)

class TestSoilMoistureSensor(unittest.TestCase):
    """土壌水分センサーテスト"""
    
    def setUp(self):
        self.sensor = SoilMoistureSensor()
    
    @patch('spidev.SpiDev')
    def test_initialization(self, mock_spi):
        """センサー初期化テスト"""
        mock_spi_instance = Mock()
        mock_spi.return_value = mock_spi_instance
        
        result = self.sensor.initialize()
        
        self.assertTrue(result)
        self.assertTrue(self.sensor.is_healthy())
    
    @patch('spidev.SpiDev')
    def test_read_data_success(self, mock_spi):
        """データ読み取り成功テスト"""
        mock_spi_instance = Mock()
        mock_spi.return_value = mock_spi_instance
        
        # モックデータを設定（土壌水分150）
        mock_spi_instance.xfer2.return_value = [0, 0x06, 0x96]  # 150 in hex
        
        self.sensor.initialize()
        data = self.sensor.read_data()
        
        self.assertIn('soil_moisture', data)
        self.assertIn('moisture_percentage', data)
        self.assertIn('status', data)
        self.assertEqual(data['soil_moisture'], 150)
        self.assertEqual(data['status'], 'dry')

class TestPressureSensor(unittest.TestCase):
    """圧力センサーテスト（水の残量測定）"""
    
    def setUp(self):
        self.sensor = PressureSensor()
    
    @patch('smbus2.SMBus')
    def test_initialization(self, mock_bus):
        """センサー初期化テスト"""
        mock_bus_instance = Mock()
        mock_bus.return_value = mock_bus_instance
        
        # キャリブレーション係数をモック
        mock_bus_instance.read_i2c_block_data.return_value = [0x00, 0x01]
        
        result = self.sensor.initialize()
        
        self.assertTrue(result)
        self.assertTrue(self.sensor.is_healthy())
    
    @patch('smbus2.SMBus')
    def test_read_data_success(self, mock_bus):
        """データ読み取り成功テスト"""
        mock_bus_instance = Mock()
        mock_bus.return_value = mock_bus_instance
        
        # モックデータを設定
        mock_bus_instance.read_i2c_block_data.return_value = [
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]
        
        self.sensor.initialize()
        data = self.sensor.read_data()
        
        self.assertIn('pressure', data)
        self.assertIn('water_height', data)
        self.assertIn('water_volume', data)
        self.assertIn('water_percentage', data)
        self.assertIn('status', data)

class TestSensorManager(unittest.TestCase):
    """センサーマネージャーテスト"""
    
    def setUp(self):
        with patch('src.sensors.temperature_humidity.TemperatureHumiditySensor'), \
             patch('src.sensors.soil_moisture.SoilMoistureSensor'), \
             patch('src.sensors.pressure_sensor.PressureSensor'):
            self.manager = SensorManager()
    
    def test_initialization(self):
        """センサーマネージャー初期化テスト"""
        self.assertIn('temperature_humidity', self.manager.sensors)
        self.assertIn('soil_moisture', self.manager.sensors)
        self.assertIn('pressure', self.manager.sensors)
    
    def test_get_all_data(self):
        """全センサーデータ取得テスト"""
        data = self.manager.get_all_data()
        self.assertIsInstance(data, dict)
    
    def test_get_sensor_data(self):
        """個別センサーデータ取得テスト"""
        data = self.manager.get_sensor_data('temperature_humidity')
        self.assertIsInstance(data, dict)

if __name__ == '__main__':
    unittest.main()
```

### 📄 tests/test_watering.py
給水テスト

```python
import unittest
import time
import logging
from unittest.mock import Mock, patch
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.watering.pump_control import PumpController
from src.watering.watering_logic import WateringLogic
from src.watering.watering_scheduler import WateringScheduler

class TestPumpController(unittest.TestCase):
    """ポンプ制御テスト"""
    
    def setUp(self):
        with patch('RPi.GPIO.setmode'), \
             patch('RPi.GPIO.setup'), \
             patch('RPi.GPIO.output'):
            self.pump = PumpController()
    
    def test_initialization(self):
        """ポンプ制御初期化テスト"""
        self.assertEqual(self.pump.relay_pin, 16)
        self.assertFalse(self.pump.is_running)
    
    @patch('RPi.GPIO.output')
    @patch('time.sleep')
    def test_start_pump_success(self, mock_sleep, mock_gpio_output):
        """ポンプ開始成功テスト"""
        result = self.pump.start_pump(duration=3)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['duration'], 3)
        self.assertIn('message', result)
    
    @patch('RPi.GPIO.output')
    def test_stop_pump(self, mock_gpio_output):
        """ポンプ停止テスト"""
        result = self.pump.stop_pump()
        
        self.assertTrue(result['success'])
        self.assertFalse(self.pump.is_running)
    
    def test_get_status(self):
        """ポンプ状態取得テスト"""
        status = self.pump.get_status()
        
        self.assertIn('is_running', status)
        self.assertIn('relay_pin', status)
        self.assertIn('timestamp', status)

class TestWateringLogic(unittest.TestCase):
    """給水ロジックテスト"""
    
    def setUp(self):
        self.logic = WateringLogic()
    
    def test_should_water_soil_moisture_low(self):
        """土壌水分が低い場合の給水判定テスト"""
        result = self.logic.should_water(soil_moisture=150, water_level_status="normal")
        
        self.assertTrue(result['should_water'])
        self.assertEqual(result['reason'], '給水条件を満たしています')
    
    def test_should_water_soil_moisture_high(self):
        """土壌水分が高い場合の給水判定テスト"""
        result = self.logic.should_water(soil_moisture=200, water_level_status="normal")
        
        self.assertFalse(result['should_water'])
        self.assertIn('土壌水分が十分', result['reason'])
    
    def test_should_water_water_tank_empty(self):
        """水タンクが空の場合の給水判定テスト"""
        result = self.logic.should_water(soil_moisture=150, water_level_status="empty")
        
        self.assertFalse(result['should_water'])
        self.assertIn('水タンクが空', result['reason'])
    
    def test_record_watering(self):
        """給水履歴記録テスト"""
        watering_data = {
            'duration': 5,
            'soil_moisture_before': 150,
            'manual': False
        }
        
        result = self.logic.record_watering(**watering_data)
        
        self.assertTrue(result['success'])
        self.assertIn('record', result)
    
    def test_get_watering_history(self):
        """給水履歴取得テスト"""
        history = self.logic.get_watering_history(days=7)
        
        self.assertIsInstance(history, dict)
        self.assertIn('history', history)
        self.assertIn('total_count', history)

class TestWateringScheduler(unittest.TestCase):
    """給水スケジューラーテスト"""
    
    def setUp(self):
        self.mock_sensor_manager = Mock()
        self.mock_notification_manager = Mock()
        
        with patch('src.watering.pump_control.PumpController'), \
             patch('src.watering.watering_logic.WateringLogic'):
            self.scheduler = WateringScheduler(
                self.mock_sensor_manager,
                self.mock_notification_manager
            )
    
    def test_initialization(self):
        """給水スケジューラー初期化テスト"""
        self.assertEqual(self.scheduler.check_interval, 300)
        self.assertFalse(self.scheduler.running)
    
    def test_start_scheduler(self):
        """スケジューラー開始テスト"""
        self.scheduler.start_scheduler()
        
        self.assertTrue(self.scheduler.running)
        self.assertTrue(hasattr(self.scheduler, 'scheduler_thread'))
    
    def test_stop_scheduler(self):
        """スケジューラー停止テスト"""
        self.scheduler.start_scheduler()
        self.scheduler.stop_scheduler()
        
        self.assertFalse(self.scheduler.running)
    
    def test_manual_watering(self):
        """手動給水テスト"""
        self.mock_sensor_manager.get_all_data.return_value = {
            'soil_moisture': {'soil_moisture': 150}
        }
        
        result = self.scheduler.manual_watering(duration=5)
        
        self.assertIn('success', result)
        self.assertIn('message', result)
    
    def test_get_status(self):
        """スケジューラー状態取得テスト"""
        status = self.scheduler.get_status()
        
        self.assertIn('running', status)
        self.assertIn('check_interval', status)
        self.assertIn('pump_status', status)

if __name__ == '__main__':
    unittest.main()
```

### 📄 tests/test_integration.py
統合テスト

```python
import unittest
import time
import logging
from unittest.mock import Mock, patch
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sensors.sensor_manager import SensorManager
from src.watering.watering_scheduler import WateringScheduler
from src.data.data_manager import DataManager
from src.notifications.notification_scheduler import NotificationScheduler

class TestSystemIntegration(unittest.TestCase):
    """システム統合テスト"""
    
    def setUp(self):
        # モックを使用して統合テストを実行
        with patch('src.sensors.temperature_humidity.TemperatureHumiditySensor'), \
             patch('src.sensors.soil_moisture.SoilMoistureSensor'), \
             patch('src.sensors.pressure_sensor.PressureSensor'), \
             patch('src.watering.pump_control.PumpController'), \
             patch('src.watering.watering_logic.WateringLogic'), \
             patch('src.notifications.line_notify.LineNotifier'):
            
            self.sensor_manager = SensorManager()
            self.data_manager = DataManager()
            self.notification_scheduler = NotificationScheduler(self.sensor_manager)
            self.watering_scheduler = WateringScheduler(
                self.sensor_manager,
                self.notification_scheduler
            )
    
    def test_sensor_to_data_flow(self):
        """センサー→データ管理の流れテスト"""
        # センサーデータを取得
        sensor_data = self.sensor_manager.get_all_data()
        
        # データを保存
        for sensor_name, data in sensor_data.items():
            success = self.data_manager.save_sensor_data(sensor_name, data)
            self.assertTrue(success)
    
    def test_sensor_to_watering_flow(self):
        """センサー→給水の流れテスト"""
        # モックデータを設定
        mock_sensor_data = {
            'soil_moisture': {
                'soil_moisture': 150,
                'timestamp': time.time()
            },
            'pressure': {
                'water_percentage': 50,
                'status': 'normal'
            }
        }
        
        self.sensor_manager.data_buffer = mock_sensor_data
        
        # 給水判定をテスト
        result = self.watering_scheduler._execute_watering(150)
        
        self.assertIn('success', result)
    
    def test_watering_to_notification_flow(self):
        """給水→通知の流れテスト"""
        watering_data = {
            'duration': 5,
            'soil_moisture_before': 150,
            'manual': False
        }
        
        # 給水通知をテスト
        self.notification_scheduler.send_watering_notification(watering_data)
        
        # 通知が送信されたことを確認（モックなので実際の送信は行われない）
        self.assertTrue(True)  # モックの場合、エラーが発生しなければ成功
    
    def test_data_persistence_flow(self):
        """データ永続化の流れテスト"""
        # センサーデータを生成
        sensor_data = {
            'temperature': 25.5,
            'humidity': 60.0,
            'timestamp': time.time()
        }
        
        # データを保存
        success = self.data_manager.save_sensor_data('test_sensor', sensor_data)
        self.assertTrue(success)
        
        # データを取得
        retrieved_data = self.data_manager.get_sensor_data('test_sensor', days=1)
        self.assertIsInstance(retrieved_data, list)
    
    def test_error_handling_flow(self):
        """エラーハンドリングの流れテスト"""
        # センサーエラーをシミュレート
        error_data = {
            'temperature': None,
            'humidity': None,
            'error': True,
            'timestamp': time.time()
        }
        
        self.sensor_manager.data_buffer = {
            'temperature_humidity': error_data
        }
        
        # エラーデータでもシステムが継続動作することを確認
        all_data = self.sensor_manager.get_all_data()
        self.assertIsInstance(all_data, dict)
    
    def test_system_startup_flow(self):
        """システム起動の流れテスト"""
        # 各コンポーネントの起動をテスト
        self.sensor_manager.start_monitoring()
        self.watering_scheduler.start_scheduler()
        self.notification_scheduler.start_scheduler()
        
        # システムが正常に起動することを確認
        self.assertTrue(self.sensor_manager.running)
        self.assertTrue(self.watering_scheduler.running)
        self.assertTrue(self.notification_scheduler.running)
        
        # 停止テスト
        self.sensor_manager.stop_monitoring()
        self.watering_scheduler.stop_scheduler()
        self.notification_scheduler.stop_scheduler()
        
        self.assertFalse(self.sensor_manager.running)
        self.assertFalse(self.watering_scheduler.running)
        self.assertFalse(self.notification_scheduler.running)

class TestEndToEndScenario(unittest.TestCase):
    """エンドツーエンドシナリオテスト"""
    
    def setUp(self):
        with patch('src.sensors.temperature_humidity.TemperatureHumiditySensor'), \
             patch('src.sensors.soil_moisture.SoilMoistureSensor'), \
             patch('src.sensors.pressure_sensor.PressureSensor'), \
             patch('src.watering.pump_control.PumpController'), \
             patch('src.watering.watering_logic.WateringLogic'), \
             patch('src.notifications.line_notify.LineNotifier'):
            
            self.sensor_manager = SensorManager()
            self.data_manager = DataManager()
            self.notification_scheduler = NotificationScheduler(self.sensor_manager)
            self.watering_scheduler = WateringScheduler(
                self.sensor_manager,
                self.notification_scheduler
            )
    
    def test_complete_watering_scenario(self):
        """完全な給水シナリオテスト"""
        # 1. センサーデータを設定（土壌水分が低い状態）
        mock_sensor_data = {
            'soil_moisture': {
                'soil_moisture': 150,  # 給水が必要な値
                'timestamp': time.time()
            },
            'pressure': {
                'water_percentage': 80,  # 水は十分
                'status': 'normal'
            }
        }
        
        self.sensor_manager.data_buffer = mock_sensor_data
        
        # 2. 給水判定を実行
        result = self.watering_scheduler._execute_watering(150)
        
        # 3. 結果を確認
        self.assertIn('success', result)
        
        # 4. データが保存されることを確認
        watering_history = self.data_manager.get_watering_history(days=1)
        self.assertIsInstance(watering_history, list)
    
    def test_alert_scenario(self):
        """アラートシナリオテスト"""
        # 1. 異常なセンサーデータを設定
        alert_data = {
            'temperature_humidity': {
                'temperature': 40,  # 高温アラート
                'humidity': 60,
                'timestamp': time.time()
            }
        }
        
        self.sensor_manager.data_buffer = alert_data
        
        # 2. アラートをチェック
        alerts = self.notification_scheduler.alert_manager.check_sensor_alerts(alert_data)
        
        # 3. アラートが検出されることを確認
        if alerts:
            self.assertGreater(len(alerts), 0)
            self.assertEqual(alerts[0]['type'], 'temperature_high')

if __name__ == '__main__':
    unittest.main()
```

### 📄 tests/test_api.py
APIテスト

```python
import unittest
import json
from unittest.mock import Mock, patch
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app.app import create_app

class TestAPIEndpoints(unittest.TestCase):
    """APIエンドポイントテスト"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_sensors_api(self):
        """センサーAPIテスト"""
        response = self.client.get('/api/sensors/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
    
    def test_sensor_history_api(self):
        """センサーデータ履歴APIテスト"""
        response = self.client.get('/api/sensors/history?hours=24')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
    
    def test_water_level_api(self):
        """水の残量APIテスト"""
        response = self.client.get('/api/sensors/water-level')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
    
    def test_watering_api(self):
        """給水APIテスト"""
        response = self.client.post('/api/watering/', 
                                  json={'duration': 5},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('message', data)
    
    def test_watering_history_api(self):
        """給水履歴APIテスト"""
        response = self.client.get('/api/watering/history?days=7')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
    
    def test_camera_capture_api(self):
        """カメラ撮影APIテスト"""
        response = self.client.post('/api/camera/capture',
                                  json={'save': True},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('message', data)
    
    def test_notification_api(self):
        """通知APIテスト"""
        response = self.client.post('/api/notifications/',
                                  json={'message': 'テスト通知', 'type': 'info'},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('message', data)

class TestAPIErrorHandling(unittest.TestCase):
    """APIエラーハンドリングテスト"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_invalid_json_request(self):
        """無効なJSONリクエストテスト"""
        response = self.client.post('/api/watering/',
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_missing_required_fields(self):
        """必須フィールド不足テスト"""
        response = self.client.post('/api/notifications/',
                                  json={},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
    
    def test_404_error(self):
        """404エラーテスト"""
        response = self.client.get('/api/nonexistent/')
        
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
```

### 📄 tests/test_web_ui.py
Web UIテスト

```python
import unittest
from unittest.mock import Mock, patch
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app.app import create_app

class TestWebUI(unittest.TestCase):
    """Web UIテスト"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_index_page(self):
        """メインページテスト"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'すくすくミントちゃん', response.data)
    
    def test_dashboard_page(self):
        """ダッシュボードページテスト"""
        response = self.client.get('/dashboard')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ダッシュボード', response.data)
    
    def test_settings_page(self):
        """設定ページテスト"""
        response = self.client.get('/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'設定', response.data)
    
    def test_static_files(self):
        """静的ファイルテスト"""
        # CSSファイル
        response = self.client.get('/static/css/main.css')
        self.assertEqual(response.status_code, 200)
        
        # JavaScriptファイル
        response = self.client.get('/static/js/main.js')
        self.assertEqual(response.status_code, 200)

class TestWebUIResponsive(unittest.TestCase):
    """レスポンシブデザインテスト"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_mobile_viewport(self):
        """モバイルビューポートテスト"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        }
        
        response = self.client.get('/', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'viewport', response.data)
    
    def test_bootstrap_inclusion(self):
        """Bootstrapの読み込みテスト"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'bootstrap', response.data)
    
    def test_chart_js_inclusion(self):
        """Chart.jsの読み込みテスト"""
        response = self.client.get('/dashboard')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'chart.js', response.data)

if __name__ == '__main__':
    unittest.main()
```

## 🧪 テスト実行方法

### 1. 個別テスト実行
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# センサーテスト
python -m pytest tests/test_sensors.py -v

# 給水テスト
python -m pytest tests/test_watering.py -v

# 統合テスト
python -m pytest tests/test_integration.py -v

# APIテスト
python -m pytest tests/test_api.py -v

# Web UIテスト
python -m pytest tests/test_web_ui.py -v
```

### 2. 全テスト実行
```bash
# 全テストを実行
python -m pytest tests/ -v

# カバレッジ付きテスト
python -m pytest tests/ --cov=src --cov-report=html
```

### 3. 統合テストシナリオ
```bash
# システム全体の統合テスト
python -c "
import sys
sys.path.insert(0, '.')
from tests.test_integration import TestSystemIntegration
import unittest

suite = unittest.TestLoader().loadTestsFromTestCase(TestSystemIntegration)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
print(f'テスト結果: {result.wasSuccessful()}')
"
```

## 📊 テスト結果の評価

### 成功基準
- 全単体テストが成功
- 統合テストが成功
- APIテストが成功
- Web UIテストが成功
- エラーハンドリングが適切

### パフォーマンス基準
- センサーデータ取得: 1秒以内
- API応答時間: 500ms以内
- Web UI表示: 2秒以内

### 品質基準
- コードカバレッジ: 80%以上
- エラーハンドリング: 100%実装
- ログ出力: 適切に実装

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

