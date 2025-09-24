# 給水制御機能 統合実装ガイド

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

## 📁 ファイル作成手順

### Step 1: 給水ディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# 給水ディレクトリの確認
ls -la src/watering/
```

### Step 2: 各ファイルの作成順序
1. `src/watering/pump_control.py` - ポンプ制御
2. `src/watering/watering_logic.py` - 給水判定ロジック
3. `src/watering/watering_scheduler.py` - スケジューラー

### Step 3: ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/watering/pump_control.py
touch src/watering/watering_logic.py
touch src/watering/watering_scheduler.py
```

## 📄 実装コード

### 📄 src/watering/pump_control.py
水ポンプ制御クラス

```python
import RPi.GPIO as GPIO
import time
import logging
from typing import Dict, Any

class PumpController:
    """水ポンプ制御クラス"""
    
    def __init__(self, relay_pin: int = 16):
        self.relay_pin = relay_pin
        self.is_running = False
        self.logger = logging.getLogger("pump_controller")
        
        # GPIO設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.LOW)  # 初期状態はOFF
        
        self.logger.info(f"ポンプ制御が初期化されました (GPIO: {relay_pin})")
    
    def start_pump(self, duration: int = 5) -> Dict[str, Any]:
        """ポンプを開始"""
        try:
            if self.is_running:
                return {
                    'success': False,
                    'message': 'ポンプは既に稼働中です',
                    'timestamp': time.time()
                }
            
            self.logger.info(f"ポンプを開始します (時間: {duration}秒)")
            
            # リレーをON（ポンプ開始）
            GPIO.output(self.relay_pin, GPIO.HIGH)
            self.is_running = True
            
            # 指定時間待機
            time.sleep(duration)
            
            # リレーをOFF（ポンプ停止）
            GPIO.output(self.relay_pin, GPIO.LOW)
            self.is_running = False
            
            self.logger.info(f"ポンプを停止しました (稼働時間: {duration}秒)")
            
            return {
                'success': True,
                'message': f'ポンプが正常に稼働しました (時間: {duration}秒)',
                'duration': duration,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"ポンプ制御エラー: {str(e)}")
            
            # エラー時は強制的にポンプを停止
            GPIO.output(self.relay_pin, GPIO.LOW)
            self.is_running = False
            
            return {
                'success': False,
                'message': f'ポンプ制御エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def stop_pump(self) -> Dict[str, Any]:
        """ポンプを強制停止"""
        try:
            GPIO.output(self.relay_pin, GPIO.LOW)
            self.is_running = False
            
            self.logger.info("ポンプを強制停止しました")
            
            return {
                'success': True,
                'message': 'ポンプを強制停止しました',
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"ポンプ強制停止エラー: {str(e)}")
            return {
                'success': False,
                'message': f'ポンプ強制停止エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """ポンプの状態を取得"""
        return {
            'is_running': self.is_running,
            'relay_pin': self.relay_pin,
            'timestamp': time.time()
        }
    
    def cleanup(self):
        """GPIOのクリーンアップ"""
        GPIO.output(self.relay_pin, GPIO.LOW)
        GPIO.cleanup()
        self.logger.info("GPIOをクリーンアップしました")
```

### 📄 src/watering/watering_logic.py
給水判定ロジッククラス

```python
import time
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

class WateringLogic:
    """給水判定ロジッククラス"""
    
    def __init__(self, 
                 soil_moisture_threshold: int = 159,
                 watering_interval_hours: int = 12,
                 max_consecutive_waterings: int = 2):
        
        self.soil_moisture_threshold = soil_moisture_threshold
        self.watering_interval_hours = watering_interval_hours
        self.max_consecutive_waterings = max_consecutive_waterings
        
        self.logger = logging.getLogger("watering_logic")
        self.history_file = Path("data/watering_history/watering_log.json")
        
        # 履歴ファイルのディレクトリを作成
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("給水判定ロジックが初期化されました")
    
    def should_water(self, 
                    soil_moisture: int,
                    water_level_status: str = "normal") -> Dict[str, Any]:
        """給水が必要かどうかを判定"""
        
        try:
            # 水タンクが空の場合は給水しない
            if water_level_status == "empty":
                return {
                    'should_water': False,
                    'reason': '水タンクが空のため給水できません',
                    'timestamp': time.time()
                }
            
            # 土壌水分が閾値より高い場合は給水しない
            if soil_moisture > self.soil_moisture_threshold:
                return {
                    'should_water': False,
                    'reason': f'土壌水分が十分です ({soil_moisture} > {self.soil_moisture_threshold})',
                    'soil_moisture': soil_moisture,
                    'timestamp': time.time()
                }
            
            # 前回給水からの時間をチェック
            last_watering = self._get_last_watering_time()
            if last_watering:
                time_since_last = time.time() - last_watering
                hours_since_last = time_since_last / 3600
                
                if hours_since_last < self.watering_interval_hours:
                    return {
                        'should_water': False,
                        'reason': f'前回給水から{hours_since_last:.1f}時間しか経過していません',
                        'hours_since_last': hours_since_last,
                        'required_interval': self.watering_interval_hours,
                        'timestamp': time.time()
                    }
            
            # 連続給水回数をチェック
            consecutive_count = self._get_consecutive_watering_count()
            if consecutive_count >= self.max_consecutive_waterings:
                return {
                    'should_water': False,
                    'reason': f'連続給水回数が上限に達しています ({consecutive_count}/{self.max_consecutive_waterings})',
                    'consecutive_count': consecutive_count,
                    'timestamp': time.time()
                }
            
            # 給水条件を満たしている
            return {
                'should_water': True,
                'reason': '給水条件を満たしています',
                'soil_moisture': soil_moisture,
                'threshold': self.soil_moisture_threshold,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"給水判定エラー: {str(e)}")
            return {
                'should_water': False,
                'reason': f'給水判定エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def record_watering(self, 
                       duration: int,
                       soil_moisture_before: int,
                       soil_moisture_after: int = None,
                       manual: bool = False) -> Dict[str, Any]:
        """給水履歴を記録"""
        
        try:
            watering_record = {
                'timestamp': time.time(),
                'datetime': datetime.now().isoformat(),
                'duration': duration,
                'soil_moisture_before': soil_moisture_before,
                'soil_moisture_after': soil_moisture_after,
                'manual': manual,
                'success': True
            }
            
            # 履歴ファイルに追加
            self._append_to_history(watering_record)
            
            self.logger.info(f"給水履歴を記録しました: {watering_record}")
            
            return {
                'success': True,
                'message': '給水履歴を記録しました',
                'record': watering_record
            }
            
        except Exception as e:
            self.logger.error(f"給水履歴記録エラー: {str(e)}")
            return {
                'success': False,
                'message': f'給水履歴記録エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def _get_last_watering_time(self) -> Optional[float]:
        """最後の給水時間を取得"""
        try:
            if not self.history_file.exists():
                return None
            
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            if not history:
                return None
            
            # 最後の給水記録を取得
            last_record = history[-1]
            return last_record.get('timestamp')
            
        except Exception as e:
            self.logger.error(f"最後の給水時間取得エラー: {str(e)}")
            return None
    
    def _get_consecutive_watering_count(self) -> int:
        """連続給水回数を取得"""
        try:
            if not self.history_file.exists():
                return 0
            
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            if not history:
                return 0
            
            # 24時間以内の給水回数をカウント
            current_time = time.time()
            count = 0
            
            for record in reversed(history):
                record_time = record.get('timestamp', 0)
                if current_time - record_time > 24 * 3600:  # 24時間を超えたら終了
                    break
                count += 1
            
            return count
            
        except Exception as e:
            self.logger.error(f"連続給水回数取得エラー: {str(e)}")
            return 0
    
    def _append_to_history(self, record: Dict[str, Any]):
        """履歴ファイルに記録を追加"""
        try:
            # 既存の履歴を読み込み
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            # 新しい記録を追加
            history.append(record)
            
            # 履歴を保存（最新100件のみ保持）
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"履歴ファイル書き込みエラー: {str(e)}")
    
    def get_watering_history(self, days: int = 7) -> Dict[str, Any]:
        """給水履歴を取得"""
        try:
            if not self.history_file.exists():
                return {'history': [], 'total_count': 0}
            
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            # 指定日数以内の記録のみフィルタリング
            cutoff_time = time.time() - (days * 24 * 3600)
            filtered_history = [
                record for record in history 
                if record.get('timestamp', 0) >= cutoff_time
            ]
            
            return {
                'history': filtered_history,
                'total_count': len(filtered_history),
                'days': days
            }
            
        except Exception as e:
            self.logger.error(f"給水履歴取得エラー: {str(e)}")
            return {'history': [], 'total_count': 0, 'error': str(e)}
```

### 📄 src/watering/watering_scheduler.py
給水スケジューラークラス

```python
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any
from .pump_control import PumpController
from .watering_logic import WateringLogic

class WateringScheduler:
    """給水スケジューラークラス"""
    
    def __init__(self, 
                 sensor_manager,
                 notification_manager=None):
        
        self.sensor_manager = sensor_manager
        self.notification_manager = notification_manager
        
        self.pump_controller = PumpController()
        self.watering_logic = WateringLogic()
        
        self.running = False
        self.check_interval = 300  # 5分間隔でチェック
        
        self.logger = logging.getLogger("watering_scheduler")
        
        self.logger.info("給水スケジューラーが初期化されました")
    
    def start_scheduler(self):
        """スケジューラーを開始"""
        if self.running:
            self.logger.warning("スケジューラーは既に稼働中です")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.logger.info("給水スケジューラーを開始しました")
    
    def stop_scheduler(self):
        """スケジューラーを停止"""
        if not self.running:
            self.logger.warning("スケジューラーは稼働していません")
            return
        
        self.running = False
        if hasattr(self, 'scheduler_thread'):
            self.scheduler_thread.join()
        
        self.logger.info("給水スケジューラーを停止しました")
    
    def _scheduler_loop(self):
        """スケジューラーのメインループ"""
        while self.running:
            try:
                # センサーデータを取得
                sensor_data = self.sensor_manager.get_all_data()
                
                # 土壌水分データを取得
                soil_data = sensor_data.get('soil_moisture', {})
                soil_moisture = soil_data.get('soil_moisture')
                
                # 水の残量データを取得
                pressure_data = sensor_data.get('pressure', {})
                water_status = pressure_data.get('status', 'normal')
                
                if soil_moisture is not None:
                    # 給水判定
                    watering_decision = self.watering_logic.should_water(
                        soil_moisture, water_status
                    )
                    
                    if watering_decision['should_water']:
                        self.logger.info(f"給水を実行します: {watering_decision['reason']}")
                        self._execute_watering(soil_moisture)
                    else:
                        self.logger.debug(f"給水は不要です: {watering_decision['reason']}")
                else:
                    self.logger.warning("土壌水分データが取得できませんでした")
                
                # 次のチェックまで待機
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"スケジューラーループエラー: {str(e)}")
                time.sleep(60)  # エラー時は1分待機
    
    def _execute_watering(self, soil_moisture_before: int) -> Dict[str, Any]:
        """給水を実行"""
        try:
            # ポンプを開始（5秒間）
            result = self.pump_controller.start_pump(duration=5)
            
            if result['success']:
                # 給水履歴を記録
                self.watering_logic.record_watering(
                    duration=5,
                    soil_moisture_before=soil_moisture_before,
                    manual=False
                )
                
                # 通知を送信
                if self.notification_manager:
                    message = f"🌧️ 自動給水が完了しました\n土壌水分: {soil_moisture_before} → 給水後は上昇予定"
                    self.notification_manager.send_notification(message)
                
                self.logger.info("給水が正常に完了しました")
                
            else:
                self.logger.error(f"給水実行エラー: {result['message']}")
                
                # エラー通知を送信
                if self.notification_manager:
                    message = f"❌ 給水エラーが発生しました\n{result['message']}"
                    self.notification_manager.send_notification(message)
            
            return result
            
        except Exception as e:
            self.logger.error(f"給水実行エラー: {str(e)}")
            return {
                'success': False,
                'message': f'給水実行エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def manual_watering(self, duration: int = 5) -> Dict[str, Any]:
        """手動給水を実行"""
        try:
            # センサーデータを取得
            sensor_data = self.sensor_manager.get_all_data()
            soil_data = sensor_data.get('soil_moisture', {})
            soil_moisture = soil_data.get('soil_moisture', 0)
            
            # ポンプを開始
            result = self.pump_controller.start_pump(duration=duration)
            
            if result['success']:
                # 給水履歴を記録
                self.watering_logic.record_watering(
                    duration=duration,
                    soil_moisture_before=soil_moisture,
                    manual=True
                )
                
                self.logger.info(f"手動給水が完了しました (時間: {duration}秒)")
                
            return result
            
        except Exception as e:
            self.logger.error(f"手動給水エラー: {str(e)}")
            return {
                'success': False,
                'message': f'手動給水エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """スケジューラーの状態を取得"""
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'pump_status': self.pump_controller.get_status(),
            'timestamp': time.time()
        }
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        self.stop_scheduler()
        self.pump_controller.cleanup()
        self.logger.info("給水スケジューラーのクリーンアップが完了しました")
```

## 🧪 テスト方法

### 1. ポンプ制御テスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# ポンプ制御テスト
python -c "
from src.watering.pump_control import PumpController
pump = PumpController()
result = pump.start_pump(3)  # 3秒間給水
print(f'給水結果: {result}')
"
```

### 2. 給水判定ロジックテスト
```bash
# 給水判定テスト
python -c "
from src.watering.watering_logic import WateringLogic
logic = WateringLogic()
result = logic.should_water(150)  # 土壌水分150でテスト
print(f'給水判定: {result}')
"
```

### 3. 統合テスト
```bash
# 給水スケジューラーのテスト
python -c "
from src.watering.watering_scheduler import WateringScheduler
from src.sensors.sensor_manager import SensorManager

sensor_manager = SensorManager()
scheduler = WateringScheduler(sensor_manager)
scheduler.start_scheduler()
time.sleep(60)
status = scheduler.get_status()
print(f'スケジューラー状態: {status}')
scheduler.stop_scheduler()
"
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

