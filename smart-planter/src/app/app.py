# すくすくミントちゃん Flaskアプリケーション

"""
Flaskアプリケーションのメインファイル
"""

from flask import Flask, render_template, jsonify, request
import os
import logging
from datetime import datetime

def create_app():
    """Flaskアプリケーションを作成・設定"""
    
    # テンプレートディレクトリを指定
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # 設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    @app.route('/')
    def index():
        """メインページ"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """ダッシュボードページ"""
        return render_template('dashboard.html')
    
    @app.route('/settings')
    def settings():
        """設定ページ"""
        return render_template('settings.html')
    
    @app.route('/logs')
    def logs():
        """ログページ"""
        # TODO: ログページを実装
        return render_template('index.html')  # 暫定的にindex.htmlを表示
    
    @app.route('/api/status')
    def api_status():
        """システムステータスAPI"""
        return jsonify({
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/api/sensors')
    def api_sensors():
        """センサーデータAPI"""
        # TODO: 実際のセンサーデータを取得
        return jsonify({
            'status': 'success',
            'data': {
                'temperature': 25.5,
                'humidity': 60.0,
                'soil_moisture': 180,
                'water_volume': 1500,
                'water_percentage': 75,
                'pressure': None,
                'timestamp': datetime.now().isoformat()
            }
        })
    
    @app.route('/api/watering', methods=['POST'])
    def api_watering():
        """手動給水API"""
        # TODO: 実際の給水制御を実装
        logger.info("手動給水が実行されました")
        return jsonify({
            'status': 'success',
            'message': '給水が完了しました',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/settings', methods=['GET', 'POST'])
    def api_settings():
        """設定API"""
        if request.method == 'GET':
            # TODO: 実際の設定を取得
            return jsonify({
                'status': 'success',
                'data': {
                    'temperatureHumidityInterval': 1800,
                    'soilMoistureInterval': 300,
                    'sensorCheckInterval': 60,
                    'soilMoistureThreshold': 159,
                    'wateringIntervalHours': 12,
                    'wateringDurationSeconds': 5,
                    'waterAmountMl': 100,
                    'cameraResolutionWidth': 1280,
                    'cameraResolutionHeight': 720,
                    'autoCaptureTime': '06:00',
                    'imageRetentionDays': 90,
                    'lineNotifyToken': '',
                    'notifyWatering': True,
                    'notifyError': True,
                    'notifyWaterLow': True,
                    'notifyDaily': False,
                    'dataBasePath': '/mnt/usb-storage',
                    'logLevel': 'INFO',
                    'debugMode': False,
                    'autoRestart': True,
                    'tempAlertMin': 5,
                    'tempAlertMax': 35,
                    'humidityAlertMin': 30,
                    'humidityAlertMax': 80,
                    'sensorErrorThreshold': 3
                }
            })
        else:
            # TODO: 設定を保存
            settings_data = request.get_json()
            logger.info(f"設定を保存: {settings_data}")
            return jsonify({
                'status': 'success',
                'message': '設定を保存しました'
            })
    
    @app.route('/api/camera/capture', methods=['POST'])
    def api_camera_capture():
        """カメラ撮影API"""
        # TODO: 実際のカメラ制御を実装
        logger.info("写真撮影が実行されました")
        return jsonify({
            'status': 'success',
            'message': '写真を撮影しました',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/watering/history')
    def api_watering_history():
        """給水履歴API"""
        # TODO: 実際の給水履歴を取得
        days = request.args.get('days', 7, type=int)
        return jsonify({
            'status': 'success',
            'data': []  # 空の履歴
        })
    
    @app.route('/api/watering/stop', methods=['POST'])
    def api_watering_stop():
        """緊急停止API"""
        # TODO: 実際の緊急停止を実装
        logger.warning("緊急停止が実行されました")
        return jsonify({
            'status': 'success',
            'message': '緊急停止を実行しました'
        })
    
    @app.route('/api/notifications/test', methods=['POST'])
    def api_notifications_test():
        """テスト通知API"""
        # TODO: 実際の通知を実装
        logger.info("テスト通知が送信されました")
        return jsonify({
            'status': 'success',
            'message': 'テスト通知を送信しました'
        })
    
    # エラーハンドリング
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info("Flaskアプリケーションが作成されました")
    return app
