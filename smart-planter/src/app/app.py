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
            'temperature': 25.5,
            'humidity': 60.0,
            'soil_moisture': 180,
            'timestamp': datetime.now().isoformat()
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
    
    # エラーハンドリング
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info("Flaskアプリケーションが作成されました")
    return app
