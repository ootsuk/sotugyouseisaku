# データベース統合機能 実装ガイド

## 📋 概要
SQLiteデータベースを使用したデータ統合管理機能の実装手順書。センサーデータ、給水履歴、画像メタデータの統合管理

## 🎯 実装目標
- SQLiteデータベースの設計・構築
- センサーデータの統合管理
- 給水履歴の統合管理
- 画像メタデータの統合管理
- データクエリ・分析機能
- データベースバックアップ・復元

## 🛠️ 必要な環境

### ソフトウェア
- Python 3.11.x
- sqlite3 (標準ライブラリ)
- SQLAlchemy (ORM)
- pandas (データ分析)

## 📁 ファイル作成手順

### Step 1: データベースディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# データベースディレクトリの確認
ls -la src/data/
```

### Step 2: 各ファイルの作成順序
1. `src/data/database_models.py` - データベースモデル
2. `src/data/database_manager.py` - データベース管理
3. `src/data/data_analyzer.py` - データ分析

### Step 3: ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/data/database_models.py
touch src/data/database_manager.py
touch src/data/data_analyzer.py
```

### Step 4: 依存関係のインストール
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# 必要なライブラリをインストール
pip install SQLAlchemy
pip install pandas
pip install matplotlib

# requirements.txtを更新
pip freeze > requirements.txt
```

## 📄 実装コード

### 📄 src/data/database_models.py
データベースモデル定義

```python
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

Base = declarative_base()

class SensorData(Base):
    """センサーデータテーブル"""
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_name = Column(String(50), nullable=False, index=True)
    data_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    raw_data = Column(Text, nullable=True)  # JSON形式の生データ
    quality_score = Column(Float, default=1.0)  # データ品質スコア
    
    def __repr__(self):
        return f"<SensorData(id={self.id}, sensor={self.sensor_name}, type={self.data_type}, value={self.value})>"

class WateringHistory(Base):
    """給水履歴テーブル"""
    __tablename__ = 'watering_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration = Column(Integer, nullable=False)  # 給水時間（秒）
    soil_moisture_before = Column(Integer, nullable=True)
    soil_moisture_after = Column(Integer, nullable=True)
    manual = Column(Boolean, default=False)  # 手動給水フラグ
    success = Column(Boolean, default=True)  # 成功フラグ
    error_message = Column(Text, nullable=True)
    water_level_before = Column(Float, nullable=True)  # 給水前の水位
    water_level_after = Column(Float, nullable=True)  # 給水後の水位
    
    def __repr__(self):
        return f"<WateringHistory(id={self.id}, duration={self.duration}, manual={self.manual})>"

class ImageMetadata(Base):
    """画像メタデータテーブル"""
    __tablename__ = 'image_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    image_type = Column(String(50), nullable=True)  # photo, timelapse_frame, etc.
    session_id = Column(String(100), nullable=True)  # タイムラプスセッションID
    analysis_data = Column(Text, nullable=True)  # 画像分析結果（JSON）
    
    def __repr__(self):
        return f"<ImageMetadata(id={self.id}, filename={self.filename}, type={self.image_type})>"

class SystemLogs(Base):
    """システムログテーブル"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    component = Column(String(50), nullable=False)  # sensor, watering, camera, etc.
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # 追加詳細情報（JSON）
    
    def __repr__(self):
        return f"<SystemLogs(id={self.id}, level={self.level}, component={self.component})>"

class NotificationHistory(Base):
    """通知履歴テーブル"""
    __tablename__ = 'notification_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    notification_type = Column(String(50), nullable=False)  # alert, watering, daily_report
    message = Column(Text, nullable=False)
    recipient = Column(String(100), nullable=True)  # LINE Notify, email, etc.
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<NotificationHistory(id={self.id}, type={self.notification_type}, success={self.success})>"

class SystemSettings(Base):
    """システム設定テーブル"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String(100), nullable=False, unique=True)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(20), nullable=False)  # string, int, float, bool, json
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemSettings(key={self.setting_key}, value={self.setting_value})>"
```

### 📄 src/data/database_manager.py
データベース管理クラス

```python
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from sqlalchemy import create_engine, func, desc, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .database_models import (
    Base, SensorData, WateringHistory, ImageMetadata, 
    SystemLogs, NotificationHistory, SystemSettings
)

class DatabaseManager:
    """データベース管理クラス"""
    
    def __init__(self, db_path: str = "/mnt/usb-storage/smart_planter.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('database_manager')
        
        # SQLAlchemyエンジンとセッションを作成
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # データベースを初期化
        self._init_database()
        
        self.logger.info(f"データベースマネージャーが初期化されました: {self.db_path}")
    
    def _init_database(self):
        """データベースを初期化"""
        try:
            # テーブルを作成
            Base.metadata.create_all(bind=self.engine)
            
            # デフォルト設定を挿入
            self._insert_default_settings()
            
            self.logger.info("データベースが初期化されました")
            
        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {str(e)}")
            raise
    
    def _insert_default_settings(self):
        """デフォルト設定を挿入"""
        default_settings = [
            {
                'setting_key': 'soil_moisture_threshold',
                'setting_value': '159',
                'setting_type': 'int',
                'description': '土壌水分の給水閾値'
            },
            {
                'setting_key': 'watering_interval_hours',
                'setting_value': '12',
                'setting_type': 'int',
                'description': '給水間隔（時間）'
            },
            {
                'setting_key': 'notification_enabled',
                'setting_value': 'true',
                'setting_type': 'bool',
                'description': '通知機能の有効/無効'
            },
            {
                'setting_key': 'camera_enabled',
                'setting_value': 'true',
                'setting_type': 'bool',
                'description': 'カメラ機能の有効/無効'
            }
        ]
        
        try:
            with self.get_session() as session:
                for setting in default_settings:
                    existing = session.query(SystemSettings).filter(
                        SystemSettings.setting_key == setting['setting_key']
                    ).first()
                    
                    if not existing:
                        db_setting = SystemSettings(**setting)
                        session.add(db_setting)
                
                session.commit()
                self.logger.info("デフォルト設定を挿入しました")
                
        except Exception as e:
            self.logger.error(f"デフォルト設定挿入エラー: {str(e)}")
    
    def get_session(self) -> Session:
        """データベースセッションを取得"""
        return self.SessionLocal()
    
    def save_sensor_data(self, sensor_name: str, data: Dict[str, Any]) -> bool:
        """センサーデータを保存"""
        try:
            with self.get_session() as session:
                for key, value in data.items():
                    if key not in ['timestamp', 'sensor', 'error']:
                        sensor_record = SensorData(
                            sensor_name=sensor_name,
                            data_type=key,
                            value=float(value) if isinstance(value, (int, float)) else None,
                            unit=self._get_unit(key),
                            raw_data=json.dumps(data),
                            quality_score=self._calculate_quality_score(value)
                        )
                        session.add(sensor_record)
                
                session.commit()
                self.logger.debug(f"センサーデータを保存しました: {sensor_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"センサーデータ保存エラー: {str(e)}")
            return False
    
    def save_watering_history(self, watering_data: Dict[str, Any]) -> bool:
        """給水履歴を保存"""
        try:
            with self.get_session() as session:
                watering_record = WateringHistory(
                    duration=watering_data.get('duration', 0),
                    soil_moisture_before=watering_data.get('soil_moisture_before'),
                    soil_moisture_after=watering_data.get('soil_moisture_after'),
                    manual=watering_data.get('manual', False),
                    success=watering_data.get('success', True),
                    error_message=watering_data.get('error_message'),
                    water_level_before=watering_data.get('water_level_before'),
                    water_level_after=watering_data.get('water_level_after')
                )
                session.add(watering_record)
                session.commit()
                
                self.logger.info(f"給水履歴を保存しました: ID {watering_record.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"給水履歴保存エラー: {str(e)}")
            return False
    
    def save_image_metadata(self, image_data: Dict[str, Any]) -> bool:
        """画像メタデータを保存"""
        try:
            with self.get_session() as session:
                image_record = ImageMetadata(
                    filename=image_data['filename'],
                    file_path=image_data['file_path'],
                    file_size=image_data['file_size'],
                    width=image_data.get('width'),
                    height=image_data.get('height'),
                    image_type=image_data.get('image_type', 'photo'),
                    session_id=image_data.get('session_id'),
                    analysis_data=json.dumps(image_data.get('analysis_data')) if image_data.get('analysis_data') else None
                )
                session.add(image_record)
                session.commit()
                
                self.logger.info(f"画像メタデータを保存しました: {image_data['filename']}")
                return True
                
        except Exception as e:
            self.logger.error(f"画像メタデータ保存エラー: {str(e)}")
            return False
    
    def save_system_log(self, level: str, component: str, message: str, details: Dict[str, Any] = None) -> bool:
        """システムログを保存"""
        try:
            with self.get_session() as session:
                log_record = SystemLogs(
                    level=level,
                    component=component,
                    message=message,
                    details=json.dumps(details) if details else None
                )
                session.add(log_record)
                session.commit()
                
                return True
                
        except Exception as e:
            self.logger.error(f"システムログ保存エラー: {str(e)}")
            return False
    
    def save_notification_history(self, notification_data: Dict[str, Any]) -> bool:
        """通知履歴を保存"""
        try:
            with self.get_session() as session:
                notification_record = NotificationHistory(
                    notification_type=notification_data.get('type', 'unknown'),
                    message=notification_data.get('message', ''),
                    recipient=notification_data.get('recipient'),
                    success=notification_data.get('success', True),
                    error_message=notification_data.get('error_message')
                )
                session.add(notification_record)
                session.commit()
                
                return True
                
        except Exception as e:
            self.logger.error(f"通知履歴保存エラー: {str(e)}")
            return False
    
    def get_sensor_data(self, 
                       sensor_name: str = None, 
                       data_type: str = None,
                       start_date: datetime = None,
                       end_date: datetime = None,
                       limit: int = 1000) -> List[Dict[str, Any]]:
        """センサーデータを取得"""
        try:
            with self.get_session() as session:
                query = session.query(SensorData)
                
                # フィルタリング
                if sensor_name:
                    query = query.filter(SensorData.sensor_name == sensor_name)
                if data_type:
                    query = query.filter(SensorData.data_type == data_type)
                if start_date:
                    query = query.filter(SensorData.timestamp >= start_date)
                if end_date:
                    query = query.filter(SensorData.timestamp <= end_date)
                
                # ソートとリミット
                query = query.order_by(desc(SensorData.timestamp)).limit(limit)
                
                results = query.all()
                
                return [
                    {
                        'id': record.id,
                        'sensor_name': record.sensor_name,
                        'data_type': record.data_type,
                        'value': record.value,
                        'unit': record.unit,
                        'timestamp': record.timestamp.isoformat(),
                        'raw_data': json.loads(record.raw_data) if record.raw_data else None,
                        'quality_score': record.quality_score
                    }
                    for record in results
                ]
                
        except Exception as e:
            self.logger.error(f"センサーデータ取得エラー: {str(e)}")
            return []
    
    def get_watering_history(self, 
                           start_date: datetime = None,
                           end_date: datetime = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """給水履歴を取得"""
        try:
            with self.get_session() as session:
                query = session.query(WateringHistory)
                
                # フィルタリング
                if start_date:
                    query = query.filter(WateringHistory.timestamp >= start_date)
                if end_date:
                    query = query.filter(WateringHistory.timestamp <= end_date)
                
                # ソートとリミット
                query = query.order_by(desc(WateringHistory.timestamp)).limit(limit)
                
                results = query.all()
                
                return [
                    {
                        'id': record.id,
                        'timestamp': record.timestamp.isoformat(),
                        'duration': record.duration,
                        'soil_moisture_before': record.soil_moisture_before,
                        'soil_moisture_after': record.soil_moisture_after,
                        'manual': record.manual,
                        'success': record.success,
                        'error_message': record.error_message,
                        'water_level_before': record.water_level_before,
                        'water_level_after': record.water_level_after
                    }
                    for record in results
                ]
                
        except Exception as e:
            self.logger.error(f"給水履歴取得エラー: {str(e)}")
            return []
    
    def get_system_statistics(self, days: int = 7) -> Dict[str, Any]:
        """システム統計情報を取得"""
        try:
            with self.get_session() as session:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=days)
                
                # センサーデータ統計
                sensor_count = session.query(func.count(SensorData.id)).filter(
                    SensorData.timestamp >= start_date
                ).scalar()
                
                # 給水統計
                watering_count = session.query(func.count(WateringHistory.id)).filter(
                    WateringHistory.timestamp >= start_date
                ).scalar()
                
                manual_watering_count = session.query(func.count(WateringHistory.id)).filter(
                    and_(
                        WateringHistory.timestamp >= start_date,
                        WateringHistory.manual == True
                    )
                ).scalar()
                
                # 画像統計
                image_count = session.query(func.count(ImageMetadata.id)).filter(
                    ImageMetadata.timestamp >= start_date
                ).scalar()
                
                # 通知統計
                notification_count = session.query(func.count(NotificationHistory.id)).filter(
                    NotificationHistory.timestamp >= start_date
                ).scalar()
                
                # エラー統計
                error_count = session.query(func.count(SystemLogs.id)).filter(
                    and_(
                        SystemLogs.timestamp >= start_date,
                        SystemLogs.level == 'ERROR'
                    )
                ).scalar()
                
                return {
                    'period_days': days,
                    'sensor_data_count': sensor_count,
                    'watering_count': watering_count,
                    'manual_watering_count': manual_watering_count,
                    'image_count': image_count,
                    'notification_count': notification_count,
                    'error_count': error_count,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"システム統計取得エラー: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days: int = 90) -> Dict[str, int]:
        """古いデータを削除"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with self.get_session() as session:
                # センサーデータ削除
                sensor_deleted = session.query(SensorData).filter(
                    SensorData.timestamp < cutoff_date
                ).delete()
                
                # システムログ削除
                logs_deleted = session.query(SystemLogs).filter(
                    SystemLogs.timestamp < cutoff_date
                ).delete()
                
                # 通知履歴削除
                notifications_deleted = session.query(NotificationHistory).filter(
                    NotificationHistory.timestamp < cutoff_date
                ).delete()
                
                session.commit()
                
                result = {
                    'sensor_data_deleted': sensor_deleted,
                    'system_logs_deleted': logs_deleted,
                    'notifications_deleted': notifications_deleted,
                    'cutoff_date': cutoff_date.isoformat()
                }
                
                self.logger.info(f"古いデータを削除しました: {result}")
                return result
                
        except Exception as e:
            self.logger.error(f"古いデータ削除エラー: {str(e)}")
            return {}
    
    def _get_unit(self, data_type: str) -> str:
        """データタイプに対応する単位を取得"""
        units = {
            'temperature': '°C',
            'humidity': '%',
            'soil_moisture': '',
            'pressure': 'Pa',
            'water_height': 'cm',
            'water_volume': 'ml',
            'water_percentage': '%'
        }
        return units.get(data_type, '')
    
    def _calculate_quality_score(self, value: Any) -> float:
        """データ品質スコアを計算"""
        try:
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                # 異常値チェック（例：温度-50〜100°C、湿度0〜100%）
                if -50 <= value <= 100:
                    return 1.0
                else:
                    return 0.5
            return 1.0
        except:
            return 0.0
    
    def backup_database(self, backup_path: str = None) -> Dict[str, Any]:
        """データベースをバックアップ"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"/mnt/usb-storage/backup/smart_planter_backup_{timestamp}.db"
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # SQLiteデータベースをコピー
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            backup_size = backup_path.stat().st_size
            
            self.logger.info(f"データベースをバックアップしました: {backup_path}")
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'backup_size_bytes': backup_size,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"データベースバックアップエラー: {str(e)}")
            return {
                'success': False,
                'message': f'データベースバックアップエラー: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_setting(self, key: str, default_value: Any = None) -> Any:
        """システム設定を取得"""
        try:
            with self.get_session() as session:
                setting = session.query(SystemSettings).filter(
                    SystemSettings.setting_key == key
                ).first()
                
                if setting:
                    return self._convert_setting_value(setting.setting_value, setting.setting_type)
                else:
                    return default_value
                    
        except Exception as e:
            self.logger.error(f"システム設定取得エラー: {str(e)}")
            return default_value
    
    def set_system_setting(self, key: str, value: Any, setting_type: str = 'string', description: str = None) -> bool:
        """システム設定を設定"""
        try:
            with self.get_session() as session:
                setting = session.query(SystemSettings).filter(
                    SystemSettings.setting_key == key
                ).first()
                
                if setting:
                    # 既存設定を更新
                    setting.setting_value = str(value)
                    setting.setting_type = setting_type
                    if description:
                        setting.description = description
                else:
                    # 新規設定を作成
                    new_setting = SystemSettings(
                        setting_key=key,
                        setting_value=str(value),
                        setting_type=setting_type,
                        description=description
                    )
                    session.add(new_setting)
                
                session.commit()
                self.logger.info(f"システム設定を更新しました: {key} = {value}")
                return True
                
        except Exception as e:
            self.logger.error(f"システム設定設定エラー: {str(e)}")
            return False
    
    def _convert_setting_value(self, value: str, setting_type: str) -> Any:
        """設定値を適切な型に変換"""
        try:
            if setting_type == 'int':
                return int(value)
            elif setting_type == 'float':
                return float(value)
            elif setting_type == 'bool':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif setting_type == 'json':
                return json.loads(value)
            else:
                return value
        except:
            return value
```

### 📄 src/data/data_analyzer.py
データ分析クラス

```python
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

from .database_manager import DatabaseManager

class DataAnalyzer:
    """データ分析クラス"""
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.logger = logging.getLogger('data_analyzer')
    
    def analyze_sensor_trends(self, 
                            sensor_name: str = None,
                            data_type: str = None,
                            days: int = 7) -> Dict[str, Any]:
        """センサーデータのトレンド分析"""
        try:
            # データを取得
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            sensor_data = self.db_manager.get_sensor_data(
                sensor_name=sensor_name,
                data_type=data_type,
                start_date=start_date,
                end_date=end_date,
                limit=10000
            )
            
            if not sensor_data:
                return {
                    'success': False,
                    'message': '分析対象のデータがありません',
                    'timestamp': datetime.now().isoformat()
                }
            
            # DataFrameに変換
            df = pd.DataFrame(sensor_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 基本統計
            stats = {
                'count': len(df),
                'mean': df['value'].mean(),
                'std': df['value'].std(),
                'min': df['value'].min(),
                'max': df['value'].max(),
                'median': df['value'].median()
            }
            
            # トレンド分析
            df_sorted = df.sort_values('timestamp')
            df_sorted['value_diff'] = df_sorted['value'].diff()
            
            # 傾向の判定
            trend = 'stable'
            if len(df_sorted) > 1:
                recent_trend = df_sorted['value_diff'].tail(10).mean()
                if recent_trend > 0.1:
                    trend = 'increasing'
                elif recent_trend < -0.1:
                    trend = 'decreasing'
            
            # 異常値検出
            q1 = df['value'].quantile(0.25)
            q3 = df['value'].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = df[(df['value'] < lower_bound) | (df['value'] > upper_bound)]
            
            analysis_result = {
                'success': True,
                'sensor_name': sensor_name or 'all',
                'data_type': data_type or 'all',
                'period_days': days,
                'statistics': stats,
                'trend': trend,
                'outliers_count': len(outliers),
                'outliers_data': outliers.to_dict('records') if len(outliers) > 0 else [],
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"センサーデータトレンド分析完了: {sensor_name}/{data_type}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"センサーデータトレンド分析エラー: {str(e)}")
            return {
                'success': False,
                'message': f'センサーデータトレンド分析エラー: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_watering_patterns(self, days: int = 30) -> Dict[str, Any]:
        """給水パターン分析"""
        try:
            # 給水履歴を取得
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            watering_data = self.db_manager.get_watering_history(
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
            
            if not watering_data:
                return {
                    'success': False,
                    'message': '給水履歴データがありません',
                    'timestamp': datetime.now().isoformat()
                }
            
            # DataFrameに変換
            df = pd.DataFrame(watering_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 基本統計
            total_waterings = len(df)
            manual_waterings = len(df[df['manual'] == True])
            auto_waterings = len(df[df['manual'] == False])
            
            avg_duration = df['duration'].mean()
            total_watering_time = df['duration'].sum()
            
            # 日別給水回数
            df['date'] = df['timestamp'].dt.date
            daily_waterings = df.groupby('date').size().reset_index(name='count')
            
            # 時間別給水回数
            df['hour'] = df['timestamp'].dt.hour
            hourly_waterings = df.groupby('hour').size().reset_index(name='count')
            
            # 土壌水分変化分析
            soil_moisture_changes = []
            for _, row in df.iterrows():
                if pd.notna(row['soil_moisture_before']) and pd.notna(row['soil_moisture_after']):
                    change = row['soil_moisture_after'] - row['soil_moisture_before']
                    soil_moisture_changes.append({
                        'timestamp': row['timestamp'].isoformat(),
                        'change': change,
                        'duration': row['duration']
                    })
            
            analysis_result = {
                'success': True,
                'period_days': days,
                'total_waterings': total_waterings,
                'manual_waterings': manual_waterings,
                'auto_waterings': auto_waterings,
                'average_duration': round(avg_duration, 2),
                'total_watering_time_seconds': int(total_watering_time),
                'daily_watering_pattern': daily_waterings.to_dict('records'),
                'hourly_watering_pattern': hourly_waterings.to_dict('records'),
                'soil_moisture_changes': soil_moisture_changes,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"給水パターン分析完了: {days}日間")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"給水パターン分析エラー: {str(e)}")
            return {
                'success': False,
                'message': f'給水パターン分析エラー: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_growth_report(self, days: int = 30) -> Dict[str, Any]:
        """植物成長レポート生成"""
        try:
            # 画像メタデータを取得
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            with self.db_manager.get_session() as session:
                from .database_models import ImageMetadata
                
                images = session.query(ImageMetadata).filter(
                    and_(
                        ImageMetadata.timestamp >= start_date,
                        ImageMetadata.image_type == 'photo'
                    )
                ).order_by(ImageMetadata.timestamp).all()
            
            if len(images) < 2:
                return {
                    'success': False,
                    'message': '成長分析に十分な画像がありません（最低2枚必要）',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 分析データを処理
            growth_data = []
            for image in images:
                if image.analysis_data:
                    try:
                        import json
                        analysis = json.loads(image.analysis_data)
                        growth_data.append({
                            'timestamp': image.timestamp.isoformat(),
                            'green_percentage': analysis.get('green_percentage', 0),
                            'plant_area': analysis.get('largest_area', 0),
                            'filename': image.filename
                        })
                    except:
                        continue
            
            if len(growth_data) < 2:
                return {
                    'success': False,
                    'message': '有効な分析データが不足しています',
                    'timestamp': datetime.now().isoformat()
                }
            
            # 成長率計算
            growth_df = pd.DataFrame(growth_data)
            growth_df['timestamp'] = pd.to_datetime(growth_df['timestamp'])
            
            first_green = growth_df['green_percentage'].iloc[0]
            last_green = growth_df['green_percentage'].iloc[-1]
            green_growth_rate = ((last_green - first_green) / first_green) * 100 if first_green > 0 else 0
            
            first_area = growth_df['plant_area'].iloc[0]
            last_area = growth_df['plant_area'].iloc[-1]
            area_growth_rate = ((last_area - first_area) / first_area) * 100 if first_area > 0 else 0
            
            # 成長傾向
            growth_trend = 'stable'
            if green_growth_rate > 5:
                growth_trend = 'growing'
            elif green_growth_rate < -5:
                growth_trend = 'declining'
            
            report = {
                'success': True,
                'period_days': days,
                'image_count': len(images),
                'analysis_count': len(growth_data),
                'green_percentage_growth_rate': round(green_growth_rate, 2),
                'plant_area_growth_rate': round(area_growth_rate, 2),
                'growth_trend': growth_trend,
                'first_measurement': {
                    'timestamp': growth_data[0]['timestamp'],
                    'green_percentage': growth_data[0]['green_percentage'],
                    'plant_area': growth_data[0]['plant_area']
                },
                'last_measurement': {
                    'timestamp': growth_data[-1]['timestamp'],
                    'green_percentage': growth_data[-1]['green_percentage'],
                    'plant_area': growth_data[-1]['plant_area']
                },
                'growth_data': growth_data,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"植物成長レポート生成完了: {days}日間")
            return report
            
        except Exception as e:
            self.logger.error(f"植物成長レポート生成エラー: {str(e)}")
            return {
                'success': False,
                'message': f'植物成長レポート生成エラー: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def create_sensor_chart(self, 
                           sensor_name: str,
                           data_type: str,
                           days: int = 7,
                           output_path: str = None) -> Dict[str, Any]:
        """センサーデータのチャート作成"""
        try:
            # データを取得
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            sensor_data = self.db_manager.get_sensor_data(
                sensor_name=sensor_name,
                data_type=data_type,
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
            
            if not sensor_data:
                return {
                    'success': False,
                    'message': 'チャート作成対象のデータがありません',
                    'timestamp': datetime.now().isoformat()
                }
            
            # DataFrameに変換
            df = pd.DataFrame(sensor_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # チャート作成
            plt.figure(figsize=(12, 6))
            plt.plot(df['timestamp'], df['value'], marker='o', markersize=3)
            plt.title(f'{sensor_name} - {data_type} ({days}日間)')
            plt.xlabel('時間')
            plt.ylabel(f'{data_type} ({self.db_manager._get_unit(data_type)})')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # 出力パスを設定
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"/mnt/usb-storage/charts/{sensor_name}_{data_type}_{timestamp}.png"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # チャートを保存
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            # ファイルサイズを取得
            file_size = output_path.stat().st_size
            
            self.logger.info(f"センサーチャートを作成しました: {output_path}")
            
            return {
                'success': True,
                'message': 'センサーチャートを作成しました',
                'chart_path': str(output_path),
                'file_size_bytes': file_size,
                'data_points': len(df),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"センサーチャート作成エラー: {str(e)}")
            return {
                'success': False,
                'message': f'センサーチャート作成エラー: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_health_score(self, days: int = 7) -> Dict[str, Any]:
        """システムヘルススコア計算"""
        try:
            # 統計データを取得
            stats = self.db_manager.get_system_statistics(days=days)
            
            if not stats:
                return {
                    'success': False,
                    'message': 'システム統計データが取得できません',
                    'timestamp': datetime.now().isoformat()
                }
            
            # ヘルススコア計算（0-100点）
            health_score = 100
            
            # エラー率による減点
            total_logs = stats.get('error_count', 0) + 100  # 仮の正常ログ数
            error_rate = stats.get('error_count', 0) / total_logs
            health_score -= min(50, error_rate * 100)
            
            # センサーデータの充実度
            expected_sensor_data = days * 24 * 60 / 5  # 5分間隔で取得想定
            sensor_data_count = stats.get('sensor_data_count', 0)
            data_completeness = min(1.0, sensor_data_count / expected_sensor_data)
            health_score *= data_completeness
            
            # 給水システムの稼働状況
            watering_count = stats.get('watering_count', 0)
            if watering_count > 0:
                manual_ratio = stats.get('manual_watering_count', 0) / watering_count
                if manual_ratio > 0.5:  # 手動給水が50%以上
                    health_score -= 10
            
            # 最終スコア
            final_score = max(0, min(100, health_score))
            
            # ヘルスレベル判定
            if final_score >= 90:
                health_level = 'excellent'
            elif final_score >= 75:
                health_level = 'good'
            elif final_score >= 60:
                health_level = 'fair'
            elif final_score >= 40:
                health_level = 'poor'
            else:
                health_level = 'critical'
            
            result = {
                'success': True,
                'health_score': round(final_score, 1),
                'health_level': health_level,
                'period_days': days,
                'factors': {
                    'error_rate': round(error_rate * 100, 2),
                    'data_completeness': round(data_completeness * 100, 2),
                    'manual_watering_ratio': round((stats.get('manual_watering_count', 0) / max(1, watering_count)) * 100, 2)
                },
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"システムヘルススコア計算完了: {final_score:.1f}点 ({health_level})")
            return result
            
        except Exception as e:
            self.logger.error(f"システムヘルススコア計算エラー: {str(e)}")
            return {
                'success': False,
                'message': f'システムヘルススコア計算エラー: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
```

## 🧪 テスト方法

### 1. データベース初期化テスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# データベース初期化テスト
python -c "
from src.data.database_manager import DatabaseManager
db = DatabaseManager('/tmp/test.db')
print('データベース初期化成功')
"
```

### 2. データ保存テスト
```bash
# センサーデータ保存テスト
python -c "
from src.data.database_manager import DatabaseManager
db = DatabaseManager('/tmp/test.db')
data = {'temperature': 25.5, 'humidity': 60.0}
success = db.save_sensor_data('test_sensor', data)
print(f'センサーデータ保存: {success}')
"
```

### 3. データ分析テスト
```bash
# データ分析テスト
python -c "
from src.data.database_manager import DatabaseManager
from src.data.data_analyzer import DataAnalyzer

db = DatabaseManager('/tmp/test.db')
analyzer = DataAnalyzer(db)
result = analyzer.get_system_health_score(days=7)
print(f'システムヘルススコア: {result}')
"
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

