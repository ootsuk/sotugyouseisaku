# LINE通知サービス実装手順書
## すくすくミントちゃん - LINE通知機能

---

## 📋 概要
スマートプランターからの自動通知をLINEで受信するための実装手順書

## 🎯 通知内容
- 水やり完了通知
- センサー異常アラート（温度・湿度・土壌水分）
- 水タンク空の警告
- システムエラー通知
- 植物の成長状況レポート

---

## 🛠️ 必要な準備

### 1. LINEアカウント
- 個人のLINEアカウント（通知受信用）
- LINE Notify サービスへの登録

### 2. 開発環境
- Raspberry Pi 5
- Python 3.11.x
- requests ライブラリ
- インターネット接続

---

## 🔧 実装手順

### Step 1: LINE Notify サービス登録

#### 1.1 LINE Notify にアクセス
```
URL: https://notify-bot.line.me/ja/
```

#### 1.2 ログイン
1. 「ログイン」ボタンをクリック
2. LINEアカウントでログイン
3. 認証完了

#### 1.3 トークン発行
1. 「マイページ」をクリック
2. 「トークンを発行する」をクリック
3. トークン名を入力（例：「すくすくミントちゃん」）
4. 通知先を選択（個人チャット or グループ）
5. 「発行」ボタンをクリック
6. **トークンをコピーして安全に保存**

> ⚠️ **重要**: トークンは一度しか表示されません。必ずコピーして保存してください。

---

### Step 2: Python環境準備

#### 2.1 必要なライブラリインストール
```bash
# Raspberry Pi上で実行
pip install requests
pip install python-dotenv  # 環境変数管理用
```

#### 2.2 環境変数ファイル作成
```bash
# プロジェクトディレクトリで実行
cd /home/pi/smart-planter
nano .env
```

**.env ファイル内容:**
```
LINE_NOTIFY_TOKEN=your_token_here
LINE_NOTIFY_API_URL=https://notify-api.line.me/api/notify
```

---

### Step 3: LINE通知クラス実装

#### 3.1 通知クラス作成
```python
# src/line_notify.py
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

class LineNotify:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('LINE_NOTIFY_TOKEN')
        self.api_url = os.getenv('LINE_NOTIFY_API_URL')
        
        if not self.token:
            raise ValueError("LINE_NOTIFY_TOKEN が設定されていません")
    
    def send_message(self, message, image_path=None):
        """
        LINE通知を送信
        
        Args:
            message (str): 送信するメッセージ
            image_path (str): 送信する画像のパス（オプション）
        
        Returns:
            bool: 送信成功時True、失敗時False
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            
            data = {
                'message': message
            }
            
            # 画像がある場合
            if image_path and os.path.exists(image_path):
                files = {'imageFile': open(image_path, 'rb')}
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    data=data, 
                    files=files
                )
                files['imageFile'].close()
            else:
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    data=data
                )
            
            if response.status_code == 200:
                print(f"✅ LINE通知送信成功: {message[:50]}...")
                return True
            else:
                print(f"❌ LINE通知送信失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ LINE通知送信エラー: {str(e)}")
            return False
    
    def send_watering_notification(self, water_amount=100):
        """水やり完了通知"""
        message = f"""
🌱 水やり完了！

💧 給水量: {water_amount}ml
⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

植物が元気に育っています 🌿
        """.strip()
        
        return self.send_message(message)
    
    def send_sensor_alert(self, sensor_type, value, threshold):
        """センサー異常アラート"""
        sensor_names = {
            'temperature': '🌡️ 温度',
            'humidity': '💧 湿度',
            'soil_moisture': '🌱 土壌水分'
        }
        
        message = f"""
⚠️ センサー異常検知！

{sensor_names.get(sensor_type, sensor_type)}: {value}
閾値: {threshold}
⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

システムを確認してください 🔧
        """.strip()
        
        return self.send_message(message)
    
    def send_water_tank_empty(self):
        """水タンク空警告"""
        message = f"""
🚨 水タンクが空です！

⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

水を補充してください 💧
        """.strip()
        
        return self.send_message(message)
    
    def send_system_error(self, error_message):
        """システムエラー通知"""
        message = f"""
🔧 システムエラー発生

エラー内容: {error_message}
⏰ 時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

システムを確認してください ⚠️
        """.strip()
        
        return self.send_message(message)
    
    def send_growth_report(self, image_path=None):
        """成長レポート送信"""
        message = f"""
📊 植物成長レポート

📅 日付: {datetime.now().strftime('%Y-%m-%d')}
⏰ 時刻: {datetime.now().strftime('%H:%M:%S')}

植物の様子を確認してください 🌱
        """.strip()
        
        return self.send_message(message, image_path)
```

---

### Step 4: メインアプリケーション統合

#### 4.1 メインアプリケーション例
```python
# src/main_app.py
from flask import Flask, render_template, request, jsonify
from line_notify import LineNotify
import time
import threading

app = Flask(__name__)
line_notify = LineNotify()

# センサー値のシミュレーション（実際のセンサー実装時に置き換え）
def get_sensor_data():
    """センサーデータ取得（シミュレーション）"""
    return {
        'temperature': 25.5,
        'humidity': 60.0,
        'soil_moisture': 150
    }

def check_sensor_alerts():
    """センサー異常チェック"""
    data = get_sensor_data()
    
    # 温度異常チェック
    if data['temperature'] < 5 or data['temperature'] > 35:
        line_notify.send_sensor_alert('temperature', data['temperature'], '5-35℃')
    
    # 湿度異常チェック
    if data['humidity'] < 30 or data['humidity'] > 85:
        line_notify.send_sensor_alert('humidity', data['humidity'], '30-85%')
    
    # 土壌水分異常チェック
    if data['soil_moisture'] < 159:
        line_notify.send_sensor_alert('soil_moisture', data['soil_moisture'], '159以上')

def auto_watering():
    """自動水やり処理"""
    data = get_sensor_data()
    
    if data['soil_moisture'] < 159:
        # 水やり実行（シミュレーション）
        print("💧 水やり実行中...")
        time.sleep(2)  # 実際のポンプ動作時間
        
        # 水やり完了通知
        line_notify.send_watering_notification(100)
        
        # 成長レポート送信
        line_notify.send_growth_report()

@app.route('/')
def dashboard():
    """ダッシュボード"""
    data = get_sensor_data()
    return render_template('dashboard.html', data=data)

@app.route('/manual_watering', methods=['POST'])
def manual_watering():
    """手動水やり"""
    try:
        # 水やり実行
        print("💧 手動水やり実行中...")
        time.sleep(2)
        
        # 通知送信
        success = line_notify.send_watering_notification(100)
        
        return jsonify({
            'success': success,
            'message': '水やり完了' if success else '水やり完了（通知送信失敗）'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'エラー: {str(e)}'
        })

@app.route('/test_notification', methods=['POST'])
def test_notification():
    """通知テスト"""
    try:
        success = line_notify.send_message("🧪 通知テスト成功！システムは正常に動作しています。")
        return jsonify({
            'success': success,
            'message': '通知テスト完了' if success else '通知テスト失敗'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'エラー: {str(e)}'
        })

if __name__ == '__main__':
    # バックグラウンドでセンサー監視開始
    sensor_thread = threading.Thread(target=check_sensor_alerts, daemon=True)
    sensor_thread.start()
    
    print("🌱 すくすくミントちゃん起動中...")
    print("📱 LINE通知機能: 有効")
    print("🌐 Web UI: http://192.168.1.100:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

### Step 5: テスト実行

#### 5.1 基本テスト
```python
# test_line_notify.py
from src.line_notify import LineNotify

def test_line_notify():
    """LINE通知テスト"""
    try:
        notify = LineNotify()
        
        # 基本メッセージテスト
        print("📱 基本メッセージテスト...")
        notify.send_message("🧪 すくすくミントちゃん通知テスト")
        
        # 水やり通知テスト
        print("💧 水やり通知テスト...")
        notify.send_watering_notification(100)
        
        # センサーアラートテスト
        print("⚠️ センサーアラートテスト...")
        notify.send_sensor_alert('temperature', 40, '35℃以下')
        
        print("✅ 全テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")

if __name__ == '__main__':
    test_line_notify()
```

#### 5.2 テスト実行
```bash
cd /home/pi/smart-planter
python test_line_notify.py
```

---

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. トークンエラー
```
エラー: 401 Unauthorized
解決方法:
- トークンが正しく設定されているか確認
- .envファイルの内容を確認
- トークンが有効期限内か確認
```

#### 2. ネットワークエラー
```
エラー: ConnectionError
解決方法:
- インターネット接続を確認
- ファイアウォール設定を確認
- プロキシ設定を確認
```

#### 3. 画像送信エラー
```
エラー: 画像ファイルが見つからない
解決方法:
- 画像ファイルのパスを確認
- ファイルの存在確認
- ファイルの読み取り権限確認
```

---

## 📱 通知例

### 水やり完了通知
```
🌱 水やり完了！

💧 給水量: 100ml
⏰ 時刻: 2025-01-15 14:30:25

植物が元気に育っています 🌿
```

### センサー異常アラート
```
⚠️ センサー異常検知！

🌡️ 温度: 40.5
閾値: 35℃以下
⏰ 時刻: 2025-01-15 14:30:25

システムを確認してください 🔧
```

### 水タンク空警告
```
🚨 水タンクが空です！

⏰ 時刻: 2025-01-15 14:30:25

水を補充してください 💧
```

---

## 🎯 実装完了チェックリスト

- [ ] LINE Notify アカウント作成
- [ ] トークン発行・設定
- [ ] Python環境準備
- [ ] LINE通知クラス実装
- [ ] メインアプリケーション統合
- [ ] 基本テスト実行
- [ ] 通知テスト実行
- [ ] エラーハンドリング確認
- [ ] 本番環境設定

---

## 🚀 次のステップ

1. **センサー統合**: 実際のセンサーと連携
2. **画像送信**: 植物の写真をLINEで送信
3. **スケジュール通知**: 定期レポート機能
4. **グループ通知**: 複数人への通知
5. **カスタム通知**: ユーザー設定可能な通知

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS
