"""
pytest設定ファイル
テスト全体で使用するフィクスチャを定義
"""

import pytest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def app():
    """Flaskアプリケーションのフィクスチャ"""
    from src.app.app import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    
    yield app


@pytest.fixture
def client(app):
    """テストクライアントのフィクスチャ"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLIランナーのフィクスチャ"""
    return app.test_cli_runner()

