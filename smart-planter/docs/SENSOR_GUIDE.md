# センサー制御機能 統合実装ガイド

## 📋 概要
温湿度センサー(AHT25)、土壌水分センサー(SEN0193)、圧力センサー(MS583730BA01-50)の制御機能を実装するための詳細手順書

## 🎯 実装目標
- AHT25温湿度センサーのI2C通信制御
- SEN0193土壌水分センサーのADC制御
- MS583730BA01-50圧力センサーによる水の残量測定
- センサー値のフィルタリング処理
- エラーハンドリングと故障時対応
- データ取得の定期実行

## 🛠️ 必要な環境

### ハードウェア
- Raspberry Pi 5
- 温湿度センサー AHT25
- 土壌水分センサー SEN0193
- 圧力センサー MS583730BA01-50
- ADC MCP3002
- ジャンパーワイヤー
- ブレッドボード

### ソフトウェア
- Python 3.11.x
- RPi.GPIO
- smbus2 (I2C通信用)
- spidev (SPI通信用)
- numpy (データ処理用)

## 📁 ファイル作成手順

### Step 1: センサーディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd smart-planter

# センサーディレクトリの確認
ls -la src/sensors/
```

### Step 2: 各ファイルの作成順序
1. `src/sensors/base_sensor.py` - 基底クラス
2. `src/sensors/temperature_humidity.py` - 温湿度センサー
3. `src/sensors/soil_moisture.py` - 土壌水分センサー
4. `src/sensors/pressure_sensor.py` - 圧力センサー（水の残量測定）
5. `src/sensors/float_switch.py` - フロートスイッチ
6. `src/sensors/sensor_manager.py` - 統合管理

### Step 3: ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/sensors/base_sensor.py
touch src/sensors/temperature_humidity.py
touch src/sensors/soil_moisture.py
touch src/sensors/pressure_sensor.py
touch src/sensors/float_switch.py
touch src/sensors/sensor_manager.py
```

## 📄 実装コード

### 📄 src/sensors/base_sensor.py
センサーの基底クラス

```python
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseSensor(ABC):
    """センサーの基底クラス"""
    
    def __init__(self, name: str, pin: int):
        self.name = name
        self.pin = pin
        self.error_count = 0
        self.max_errors = 3
        self.is_enabled = True
        self.logger = logging.getLogger(f"sensor.{name}")
        
    @abstractmethod
    def read_data(self) -> Dict[str, Any]:
        """センサーデータを読み取る"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """センサーを初期化する"""
        pass
    
    def is_healthy(self) -> bool:
        """センサーの健全性をチェック"""
        return self.error_count < self.max_errors and self.is_enabled
    
    def reset_error_count(self):
        """エラーカウントをリセット"""
        self.error_count = 0
    
    def increment_error_count(self):
        """エラーカウントを増加"""
        self.error_count += 1
        if self.error_count >= self.max_errors:
            self.is_enabled = False
            self.logger.error(f"センサー {self.name} が無効化されました")
```

### 📄 src/sensors/temperature_humidity.py
温湿度センサー制御クラス

```python
import smbus2
import time
import logging
from typing import Dict, Any
from .base_sensor import BaseSensor

class TemperatureHumiditySensor(BaseSensor):
    """AHT25温湿度センサー制御クラス"""
    
    def __init__(self, i2c_bus: int = 1, address: int = 0x38):
        super().__init__("temperature_humidity", 0)
        self.i2c_bus = i2c_bus
        self.address = address
        self.bus = None
        self.logger = logging.getLogger("sensor.temperature_humidity")
    
    def initialize(self) -> bool:
        """センサーを初期化する"""
        try:
            self.bus = smbus2.SMBus(self.i2c_bus)
            
            # AHT25の初期化コマンド
            self.bus.write_byte(self.address, 0xBE)
            time.sleep(0.01)
            
            self.logger.info("AHT25温湿度センサーが初期化されました")
            return True
            
        except Exception as e:
            self.logger.error(f"AHT25初期化エラー: {str(e)}")
            self.increment_error_count()
            return False
    
    def read_data(self) -> Dict[str, Any]:
        """温湿度データを読み取る"""
        try:
            if not self.is_healthy():
                return self._get_error_data()
            
            # 測定開始コマンド
            self.bus.write_byte(self.address, 0xAC)
            self.bus.write_byte(self.address, 0x33)
            self.bus.write_byte(self.address, 0x00)
            
            # 測定完了まで待機
            time.sleep(0.08)
            
            # データ読み取り
            data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
            
            # データ変換
            humidity_raw = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
            temperature_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
            
            humidity = (humidity_raw / 0x100000) * 100
            temperature = (temperature_raw / 0x100000) * 200 - 50
            
            self.reset_error_count()
            
            return {
                'temperature': round(temperature, 2),
                'humidity': round(humidity, 2),
                'timestamp': time.time(),
                'sensor': 'AHT25'
            }
            
        except Exception as e:
            self.logger.error(f"温湿度センサー読み取りエラー: {str(e)}")
            self.increment_error_count()
            return self._get_error_data()
    
    def _get_error_data(self) -> Dict[str, Any]:
        """エラー時のデフォルトデータ"""
        return {
            'temperature': None,
            'humidity': None,
            'timestamp': time.time(),
            'sensor': 'AHT25',
            'error': True
        }
```

### 📄 src/sensors/soil_moisture.py
土壌水分センサー制御クラス

```python
import spidev
import time
import logging
from typing import Dict, Any
from .base_sensor import BaseSensor

class SoilMoistureSensor(BaseSensor):
    """SEN0193土壌水分センサー制御クラス"""
    
    def __init__(self, channel: int = 0):
        super().__init__("soil_moisture", channel)
        self.channel = channel
        self.spi = None
        self.logger = logging.getLogger("sensor.soil_moisture")
    
    def initialize(self) -> bool:
        """センサーを初期化する"""
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # SPI bus 0, device 0
            self.spi.max_speed_hz = 1000000
            
            self.logger.info("SEN0193土壌水分センサーが初期化されました")
            return True
            
        except Exception as e:
            self.logger.error(f"土壌水分センサー初期化エラー: {str(e)}")
            self.increment_error_count()
            return False
    
    def read_data(self) -> Dict[str, Any]:
        """土壌水分データを読み取る"""
        try:
            if not self.is_healthy():
                return self._get_error_data()
            
            # ADC読み取り
            adc_data = self.spi.xfer2([1, (8 + self.channel) << 4, 0])
            adc_value = ((adc_data[1] & 3) << 8) + adc_data[2]
            
            # 土壌水分値の変換（0-1023 → 0-100%）
            moisture_percentage = (adc_value / 1023.0) * 100
            
            # 土壌水分値の判定
            if adc_value <= 159:
                status = "dry"
            elif adc_value <= 400:
                status = "moist"
            else:
                status = "wet"
            
            self.reset_error_count()
            
            return {
                'soil_moisture': adc_value,
                'moisture_percentage': round(moisture_percentage, 2),
                'status': status,
                'timestamp': time.time(),
                'sensor': 'SEN0193'
            }
            
        except Exception as e:
            self.logger.error(f"土壌水分センサー読み取りエラー: {str(e)}")
            self.increment_error_count()
            return self._get_error_data()
    
    def _get_error_data(self) -> Dict[str, Any]:
        """エラー時のデフォルトデータ"""
        return {
            'soil_moisture': None,
            'moisture_percentage': None,
            'status': 'error',
            'timestamp': time.time(),
            'sensor': 'SEN0193',
            'error': True
        }
```

### 📄 src/sensors/pressure_sensor.py
圧力センサー制御クラス（水の残量測定）

```python
import smbus2
import time
import logging
import math
from typing import Dict, Any
from .base_sensor import BaseSensor

class PressureSensor(BaseSensor):
    """MS583730BA01-50圧力センサー制御クラス（水の残量測定）"""
    
    def __init__(self, i2c_bus: int = 1, address: int = 0x76):
        super().__init__("pressure_sensor", 0)
        self.i2c_bus = i2c_bus
        self.address = address
        self.bus = None
        self.logger = logging.getLogger("sensor.pressure")
        
        # キャリブレーション係数
        self.c = [0] * 8
        self.tank_height = 30.0  # タンクの高さ（cm）
        self.tank_diameter = 20.0  # タンクの直径（cm）
        
    def initialize(self) -> bool:
        """センサーを初期化する"""
        try:
            self.bus = smbus2.SMBus(self.i2c_bus)
            
            # リセットコマンド
            self.bus.write_byte(self.address, 0x1E)
            time.sleep(0.01)
            
            # キャリブレーション係数の読み取り
            for i in range(8):
                data = self.bus.read_i2c_block_data(self.address, 0xA0 + i * 2, 2)
                self.c[i] = (data[0] << 8) | data[1]
            
            self.logger.info("MS583730BA01-50圧力センサーが初期化されました")
            return True
            
        except Exception as e:
            self.logger.error(f"圧力センサー初期化エラー: {str(e)}")
            self.increment_error_count()
            return False
    
    def read_data(self) -> Dict[str, Any]:
        """圧力データを読み取って水の残量を計算"""
        try:
            if not self.is_healthy():
                return self._get_error_data()
            
            # 温度測定
            self.bus.write_byte(self.address, 0x44)
            time.sleep(0.01)
            
            data = self.bus.read_i2c_block_data(self.address, 0x00, 3)
            d2 = (data[0] << 16) | (data[1] << 8) | data[2]
            
            # 圧力測定
            self.bus.write_byte(self.address, 0x54)
            time.sleep(0.01)
            
            data = self.bus.read_i2c_block_data(self.address, 0x00, 3)
            d1 = (data[0] << 16) | (data[1] << 8) | data[2]
            
            # 温度計算
            dt = d2 - self.c[5] * 256
            temp = 2000 + dt * self.c[6] / 8388608
            
            # 圧力計算
            off = self.c[2] * 65536 + (self.c[4] * dt) / 128
            sens = self.c[1] * 32768 + (self.c[3] * dt) / 256
            pressure = (d1 * sens / 2097152 - off) / 8192
            
            # 水の高さ計算（cm）
            water_height = pressure / 1000  # Pa → kPa → cm
            
            # 水の残量計算
            water_volume = self._calculate_water_volume(water_height)
            water_percentage = min(100, max(0, (water_height / self.tank_height) * 100))
            
            # 残量ステータス
            if water_percentage > 80:
                status = "full"
            elif water_percentage > 30:
                status = "normal"
            elif water_percentage > 10:
                status = "low"
            else:
                status = "empty"
            
            self.reset_error_count()
            
            return {
                'pressure': round(pressure, 2),
                'water_height': round(water_height, 2),
                'water_volume': round(water_volume, 2),
                'water_percentage': round(water_percentage, 2),
                'status': status,
                'temperature': round(temp / 100, 2),
                'timestamp': time.time(),
                'sensor': 'MS583730BA01-50'
            }
            
        except Exception as e:
            self.logger.error(f"圧力センサー読み取りエラー: {str(e)}")
            self.increment_error_count()
            return self._get_error_data()
    
    def _calculate_water_volume(self, height: float) -> float:
        """水の体積を計算（ml）"""
        radius = self.tank_diameter / 2
        volume_cm3 = math.pi * radius * radius * height
        volume_ml = volume_cm3  # cm3 = ml
        return volume_ml
    
    def _get_error_data(self) -> Dict[str, Any]:
        """エラー時のデフォルトデータ"""
        return {
            'pressure': None,
            'water_height': None,
            'water_volume': None,
            'water_percentage': None,
            'status': 'error',
            'temperature': None,
            'timestamp': time.time(),
            'sensor': 'MS583730BA01-50',
            'error': True
        }
```

### 📄 src/sensors/sensor_manager.py
センサー統合管理クラス

```python
import time
import logging
import threading
from typing import Dict, Any, List
from .temperature_humidity import TemperatureHumiditySensor
from .soil_moisture import SoilMoistureSensor
from .pressure_sensor import PressureSensor
from .float_switch import FloatSwitchSensor

class SensorManager:
    """センサー統合管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger("sensor_manager")
        self.sensors = {}
        self.running = False
        self.data_buffer = {}
        self.update_interval = 30  # 秒
        
        # センサーインスタンスの作成
        self._initialize_sensors()
    
    def _initialize_sensors(self):
        """センサーを初期化"""
        try:
            # 温湿度センサー
            self.sensors['temperature_humidity'] = TemperatureHumiditySensor()
            
            # 土壌水分センサー
            self.sensors['soil_moisture'] = SoilMoistureSensor()
            
            # 圧力センサー（水の残量測定）
            self.sensors['pressure'] = PressureSensor()
            
            # フロートスイッチ
            self.sensors['float_switch'] = FloatSwitchSensor()
            
            # 各センサーを初期化
            for name, sensor in self.sensors.items():
                if sensor.initialize():
                    self.logger.info(f"センサー {name} が正常に初期化されました")
                else:
                    self.logger.error(f"センサー {name} の初期化に失敗しました")
            
        except Exception as e:
            self.logger.error(f"センサー初期化エラー: {str(e)}")
    
    def start_monitoring(self):
        """センサー監視を開始"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_sensors)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("センサー監視を開始しました")
    
    def stop_monitoring(self):
        """センサー監視を停止"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        self.logger.info("センサー監視を停止しました")
    
    def _monitor_sensors(self):
        """センサーの定期監視"""
        while self.running:
            try:
                # 各センサーからデータを取得
                for name, sensor in self.sensors.items():
                    if sensor.is_healthy():
                        data = sensor.read_data()
                        self.data_buffer[name] = data
                        
                        # エラーデータの場合は警告
                        if data.get('error', False):
                            self.logger.warning(f"センサー {name} からエラーデータを取得")
                
                # データをログに記録
                self._log_sensor_data()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"センサー監視エラー: {str(e)}")
                time.sleep(5)
    
    def get_all_data(self) -> Dict[str, Any]:
        """全センサーのデータを取得"""
        return self.data_buffer.copy()
    
    def get_sensor_data(self, sensor_name: str) -> Dict[str, Any]:
        """指定センサーのデータを取得"""
        return self.data_buffer.get(sensor_name, {})
    
    def _log_sensor_data(self):
        """センサーデータをログに記録"""
        for name, data in self.data_buffer.items():
            if not data.get('error', False):
                self.logger.info(f"センサー {name}: {data}")
```

## 🧪 テスト方法

### 1. 個別センサーテスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# 個別テスト実行
python -c "
from src.sensors.temperature_humidity import TemperatureHumiditySensor
sensor = TemperatureHumiditySensor()
if sensor.initialize():
    data = sensor.read_data()
    print(f'温湿度データ: {data}')
"
```

### 2. 統合テスト
```bash
# センサーマネージャーのテスト
python -c "
from src.sensors.sensor_manager import SensorManager
manager = SensorManager()
manager.start_monitoring()
time.sleep(60)
data = manager.get_all_data()
print(f'全センサーデータ: {data}')
manager.stop_monitoring()
"
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

