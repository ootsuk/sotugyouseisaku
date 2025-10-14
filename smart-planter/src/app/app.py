# すくすくミントちゃん Flaskアプリケーション

"""
Flaskアプリケーションのメインファイル
画面表示ルートのみを定義（APIは src/api/ に分離）
"""

from flask import Flask, render_template
import os
import logging


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
    
    # ========================================
    # 画面表示ルート（HTMLページ）
    # ========================================
    
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
    
    # ========================================
    # エラーハンドリング
    # ========================================
    
    @app.errorhandler(404)
    def not_found(error):
        """404エラー"""
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500エラー"""
        logger.error(f"Internal Server Error: {error}")
        return render_template('index.html'), 500
    
    logger.info("Flaskアプリケーションが作成されました")
    return app
