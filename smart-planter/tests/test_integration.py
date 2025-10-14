"""
統合テスト - すくすくミントちゃん
全機能の統合テストを実施
"""

import pytest
import json
from datetime import datetime


class TestWebApplication:
    """Webアプリケーションの統合テスト"""
    
    def test_app_initialization(self, client):
        """アプリケーションが正常に初期化されるか"""
        assert client is not None
    
    def test_index_page(self, client):
        """メインページが正常に表示されるか"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'すくすくミントちゃん' in response.data
    
    def test_dashboard_page(self, client):
        """ダッシュボードページが正常に表示されるか"""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'ダッシュボード' in response.data
    
    def test_settings_page(self, client):
        """設定ページが正常に表示されるか"""
        response = client.get('/settings')
        assert response.status_code == 200
        assert b'システム設定' in response.data
    
    def test_logs_page(self, client):
        """ログページが正常に表示されるか"""
        response = client.get('/logs')
        assert response.status_code == 200


class TestAPI:
    """APIエンドポイントの統合テスト"""
    
    def test_api_status(self, client):
        """システムステータスAPIが正常に動作するか"""
        response = client.get('/api/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'running'
        assert 'timestamp' in data
        assert data['version'] == '1.0.0'
    
    def test_api_sensors(self, client):
        """センサーデータAPIが正常に動作するか"""
        response = client.get('/api/sensors')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        
        sensor_data = data['data']
        assert 'temperature' in sensor_data
        assert 'humidity' in sensor_data
        assert 'soil_moisture' in sensor_data
        assert 'water_volume' in sensor_data
        assert 'water_percentage' in sensor_data
        assert 'timestamp' in sensor_data
    
    def test_api_watering_post(self, client):
        """手動給水APIが正常に動作するか"""
        response = client.post('/api/watering')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert '給水' in data['message']
    
    def test_api_settings_get(self, client):
        """設定取得APIが正常に動作するか"""
        response = client.get('/api/settings')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        
        settings = data['data']
        assert 'temperatureHumidityInterval' in settings
        assert 'soilMoistureThreshold' in settings
        assert settings['soilMoistureThreshold'] == 159
    
    def test_api_settings_post(self, client):
        """設定保存APIが正常に動作するか"""
        test_settings = {
            'soilMoistureThreshold': 150,
            'wateringIntervalHours': 24
        }
        
        response = client.post(
            '/api/settings',
            data=json.dumps(test_settings),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_api_camera_capture(self, client):
        """カメラ撮影APIが正常に動作するか"""
        response = client.post('/api/camera/capture')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_api_watering_history(self, client):
        """給水履歴APIが正常に動作するか"""
        response = client.get('/api/watering/history?days=7')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_api_watering_stop(self, client):
        """緊急停止APIが正常に動作するか"""
        response = client.post('/api/watering/stop')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_api_notifications_test(self, client):
        """テスト通知APIが正常に動作するか"""
        response = client.post('/api/notifications/test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def test_404_error(self, client):
        """存在しないページで404エラーが返されるか"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_404_error(self, client):
        """存在しないAPIで404エラーが返されるか"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404


class TestDataValidation:
    """データ検証のテスト"""
    
    def test_sensor_data_format(self, client):
        """センサーデータが正しい形式で返されるか"""
        response = client.get('/api/sensors')
        data = json.loads(response.data)
        
        sensor_data = data['data']
        
        # 温度は数値で-50〜50の範囲
        assert isinstance(sensor_data['temperature'], (int, float))
        assert -50 <= sensor_data['temperature'] <= 50
        
        # 湿度は数値で0〜100の範囲
        assert isinstance(sensor_data['humidity'], (int, float))
        assert 0 <= sensor_data['humidity'] <= 100
        
        # 土壌水分は数値
        assert isinstance(sensor_data['soil_moisture'], (int, float))
        
        # タイムスタンプはISO形式
        assert isinstance(sensor_data['timestamp'], str)
        # ISO形式の検証
        datetime.fromisoformat(sensor_data['timestamp'].replace('Z', '+00:00'))


class TestPerformance:
    """パフォーマンステスト"""
    
    def test_api_response_time(self, client):
        """APIのレスポンスタイムが適切か（1秒以内）"""
        import time
        
        start_time = time.time()
        response = client.get('/api/sensors')
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0  # 1秒以内
        assert response.status_code == 200
    
    def test_page_load_time(self, client):
        """ページのロード時間が適切か（1秒以内）"""
        import time
        
        start_time = time.time()
        response = client.get('/dashboard')
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0  # 1秒以内
        assert response.status_code == 200


@pytest.fixture
def client():
    """テスト用クライアントを作成"""
    from src.app.app import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


# テスト実行時の設定
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

