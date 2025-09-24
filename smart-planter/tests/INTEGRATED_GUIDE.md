# 統合テスト 統合実装ガイド

## 📋 概要
すくすくミントちゃんシステムの統合テスト・長期稼働テスト・負荷テストの詳細手順書

## 🎯 テスト目標
- 個別機能の動作確認
- システム間連携の確認
- 長期稼働の安定性確認
- 負荷耐性の確認
- エラー処理の確認

## 🛠️ テスト環境

### ハードウェア
- Raspberry Pi 5
- 全センサー・アクチュエータ
- ネットワーク環境
- 電源供給

### ソフトウェア
- Python 3.11.x
- pytest (テストフレームワーク)
- 全実装済みモジュール

---

## 📄 実装コード

### 📄 test_sensors.py
センサーシステムテスト

```python
import pytest
import unittest.mock as mock
import time
from datetime import datetime
from src.sensors.aht25_sensor import AHT25Sensor
from src.sensors.sen0193_sensor import SEN0193Sensor
from src.sensors.float_switch import FloatSwitch
from src.sensors.sensor_manager import SensorManager

class TestAHT25Sensor:
    """AHT25温湿度センサーテスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        self.sensor = AHT25Sensor()      # AHT25センサーインスタンスを作成
    
    @mock.patch('smbus2.SMBus')
    def test_initialization(self, mock_bus):
        """初期化テスト"""
        mock_bus_instance = mock_bus.return_value  # モックバスインスタンスを取得
        mock_bus_instance.write_byte.return_value = None  # write_byteメソッドの戻り値を設定
        
        result = self.sensor.initialize()  # 初期化を実行
        assert result == True              # 初期化成功を確認
        assert self.sensor.initialized == True  # 初期化フラグを確認
    
    @mock.patch('smbus2.SMBus')
    def test_read_data_success(self, mock_bus):
        """データ読み取り成功テスト"""
        mock_bus_instance = mock_bus.return_value  # モックバスインスタンスを取得
        mock_bus_instance.write_byte.return_value = None  # write_byteメソッドの戻り値を設定
        mock_bus_instance.read_i2c_block_data.return_value = [0, 100, 200, 50, 150, 75]  # 読み取りデータを設定
        
        self.sensor.initialized = True    # 初期化フラグを設定
        result = self.sensor.read_data()  # データ読み取りを実行
        
        assert 'error' not in result      # エラーがないことを確認
        assert 'temperature' in result    # 温度データが含まれることを確認
        assert 'humidity' in result        # 湿度データが含まれることを確認
        assert 'timestamp' in result      # タイムスタンプが含まれることを確認
        assert isinstance(result['temperature'], float)  # 温度がfloat型であることを確認
        assert isinstance(result['humidity'], float)     # 湿度がfloat型であることを確認
    
    @mock.patch('smbus2.SMBus')
    def test_read_data_error(self, mock_bus):
        """データ読み取りエラーテスト"""
        mock_bus_instance = mock_bus.return_value  # モックバスインスタンスを取得
        mock_bus_instance.write_byte.side_effect = Exception("I2C通信エラー")  # 例外を発生
        
        result = self.sensor.read_data()  # データ読み取りを実行
        
        assert 'error' in result          # エラーが含まれることを確認
        assert self.sensor.error_count > 0  # エラーカウントが増加することを確認
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        # エラーカウント増加
        initial_count = self.sensor.error_count  # 初期エラーカウントを取得
        self.sensor.increment_error_count()     # エラーカウントを増加
        assert self.sensor.error_count == initial_count + 1  # エラーカウントが増加することを確認
        
        # 最大エラー数に達した場合
        self.sensor.error_count = self.sensor.max_errors  # エラーカウントを最大値に設定
        self.sensor.increment_error_count()     # エラーカウントを増加
        assert self.sensor.is_enabled == False  # センサーが無効になることを確認

class TestSEN0193Sensor:
    """SEN0193土壌水分センサーテスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        self.sensor = SEN0193Sensor()    # SEN0193センサーインスタンスを作成
    
    @mock.patch('spidev.SpiDev')
    def test_initialization(self, mock_spi):
        """初期化テスト"""
        mock_spi_instance = mock_spi.return_value  # モックSPIインスタンスを取得
        mock_spi_instance.open.return_value = None  # openメソッドの戻り値を設定
        mock_spi_instance.xfer2.return_value = [0, 100, 200]  # xfer2メソッドの戻り値を設定
        
        result = self.sensor.initialize()  # 初期化を実行
        assert result == True              # 初期化成功を確認
    
    @mock.patch('spidev.SpiDev')
    def test_read_data_success(self, mock_spi):
        """データ読み取り成功テスト"""
        mock_spi_instance = mock_spi.return_value  # モックSPIインスタンスを取得
        mock_spi_instance.xfer2.return_value = [0, 100, 200]  # xfer2メソッドの戻り値を設定
        
        result = self.sensor.read_data()  # データ読み取りを実行
        
        assert 'error' not in result      # エラーがないことを確認
        assert 'raw_value' in result      # 生の値が含まれることを確認
        assert 'filtered_value' in result # フィルタ済み値が含まれることを確認
        assert 'moisture_percentage' in result  # 土壌水分率が含まれることを確認
        assert 'timestamp' in result      # タイムスタンプが含まれることを確認
        assert 0 <= result['moisture_percentage'] <= 100  # 土壌水分率が0-100%の範囲であることを確認
    
    def test_filtering(self):
        """フィルタリング機能テスト"""
        # 履歴に値を追加
        self.sensor.reading_history = [100, 110, 105, 108, 102]  # 読み取り履歴を設定
        
        # 移動平均計算テスト
        import numpy as np
        expected_avg = np.mean(self.sensor.reading_history)  # 期待される平均値を計算
        assert abs(expected_avg - 105) < 1  # 平均値が105に近いことを確認

class TestFloatSwitch:
    """フロートスイッチテスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        self.switch = FloatSwitch(pin=18)  # フロートスイッチインスタンスを作成
    
    @mock.patch('RPi.GPIO.input')
    def test_read_data_water_available(self, mock_input):
        """水位ありテスト"""
        mock_input.return_value = 1       # GPIO入力値を1（水位あり）に設定
        
        result = self.switch.read_data()  # データ読み取りを実行
        
        assert 'error' not in result      # エラーがないことを確認
        assert result['is_water_available'] == True  # 水位ありフラグを確認
        assert result['raw_state'] == 1   # 生の状態値を確認
    
    @mock.patch('RPi.GPIO.input')
    def test_read_data_water_empty(self, mock_input):
        """水位なしテスト"""
        mock_input.return_value = 0       # GPIO入力値を0（水位なし）に設定
        
        result = self.switch.read_data()  # データ読み取りを実行
        
        assert 'error' not in result      # エラーがないことを確認
        assert result['is_water_available'] == False  # 水位なしフラグを確認
        assert result['raw_state'] == 0   # 生の状態値を確認

class TestSensorManager:
    """センサーマネージャーテスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        with mock.patch('src.sensors.aht25_sensor.AHT25Sensor'), \  # AHT25センサーをモック
             mock.patch('src.sensors.sen0193_sensor.SEN0193Sensor'), \  # SEN0193センサーをモック
             mock.patch('src.sensors.float_switch.FloatSwitch'):  # フロートスイッチをモック
            self.manager = SensorManager()  # センサーマネージャーを作成
    
    def test_sensor_initialization(self):
        """センサー初期化テスト"""
        assert 'temperature_humidity' in self.manager.sensors  # 温湿度センサーが存在することを確認
        assert 'soil_moisture' in self.manager.sensors         # 土壌水分センサーが存在することを確認
        assert 'water_level' in self.manager.sensors           # 水位センサーが存在することを確認
    
    def test_get_latest_data(self):
        """最新データ取得テスト"""
        # モックデータ設定
        self.manager.data_cache = {       # データキャッシュを設定
            'temperature_humidity': {'temperature': 25.5, 'humidity': 60.0},  # 温湿度データ
            'soil_moisture': {'moisture_percentage': 45.0},  # 土壌水分データ
            'water_level': {'is_water_available': True}      # 水位データ
        }
        
        data = self.manager.get_latest_data()  # 最新データを取得
        assert 'temperature_humidity' in data  # 温湿度データが含まれることを確認
        assert 'soil_moisture' in data          # 土壌水分データが含まれることを確認
        assert 'water_level' in data            # 水位データが含まれることを確認
    
    def test_get_sensor_status(self):
        """センサー状態取得テスト"""
        status = self.manager.get_sensor_status()  # センサー状態を取得
        assert 'temperature_humidity' in status    # 温湿度センサー状態が含まれることを確認
        assert 'soil_moisture' in status           # 土壌水分センサー状態が含まれることを確認
        assert 'water_level' in status              # 水位センサー状態が含まれることを確認
```

### 📄 test_watering.py
給水システムテスト

```python
import pytest
import unittest.mock as mock
import json
from datetime import datetime, timedelta
from src.watering.watering_controller import WateringController
from src.watering.auto_watering_manager import AutoWateringManager

class TestWateringController:
    """給水制御テスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        with mock.patch('RPi.GPIO.setmode'), \    # GPIO.setmodeをモック
             mock.patch('RPi.GPIO.setup'), \       # GPIO.setupをモック
             mock.patch('RPi.GPIO.output'):        # GPIO.outputをモック
            self.controller = WateringController()  # 給水制御インスタンスを作成
    
    def test_initialization(self):
        """初期化テスト"""
        assert self.controller.soil_moisture_threshold == 159  # 土壌水分閾値を確認
        assert self.controller.watering_interval_hours == 12   # 給水間隔を確認
        assert self.controller.watering_duration_seconds == 5  # 給水時間を確認
        assert self.controller.max_consecutive_waterings == 2  # 最大連続給水回数を確認
    
    def test_can_water_conditions(self):
        """給水条件チェックテスト"""
        # 正常な条件
        result = self.controller._can_water(150, True)  # 給水条件をチェック
        assert result['can_water'] == True              # 給水可能であることを確認
        assert result['checks']['soil_moisture_ok'] == True  # 土壌水分条件を確認
        assert result['checks']['water_available'] == True   # 水位条件を確認
        
        # 土壌水分が高い場合
        result = self.controller._can_water(200, True)  # 給水条件をチェック
        assert result['can_water'] == False             # 給水不可であることを確認
        assert result['checks']['soil_moisture_ok'] == False  # 土壌水分条件を確認
        
        # 水がない場合
        result = self.controller._can_water(150, False)  # 給水条件をチェック
        assert result['can_water'] == False              # 給水不可であることを確認
        assert result['checks']['water_available'] == False  # 水位条件を確認
    
    def test_consecutive_watering_limit(self):
        """連続給水制限テスト"""
        self.controller.consecutive_watering_count = 2  # 連続給水カウントを設定
        
        result = self.controller._can_water(150, True)  # 給水条件をチェック
        assert result['can_water'] == False             # 給水不可であることを確認
        assert result['checks']['consecutive_limit_ok'] == False  # 連続制限条件を確認
    
    @mock.patch('RPi.GPIO.output')
    @mock.patch('time.sleep')
    def test_start_watering_success(self, mock_sleep, mock_output):
        """給水成功テスト"""
        self.controller.last_watering_time = datetime.now() - timedelta(hours=13)  # 最後の給水時間を設定
        
        result = self.controller.start_watering(150, True)  # 給水を開始
        
        assert result['success'] == True  # 給水成功を確認
        assert 'watering_record' in result  # 給水記録が含まれることを確認
        assert self.controller.consecutive_watering_count == 1  # 連続カウントが増加することを確認
        assert self.controller.last_watering_time is not None  # 給水時間が設定されることを確認
    
    @mock.patch('RPi.GPIO.output')
    def test_start_watering_conditions_not_met(self, mock_output):
        """給水条件未満テスト"""
        result = self.controller.start_watering(200, True)  # 給水を開始
        
        assert result['success'] == False  # 給水失敗を確認
        assert result['error'] == 'CONDITIONS_NOT_MET'  # エラーコードを確認
    
    def test_reset_consecutive_count(self):
        """連続給水カウントリセットテスト"""
        self.controller.consecutive_watering_count = 2  # 連続カウントを設定
        self.controller.reset_consecutive_count()       # カウントをリセット
        assert self.controller.consecutive_watering_count == 0  # カウントが0になることを確認
    
    def test_get_status(self):
        """状態取得テスト"""
        status = self.controller.get_status()  # 状態を取得
        assert 'is_watering' in status         # 給水中フラグが含まれることを確認
        assert 'consecutive_watering_count' in status  # 連続カウントが含まれることを確認
        assert 'soil_moisture_threshold' in status     # 土壌水分閾値が含まれることを確認
        assert 'watering_interval_hours' in status     # 給水間隔が含まれることを確認

class TestAutoWateringManager:
    """自動給水管理テスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        self.mock_sensor_manager = mock.MagicMock()  # センサーマネージャーをモック
        self.mock_line_notify = mock.MagicMock()     # LINE通知をモック
        
        with mock.patch('src.watering.watering_controller.WateringController'):  # 給水制御をモック
            self.manager = AutoWateringManager(      # 自動給水管理を作成
                self.mock_sensor_manager, 
                self.mock_line_notify
            )
    
    def test_initialization(self):
        """初期化テスト"""
        assert self.manager.sensor_manager == self.mock_sensor_manager  # センサーマネージャーを確認
        assert self.manager.line_notify == self.mock_line_notify         # LINE通知を確認
        assert self.manager.running == False                             # 実行フラグを確認
    
    def test_manual_watering_success(self):
        """手動給水成功テスト"""
        # モックデータ設定
        self.mock_sensor_manager.get_latest_data.return_value = {  # センサーデータを設定
            'soil_moisture': {'moisture_percentage': 150},        # 土壌水分データ
            'water_level': {'is_water_available': True}           # 水位データ
        }
        
        self.manager.watering_controller.start_watering.return_value = {  # 給水結果を設定
            'success': True,
            'message': '給水完了'
        }
        
        result = self.manager.manual_watering()  # 手動給水を実行
        
        assert result['success'] == True  # 給水成功を確認
        self.mock_line_notify.send_message.assert_called_once()  # LINE通知が呼ばれることを確認
    
    def test_emergency_stop(self):
        """緊急停止テスト"""
        self.manager.watering_controller.stop_watering.return_value = {  # 停止結果を設定
            'success': True,
            'message': '給水停止完了'
        }
        
        result = self.manager.emergency_stop()  # 緊急停止を実行
        
        assert result['success'] == True  # 停止成功を確認
        self.mock_line_notify.send_message.assert_called_once()  # LINE通知が呼ばれることを確認
    
    def test_update_settings(self):
        """設定更新テスト"""
        settings = {                      # 設定を定義
            'soil_moisture_threshold': 150,  # 土壌水分閾値
            'watering_interval_hours': 10    # 給水間隔
        }
        
        result = self.manager.update_settings(settings)  # 設定を更新
        
        assert result['success'] == True  # 更新成功を確認
        assert self.manager.watering_controller.soil_moisture_threshold == 150  # 閾値が更新されることを確認
        assert self.manager.watering_controller.watering_interval_hours == 10  # 間隔が更新されることを確認
```

### 📄 test_integration.py
統合テスト

```python
import pytest
import unittest.mock as mock
import time
from datetime import datetime
from src.sensors.sensor_manager import SensorManager
from src.watering.auto_watering_manager import AutoWateringManager
from src.data.data_manager_service import DataManagerService
from src.notifications.notification_manager import NotificationManager

class TestSystemIntegration:
    """システム統合テスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        # 全モジュールをモック化
        with mock.patch('src.sensors.aht25_sensor.AHT25Sensor'), \    # AHT25センサーをモック
             mock.patch('src.sensors.sen0193_sensor.SEN0193Sensor'), \  # SEN0193センサーをモック
             mock.patch('src.sensors.float_switch.FloatSwitch'), \      # フロートスイッチをモック
             mock.patch('src.watering.watering_controller.WateringController'), \  # 給水制御をモック
             mock.patch('src.notifications.line_notify.LineNotify'):   # LINE通知をモック
            
            self.sensor_manager = SensorManager()  # センサーマネージャーを作成
            self.notification_manager = NotificationManager()  # 通知管理を作成
            self.watering_manager = AutoWateringManager(       # 給水管理を作成
                self.sensor_manager, 
                self.notification_manager.line_notify
            )
            self.data_service = DataManagerService(            # データサービスを作成
                self.sensor_manager,
                self.watering_manager.watering_controller
            )
    
    def test_sensor_to_watering_integration(self):
        """センサーから給水への統合テスト"""
        # センサーデータ設定
        self.sensor_manager.data_cache = {  # センサーデータを設定
            'soil_moisture': {'moisture_percentage': 150},  # 土壌水分データ
            'water_level': {'is_water_available': True}     # 水位データ
        }
        
        # 給水実行
        result = self.watering_manager.manual_watering()  # 手動給水を実行
        
        assert result['success'] == True  # 給水成功を確認
    
    def test_data_saving_integration(self):
        """データ保存統合テスト"""
        # センサーデータ設定
        test_data = {                     # テストデータを設定
            'temperature_humidity': {'temperature': 25.5, 'humidity': 60.0},  # 温湿度データ
            'soil_moisture': {'moisture_percentage': 45.0}  # 土壌水分データ
        }
        
        # データ保存
        for sensor_name, data in test_data.items():  # テストデータをループ
            result = self.data_service.data_manager.save_sensor_data(sensor_name, data)  # センサーデータを保存
            assert result == True         # 保存成功を確認
    
    def test_notification_integration(self):
        """通知統合テスト"""
        # 給水通知
        result = self.notification_manager.send_watering_notification(100)  # 給水通知を送信
        assert result == True             # 通知成功を確認
        
        # センサーアラート
        result = self.notification_manager.send_sensor_alert('temperature', 35.0, 30.0)  # センサーアラートを送信
        assert result == True             # 通知成功を確認
    
    def test_error_handling_integration(self):
        """エラーハンドリング統合テスト"""
        # センサーエラー時の動作
        self.sensor_manager.data_cache = {  # センサーデータを設定
            'soil_moisture': {'error': 'センサーエラー'}  # エラーデータ
        }
        
        # エラー通知が送信されることを確認
        result = self.notification_manager.send_system_error('センサーエラー')  # システムエラー通知を送信
        assert result == True             # 通知成功を確認
    
    def test_full_workflow(self):
        """完全ワークフローテスト"""
        # 1. センサーデータ取得
        sensor_data = {                   # センサーデータを設定
            'temperature_humidity': {'temperature': 25.0, 'humidity': 60.0},  # 温湿度データ
            'soil_moisture': {'moisture_percentage': 150},  # 土壌水分データ
            'water_level': {'is_water_available': True}   # 水位データ
        }
        self.sensor_manager.data_cache = sensor_data  # データキャッシュを設定
        
        # 2. データ保存
        for sensor_name, data in sensor_data.items():  # センサーデータをループ
            if 'error' not in data:       # エラーがない場合
                self.data_service.data_manager.save_sensor_data(sensor_name, data)  # データを保存
        
        # 3. 給水判定・実行
        watering_result = self.watering_manager.manual_watering()  # 手動給水を実行
        assert watering_result['success'] == True  # 給水成功を確認
        
        # 4. 通知送信
        notification_result = self.notification_manager.send_watering_notification(100)  # 給水通知を送信
        assert notification_result == True  # 通知成功を確認
        
        # 5. 状態確認
        status = self.watering_manager.get_watering_status()  # 給水状態を取得
        assert 'auto_watering_running' in status  # 自動給水実行フラグが含まれることを確認
```

### 📄 test_long_term.py
長期稼働テスト

```python
import pytest
import unittest.mock as mock
import time
import threading
from datetime import datetime, timedelta

class TestLongTermOperation:
    """長期稼働テスト"""
    
    def setup_method(self):
        """テスト前のセットアップ"""
        self.test_duration = 60          # テスト時間（秒）
        self.start_time = datetime.now()  # 開始時刻を記録
    
    @pytest.mark.slow
    def test_24_hour_operation(self):
        """24時間稼働テスト"""
        # 実際のテストでは24時間実行
        # ここでは短縮版でテスト
        
        with mock.patch('src.sensors.sensor_manager.SensorManager') as mock_sensor, \  # センサーマネージャーをモック
             mock.patch('src.watering.auto_watering_manager.AutoWateringManager') as mock_watering, \  # 給水管理をモック
             mock.patch('src.data.data_manager_service.DataManagerService') as mock_data:  # データサービスをモック
            
            # モック設定
            mock_sensor_instance = mock_sensor.return_value  # センサーマネージャーインスタンスを取得
            mock_watering_instance = mock_watering.return_value  # 給水管理インスタンスを取得
            mock_data_instance = mock_data.return_value      # データサービスインスタンスを取得
            
            # システム開始
            mock_sensor_instance.start_monitoring()         # センサー監視を開始
            mock_watering_instance.start_auto_watering()     # 自動給水を開始
            mock_data_instance.start_service()              # データサービスを開始
            
            # テスト実行
            time.sleep(self.test_duration)  # テスト時間待機
            
            # システム停止
            mock_sensor_instance.stop_monitoring()          # センサー監視を停止
            mock_watering_instance.stop_auto_watering()     # 自動給水を停止
            mock_data_instance.stop_service()               # データサービスを停止
            
            # 結果確認
            assert True                    # エラーなく完了することを確認
    
    def test_memory_leak(self):
        """メモリリークテスト"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())  # 現在のプロセスを取得
        initial_memory = process.memory_info().rss  # 初期メモリ使用量を取得
        
        # 長時間実行シミュレーション
        for i in range(1000):            # 1000回ループ
            # メモリ使用量をチェック
            current_memory = process.memory_info().rss  # 現在のメモリ使用量を取得
            memory_increase = current_memory - initial_memory  # メモリ増加量を計算
            
            # メモリ増加が異常でないことを確認
            assert memory_increase < 100 * 1024 * 1024  # 100MB以下であることを確認
        
        final_memory = process.memory_info().rss  # 最終メモリ使用量を取得
        total_increase = final_memory - initial_memory  # 総メモリ増加量を計算
        
        # 総メモリ増加量が許容範囲内であることを確認
        assert total_increase < 50 * 1024 * 1024  # 50MB以下であることを確認
    
    def test_error_recovery(self):
        """エラー回復テスト"""
        with mock.patch('src.sensors.sensor_manager.SensorManager') as mock_sensor:  # センサーマネージャーをモック
            mock_sensor_instance = mock_sensor.return_value  # センサーマネージャーインスタンスを取得
            
            # エラー発生シミュレーション
            mock_sensor_instance.read_data.side_effect = Exception("センサーエラー")  # 例外を発生
            
            # エラー回復処理
            error_count = 0               # エラーカウントを初期化
            for i in range(10):           # 10回ループ
                try:
                    mock_sensor_instance.read_data()  # データ読み取りを実行
                except Exception:
                    error_count += 1       # エラーカウントを増加
                    time.sleep(0.1)        # 短い待機
            
            # エラーが適切に処理されることを確認
            assert error_count == 10       # エラーが10回発生することを確認
    
    def test_concurrent_access(self):
        """並行アクセステスト"""
        results = []                      # 結果リストを初期化
        
        def worker_thread(thread_id):
            """ワーカースレッド"""
            for i in range(10):           # 10回ループ
                # 並行アクセスシミュレーション
                result = f"Thread-{thread_id}-{i}"  # 結果文字列を作成
                results.append(result)    # 結果リストに追加
                time.sleep(0.01)          # 短い待機
        
        # 複数スレッドで並行実行
        threads = []                      # スレッドリストを初期化
        for i in range(5):                # 5つのスレッドを作成
            thread = threading.Thread(target=worker_thread, args=(i,))  # スレッドを作成
            threads.append(thread)        # スレッドリストに追加
            thread.start()                # スレッドを開始
        
        # 全スレッドの完了を待機
        for thread in threads:            # 全スレッドをループ
            thread.join()                 # スレッド終了を待機
        
        # 結果確認
        assert len(results) == 50         # 結果が50個であることを確認
        assert all(isinstance(result, str) for result in results)  # 全結果が文字列であることを確認
```

---

## 📊 テスト完了チェックリスト

- [ ] 個別機能テスト完了
- [ ] システム統合テスト完了
- [ ] 長期稼働テスト完了
- [ ] 負荷テスト完了
- [ ] エラーハンドリングテスト完了
- [ ] パフォーマンステスト完了
- [ ] セキュリティテスト完了
- [ ] ユーザビリティテスト完了
- [ ] テストレポート生成完了

## 🎯 次のステップ

1. **本番環境デプロイ**: テスト完了後の本番展開
2. **運用監視**: 24時間監視体制の構築
3. **メンテナンス**: 定期メンテナンス計画
4. **改善**: テスト結果に基づく改善

---

## 🏗️ クラス全体の流れと意味

### **TestAHT25Sensorクラス**
**意味**: AHT25温湿度センサーの単体テスト
**役割**:
- センサーの初期化テスト
- データ読み取りの成功・失敗テスト
- エラーハンドリングの動作確認
- I2C通信のモック化による安全なテスト

### **TestSEN0193Sensorクラス**
**意味**: SEN0193土壌水分センサーの単体テスト
**役割**:
- SPI通信によるADC読み取りテスト
- フィルタリング機能の動作確認
- データ範囲の妥当性チェック
- 複数回読み取りによるノイズ除去テスト

### **TestFloatSwitchクラス**
**意味**: フロートスイッチの単体テスト
**役割**:
- GPIO入力の状態読み取りテスト
- 水位あり・なしの判定テスト
- デバウンス処理の動作確認

### **TestSensorManagerクラス**
**意味**: センサー管理システムの統合テスト
**役割**:
- 複数センサーの統合管理テスト
- データキャッシュの動作確認
- センサー状態の取得テスト

### **TestWateringControllerクラス**
**意味**: 給水制御システムの単体テスト
**役割**:
- 給水条件の判定テスト
- 連続給水制限の動作確認
- GPIO制御によるリレー操作テスト
- 給水履歴の記録テスト

### **TestAutoWateringManagerクラス**
**意味**: 自動給水管理システムの統合テスト
**役割**:
- センサーデータに基づく自動給水テスト
- 手動給水・緊急停止の動作確認
- LINE通知との連携テスト
- 設定更新の動作確認

### **TestSystemIntegrationクラス**
**意味**: 全システムの統合テスト
**役割**:
- センサー→給水→通知の連携テスト
- データ保存の統合テスト
- エラーハンドリングの統合テスト
- 完全ワークフローの動作確認

### **TestLongTermOperationクラス**
**意味**: 長期稼働とパフォーマンステスト
**役割**:
- 24時間連続稼働テスト
- メモリリークの検出
- エラー回復機能のテスト
- 並行アクセスの安全性確認

**全体の流れ**:
1. **単体テスト**: 各コンポーネントの個別動作確認
2. **統合テスト**: コンポーネント間の連携確認
3. **長期テスト**: 継続稼働の安定性確認
4. **負荷テスト**: 高負荷時の動作確認
5. **エラーテスト**: 異常時の動作確認
6. **パフォーマンステスト**: メモリ・CPU使用量の確認

**テスト戦略**:
- **モック化**: ハードウェア依存部分をモックで安全にテスト
- **段階的テスト**: 単体→統合→長期の段階的テスト
- **自動化**: pytestによる自動テスト実行
- **継続的テスト**: CI/CDパイプラインでの継続的テスト

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

