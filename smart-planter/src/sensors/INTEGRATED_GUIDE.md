# センサー制御機能 統合実装ガイド

## 📋 概要
温湿度センサー(AHT25)と土壌水分センサー(SEN0193)の制御機能を実装するための詳細手順書

## 🎯 実装目標
- AHT25温湿度センサーのI2C通信制御
- SEN0193土壌水分センサーのADC制御
- センサー値のフィルタリング処理
- エラーハンドリングと故障時対応
- データ取得の定期実行

## 🛠️ 必要な環境

### ハードウェア
- Raspberry Pi 5
- 温湿度センサー AHT25
- 土壌水分センサー SEN0193
- ADC MCP3002
- ジャンパーワイヤー
- ブレッドボード

### ソフトウェア
- Python 3.11.x
- RPi.GPIO
- smbus2 (I2C通信用)
- spidev (SPI通信用)
- numpy (データ処理用)

## 🔧 実装手順

### Step 1: ハードウェア接続

#### 1.1 GPIOピン配置
```python
# GPIOピン定義
GPIO_PINS = {
    # I2C通信 (AHT25温湿度センサー)
    'I2C_SDA': 2,  # GPIO 2 (Pin 3)
    'I2C_SCL': 3,  # GPIO 3 (Pin 5)
    
    # SPI通信 (MCP3002 ADC)
    'SPI_MOSI': 10,  # GPIO 10 (Pin 19)
    'SPI_MISO': 9,   # GPIO 9 (Pin 21)
    'SPI_SCLK': 11,  # GPIO 11 (Pin 23)
    'SPI_CE0': 8,    # GPIO 8 (Pin 24)
    
    # フロートスイッチ
    'FLOAT_SWITCH': 18,  # GPIO 18 (Pin 12)
    
    # リレーモジュール (水ポンプ制御)
    'RELAY_PUMP': 16,    # GPIO 16 (Pin 36)
}
```

#### 1.2 配線図
```
AHT25温湿度センサー:
- VCC → 3.3V (Pin 1)
- GND → GND (Pin 6)
- SDA → GPIO 2 (Pin 3)
- SCL → GPIO 3 (Pin 5)

SEN0193土壌水分センサー:
- VCC → 5V (Pin 2)
- GND → GND (Pin 6)
- SIG → MCP3002 CH0

MCP3002 ADC:
- VDD → 3.3V (Pin 1)
- VREF → 3.3V (Pin 1)
- AGND → GND (Pin 6)
- DGND → GND (Pin 6)
- CLK → GPIO 11 (Pin 23)
- DOUT → GPIO 9 (Pin 21)
- DIN → GPIO 10 (Pin 19)
- CS/SHDN → GPIO 8 (Pin 24)
```

### Step 2: システム設定

#### 2.1 I2C・SPI有効化
```bash
# Raspberry Pi設定
sudo raspi-config

# 選択項目:
# 3 Interface Options
#   P4 I2C → Enable
#   P5 SPI → Enable

# 再起動
sudo reboot
```

#### 2.2 必要なライブラリインストール
```bash
# Pythonライブラリインストール
pip install RPi.GPIO
pip install smbus2
pip install spidev
pip install numpy
```

---

## 📁 ファイル作成手順（新人エンジニア向け）

### Step 3: ファイル構造の作成

#### 3.1 センサーディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# センサーディレクトリの確認
ls -la src/sensors/
```

#### 3.2 各ファイルの作成順序
1. `src/sensors/base_sensor.py` - 基底クラス
2. `src/sensors/temperature_humidity.py` - 温湿度センサー
3. `src/sensors/soil_moisture.py` - 土壌水分センサー
4. `src/sensors/float_switch.py` - フロートスイッチ
5. `src/sensors/sensor_manager.py` - 統合管理

#### 3.3 ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/sensors/base_sensor.py
touch src/sensors/temperature_humidity.py
touch src/sensors/soil_moisture.py
touch src/sensors/float_switch.py
touch src/sensors/sensor_manager.py
```

## 📄 実装コード

### 📄 base_sensor.py
センサーの基底クラス

```python
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseSensor(ABC):
    """センサーの基底クラス"""
    
    def __init__(self, name: str, pin: int):
        self.name = name                    # センサー名を設定
        self.pin = pin                     # GPIOピン番号を設定
        self.error_count = 0               # エラーカウントを初期化
        self.max_errors = 3                # 最大エラー数を設定
        self.is_enabled = True             # センサー有効フラグを設定
        self.logger = logging.getLogger(f"sensor.{name}")  # ロガーを取得
        
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
        return self.error_count < self.max_errors and self.is_enabled  # エラー数が閾値以下かつ有効かチェック
    
    def reset_error_count(self):
        """エラーカウントをリセット"""
        self.error_count = 0               # エラーカウントを0にリセット
    
    def increment_error_count(self):
        """エラーカウントを増加"""
        self.error_count += 1              # エラーカウントを1増加
        if self.error_count >= self.max_errors:  # 最大エラー数に達した場合
            self.logger.error(f"{self.name} センサーが故障状態になりました")  # エラーログ出力
            self.is_enabled = False        # センサーを無効化
```

### 📄 aht25_sensor.py
AHT25温湿度センサー制御クラス

```python
import smbus2
import time
from typing import Dict, Any
from .base_sensor import BaseSensor

class AHT25Sensor(BaseSensor):
    """AHT25温湿度センサー制御クラス"""
    
    def __init__(self):
        super().__init__("AHT25", 0)       # 基底クラスを初期化
        self.bus = smbus2.SMBus(1)         # I2C bus 1を初期化
        self.address = 0x38                # AHT25のI2Cアドレスを設定
        self.initialized = False           # 初期化フラグを設定
        
    def initialize(self) -> bool:
        """AHT25センサーを初期化"""
        try:
            # センサーリセット
            self.bus.write_byte(self.address, 0xBA)  # リセットコマンド送信
            time.sleep(0.1)                # 100ms待機
            
            # 初期化コマンド
            self.bus.write_byte(self.address, 0xBE)  # 初期化コマンド送信
            self.bus.write_byte(self.address, 0x08)  # パラメータ送信
            self.bus.write_byte(self.address, 0x00)  # パラメータ送信
            time.sleep(0.1)                # 100ms待機
            
            self.initialized = True        # 初期化完了フラグを設定
            self.logger.info("AHT25センサー初期化完了")  # 成功ログ出力
            return True                    # 成功を返す
            
        except Exception as e:
            self.logger.error(f"AHT25初期化エラー: {str(e)}")  # エラーログ出力
            self.increment_error_count()   # エラーカウント増加
            return False                   # 失敗を返す
    
    def read_data(self) -> Dict[str, Any]:
        """温湿度データを読み取る"""
        if not self.initialized:           # 初期化されていない場合
            if not self.initialize():      # 初期化を試行
                return {"error": "初期化失敗"}  # 初期化失敗を返す
        
        try:
            # 測定開始コマンド
            self.bus.write_byte(self.address, 0xAC)  # 測定開始コマンド送信
            self.bus.write_byte(self.address, 0x33)  # パラメータ送信
            self.bus.write_byte(self.address, 0x00)  # パラメータ送信
            
            # 測定完了待機
            time.sleep(0.1)                # 100ms待機
            
            # データ読み取り
            data = self.bus.read_i2c_block_data(self.address, 0x00, 6)  # 6バイト読み取り
            
            # データ解析
            humidity_raw = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)  # 湿度データを結合
            temperature_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]  # 温度データを結合
            
            # 値に変換
            humidity = (humidity_raw / 0x100000) * 100  # 湿度をパーセントに変換
            temperature = (temperature_raw / 0x100000) * 200 - 50  # 温度を摂氏に変換
            
            # 値の妥当性チェック
            if not (0 <= humidity <= 100) or not (-40 <= temperature <= 85):  # 範囲チェック
                raise ValueError("センサー値が範囲外です")  # 範囲外エラー
            
            self.reset_error_count()       # エラーカウントリセット
            return {                       # 成功データを返す
                "temperature": round(temperature, 1),  # 温度を小数点1桁で丸める
                "humidity": round(humidity, 1),         # 湿度を小数点1桁で丸める
                "timestamp": time.time()                 # タイムスタンプを追加
            }
            
        except Exception as e:
            self.logger.error(f"AHT25読み取りエラー: {str(e)}")  # エラーログ出力
            self.increment_error_count()   # エラーカウント増加
            return {"error": str(e)}       # エラー情報を返す
    
    def get_status(self) -> Dict[str, Any]:
        """センサー状態を取得"""
        return {                          # 状態情報を返す
            "name": self.name,            # センサー名
            "enabled": self.is_enabled,   # 有効フラグ
            "error_count": self.error_count,  # エラーカウント
            "healthy": self.is_healthy(), # 健全性
            "initialized": self.initialized  # 初期化フラグ
        }
```

### 📄 sen0193_sensor.py
SEN0193土壌水分センサー制御クラス

```python
import spidev
import time
import numpy as np
from typing import Dict, Any, List
from .base_sensor import BaseSensor

class SEN0193Sensor(BaseSensor):
    """SEN0193土壌水分センサー制御クラス"""
    
    def __init__(self):
        super().__init__("SEN0193", 0)     # 基底クラスを初期化
        self.spi = spidev.SpiDev()         # SPIデバイスを初期化
        self.spi.open(0, 0)               # SPI bus 0, device 0を開く
        self.spi.max_speed_hz = 1000000   # SPI速度を1MHzに設定
        self.channel = 0                  # MCP3002 CH0を設定
        self.reading_history = []         # 読み取り履歴を初期化
        self.max_history = 10             # 最大履歴数を設定
        
    def initialize(self) -> bool:
        """SEN0193センサーを初期化"""
        try:
            # SPI通信テスト
            test_data = self._read_adc(self.channel)  # ADC読み取りテスト
            if test_data is None:         # テスト失敗の場合
                raise Exception("SPI通信テスト失敗")  # エラー発生
            
            self.logger.info("SEN0193センサー初期化完了")  # 成功ログ出力
            return True                    # 成功を返す
            
        except Exception as e:
            self.logger.error(f"SEN0193初期化エラー: {str(e)}")  # エラーログ出力
            self.increment_error_count()   # エラーカウント増加
            return False                   # 失敗を返す
    
    def _read_adc(self, channel: int) -> Optional[int]:
        """ADCから値を読み取る"""
        try:
            # MCP3002用のSPI通信
            adc = self.spi.xfer2([1, (8 + channel) << 4, 0])  # SPI通信実行
            data = ((adc[1] & 3) << 8) + adc[2]  # データを結合
            return data                    # データを返す
        except Exception as e:
            self.logger.error(f"ADC読み取りエラー: {str(e)}")  # エラーログ出力
            return None                   # Noneを返す
    
    def read_data(self) -> Dict[str, Any]:
        """土壌水分データを読み取る"""
        try:
            # 複数回読み取りでノイズ除去
            readings = []                 # 読み取り値リストを初期化
            for _ in range(5):            # 5回読み取り
                value = self._read_adc(self.channel)  # ADC読み取り
                if value is not None:     # 読み取り成功の場合
                    readings.append(value) # リストに追加
                time.sleep(0.01)          # 10ms待機
            
            if not readings:              # 読み取り値がない場合
                raise Exception("ADC読み取り失敗")  # エラー発生
            
            # 平均値計算
            raw_value = np.mean(readings) # 平均値を計算
            
            # 履歴に追加
            self.reading_history.append(raw_value)  # 履歴に追加
            if len(self.reading_history) > self.max_history:  # 履歴数が上限を超えた場合
                self.reading_history.pop(0)  # 古い履歴を削除
            
            # 移動平均でフィルタリング
            filtered_value = np.mean(self.reading_history)  # 移動平均を計算
            
            # 土壌水分率に変換 (0-1023 → 0-100%)
            moisture_percentage = (filtered_value / 1023) * 100  # パーセントに変換
            
            # 値の妥当性チェック
            if not (0 <= moisture_percentage <= 100):  # 範囲チェック
                raise ValueError("土壌水分値が範囲外です")  # 範囲外エラー
            
            self.reset_error_count()       # エラーカウントリセット
            return {                       # 成功データを返す
                "raw_value": int(raw_value),  # 生の値を整数で返す
                "filtered_value": int(filtered_value),  # フィルタ済み値を整数で返す
                "moisture_percentage": round(moisture_percentage, 1),  # 土壌水分率を小数点1桁で返す
                "timestamp": time.time()   # タイムスタンプを追加
            }
            
        except Exception as e:
            self.logger.error(f"SEN0193読み取りエラー: {str(e)}")  # エラーログ出力
            self.increment_error_count()   # エラーカウント増加
            return {"error": str(e)}       # エラー情報を返す
    
    def get_status(self) -> Dict[str, Any]:
        """センサー状態を取得"""
        return {                          # 状態情報を返す
            "name": self.name,            # センサー名
            "enabled": self.is_enabled,   # 有効フラグ
            "error_count": self.error_count,  # エラーカウント
            "healthy": self.is_healthy(), # 健全性
            "reading_history_length": len(self.reading_history)  # 履歴長
        }
```

### 📄 float_switch.py
フロートスイッチ制御クラス

```python
import RPi.GPIO as GPIO
import time
from typing import Dict, Any
from .base_sensor import BaseSensor

class FloatSwitch(BaseSensor):
    """フロートスイッチ制御クラス"""
    
    def __init__(self, pin: int = 18):
        super().__init__("FloatSwitch", pin)  # 基底クラスを初期化
        GPIO.setmode(GPIO.BCM)            # GPIO番号をBCMモードに設定
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # ピンを入力に設定、プルアップ有効
        
    def initialize(self) -> bool:
        """フロートスイッチを初期化"""
        try:
            # 初期状態確認
            initial_state = self.read_data()  # 初期状態を読み取り
            self.logger.info(f"フロートスイッチ初期化完了: {initial_state}")  # 成功ログ出力
            return True                    # 成功を返す
        except Exception as e:
            self.logger.error(f"フロートスイッチ初期化エラー: {str(e)}")  # エラーログ出力
            self.increment_error_count()   # エラーカウント増加
            return False                   # 失敗を返す
    
    def read_data(self) -> Dict[str, Any]:
        """フロートスイッチの状態を読み取る"""
        try:
            # デバウンス処理
            readings = []                 # 読み取り値リストを初期化
            for _ in range(5):            # 5回読み取り
                readings.append(GPIO.input(self.pin))  # GPIO状態を読み取り
                time.sleep(0.01)          # 10ms待機
            
            # 多数決で状態決定
            state = 1 if sum(readings) >= 3 else 0  # 3回以上HIGHなら1、そうでなければ0
            is_water_available = bool(state)  # ブール値に変換
            
            self.reset_error_count()       # エラーカウントリセット
            return {                       # 成功データを返す
                "is_water_available": is_water_available,  # 水位有無フラグ
                "raw_state": state,        # 生の状態値
                "timestamp": time.time()   # タイムスタンプ
            }
            
        except Exception as e:
            self.logger.error(f"フロートスイッチ読み取りエラー: {str(e)}")  # エラーログ出力
            self.increment_error_count()   # エラーカウント増加
            return {"error": str(e)}       # エラー情報を返す
    
    def get_status(self) -> Dict[str, Any]:
        """センサー状態を取得"""
        return {                          # 状態情報を返す
            "name": self.name,            # センサー名
            "enabled": self.is_enabled,   # 有効フラグ
            "error_count": self.error_count,  # エラーカウント
            "healthy": self.is_healthy(), # 健全性
            "pin": self.pin               # GPIOピン番号
        }
```

### 📄 sensor_manager.py
センサー管理クラス

```python
import threading
import time
import logging
from typing import Dict, Any, List
from .aht25_sensor import AHT25Sensor
from .sen0193_sensor import SEN0193Sensor
from .float_switch import FloatSwitch

class SensorManager:
    """センサー管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger("sensor_manager")  # ロガーを取得
        self.sensors = {}                 # センサー辞書を初期化
        self.data_cache = {}              # データキャッシュを初期化
        self.running = False              # 実行フラグを初期化
        self.threads = {}                 # スレッド辞書を初期化
        
        # センサー初期化
        self._initialize_sensors()        # センサーを初期化
        
    def _initialize_sensors(self):
        """センサーを初期化"""
        try:
            # 温湿度センサー
            self.sensors['temperature_humidity'] = AHT25Sensor()  # AHT25センサーを作成
            
            # 土壌水分センサー
            self.sensors['soil_moisture'] = SEN0193Sensor()  # SEN0193センサーを作成
            
            # フロートスイッチ
            self.sensors['water_level'] = FloatSwitch()  # フロートスイッチを作成
            
            self.logger.info("全センサー初期化完了")  # 成功ログ出力
            
        except Exception as e:
            self.logger.error(f"センサー初期化エラー: {str(e)}")  # エラーログ出力
    
    def start_monitoring(self):
        """センサー監視開始"""
        self.running = True               # 実行フラグを設定
        
        # 温湿度センサー監視 (30分間隔)
        self.threads['temperature_humidity'] = threading.Thread(  # スレッドを作成
            target=self._monitor_temperature_humidity,  # 監視関数を指定
            daemon=True                   # デーモンスレッドに設定
        )
        self.threads['temperature_humidity'].start()  # スレッド開始
        
        # 土壌水分センサー監視 (5分間隔)
        self.threads['soil_moisture'] = threading.Thread(  # スレッドを作成
            target=self._monitor_soil_moisture,  # 監視関数を指定
            daemon=True                   # デーモンスレッドに設定
        )
        self.threads['soil_moisture'].start()  # スレッド開始
        
        # フロートスイッチ監視 (1分間隔)
        self.threads['water_level'] = threading.Thread(  # スレッドを作成
            target=self._monitor_water_level,  # 監視関数を指定
            daemon=True                   # デーモンスレッドに設定
        )
        self.threads['water_level'].start()  # スレッド開始
        
        self.logger.info("センサー監視開始")  # 開始ログ出力
    
    def stop_monitoring(self):
        """センサー監視停止"""
        self.running = False              # 実行フラグをクリア
        self.logger.info("センサー監視停止")  # 停止ログ出力
    
    def _monitor_temperature_humidity(self):
        """温湿度センサー監視"""
        while self.running:               # 実行中の場合
            try:
                data = self.sensors['temperature_humidity'].read_data()  # データ読み取り
                if 'error' not in data:   # エラーがない場合
                    self.data_cache['temperature_humidity'] = data  # キャッシュに保存
                    self.logger.debug(f"温湿度データ更新: {data}")  # デバッグログ出力
                else:
                    self.logger.error(f"温湿度センサーエラー: {data['error']}")  # エラーログ出力
                
                time.sleep(1800)          # 30分待機
                
            except Exception as e:
                self.logger.error(f"温湿度監視エラー: {str(e)}")  # エラーログ出力
                time.sleep(60)            # エラー時は1分待機
    
    def _monitor_soil_moisture(self):
        """土壌水分センサー監視"""
        while self.running:               # 実行中の場合
            try:
                data = self.sensors['soil_moisture'].read_data()  # データ読み取り
                if 'error' not in data:   # エラーがない場合
                    self.data_cache['soil_moisture'] = data  # キャッシュに保存
                    self.logger.debug(f"土壌水分データ更新: {data}")  # デバッグログ出力
                else:
                    self.logger.error(f"土壌水分センサーエラー: {data['error']}")  # エラーログ出力
                
                time.sleep(300)            # 5分待機
                
            except Exception as e:
                self.logger.error(f"土壌水分監視エラー: {str(e)}")  # エラーログ出力
                time.sleep(60)            # エラー時は1分待機
    
    def _monitor_water_level(self):
        """フロートスイッチ監視"""
        while self.running:               # 実行中の場合
            try:
                data = self.sensors['water_level'].read_data()  # データ読み取り
                if 'error' not in data:   # エラーがない場合
                    self.data_cache['water_level'] = data  # キャッシュに保存
                    self.logger.debug(f"水位データ更新: {data}")  # デバッグログ出力
                else:
                    self.logger.error(f"フロートスイッチエラー: {data['error']}")  # エラーログ出力
                
                time.sleep(60)             # 1分待機
                
            except Exception as e:
                self.logger.error(f"水位監視エラー: {str(e)}")  # エラーログ出力
                time.sleep(30)             # エラー時は30秒待機
    
    def get_latest_data(self, sensor_name: str = None) -> Dict[str, Any]:
        """最新のセンサーデータを取得"""
        if sensor_name:                   # 特定センサー指定の場合
            return self.data_cache.get(sensor_name, {})  # 指定センサーのデータを返す
        return self.data_cache.copy()     # 全センサーデータをコピーして返す
    
    def get_sensor_status(self) -> Dict[str, Any]:
        """全センサーの状態を取得"""
        status = {}                       # 状態辞書を初期化
        for name, sensor in self.sensors.items():  # 全センサーをループ
            status[name] = sensor.get_status()  # 各センサーの状態を取得
        return status                     # 状態辞書を返す
    
    def force_read(self, sensor_name: str) -> Dict[str, Any]:
        """指定センサーの強制読み取り"""
        if sensor_name in self.sensors:   # センサーが存在する場合
            return self.sensors[sensor_name].read_data()  # データ読み取りを実行
        return {"error": "センサーが見つかりません"}  # エラーを返す
```

---

## 📊 実装完了チェックリスト

- [ ] ハードウェア接続完了
- [ ] I2C・SPI有効化完了
- [ ] 必要なライブラリインストール完了
- [ ] 基本センサークラス実装完了
- [ ] AHT25センサークラス実装完了
- [ ] SEN0193センサークラス実装完了
- [ ] フロートスイッチクラス実装完了
- [ ] センサーマネージャークラス実装完了
- [ ] テストスクリプト実行完了
- [ ] エラーハンドリング確認完了
- [ ] ログ出力確認完了

## 🎯 次のステップ

1. **自動給水機能実装**: センサーデータに基づく給水制御
2. **データ保存機能**: CSV形式でのデータ保存
3. **LINE通知統合**: センサー異常時の通知
4. **Web UI統合**: リアルタイムデータ表示

---

## 🏗️ クラス全体の流れと意味

### **BaseSensorクラス**
**意味**: 全てのセンサーの共通機能を提供する基底クラス
**役割**: 
- センサーの基本的な状態管理（有効/無効、エラーカウント）
- 共通のエラーハンドリング機能
- 抽象メソッドでサブクラスに実装を強制

### **AHT25Sensorクラス**
**意味**: AHT25温湿度センサー専用の制御クラス
**役割**:
- I2C通信による温湿度データ取得
- データの妥当性チェックと変換
- センサー固有の初期化処理

### **SEN0193Sensorクラス**
**意味**: SEN0193土壌水分センサー専用の制御クラス
**役割**:
- SPI通信によるADC値読み取り
- ノイズ除去のための複数回読み取り
- 移動平均によるフィルタリング

### **FloatSwitchクラス**
**意味**: フロートスイッチによる水位検知クラス
**役割**:
- GPIO入力による水位状態検知
- デバウンス処理による誤検知防止
- 水タンクの空状態監視

### **SensorManagerクラス**
**意味**: 全センサーの統合管理クラス
**役割**:
- 複数センサーの並行監視
- データキャッシュによる効率的なデータ管理
- スレッドベースの非同期監視

**全体の流れ**:
1. **初期化**: 各センサーを個別に初期化
2. **監視開始**: 各センサーを独立したスレッドで監視
3. **データ取得**: 定期的にセンサーデータを読み取り
4. **データ管理**: 取得したデータをキャッシュに保存
5. **状態管理**: センサーの健全性を継続的に監視
6. **エラー処理**: 故障時は自動的に無効化

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

