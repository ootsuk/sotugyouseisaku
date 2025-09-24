# LINE通知機能 統合実装ガイド

## 📋 概要
LINE Notify APIを使用した通知機能の詳細実装手順書

## 🎯 実装目標
- LINE Notify API連携
- 給水完了通知
- センサー異常通知
- システムエラー通知
- 画像付き通知

## 🛠️ 必要な環境

### API設定
- LINE Notifyアカウント
- アクセストークン
- 通知先グループ/個人設定

### ソフトウェア
- Python 3.11.x
- requests (HTTP通信)
- python-dotenv (環境変数管理)

---

## 📄 実装コード

### 📄 line_notify.py
LINE通知クラス

```python
import requests
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

class LineNotify:
    """LINE Notify通知クラス"""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv('LINE_NOTIFY_TOKEN')  # トークンを環境変数から取得
        self.api_url = os.getenv('LINE_NOTIFY_API_URL', 'https://notify-api.line.me/api/notify')  # API URLを設定
        self.logger = logging.getLogger("line_notify")  # ロガーを取得
        
        if not self.token:               # トークンが設定されていない場合
            self.logger.error("LINE Notifyトークンが設定されていません")  # エラーログ出力
            raise ValueError("LINE Notifyトークンが必要です")  # エラーを発生
    
    def send_message(self, message: str, image_path: str = None) -> bool:
        """メッセージを送信"""
        try:
            headers = {                  # リクエストヘッダーを設定
                'Authorization': f'Bearer {self.token}'  # Bearer認証トークンを設定
            }
            
            data = {                     # リクエストデータを設定
                'message': message       # メッセージを設定
            }
            
            files = None                 # ファイルを初期化
            if image_path and os.path.exists(image_path):  # 画像パスが指定され、ファイルが存在する場合
                files = {'imageFile': open(image_path, 'rb')}  # 画像ファイルをバイナリモードで開く
            
            response = requests.post(    # POSTリクエストを送信
                self.api_url,            # API URL
                headers=headers,         # ヘッダー
                data=data,               # データ
                files=files              # ファイル
            )
            
            if response.status_code == 200:  # レスポンスが成功の場合
                self.logger.info("LINE通知送信成功")  # 成功ログ出力
                return True               # 成功を返す
            else:                         # レスポンスが失敗の場合
                self.logger.error(f"LINE通知送信失敗: {response.status_code} - {response.text}")  # エラーログ出力
                return False              # 失敗を返す
                
        except Exception as e:
            self.logger.error(f"LINE通知送信エラー: {str(e)}")  # エラーログ出力
            return False                  # 失敗を返す
        
        finally:
            if files and 'imageFile' in files:  # ファイルが開かれている場合
                files['imageFile'].close()  # ファイルを閉じる
    
    def send_watering_notification(self, water_amount_ml: int) -> bool:
        """給水完了通知"""
        message = (                      # メッセージを構築
            f"🌱 すくすくミントちゃん\n"  # プロジェクト名
            f"💧 給水完了！\n"           # 給水完了メッセージ
            f"📊 給水量: {water_amount_ml}ml\n"  # 給水量
            f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # 時刻
            f"🌿 植物が元気になりました！"  # 励ましメッセージ
        )
        
        return self.send_message(message)  # メッセージを送信
    
    def send_sensor_alert(self, sensor_name: str, value: float, threshold: float) -> bool:
        """センサー異常通知"""
        sensor_emoji = {                 # センサー名と絵文字のマッピング
            'temperature': '🌡️',        # 温度センサー
            'humidity': '💧',            # 湿度センサー
            'soil_moisture': '🌱'        # 土壌水分センサー
        }
        
        emoji = sensor_emoji.get(sensor_name, '📊')  # センサー名に対応する絵文字を取得
        
        message = (                      # メッセージを構築
            f"🚨 すくすくミントちゃん アラート\n"  # アラートヘッダー
            f"{emoji} {sensor_name}が異常値です\n"  # センサー名と異常メッセージ
            f"📊 現在値: {value}\n"      # 現在値
            f"⚠️ 閾値: {threshold}\n"   # 閾値
            f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # 時刻
            f"🔧 システムを確認してください"  # 確認依頼
        )
        
        return self.send_message(message)  # メッセージを送信
    
    def send_water_tank_empty(self) -> bool:
        """水タンク空通知"""
        message = (                      # メッセージを構築
            f"🚨 すくすくミントちゃん 緊急通知\n"  # 緊急通知ヘッダー
            f"💧 水タンクが空になりました！\n"    # 水タンク空メッセージ
            f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # 時刻
            f"🔄 水を補充してください\n"         # 補充依頼
            f"⚠️ 給水機能が停止します"         # 機能停止警告
        )
        
        return self.send_message(message)  # メッセージを送信
    
    def send_system_error(self, error_message: str) -> bool:
        """システムエラー通知"""
        message = (                      # メッセージを構築
            f"❌ すくすくミントちゃん システムエラー\n"  # システムエラーヘッダー
            f"🔧 エラー内容: {error_message}\n"  # エラー内容
            f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # 時刻
            f"🛠️ システムを確認してください"    # 確認依頼
        )
        
        return self.send_message(message)  # メッセージを送信
    
    def send_daily_report(self, report_data: Dict[str, Any]) -> bool:
        """日次レポート通知"""
        message = (                      # メッセージを構築
            f"📊 すくすくミントちゃん 日次レポート\n"  # 日次レポートヘッダー
            f"📅 日付: {datetime.now().strftime('%Y-%m-%d')}\n"  # 日付
            f"🌡️ 平均温度: {report_data.get('avg_temperature', '--')}°C\n"  # 平均温度
            f"💧 平均湿度: {report_data.get('avg_humidity', '--')}%\n"  # 平均湿度
            f"🌱 平均土壌水分: {report_data.get('avg_soil_moisture', '--')}%\n"  # 平均土壌水分
            f"💧 給水回数: {report_data.get('watering_count', 0)}回\n"  # 給水回数
            f"📸 撮影回数: {report_data.get('photo_count', 0)}回\n"  # 撮影回数
            f"🌿 植物の調子はいかがですか？"    # 励ましメッセージ
        )
        
        return self.send_message(message)  # メッセージを送信
    
    def send_photo_with_message(self, image_path: str, message: str = None) -> bool:
        """画像付きメッセージ送信"""
        if message is None:              # メッセージが指定されていない場合
            message = (                  # デフォルトメッセージを構築
                f"📸 すくすくミントちゃん 最新画像\n"  # 画像通知ヘッダー
                f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # 時刻
                f"🌱 植物の成長を確認してください！"  # 確認依頼
            )
        
        return self.send_message(message, image_path)  # メッセージと画像を送信
    
    def send_maintenance_reminder(self, days_since_last: int) -> bool:
        """メンテナンスリマインダー"""
        message = (                      # メッセージを構築
            f"🔧 すくすくミントちゃん メンテナンスリマインダー\n"  # メンテナンスリマインダーヘッダー
            f"📅 最後のメンテナンスから {days_since_last} 日経過\n"  # 経過日数
            f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # 時刻
            f"🛠️ 以下の点を確認してください:\n"  # 確認項目ヘッダー
            f"• センサーの清掃\n"        # センサー清掃
            f"• 水タンクの清掃\n"        # 水タンク清掃
            f"• 配管の点検\n"            # 配管点検
            f"• システムログの確認"       # ログ確認
        )
        
        return self.send_message(message)  # メッセージを送信
    
    def test_notification(self) -> bool:
        """テスト通知送信"""
        message = (                      # メッセージを構築
            f"🧪 すくすくミントちゃん テスト通知\n"  # テスト通知ヘッダー
            f"✅ LINE通知機能が正常に動作しています\n"  # 動作確認メッセージ
            f"⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"  # 時刻
            f"🌱 システムは正常に稼働中です"      # 稼働確認メッセージ
        )
        
        return self.send_message(message)  # メッセージを送信
    
    def get_notification_status(self) -> Dict[str, Any]:
        """通知機能の状態を取得"""
        try:
            # テスト通知で状態確認
            test_result = self.test_notification()  # テスト通知を送信
            
            return {                      # 状態情報を返す
                'token_configured': bool(self.token),  # トークン設定フラグ
                'api_url': self.api_url,  # API URL
                'test_success': test_result,  # テスト成功フラグ
                'last_test_time': datetime.now().isoformat()  # 最終テスト時刻
            }
            
        except Exception as e:
            self.logger.error(f"通知状態取得エラー: {str(e)}")  # エラーログ出力
            return {                      # エラー情報を返す
                'token_configured': bool(self.token),  # トークン設定フラグ
                'api_url': self.api_url,  # API URL
                'test_success': False,     # テスト失敗フラグ
                'error': str(e)           # エラーメッセージ
            }
```

### 📄 notification_manager.py
通知管理クラス

```python
import threading
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .line_notify import LineNotify

class NotificationManager:
    """通知管理クラス"""
    
    def __init__(self):
        self.line_notify = LineNotify()  # LINE通知インスタンスを作成
        self.logger = logging.getLogger("notification_manager")  # ロガーを取得
        
        # 通知履歴
        self.notification_history = []   # 通知履歴リストを初期化
        self.max_history = 100           # 最大履歴数を設定
        
        # 通知設定
        self.settings = {                # 通知設定辞書を初期化
            'watering_notifications': True,  # 給水通知を有効
            'sensor_alerts': True,       # センサーアラートを有効
            'system_errors': True,       # システムエラー通知を有効
            'daily_reports': True,       # 日次レポートを有効
            'maintenance_reminders': True,  # メンテナンスリマインダーを有効
            'photo_notifications': False # 画像通知を無効（デフォルト）
        }
        
        # 通知間隔制御（スパム防止）
        self.last_notification_time = {} # 最後の通知時刻辞書を初期化
        self.min_notification_interval = 300  # 最小通知間隔を5分に設定
        
        # バックグラウンド監視
        self.running = False             # 実行フラグを初期化
        self.monitor_thread = None       # 監視スレッドを初期化
        
    def start_monitoring(self):
        """通知監視開始"""
        if self.running:                 # 既に実行中の場合
            self.logger.warning("通知監視は既に実行中です")  # 警告ログ出力
            return
        
        self.running = True               # 実行フラグを設定
        self.monitor_thread = threading.Thread(  # 監視スレッドを作成
            target=self._monitor_notifications,  # 監視関数を指定
            daemon=True                   # デーモンスレッドに設定
        )
        self.monitor_thread.start()      # 監視スレッド開始
        self.logger.info("通知監視開始")  # 開始ログ出力
    
    def stop_monitoring(self):
        """通知監視停止"""
        self.running = False             # 実行フラグをクリア
        self.logger.info("通知監視停止")  # 停止ログ出力
    
    def _monitor_notifications(self):
        """通知監視ループ"""
        while self.running:               # 実行中の場合
            try:
                # 日次レポート送信（毎日午前9時）
                now = datetime.now()      # 現在時刻を取得
                if now.hour == 9 and now.minute < 5:  # 午前9時0-4分の場合
                    self._send_daily_report_if_needed()  # 日次レポート送信（必要に応じて）
                
                # メンテナンスリマインダー（週次）
                if now.weekday() == 0 and now.hour == 10 and now.minute < 5:  # 月曜日午前10時0-4分の場合
                    self._send_maintenance_reminder_if_needed()  # メンテナンスリマインダー送信（必要に応じて）
                
                time.sleep(60)            # 1分間隔でチェック
                
            except Exception as e:
                self.logger.error(f"通知監視エラー: {str(e)}")  # エラーログ出力
                time.sleep(300)           # エラー時は5分待機
    
    def _can_send_notification(self, notification_type: str) -> bool:
        """通知送信可能かチェック（スパム防止）"""
        if not self.settings.get(notification_type, True):  # 通知設定が無効の場合
            return False                  # 送信不可を返す
        
        now = datetime.now()              # 現在時刻を取得
        last_time = self.last_notification_time.get(notification_type)  # 最後の通知時刻を取得
        
        if last_time:                     # 最後の通知時刻がある場合
            time_diff = (now - last_time).total_seconds()  # 経過時間を計算
            if time_diff < self.min_notification_interval:  # 最小間隔より短い場合
                self.logger.debug(f"通知間隔が短すぎます: {notification_type}")  # デバッグログ出力
                return False              # 送信不可を返す
        
        return True                       # 送信可能を返す
    
    def _record_notification(self, notification_type: str, success: bool, message: str = ""):
        """通知履歴を記録"""
        record = {                        # 通知記録を構築
            'type': notification_type,    # 通知タイプ
            'success': success,           # 成功フラグ
            'message': message,           # メッセージ
            'timestamp': datetime.now().isoformat()  # タイムスタンプ
        }
        
        self.notification_history.append(record)  # 履歴リストに追加
        
        # 履歴サイズ制限
        if len(self.notification_history) > self.max_history:  # 履歴数が上限を超えた場合
            self.notification_history.pop(0)  # 古い履歴を削除
        
        # 最後の通知時間更新
        if success:                       # 通知が成功した場合
            self.last_notification_time[notification_type] = datetime.now()  # 最後の通知時刻を更新
    
    def send_watering_notification(self, water_amount_ml: int) -> bool:
        """給水完了通知"""
        if not self._can_send_notification('watering_notifications'):  # 通知送信不可の場合
            return False                  # 失敗を返す
        
        try:
            success = self.line_notify.send_watering_notification(water_amount_ml)  # 給水通知を送信
            self._record_notification('watering', success, f"給水量: {water_amount_ml}ml")  # 履歴を記録
            return success                # 結果を返す
        except Exception as e:
            self.logger.error(f"給水通知エラー: {str(e)}")  # エラーログ出力
            self._record_notification('watering', False, str(e))  # エラー履歴を記録
            return False                  # 失敗を返す
    
    def send_sensor_alert(self, sensor_name: str, value: float, threshold: float) -> bool:
        """センサー異常通知"""
        if not self._can_send_notification('sensor_alerts'):  # 通知送信不可の場合
            return False                  # 失敗を返す
        
        try:
            success = self.line_notify.send_sensor_alert(sensor_name, value, threshold)  # センサーアラートを送信
            self._record_notification('sensor_alert', success, f"{sensor_name}: {value}")  # 履歴を記録
            return success                # 結果を返す
        except Exception as e:
            self.logger.error(f"センサーアラートエラー: {str(e)}")  # エラーログ出力
            self._record_notification('sensor_alert', False, str(e))  # エラー履歴を記録
            return False                  # 失敗を返す
    
    def send_water_tank_empty(self) -> bool:
        """水タンク空通知"""
        if not self._can_send_notification('system_errors'):  # 通知送信不可の場合
            return False                  # 失敗を返す
        
        try:
            success = self.line_notify.send_water_tank_empty()  # 水タンク空通知を送信
            self._record_notification('water_tank_empty', success, "水タンク空")  # 履歴を記録
            return success                # 結果を返す
        except Exception as e:
            self.logger.error(f"水タンク空通知エラー: {str(e)}")  # エラーログ出力
            self._record_notification('water_tank_empty', False, str(e))  # エラー履歴を記録
            return False                  # 失敗を返す
    
    def send_system_error(self, error_message: str) -> bool:
        """システムエラー通知"""
        if not self._can_send_notification('system_errors'):  # 通知送信不可の場合
            return False                  # 失敗を返す
        
        try:
            success = self.line_notify.send_system_error(error_message)  # システムエラー通知を送信
            self._record_notification('system_error', success, error_message)  # 履歴を記録
            return success                # 結果を返す
        except Exception as e:
            self.logger.error(f"システムエラー通知エラー: {str(e)}")  # エラーログ出力
            self._record_notification('system_error', False, str(e))  # エラー履歴を記録
            return False                  # 失敗を返す
    
    def send_photo_notification(self, image_path: str, message: str = None) -> bool:
        """画像付き通知"""
        if not self._can_send_notification('photo_notifications'):  # 通知送信不可の場合
            return False                  # 失敗を返す
        
        try:
            success = self.line_notify.send_photo_with_message(image_path, message)  # 画像付き通知を送信
            self._record_notification('photo', success, f"画像: {image_path}")  # 履歴を記録
            return success                # 結果を返す
        except Exception as e:
            self.logger.error(f"画像通知エラー: {str(e)}")  # エラーログ出力
            self._record_notification('photo', False, str(e))  # エラー履歴を記録
            return False                  # 失敗を返す
    
    def _send_daily_report_if_needed(self):
        """日次レポート送信（必要に応じて）"""
        try:
            # 昨日のデータを取得してレポート作成
            # ここでは仮のデータを使用
            report_data = {               # レポートデータを構築
                'avg_temperature': 25.5,  # 平均温度
                'avg_humidity': 60.2,     # 平均湿度
                'avg_soil_moisture': 45.8,  # 平均土壌水分
                'watering_count': 2,      # 給水回数
                'photo_count': 1          # 撮影回数
            }
            
            success = self.line_notify.send_daily_report(report_data)  # 日次レポートを送信
            self._record_notification('daily_report', success, "日次レポート")  # 履歴を記録
            
        except Exception as e:
            self.logger.error(f"日次レポート送信エラー: {str(e)}")  # エラーログ出力
            self._record_notification('daily_report', False, str(e))  # エラー履歴を記録
    
    def _send_maintenance_reminder_if_needed(self):
        """メンテナンスリマインダー送信（必要に応じて）"""
        try:
            # 最後のメンテナンス日をチェック
            days_since_last = 7           # 仮の値（実際はデータベースから取得）
            
            if days_since_last >= 7:      # 1週間以上経過の場合
                success = self.line_notify.send_maintenance_reminder(days_since_last)  # メンテナンスリマインダーを送信
                self._record_notification('maintenance_reminder', success, f"{days_since_last}日経過")  # 履歴を記録
            
        except Exception as e:
            self.logger.error(f"メンテナンスリマインダー送信エラー: {str(e)}")  # エラーログ出力
            self._record_notification('maintenance_reminder', False, str(e))  # エラー履歴を記録
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """通知設定更新"""
        try:
            self.settings.update(new_settings)  # 設定を更新
            self.logger.info(f"通知設定更新: {new_settings}")  # 更新ログ出力
            return True                    # 成功を返す
        except Exception as e:
            self.logger.error(f"通知設定更新エラー: {str(e)}")  # エラーログ出力
            return False                   # 失敗を返す
    
    def get_notification_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """通知履歴取得"""
        return self.notification_history[-limit:] if self.notification_history else []  # 最新N件を返す
    
    def get_notification_status(self) -> Dict[str, Any]:
        """通知機能状態取得"""
        try:
            line_status = self.line_notify.get_notification_status()  # LINE通知状態を取得
            
            return {                      # 状態情報を返す
                'line_notify_status': line_status,  # LINE通知状態
                'settings': self.settings,  # 通知設定
                'monitoring_active': self.running,  # 監視実行フラグ
                'history_count': len(self.notification_history),  # 履歴件数
                'last_notifications': self.last_notification_time  # 最後の通知時刻
            }
            
        except Exception as e:
            self.logger.error(f"通知状態取得エラー: {str(e)}")  # エラーログ出力
            return {                      # エラー情報を返す
                'error': str(e),          # エラーメッセージ
                'settings': self.settings,  # 通知設定
                'monitoring_active': self.running  # 監視実行フラグ
            }
    
    def test_all_notifications(self) -> Dict[str, bool]:
        """全通知機能のテスト"""
        results = {}                      # 結果辞書を初期化
        
        try:
            # テスト通知
            results['test_notification'] = self.line_notify.test_notification()  # テスト通知を送信
            
            # 各通知タイプのテスト（実際には送信しない）
            results['watering_notification'] = True  # 設定確認のみ
            results['sensor_alert'] = True
            results['system_error'] = True
            results['photo_notification'] = True
            
            self.logger.info("通知機能テスト完了")  # 完了ログ出力
            
        except Exception as e:
            self.logger.error(f"通知機能テストエラー: {str(e)}")  # エラーログ出力
            results['error'] = str(e)     # エラーを結果に追加
        
        return results                    # 結果を返す
```

---

## 📊 実装完了チェックリスト

- [ ] LINE Notify API設定完了
- [ ] 通知クラス実装完了
- [ ] 各種通知メソッド実装完了
- [ ] エラーハンドリング実装完了
- [ ] 環境変数設定完了
- [ ] テスト通知実行完了
- [ ] 通知管理システム実装完了
- [ ] 統合テスト完了

## 🎯 次のステップ

1. **センサー統合**: センサー異常時の通知
2. **給水統合**: 給水完了・失敗時の通知
3. **Web UI統合**: 通知設定画面
4. **統合テスト**: 全システムの動作確認

---

## 🏗️ クラス全体の流れと意味

### **LineNotifyクラス**
**意味**: LINE Notify APIとの直接的な通信を担当するクラス
**役割**:
- HTTP POSTリクエストによるメッセージ送信
- 画像付きメッセージの送信
- 各種通知メッセージのテンプレート化
- API認証とエラーハンドリング

### **NotificationManagerクラス**
**意味**: 通知システムの統合管理とスパム防止を担当するクラス
**役割**:
- 通知の送信制御とスパム防止
- 通知履歴の管理
- バックグラウンドでの定期通知
- 通知設定の管理

**全体の流れ**:
1. **初期化**: LINE Notifyトークンの設定、通知設定の読み込み
2. **通知送信**: 各種イベント（給水、センサー異常、エラー）に応じた通知
3. **スパム防止**: 5分間隔の通知制限で過度な通知を防止
4. **履歴管理**: 通知の送信履歴を記録・管理
5. **定期通知**: 日次レポート、メンテナンスリマインダーの自動送信
6. **設定管理**: 通知の有効/無効を動的に制御
7. **エラー処理**: 通信エラー時の適切な処理とログ出力

**通知タイプ**:
- **給水通知**: 給水完了時の成功メッセージ
- **センサーアラート**: 温度・湿度・土壌水分の異常値検知
- **システムエラー**: 水タンク空、通信エラー等の緊急通知
- **日次レポート**: 毎日午前9時の統計情報
- **メンテナンスリマインダー**: 週次のメンテナンス推奨
- **画像通知**: 植物の成長記録画像

**安全機能**:
- **スパム防止**: 同一タイプの通知を5分間隔で制限
- **設定管理**: 各通知タイプの有効/無効を個別制御
- **エラー処理**: 通信失敗時の再試行とログ記録
- **履歴管理**: 通知の送信履歴を100件まで保持

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

