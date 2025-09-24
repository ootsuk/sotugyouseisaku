# 自動給水機能 統合実装ガイド

## 📋 概要
土壌水分センサーの値に基づいて自動で水やりを行う機能の詳細実装手順書

## 🎯 実装目標
- 土壌水分値159以下での自動給水判定
- 前回給水から12時間経過の確認
- リレーモジュールによる水ポンプ制御
- 安全機能（連続給水防止、水タンク空検知）
- 給水履歴の記録と通知

## 🛠️ 必要な環境

### ハードウェア
- Raspberry Pi 5
- リレーモジュール AE-G5V-DRV
- 水中ポンプ（12V DC）
- 外部電源（ポンプ用）
- 水タンク
- 配管・ホース

### ソフトウェア
- Python 3.11.x
- RPi.GPIO
- センサー制御システム（前回実装）
- LINE通知システム

## 🔧 実装手順

### Step 1: ハードウェア接続

#### 1.1 リレーモジュール接続
```python
# GPIOピン定義
GPIO_PINS = {
    'RELAY_PUMP': 16,    # GPIO 16 (Pin 36) - ポンプ制御
    'RELAY_LED': 20,     # GPIO 20 (Pin 38) - LED制御（将来用）
}
```

#### 1.2 配線図
```
リレーモジュール AE-G5V-DRV:
- VCC → 5V (Pin 2)
- GND → GND (Pin 6)
- IN1 → GPIO 16 (Pin 36) - ポンプ制御
- IN2 → GPIO 20 (Pin 38) - LED制御（将来用）

水中ポンプ:
- 正極 → リレーモジュール NO1
- 負極 → リレーモジュール COM1
- 電源 → 外部12V電源

外部電源:
- 12V電源アダプター
- リレーモジュール VCC/GND接続
```

#### 1.3 安全回路
```
安全機能:
1. フロートスイッチによる水タンク空検知
2. 連続給水回数制限（最大2回）
3. 給水時間制限（最大5秒）
4. 緊急停止機能
```

---

## 📁 ファイル作成手順（新人エンジニア向け）

### Step 3: ファイル構造の作成

#### 3.1 給水ディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# 給水ディレクトリの確認
ls -la src/watering/
```

#### 3.2 各ファイルの作成順序
1. `src/watering/pump_control.py` - ポンプ制御
2. `src/watering/watering_logic.py` - 給水判定ロジック
3. `src/watering/watering_scheduler.py` - スケジューラー

#### 3.3 ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/watering/pump_control.py
touch src/watering/watering_logic.py
touch src/watering/watering_scheduler.py
```

## 📄 実装コード

### 📄 watering_controller.py
給水制御クラス

```python
import RPi.GPIO as GPIO
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

class WateringController:
    """自動給水制御クラス"""
    
    def __init__(self, relay_pin: int = 16):
        self.relay_pin = relay_pin        # リレーピン番号を設定
        self.logger = logging.getLogger("watering_controller")  # ロガーを取得
        
        # 給水設定
        self.soil_moisture_threshold = 159  # 給水閾値を設定
        self.watering_interval_hours = 12   # 給水間隔（時間）を設定
        self.watering_duration_seconds = 5  # 給水時間（秒）を設定
        self.max_consecutive_waterings = 2  # 最大連続給水回数を設定
        self.water_amount_ml = 100          # 給水量（ml）を設定
        
        # 状態管理
        self.last_watering_time = None     # 最後の給水時間を初期化
        self.consecutive_watering_count = 0  # 連続給水カウントを初期化
        self.is_watering = False           # 給水中フラグを初期化
        self.watering_history = []         # 給水履歴を初期化
        
        # ファイルパス
        self.data_dir = Path("/mnt/usb-storage/watering_data")  # データディレクトリを設定
        self.data_dir.mkdir(exist_ok=True) # ディレクトリを作成
        self.history_file = self.data_dir / "watering_history.json"  # 履歴ファイルパスを設定
        
        # GPIO初期化
        self._initialize_gpio()           # GPIOを初期化
        
        # 履歴読み込み
        self._load_watering_history()     # 給水履歴を読み込み
    
    def _initialize_gpio(self):
        """GPIO初期化"""
        try:
            GPIO.setmode(GPIO.BCM)        # GPIO番号をBCMモードに設定
            GPIO.setup(self.relay_pin, GPIO.OUT)  # リレーピンを出力に設定
            GPIO.output(self.relay_pin, GPIO.HIGH)  # リレーOFF（HIGHでOFF）
            self.logger.info("GPIO初期化完了")  # 成功ログ出力
        except Exception as e:
            self.logger.error(f"GPIO初期化エラー: {str(e)}")  # エラーログ出力
            raise                        # エラーを再発生
    
    def _load_watering_history(self):
        """給水履歴を読み込み"""
        try:
            if self.history_file.exists(): # 履歴ファイルが存在する場合
                with open(self.history_file, 'r', encoding='utf-8') as f:  # ファイルを開く
                    history_data = json.load(f)  # JSONデータを読み込み
                    self.watering_history = history_data.get('history', [])  # 履歴を取得
                    if self.watering_history:  # 履歴がある場合
                        last_record = self.watering_history[-1]  # 最後の記録を取得
                        self.last_watering_time = datetime.fromisoformat(  # 時間を復元
                            last_record['timestamp']
                        )
                        self.consecutive_watering_count = last_record.get(  # 連続カウントを復元
                            'consecutive_count', 0
                        )
                self.logger.info(f"給水履歴読み込み完了: {len(self.watering_history)}件")  # 成功ログ出力
        except Exception as e:
            self.logger.error(f"給水履歴読み込みエラー: {str(e)}")  # エラーログ出力
            self.watering_history = []    # 履歴を空にリセット
    
    def _save_watering_history(self):
        """給水履歴を保存"""
        try:
            history_data = {              # 履歴データを構築
                'last_updated': datetime.now().isoformat(),  # 最終更新時間を設定
                'history': self.watering_history[-100:]  # 最新100件のみ保存
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:  # ファイルを開く
                json.dump(history_data, f, ensure_ascii=False, indent=2)  # JSONで保存
        except Exception as e:
            self.logger.error(f"給水履歴保存エラー: {str(e)}")  # エラーログ出力
    
    def _can_water(self, soil_moisture: float, water_available: bool) -> Dict[str, Any]:
        """給水可能かチェック"""
        checks = {                        # チェック項目を初期化
            'soil_moisture_ok': soil_moisture <= self.soil_moisture_threshold,  # 土壌水分チェック
            'water_available': water_available,  # 水位チェック
            'interval_ok': True,          # 間隔チェックを初期化
            'consecutive_limit_ok': self.consecutive_watering_count < self.max_consecutive_waterings,  # 連続制限チェック
            'not_currently_watering': not self.is_watering  # 給水中でないかチェック
        }
        
        # 給水間隔チェック
        if self.last_watering_time:       # 最後の給水時間がある場合
            time_since_last = datetime.now() - self.last_watering_time  # 経過時間を計算
            checks['interval_ok'] = time_since_last >= timedelta(hours=self.watering_interval_hours)  # 間隔チェック
        
        can_water = all(checks.values())  # 全条件を満たすかチェック
        
        return {                          # チェック結果を返す
            'can_water': can_water,       # 給水可能フラグ
            'checks': checks,             # 各チェック結果
            'time_since_last': str(time_since_last) if self.last_watering_time else None  # 経過時間
        }
    
    def start_watering(self, soil_moisture: float, water_available: bool) -> Dict[str, Any]:
        """給水開始"""
        if self.is_watering:              # 既に給水中の場合
            return {                      # エラーを返す
                'success': False,
                'message': '既に給水中です',
                'error': 'ALREADY_WATERING'
            }
        
        # 給水可能かチェック
        check_result = self._can_water(soil_moisture, water_available)  # 給水条件をチェック
        if not check_result['can_water']: # 給水条件を満たさない場合
            return {                      # エラーを返す
                'success': False,
                'message': '給水条件を満たしていません',
                'error': 'CONDITIONS_NOT_MET',
                'checks': check_result['checks']
            }
        
        try:
            self.is_watering = True      # 給水中フラグを設定
            self.logger.info("給水開始")  # 開始ログ出力
            
            # リレーON（LOWでON）
            GPIO.output(self.relay_pin, GPIO.LOW)  # リレーをONに設定
            
            # 給水時間待機
            time.sleep(self.watering_duration_seconds)  # 給水時間待機
            
            # リレーOFF
            GPIO.output(self.relay_pin, GPIO.HIGH)  # リレーをOFFに設定
            
            # 状態更新
            self.last_watering_time = datetime.now()  # 給水時間を記録
            self.consecutive_watering_count += 1     # 連続カウントを増加
            
            # 履歴記録
            watering_record = {           # 給水記録を構築
                'timestamp': self.last_watering_time.isoformat(),  # タイムスタンプ
                'soil_moisture': soil_moisture,  # 土壌水分値
                'duration_seconds': self.watering_duration_seconds,  # 給水時間
                'water_amount_ml': self.water_amount_ml,  # 給水量
                'consecutive_count': self.consecutive_watering_count,  # 連続カウント
                'success': True           # 成功フラグ
            }
            self.watering_history.append(watering_record)  # 履歴に追加
            self._save_watering_history() # 履歴を保存
            
            self.logger.info(f"給水完了: {self.water_amount_ml}ml")  # 完了ログ出力
            
            return {                      # 成功結果を返す
                'success': True,
                'message': f'給水完了: {self.water_amount_ml}ml',
                'watering_record': watering_record
            }
            
        except Exception as e:
            self.logger.error(f"給水エラー: {str(e)}")  # エラーログ出力
            
            # リレーOFF（安全のため）
            GPIO.output(self.relay_pin, GPIO.HIGH)  # リレーを強制OFF
            
            # エラー履歴記録
            error_record = {              # エラー記録を構築
                'timestamp': datetime.now().isoformat(),  # タイムスタンプ
                'soil_moisture': soil_moisture,  # 土壌水分値
                'error': str(e),           # エラーメッセージ
                'success': False           # 失敗フラグ
            }
            self.watering_history.append(error_record)  # 履歴に追加
            self._save_watering_history() # 履歴を保存
            
            return {                      # エラー結果を返す
                'success': False,
                'message': f'給水エラー: {str(e)}',
                'error': 'WATERING_ERROR'
            }
        
        finally:
            self.is_watering = False     # 給水中フラグをクリア
    
    def stop_watering(self) -> Dict[str, Any]:
        """給水強制停止"""
        try:
            if self.is_watering:          # 給水中の場合
                GPIO.output(self.relay_pin, GPIO.HIGH)  # リレーをOFFに設定
                self.is_watering = False # 給水中フラグをクリア
                self.logger.info("給水強制停止")  # 停止ログ出力
                return {'success': True, 'message': '給水停止完了'}  # 成功を返す
            else:
                return {'success': False, 'message': '給水中ではありません'}  # エラーを返す
        except Exception as e:
            self.logger.error(f"給水停止エラー: {str(e)}")  # エラーログ出力
            return {'success': False, 'message': f'停止エラー: {str(e)}'}  # エラーを返す
    
    def reset_consecutive_count(self):
        """連続給水カウントリセット"""
        self.consecutive_watering_count = 0  # 連続カウントをリセット
        self.logger.info("連続給水カウントリセット")  # リセットログ出力
    
    def get_status(self) -> Dict[str, Any]:
        """給水システム状態取得"""
        return {                          # 状態情報を返す
            'is_watering': self.is_watering,  # 給水中フラグ
            'last_watering_time': self.last_watering_time.isoformat() if self.last_watering_time else None,  # 最後の給水時間
            'consecutive_watering_count': self.consecutive_watering_count,  # 連続給水カウント
            'max_consecutive_waterings': self.max_consecutive_waterings,  # 最大連続給水回数
            'soil_moisture_threshold': self.soil_moisture_threshold,  # 土壌水分閾値
            'watering_interval_hours': self.watering_interval_hours,  # 給水間隔
            'watering_duration_seconds': self.watering_duration_seconds,  # 給水時間
            'water_amount_ml': self.water_amount_ml,  # 給水量
            'history_count': len(self.watering_history)  # 履歴件数
        }
    
    def get_recent_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """最近の給水履歴取得"""
        return self.watering_history[-count:] if self.watering_history else []  # 最新N件を返す
    
    def cleanup(self):
        """リソースクリーンアップ"""
        try:
            GPIO.output(self.relay_pin, GPIO.HIGH)  # リレーOFF
            GPIO.cleanup()               # GPIOクリーンアップ
            self.logger.info("GPIOクリーンアップ完了")  # 完了ログ出力
        except Exception as e:
            self.logger.error(f"クリーンアップエラー: {str(e)}")  # エラーログ出力
```

### 📄 auto_watering_manager.py
自動給水管理クラス

```python
import threading
import time
import logging
from datetime import datetime
from typing import Dict, Any
from .watering_controller import WateringController
from ..sensors.sensor_manager import SensorManager
from ..notifications.line_notify import LineNotify

class AutoWateringManager:
    """自動給水管理クラス"""
    
    def __init__(self, sensor_manager: SensorManager, line_notify: LineNotify):
        self.sensor_manager = sensor_manager  # センサーマネージャーを設定
        self.line_notify = line_notify        # LINE通知を設定
        self.watering_controller = WateringController()  # 給水制御を初期化
        self.logger = logging.getLogger("auto_watering_manager")  # ロガーを取得
        
        self.running = False              # 実行フラグを初期化
        self.monitor_thread = None        # 監視スレッドを初期化
        
        # 保存間隔（秒）
        self.check_interval = 60         # チェック間隔を1分に設定
        
    def start_auto_watering(self):
        """自動給水開始"""
        if self.running:                  # 既に実行中の場合
            self.logger.warning("自動給水は既に実行中です")  # 警告ログ出力
            return
        
        self.running = True               # 実行フラグを設定
        self.monitor_thread = threading.Thread(  # 監視スレッドを作成
            target=self._monitor_and_water,  # 監視関数を指定
            daemon=True                   # デーモンスレッドに設定
        )
        self.monitor_thread.start()      # スレッド開始
        self.logger.info("自動給水監視開始")  # 開始ログ出力
    
    def stop_auto_watering(self):
        """自動給水停止"""
        self.running = False              # 実行フラグをクリア
        if self.monitor_thread:          # 監視スレッドがある場合
            self.monitor_thread.join(timeout=5)  # スレッド終了を待機
        self.logger.info("自動給水監視停止")  # 停止ログ出力
    
    def _monitor_and_water(self):
        """給水監視と実行"""
        while self.running:               # 実行中の場合
            try:
                # センサーデータ取得
                sensor_data = self.sensor_manager.get_latest_data()  # 最新データを取得
                
                # 土壌水分データ確認
                soil_moisture_data = sensor_data.get('soil_moisture', {})  # 土壌水分データを取得
                if 'error' in soil_moisture_data:  # エラーがある場合
                    self.logger.error(f"土壌水分センサーエラー: {soil_moisture_data['error']}")  # エラーログ出力
                    time.sleep(self.check_interval)  # チェック間隔待機
                    continue              # 次のループへ
                
                soil_moisture = soil_moisture_data.get('moisture_percentage', 0)  # 土壌水分値を取得
                
                # 水位データ確認
                water_level_data = sensor_data.get('water_level', {})  # 水位データを取得
                if 'error' in water_level_data:  # エラーがある場合
                    self.logger.error(f"フロートスイッチエラー: {water_level_data['error']}")  # エラーログ出力
                    time.sleep(self.check_interval)  # チェック間隔待機
                    continue              # 次のループへ
                
                water_available = water_level_data.get('is_water_available', False)  # 水位フラグを取得
                
                # 給水判定
                if soil_moisture <= self.watering_controller.soil_moisture_threshold:  # 土壌水分が閾値以下の場合
                    self.logger.info(f"土壌水分低下検知: {soil_moisture}%")  # 検知ログ出力
                    
                    # 給水実行
                    result = self.watering_controller.start_watering(  # 給水を実行
                        soil_moisture, water_available
                    )
                    
                    if result['success']: # 給水成功の場合
                        # 給水成功通知
                        self.line_notify.send_watering_notification(  # LINE通知送信
                            self.watering_controller.water_amount_ml
                        )
                        self.logger.info("給水完了通知送信")  # 通知ログ出力
                    else:
                        # 給水失敗通知
                        error_msg = result.get('message', '不明なエラー')  # エラーメッセージを取得
                        self.line_notify.send_system_error(f"給水失敗: {error_msg}")  # エラー通知送信
                        self.logger.error(f"給水失敗: {error_msg}")  # エラーログ出力
                
                # 水タンク空警告
                if not water_available:   # 水がない場合
                    self.logger.warning("水タンク空警告")  # 警告ログ出力
                    self.line_notify.send_water_tank_empty()  # 空警告通知送信
                
                time.sleep(self.check_interval)  # チェック間隔待機
                
            except Exception as e:
                self.logger.error(f"自動給水監視エラー: {str(e)}")  # エラーログ出力
                time.sleep(30)            # エラー時は30秒待機
    
    def manual_watering(self) -> Dict[str, Any]:
        """手動給水実行"""
        try:
            # 現在のセンサーデータ取得
            sensor_data = self.sensor_manager.get_latest_data()  # 最新データを取得
            soil_moisture = sensor_data.get('soil_moisture', {}).get('moisture_percentage', 0)  # 土壌水分値を取得
            water_available = sensor_data.get('water_level', {}).get('is_water_available', True)  # 水位フラグを取得
            
            # 手動給水実行
            result = self.watering_controller.start_watering(soil_moisture, water_available)  # 給水を実行
            
            if result['success']:         # 給水成功の場合
                # 手動給水完了通知
                self.line_notify.send_message(  # LINE通知送信
                    f"🌱 手動給水完了！\n"
                    f"💧 給水量: {self.watering_controller.water_amount_ml}ml\n"
                    f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            return result                 # 結果を返す
            
        except Exception as e:
            self.logger.error(f"手動給水エラー: {str(e)}")  # エラーログ出力
            return {                      # エラー結果を返す
                'success': False,
                'message': f'手動給水エラー: {str(e)}',
                'error': 'MANUAL_WATERING_ERROR'
            }
    
    def emergency_stop(self) -> Dict[str, Any]:
        """緊急停止"""
        try:
            result = self.watering_controller.stop_watering()  # 給水を停止
            
            # 緊急停止通知
            self.line_notify.send_message(  # LINE通知送信
                f"🚨 緊急停止実行！\n"
                f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"システムを確認してください"
            )
            
            return result                 # 結果を返す
            
        except Exception as e:
            self.logger.error(f"緊急停止エラー: {str(e)}")  # エラーログ出力
            return {                      # エラー結果を返す
                'success': False,
                'message': f'緊急停止エラー: {str(e)}',
                'error': 'EMERGENCY_STOP_ERROR'
            }
    
    def get_watering_status(self) -> Dict[str, Any]:
        """給水システム状態取得"""
        return {                          # 状態情報を返す
            'auto_watering_running': self.running,  # 自動給水実行フラグ
            'watering_controller_status': self.watering_controller.get_status(),  # 給水制御状態
            'recent_history': self.watering_controller.get_recent_history(5)  # 最近の履歴
        }
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """給水設定更新"""
        try:
            if 'soil_moisture_threshold' in settings:  # 土壌水分閾値が指定された場合
                self.watering_controller.soil_moisture_threshold = settings['soil_moisture_threshold']  # 閾値を更新
            
            if 'watering_interval_hours' in settings:  # 給水間隔が指定された場合
                self.watering_controller.watering_interval_hours = settings['watering_interval_hours']  # 間隔を更新
            
            if 'watering_duration_seconds' in settings:  # 給水時間が指定された場合
                self.watering_controller.watering_duration_seconds = settings['watering_duration_seconds']  # 時間を更新
            
            if 'water_amount_ml' in settings:  # 給水量が指定された場合
                self.watering_controller.water_amount_ml = settings['water_amount_ml']  # 給水量を更新
            
            self.logger.info(f"給水設定更新: {settings}")  # 更新ログ出力
            return {'success': True, 'message': '設定更新完了'}  # 成功を返す
            
        except Exception as e:
            self.logger.error(f"設定更新エラー: {str(e)}")  # エラーログ出力
            return {'success': False, 'message': f'設定更新エラー: {str(e)}'}  # エラーを返す
```

---

## 📊 実装完了チェックリスト

- [ ] ハードウェア接続完了
- [ ] リレーモジュール接続完了
- [ ] 給水制御クラス実装完了
- [ ] 自動給水マネージャー実装完了
- [ ] Web API実装完了
- [ ] テストスクリプト実行完了
- [ ] 安全機能確認完了
- [ ] 給水履歴機能確認完了
- [ ] LINE通知統合完了
- [ ] エラーハンドリング確認完了

## 🎯 次のステップ

1. **Web UI実装**: 給水制御のWebインターフェース
2. **データ可視化**: 給水履歴のグラフ表示
3. **設定画面**: 給水パラメータの動的変更
4. **統合テスト**: 全システムの動作確認

---

## 🏗️ クラス全体の流れと意味

### **WateringControllerクラス**
**意味**: 給水システムの核となる制御クラス
**役割**:
- リレーモジュールによる水ポンプのON/OFF制御
- 給水条件の判定（土壌水分、間隔、連続回数）
- 給水履歴の記録とJSON形式での永続化
- 安全機能（緊急停止、連続給水制限）

### **AutoWateringManagerクラス**
**意味**: 自動給水システムの統合管理クラス
**役割**:
- センサーデータに基づく自動給水判定
- バックグラウンドでの継続的な監視
- LINE通知との連携
- 手動給水・緊急停止の提供

**全体の流れ**:
1. **初期化**: GPIO設定、履歴読み込み、設定値の初期化
2. **監視開始**: バックグラウンドスレッドでセンサーデータを監視
3. **給水判定**: 土壌水分値と給水間隔をチェック
4. **給水実行**: リレーをONにして指定時間給水
5. **安全制御**: 連続給水制限、水タンク空検知
6. **履歴記録**: 給水結果をJSONファイルに保存
7. **通知送信**: LINE通知で給水完了・エラーを報告
8. **状態管理**: 給水システムの状態を継続的に監視

**安全機能**:
- **連続給水制限**: 最大2回まで連続給水可能
- **給水間隔制限**: 12時間以内の再給水を防止
- **水タンク空検知**: フロートスイッチによる水位監視
- **緊急停止**: 手動での即座な給水停止
- **エラー処理**: 給水失敗時の自動リレーOFF

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

