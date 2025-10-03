# LINE通知機能 統合実装ガイド

## 📋 概要
LINE Notify APIを使用した通知機能の実装手順書。センサー異常、給水完了、システム状態の通知

## 🎯 実装目標
- LINE Notify APIとの連携
- センサー異常時のアラート通知
- 給水完了の通知
- 定期的なシステム状態報告
- 通知履歴の管理

## 🛠️ 必要な環境

### ソフトウェア
- Python 3.11.x
- requests (HTTP通信)
- Flask 2.3.3
- 既存のセンサー・給水システム

### LINE設定
- LINE Notify APIトークン
- 通知先グループ・チャットの設定

## 📁 ファイル作成手順

### Step 1: 通知ディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# 通知ディレクトリの確認
ls -la src/notifications/
```

### Step 2: 各ファイルの作成順序
1. `src/notifications/line_notify.py` - LINE通知送信
2. `src/notifications/alert_manager.py` - アラート管理
3. `src/notifications/notification_scheduler.py` - 通知スケジューラー

### Step 3: ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/notifications/line_notify.py
touch src/notifications/alert_manager.py
touch src/notifications/notification_scheduler.py
```

## 📄 実装コード

### 📄 src/notifications/line_notify.py
LINE通知送信クラス

```python
import requests
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import os

class LineNotifier:
    """LINE通知送信クラス"""
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get('LINE_NOTIFY_TOKEN')
        self.api_url = 'https://notify-api.line.me/api/notify'
        self.logger = logging.getLogger('line_notifier')
        
        if not self.token:
            self.logger.warning("LINE Notifyトークンが設定されていません")
    
    def send_notification(self, message: str, image_path: str = None) -> Dict[str, Any]:
        """LINE通知を送信"""
        try:
            if not self.token:
                return {
                    'success': False,
                    'message': 'LINE Notifyトークンが設定されていません',
                    'timestamp': time.time()
                }
            
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            
            data = {
                'message': message
            }
            
            # 画像が指定されている場合は追加
            files = None
            if image_path and os.path.exists(image_path):
                files = {'imageFile': open(image_path, 'rb')}
            
            response = requests.post(
                self.api_url,
                headers=headers,
                data=data,
                files=files
            )
            
            if response.status_code == 200:
                self.logger.info(f"LINE通知を送信しました: {message}")
                return {
                    'success': True,
                    'message': 'LINE通知を送信しました',
                    'response': response.json(),
                    'timestamp': time.time()
                }
            else:
                self.logger.error(f"LINE通知送信エラー: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'message': f'LINE通知送信エラー: {response.status_code}',
                    'error': response.text,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            self.logger.error(f"LINE通知送信エラー: {str(e)}")
            return {
                'success': False,
                'message': f'LINE通知送信エラー: {str(e)}',
                'timestamp': time.time()
            }
        finally:
            if files and 'imageFile' in files:
                files['imageFile'].close()
    
    def send_sensor_alert(self, sensor_name: str, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """センサー異常のアラート通知"""
        try:
            alert_type = self._determine_alert_type(sensor_name, sensor_data)
            
            if alert_type:
                message = self._format_sensor_alert_message(sensor_name, sensor_data, alert_type)
                return self.send_notification(message)
            else:
                return {
                    'success': True,
                    'message': 'アラート条件に該当しませんでした',
                    'timestamp': time.time()
                }
                
        except Exception as e:
            self.logger.error(f"センサーアラート送信エラー: {str(e)}")
            return {
                'success': False,
                'message': f'センサーアラート送信エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def send_watering_notification(self, watering_data: Dict[str, Any]) -> Dict[str, Any]:
        """給水完了の通知"""
        try:
            message = self._format_watering_message(watering_data)
            return self.send_notification(message)
            
        except Exception as e:
            self.logger.error(f"給水通知送信エラー: {str(e)}")
            return {
                'success': False,
                'message': f'給水通知送信エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def send_system_status(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """システム状態の定期報告"""
        try:
            message = self._format_system_status_message(system_data)
            return self.send_notification(message)
            
        except Exception as e:
            self.logger.error(f"システム状態通知送信エラー: {str(e)}")
            return {
                'success': False,
                'message': f'システム状態通知送信エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def _determine_alert_type(self, sensor_name: str, sensor_data: Dict[str, Any]) -> Optional[str]:
        """アラートタイプを判定"""
        try:
            if sensor_name == 'temperature_humidity':
                temperature = sensor_data.get('temperature')
                humidity = sensor_data.get('humidity')
                
                if temperature is not None:
                    if temperature < 10:
                        return 'temperature_low'
                    elif temperature > 35:
                        return 'temperature_high'
                
                if humidity is not None:
                    if humidity < 30:
                        return 'humidity_low'
                    elif humidity > 80:
                        return 'humidity_high'
            
            elif sensor_name == 'soil_moisture':
                soil_moisture = sensor_data.get('soil_moisture')
                if soil_moisture is not None and soil_moisture > 400:
                    return 'soil_moisture_high'
            
            elif sensor_name == 'pressure':
                water_percentage = sensor_data.get('water_percentage')
                if water_percentage is not None and water_percentage < 10:
                    return 'water_level_low'
            
            return None
            
        except Exception as e:
            self.logger.error(f"アラートタイプ判定エラー: {str(e)}")
            return None
    
    def _format_sensor_alert_message(self, sensor_name: str, sensor_data: Dict[str, Any], alert_type: str) -> str:
        """センサーアラートメッセージをフォーマット"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        alert_messages = {
            'temperature_low': f"❄️ 低温アラート\n温度: {sensor_data.get('temperature', 'N/A')}°C\n時間: {timestamp}",
            'temperature_high': f"🔥 高温アラート\n温度: {sensor_data.get('temperature', 'N/A')}°C\n時間: {timestamp}",
            'humidity_low': f"🌵 低湿度アラート\n湿度: {sensor_data.get('humidity', 'N/A')}%\n時間: {timestamp}",
            'humidity_high': f"💧 高湿度アラート\n湿度: {sensor_data.get('humidity', 'N/A')}%\n時間: {timestamp}",
            'soil_moisture_high': f"💧 土壌水分過多アラート\n土壌水分: {sensor_data.get('soil_moisture', 'N/A')}\n時間: {timestamp}",
            'water_level_low': f"⚠️ 水不足アラート\n残量: {sensor_data.get('water_percentage', 'N/A')}%\n時間: {timestamp}"
        }
        
        return alert_messages.get(alert_type, f"⚠️ センサーアラート\nセンサー: {sensor_name}\n時間: {timestamp}")
    
    def _format_watering_message(self, watering_data: Dict[str, Any]) -> str:
        """給水完了メッセージをフォーマット"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = watering_data.get('duration', 0)
        manual = watering_data.get('manual', False)
        soil_moisture_before = watering_data.get('soil_moisture_before', 'N/A')
        
        watering_type = "手動給水" if manual else "自動給水"
        
        return f"""🌧️ {watering_type}完了

⏱️ 給水時間: {duration}秒
🌱 給水前土壌水分: {soil_moisture_before}
🕐 実行時間: {timestamp}

植物の様子を確認してください。"""
    
    def _format_system_status_message(self, system_data: Dict[str, Any]) -> str:
        """システム状態メッセージをフォーマット"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        temperature = system_data.get('temperature', 'N/A')
        humidity = system_data.get('humidity', 'N/A')
        soil_moisture = system_data.get('soil_moisture', 'N/A')
        water_percentage = system_data.get('water_percentage', 'N/A')
        
        return f"""📊 システム状態報告

🌡️ 温度: {temperature}°C
💧 湿度: {humidity}%
🌱 土壌水分: {soil_moisture}
💧 水の残量: {water_percentage}%

🕐 報告時間: {timestamp}

システムは正常に稼働しています。"""
```

### 📄 src/notifications/alert_manager.py
アラート管理クラス

```python
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .line_notify import LineNotifier

class AlertManager:
    """アラート管理クラス"""
    
    def __init__(self, line_notifier: LineNotifier = None):
        self.line_notifier = line_notifier or LineNotifier()
        self.logger = logging.getLogger('alert_manager')
        
        # アラート履歴（重複通知防止用）
        self.alert_history = {}
        
        # アラート設定
        self.alert_settings = {
            'temperature_low': {'threshold': 10, 'enabled': True},
            'temperature_high': {'threshold': 35, 'enabled': True},
            'humidity_low': {'threshold': 30, 'enabled': True},
            'humidity_high': {'threshold': 80, 'enabled': True},
            'soil_moisture_high': {'threshold': 400, 'enabled': True},
            'water_level_low': {'threshold': 10, 'enabled': True}
        }
        
        # 通知間隔（分）
        self.notification_intervals = {
            'temperature_low': 60,  # 1時間
            'temperature_high': 30,  # 30分
            'humidity_low': 120,     # 2時間
            'humidity_high': 120,    # 2時間
            'soil_moisture_high': 240,  # 4時間
            'water_level_low': 30   # 30分
        }
    
    def check_sensor_alerts(self, sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """センサーデータをチェックしてアラートを判定"""
        alerts = []
        
        try:
            for sensor_name, data in sensor_data.items():
                if data.get('error', False):
                    continue
                
                sensor_alerts = self._check_sensor_data(sensor_name, data)
                alerts.extend(sensor_alerts)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"センサーアラートチェックエラー: {str(e)}")
            return []
    
    def _check_sensor_data(self, sensor_name: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """個別センサーデータをチェック"""
        alerts = []
        
        try:
            if sensor_name == 'temperature_humidity':
                temperature = data.get('temperature')
                humidity = data.get('humidity')
                
                if temperature is not None:
                    if temperature < self.alert_settings['temperature_low']['threshold']:
                        alert = self._create_alert('temperature_low', sensor_name, data)
                        if alert:
                            alerts.append(alert)
                    
                    elif temperature > self.alert_settings['temperature_high']['threshold']:
                        alert = self._create_alert('temperature_high', sensor_name, data)
                        if alert:
                            alerts.append(alert)
                
                if humidity is not None:
                    if humidity < self.alert_settings['humidity_low']['threshold']:
                        alert = self._create_alert('humidity_low', sensor_name, data)
                        if alert:
                            alerts.append(alert)
                    
                    elif humidity > self.alert_settings['humidity_high']['threshold']:
                        alert = self._create_alert('humidity_high', sensor_name, data)
                        if alert:
                            alerts.append(alert)
            
            elif sensor_name == 'soil_moisture':
                soil_moisture = data.get('soil_moisture')
                if soil_moisture is not None and soil_moisture > self.alert_settings['soil_moisture_high']['threshold']:
                    alert = self._create_alert('soil_moisture_high', sensor_name, data)
                    if alert:
                        alerts.append(alert)
            
            elif sensor_name == 'pressure':
                water_percentage = data.get('water_percentage')
                if water_percentage is not None and water_percentage < self.alert_settings['water_level_low']['threshold']:
                    alert = self._create_alert('water_level_low', sensor_name, data)
                    if alert:
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"センサーデータチェックエラー: {str(e)}")
            return []
    
    def _create_alert(self, alert_type: str, sensor_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """アラートを作成（重複チェック付き）"""
        try:
            # アラートが有効かチェック
            if not self.alert_settings.get(alert_type, {}).get('enabled', False):
                return None
            
            # 重複通知をチェック
            alert_key = f"{alert_type}_{sensor_name}"
            last_notification = self.alert_history.get(alert_key, 0)
            current_time = time.time()
            
            notification_interval = self.notification_intervals.get(alert_type, 60) * 60  # 秒に変換
            
            if current_time - last_notification < notification_interval:
                return None
            
            # アラートを作成
            alert = {
                'type': alert_type,
                'sensor_name': sensor_name,
                'data': data,
                'timestamp': current_time,
                'datetime': datetime.now().isoformat()
            }
            
            # 通知履歴を更新
            self.alert_history[alert_key] = current_time
            
            self.logger.info(f"アラートを作成しました: {alert_type} - {sensor_name}")
            return alert
            
        except Exception as e:
            self.logger.error(f"アラート作成エラー: {str(e)}")
            return None
    
    def send_alert_notification(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """アラート通知を送信"""
        try:
            result = self.line_notifier.send_sensor_alert(
                alert['sensor_name'], 
                alert['data']
            )
            
            if result['success']:
                self.logger.info(f"アラート通知を送信しました: {alert['type']}")
            else:
                self.logger.error(f"アラート通知送信失敗: {result['message']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"アラート通知送信エラー: {str(e)}")
            return {
                'success': False,
                'message': f'アラート通知送信エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def update_alert_settings(self, settings: Dict[str, Any]) -> bool:
        """アラート設定を更新"""
        try:
            for alert_type, setting in settings.items():
                if alert_type in self.alert_settings:
                    self.alert_settings[alert_type].update(setting)
            
            self.logger.info("アラート設定を更新しました")
            return True
            
        except Exception as e:
            self.logger.error(f"アラート設定更新エラー: {str(e)}")
            return False
    
    def get_alert_settings(self) -> Dict[str, Any]:
        """アラート設定を取得"""
        return self.alert_settings.copy()
    
    def clear_alert_history(self):
        """アラート履歴をクリア"""
        self.alert_history.clear()
        self.logger.info("アラート履歴をクリアしました")
```

### 📄 src/notifications/notification_scheduler.py
通知スケジューラークラス

```python
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .line_notify import LineNotifier
from .alert_manager import AlertManager

class NotificationScheduler:
    """通知スケジューラークラス"""
    
    def __init__(self, sensor_manager=None, watering_scheduler=None):
        self.sensor_manager = sensor_manager
        self.watering_scheduler = watering_scheduler
        
        self.line_notifier = LineNotifier()
        self.alert_manager = AlertManager(self.line_notifier)
        
        self.running = False
        self.logger = logging.getLogger('notification_scheduler')
        
        # 通知設定
        self.notification_settings = {
            'daily_report_enabled': True,
            'daily_report_time': '09:00',
            'watering_notifications_enabled': True,
            'sensor_alerts_enabled': True,
            'system_status_enabled': True
        }
        
        # 最後の通知時刻
        self.last_daily_report = None
        self.last_system_status = None
    
    def start_scheduler(self):
        """スケジューラーを開始"""
        if self.running:
            self.logger.warning("通知スケジューラーは既に稼働中です")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.logger.info("通知スケジューラーを開始しました")
    
    def stop_scheduler(self):
        """スケジューラーを停止"""
        if not self.running:
            self.logger.warning("通知スケジューラーは稼働していません")
            return
        
        self.running = False
        if hasattr(self, 'scheduler_thread'):
            self.scheduler_thread.join()
        
        self.logger.info("通知スケジューラーを停止しました")
    
    def _scheduler_loop(self):
        """スケジューラーのメインループ"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # 日次レポートの送信
                if self.notification_settings['daily_report_enabled']:
                    self._check_daily_report(current_time)
                
                # システム状態の定期通知
                if self.notification_settings['system_status_enabled']:
                    self._check_system_status_notification(current_time)
                
                # センサーアラートのチェック
                if self.notification_settings['sensor_alerts_enabled'] and self.sensor_manager:
                    self._check_sensor_alerts()
                
                # 60秒待機
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"通知スケジューラーループエラー: {str(e)}")
                time.sleep(60)
    
    def _check_daily_report(self, current_time: datetime):
        """日次レポートの送信をチェック"""
        try:
            if not self.last_daily_report:
                self.last_daily_report = current_time - timedelta(days=1)
            
            # 指定時刻をチェック
            report_time = self.notification_settings['daily_report_time']
            hour, minute = map(int, report_time.split(':'))
            
            target_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 前回の日次レポートから24時間以上経過し、指定時刻を過ぎている場合
            if (current_time - self.last_daily_report >= timedelta(days=1) and 
                current_time >= target_time):
                
                self._send_daily_report()
                self.last_daily_report = current_time
                
        except Exception as e:
            self.logger.error(f"日次レポートチェックエラー: {str(e)}")
    
    def _check_system_status_notification(self, current_time: datetime):
        """システム状態通知の送信をチェック"""
        try:
            # 6時間ごとにシステム状態を通知
            if (not self.last_system_status or 
                current_time - self.last_system_status >= timedelta(hours=6)):
                
                self._send_system_status()
                self.last_system_status = current_time
                
        except Exception as e:
            self.logger.error(f"システム状態通知チェックエラー: {str(e)}")
    
    def _check_sensor_alerts(self):
        """センサーアラートをチェック"""
        try:
            if not self.sensor_manager:
                return
            
            # センサーデータを取得
            sensor_data = self.sensor_manager.get_all_data()
            
            # アラートをチェック
            alerts = self.alert_manager.check_sensor_alerts(sensor_data)
            
            # アラート通知を送信
            for alert in alerts:
                self.alert_manager.send_alert_notification(alert)
                
        except Exception as e:
            self.logger.error(f"センサーアラートチェックエラー: {str(e)}")
    
    def _send_daily_report(self):
        """日次レポートを送信"""
        try:
            if not self.sensor_manager:
                return
            
            # センサーデータを取得
            sensor_data = self.sensor_manager.get_all_data()
            
            # 給水履歴を取得
            watering_history = []
            if self.watering_scheduler:
                watering_history = self.watering_scheduler.get_watering_history(days=1)
            
            # レポートメッセージを作成
            message = self._format_daily_report(sensor_data, watering_history)
            
            # 通知を送信
            result = self.line_notifier.send_notification(message)
            
            if result['success']:
                self.logger.info("日次レポートを送信しました")
            else:
                self.logger.error(f"日次レポート送信失敗: {result['message']}")
                
        except Exception as e:
            self.logger.error(f"日次レポート送信エラー: {str(e)}")
    
    def _send_system_status(self):
        """システム状態を送信"""
        try:
            if not self.sensor_manager:
                return
            
            # センサーデータを取得
            sensor_data = self.sensor_manager.get_all_data()
            
            # システム状態メッセージを作成
            message = self._format_system_status(sensor_data)
            
            # 通知を送信
            result = self.line_notifier.send_notification(message)
            
            if result['success']:
                self.logger.info("システム状態通知を送信しました")
            else:
                self.logger.error(f"システム状態通知送信失敗: {result['message']}")
                
        except Exception as e:
            self.logger.error(f"システム状態通知送信エラー: {str(e)}")
    
    def _format_daily_report(self, sensor_data: Dict[str, Any], watering_history: List[Dict[str, Any]]) -> str:
        """日次レポートメッセージをフォーマット"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # センサーデータの取得
        temp_data = sensor_data.get('temperature_humidity', {})
        soil_data = sensor_data.get('soil_moisture', {})
        pressure_data = sensor_data.get('pressure', {})
        
        temperature = temp_data.get('temperature', 'N/A')
        humidity = temp_data.get('humidity', 'N/A')
        soil_moisture = soil_data.get('soil_moisture', 'N/A')
        water_percentage = pressure_data.get('water_percentage', 'N/A')
        
        # 給水回数
        watering_count = len(watering_history)
        
        return f"""📊 日次レポート ({timestamp})

🌡️ 現在の温度: {temperature}°C
💧 現在の湿度: {humidity}%
🌱 現在の土壌水分: {soil_moisture}
💧 水の残量: {water_percentage}%

🌧️ 本日の給水回数: {watering_count}回

植物の成長を見守っています。"""
    
    def _format_system_status(self, sensor_data: Dict[str, Any]) -> str:
        """システム状態メッセージをフォーマット"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # センサーデータの取得
        temp_data = sensor_data.get('temperature_humidity', {})
        soil_data = sensor_data.get('soil_moisture', {})
        pressure_data = sensor_data.get('pressure', {})
        
        temperature = temp_data.get('temperature', 'N/A')
        humidity = temp_data.get('humidity', 'N/A')
        soil_moisture = soil_data.get('soil_moisture', 'N/A')
        water_percentage = pressure_data.get('water_percentage', 'N/A')
        
        return f"""🖥️ システム状態報告

🌡️ 温度: {temperature}°C
💧 湿度: {humidity}%
🌱 土壌水分: {soil_moisture}
💧 水の残量: {water_percentage}%

🕐 報告時間: {timestamp}

システムは正常に稼働しています。"""
    
    def send_watering_notification(self, watering_data: Dict[str, Any]):
        """給水完了通知を送信"""
        try:
            if not self.notification_settings['watering_notifications_enabled']:
                return
            
            result = self.line_notifier.send_watering_notification(watering_data)
            
            if result['success']:
                self.logger.info("給水完了通知を送信しました")
            else:
                self.logger.error(f"給水完了通知送信失敗: {result['message']}")
                
        except Exception as e:
            self.logger.error(f"給水完了通知送信エラー: {str(e)}")
    
    def update_notification_settings(self, settings: Dict[str, Any]) -> bool:
        """通知設定を更新"""
        try:
            self.notification_settings.update(settings)
            self.logger.info("通知設定を更新しました")
            return True
            
        except Exception as e:
            self.logger.error(f"通知設定更新エラー: {str(e)}")
            return False
    
    def get_notification_settings(self) -> Dict[str, Any]:
        """通知設定を取得"""
        return self.notification_settings.copy()
```

## 🧪 テスト方法

### 1. LINE通知テスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# LINE通知テスト
python -c "
from src.notifications.line_notify import LineNotifier
notifier = LineNotifier()
result = notifier.send_notification('テスト通知です')
print(f'通知結果: {result}')
"
```

### 2. アラート管理テスト
```bash
# アラート管理テスト
python -c "
from src.notifications.alert_manager import AlertManager
manager = AlertManager()
sensor_data = {'temperature_humidity': {'temperature': 5, 'humidity': 60}}
alerts = manager.check_sensor_alerts(sensor_data)
print(f'アラート: {alerts}')
"
```

### 3. 統合テスト
```bash
# 通知スケジューラーのテスト
python -c "
from src.notifications.notification_scheduler import NotificationScheduler
scheduler = NotificationScheduler()
scheduler.start_scheduler()
time.sleep(60)
scheduler.stop_scheduler()
"
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

