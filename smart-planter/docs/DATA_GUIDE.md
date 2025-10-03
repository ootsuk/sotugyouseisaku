# データ管理機能 統合実装ガイド

## 📋 概要
センサーデータ、給水履歴、画像データの保存・管理・削除機能の詳細実装手順書

## 🎯 実装目標
- CSV形式でのセンサーデータ保存
- JSON形式での給水履歴保存
- JPEG形式での画像保存
- 90日間の自動削除機能
- USBストレージへの安全な保存

## 🛠️ 必要な環境

### ストレージ
- USBストレージ（本番環境）
- SDカード（フォールバック）
- 十分な空き容量（最低1GB）

### ソフトウェア
- Python 3.11.x
- pandas (CSV処理)
- Pillow (画像処理)
- pathlib (パス管理)

## 📁 ファイル作成手順

### Step 1: データディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd smart-planter

# データディレクトリの確認
ls -la src/data/
```

### Step 2: 各ファイルの作成順序
1. `src/data/csv_handler.py` - CSVファイル操作
2. `src/data/data_manager.py` - データ統合管理
3. `src/data/database.py` - データベース操作（将来用）

### Step 3: ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/data/csv_handler.py
touch src/data/data_manager.py
touch src/data/database.py
```

## 📄 実装コード

### 📄 src/data/csv_handler.py
CSVファイル操作クラス

```python
import csv
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

class CSVHandler:
    """CSVファイル操作クラス"""
    
    def __init__(self, base_path: str = "/mnt/usb-storage"):
        self.base_path = Path(base_path)
        self.csv_dir = self.base_path / "sensor_data"
        self.logger = logging.getLogger("csv_handler")
        
        # ディレクトリを作成
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"CSVハンドラーが初期化されました: {self.csv_dir}")
    
    def save_sensor_data(self, sensor_name: str, data: Dict[str, Any]) -> bool:
        """センサーデータをCSVに保存"""
        try:
            # ファイル名を生成（日付別）
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"{sensor_name}_{date_str}.csv"
            filepath = self.csv_dir / filename
            
            # CSVファイルが存在するかチェック
            file_exists = filepath.exists()
            
            # データを準備
            csv_data = {
                'timestamp': datetime.now().isoformat(),
                'sensor': sensor_name
            }
            csv_data.update(data)
            
            # CSVファイルに書き込み
            with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = csv_data.keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # ヘッダーを書き込み（新規ファイルの場合のみ）
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(csv_data)
            
            self.logger.debug(f"センサーデータを保存しました: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV保存エラー: {str(e)}")
            return False
    
    def read_sensor_data(self, 
                        sensor_name: str, 
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """センサーデータをCSVから読み取り"""
        try:
            data_list = []
            
            # 日付範囲が指定されていない場合は過去7日間
            if not start_date:
                start_date = datetime.now() - timedelta(days=7)
            if not end_date:
                end_date = datetime.now()
            
            # 指定期間内のファイルを検索
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y%m%d")
                filename = f"{sensor_name}_{date_str}.csv"
                filepath = self.csv_dir / filename
                
                if filepath.exists():
                    # CSVファイルを読み取り
                    df = pd.read_csv(filepath)
                    
                    # タイムスタンプでフィルタリング
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    filtered_df = df[
                        (df['timestamp'] >= start_date) & 
                        (df['timestamp'] <= end_date)
                    ]
                    
                    # 辞書のリストに変換
                    data_list.extend(filtered_df.to_dict('records'))
                
                current_date += timedelta(days=1)
            
            self.logger.info(f"センサーデータを読み取りました: {len(data_list)}件")
            return data_list
            
        except Exception as e:
            self.logger.error(f"CSV読み取りエラー: {str(e)}")
            return []
    
    def get_latest_data(self, sensor_name: str, count: int = 10) -> List[Dict[str, Any]]:
        """最新のセンサーデータを取得"""
        try:
            # 過去7日間のデータを取得
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            data_list = self.read_sensor_data(sensor_name, start_date, end_date)
            
            # タイムスタンプでソート（新しい順）
            data_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # 指定件数まで取得
            return data_list[:count]
            
        except Exception as e:
            self.logger.error(f"最新データ取得エラー: {str(e)}")
            return []
    
    def cleanup_old_files(self, days: int = 90) -> int:
        """古いCSVファイルを削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            # CSVディレクトリ内のファイルをチェック
            for filepath in self.csv_dir.glob("*.csv"):
                # ファイルの作成日時を取得
                file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    filepath.unlink()
                    deleted_count += 1
                    self.logger.info(f"古いファイルを削除しました: {filepath}")
            
            self.logger.info(f"古いCSVファイルの削除が完了しました: {deleted_count}件")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"古いファイル削除エラー: {str(e)}")
            return 0
    
    def get_file_info(self) -> Dict[str, Any]:
        """CSVファイルの情報を取得"""
        try:
            total_files = 0
            total_size = 0
            
            for filepath in self.csv_dir.glob("*.csv"):
                total_files += 1
                total_size += filepath.stat().st_size
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'directory': str(self.csv_dir)
            }
            
        except Exception as e:
            self.logger.error(f"ファイル情報取得エラー: {str(e)}")
            return {'total_files': 0, 'total_size_mb': 0, 'error': str(e)}
```

### 📄 src/data/data_manager.py
データ統合管理クラス

```python
import os
import json
import csv
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
import pandas as pd

from .csv_handler import CSVHandler

class DataManager:
    """データ管理クラス"""
    
    def __init__(self, base_path: str = "/mnt/usb-storage"):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger("data_manager")
        
        # ディレクトリ構造を作成
        self.directories = {
            'sensor_data': self.base_path / "sensor_data",
            'watering_history': self.base_path / "watering_history",
            'images': self.base_path / "images",
            'backup': self.base_path / "backup",
            'logs': self.base_path / "logs"
        }
        
        # 各ディレクトリを作成
        for dir_name, dir_path in self.directories.items():
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"ディレクトリを作成/確認しました: {dir_path}")
        
        # CSVハンドラーを初期化
        self.csv_handler = CSVHandler(str(self.base_path))
        
        self.logger.info("データマネージャーが初期化されました")
    
    def save_sensor_data(self, sensor_name: str, data: Dict[str, Any]) -> bool:
        """センサーデータを保存"""
        try:
            # CSVに保存
            success = self.csv_handler.save_sensor_data(sensor_name, data)
            
            if success:
                self.logger.debug(f"センサーデータを保存しました: {sensor_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"センサーデータ保存エラー: {str(e)}")
            return False
    
    def save_watering_history(self, watering_data: Dict[str, Any]) -> bool:
        """給水履歴を保存"""
        try:
            history_file = self.directories['watering_history'] / "watering_log.json"
            
            # 既存の履歴を読み込み
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            # 新しい記録を追加
            watering_record = {
                'timestamp': time.time(),
                'datetime': datetime.now().isoformat(),
                **watering_data
            }
            
            history.append(watering_record)
            
            # 履歴を保存（最新1000件のみ保持）
            if len(history) > 1000:
                history = history[-1000:]
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            self.logger.info(f"給水履歴を保存しました: {watering_record}")
            return True
            
        except Exception as e:
            self.logger.error(f"給水履歴保存エラー: {str(e)}")
            return False
    
    def save_image(self, image_data: bytes, filename: str = None) -> str:
        """画像を保存"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"plant_{timestamp}.jpg"
            
            image_path = self.directories['images'] / filename
            
            # 画像データを保存
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            # 画像のメタデータを記録
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    image_info = {
                        'filename': filename,
                        'path': str(image_path),
                        'width': width,
                        'height': height,
                        'size_bytes': len(image_data),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # 画像情報をJSONファイルに保存
                    info_file = self.directories['images'] / f"{filename}.json"
                    with open(info_file, 'w') as f:
                        json.dump(image_info, f, indent=2)
                    
            except Exception as e:
                self.logger.warning(f"画像メタデータ保存エラー: {str(e)}")
            
            self.logger.info(f"画像を保存しました: {image_path}")
            return str(image_path)
            
        except Exception as e:
            self.logger.error(f"画像保存エラー: {str(e)}")
            return None
    
    def get_sensor_data(self, 
                       sensor_name: str, 
                       days: int = 7) -> List[Dict[str, Any]]:
        """センサーデータを取得"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            return self.csv_handler.read_sensor_data(sensor_name, start_date, end_date)
            
        except Exception as e:
            self.logger.error(f"センサーデータ取得エラー: {str(e)}")
            return []
    
    def get_watering_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """給水履歴を取得"""
        try:
            history_file = self.directories['watering_history'] / "watering_log.json"
            
            if not history_file.exists():
                return []
            
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # 指定日数以内の記録のみフィルタリング
            cutoff_time = time.time() - (days * 24 * 3600)
            filtered_history = [
                record for record in history 
                if record.get('timestamp', 0) >= cutoff_time
            ]
            
            return filtered_history
            
        except Exception as e:
            self.logger.error(f"給水履歴取得エラー: {str(e)}")
            return []
    
    def get_image_list(self, days: int = 30) -> List[Dict[str, Any]]:
        """画像リストを取得"""
        try:
            image_list = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for image_file in self.directories['images'].glob("*.jpg"):
                # ファイルの作成日時をチェック
                file_mtime = datetime.fromtimestamp(image_file.stat().st_mtime)
                
                if file_mtime >= cutoff_date:
                    # 画像情報ファイルを読み取り
                    info_file = self.directories['images'] / f"{image_file.name}.json"
                    
                    if info_file.exists():
                        with open(info_file, 'r') as f:
                            image_info = json.load(f)
                        image_list.append(image_info)
                    else:
                        # 情報ファイルがない場合は基本情報のみ
                        image_list.append({
                            'filename': image_file.name,
                            'path': str(image_file),
                            'timestamp': file_mtime.isoformat()
                        })
            
            # タイムスタンプでソート（新しい順）
            image_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return image_list
            
        except Exception as e:
            self.logger.error(f"画像リスト取得エラー: {str(e)}")
            return []
    
    def cleanup_old_data(self, days: int = 90) -> Dict[str, int]:
        """古いデータを削除"""
        try:
            cleanup_results = {
                'sensor_data': 0,
                'watering_history': 0,
                'images': 0,
                'logs': 0
            }
            
            # センサーデータの削除
            cleanup_results['sensor_data'] = self.csv_handler.cleanup_old_files(days)
            
            # 給水履歴の削除
            history_file = self.directories['watering_history'] / "watering_log.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                cutoff_time = time.time() - (days * 24 * 3600)
                original_count = len(history)
                history = [record for record in history if record.get('timestamp', 0) >= cutoff_time]
                
                if len(history) < original_count:
                    with open(history_file, 'w') as f:
                        json.dump(history, f, indent=2)
                    cleanup_results['watering_history'] = original_count - len(history)
            
            # 画像の削除
            cutoff_date = datetime.now() - timedelta(days=days)
            for image_file in self.directories['images'].glob("*.jpg"):
                file_mtime = datetime.fromtimestamp(image_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    image_file.unlink()
                    cleanup_results['images'] += 1
                    
                    # 対応する情報ファイルも削除
                    info_file = self.directories['images'] / f"{image_file.name}.json"
                    if info_file.exists():
                        info_file.unlink()
            
            # ログファイルの削除
            for log_file in self.directories['logs'].glob("*.log"):
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    log_file.unlink()
                    cleanup_results['logs'] += 1
            
            total_cleaned = sum(cleanup_results.values())
            self.logger.info(f"古いデータの削除が完了しました: {cleanup_results}")
            
            return cleanup_results
            
        except Exception as e:
            self.logger.error(f"古いデータ削除エラー: {str(e)}")
            return {'error': str(e)}
    
    def create_backup(self) -> str:
        """データのバックアップを作成"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.directories['backup'] / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # 各ディレクトリをバックアップ
            for dir_name, source_dir in self.directories.items():
                if dir_name == 'backup':  # バックアップディレクトリは除外
                    continue
                
                if source_dir.exists():
                    dest_dir = backup_dir / dir_name
                    shutil.copytree(source_dir, dest_dir)
            
            self.logger.info(f"バックアップを作成しました: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            self.logger.error(f"バックアップ作成エラー: {str(e)}")
            return None
    
    def get_storage_info(self) -> Dict[str, Any]:
        """ストレージ情報を取得"""
        try:
            info = {
                'base_path': str(self.base_path),
                'directories': {},
                'total_size_mb': 0
            }
            
            # 各ディレクトリの情報を取得
            for dir_name, dir_path in self.directories.items():
                if dir_path.exists():
                    # ファイル数をカウント
                    file_count = len(list(dir_path.rglob("*")))
                    
                    # ディレクトリサイズを計算
                    dir_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                    dir_size_mb = round(dir_size / (1024 * 1024), 2)
                    
                    info['directories'][dir_name] = {
                        'path': str(dir_path),
                        'file_count': file_count,
                        'size_mb': dir_size_mb
                    }
                    
                    info['total_size_mb'] += dir_size_mb
            
            return info
            
        except Exception as e:
            self.logger.error(f"ストレージ情報取得エラー: {str(e)}")
            return {'error': str(e)}
```

### 📄 src/data/database.py
データベース操作クラス（将来用）

```python
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class DatabaseManager:
    """データベース管理クラス（将来の拡張用）"""
    
    def __init__(self, db_path: str = "/mnt/usb-storage/smart_planter.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger("database_manager")
        
        # データベースディレクトリを作成
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # データベースを初期化
        self._init_database()
        
        self.logger.info(f"データベースマネージャーが初期化されました: {self.db_path}")
    
    def _init_database(self):
        """データベースを初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # センサーデータテーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sensor_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sensor_name TEXT NOT NULL,
                        data_type TEXT NOT NULL,
                        value REAL,
                        unit TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 給水履歴テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS watering_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        duration INTEGER NOT NULL,
                        soil_moisture_before INTEGER,
                        soil_moisture_after INTEGER,
                        manual BOOLEAN DEFAULT 0,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 画像メタデータテーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS image_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        width INTEGER,
                        height INTEGER,
                        size_bytes INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                self.logger.info("データベーステーブルが初期化されました")
                
        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {str(e)}")
    
    def save_sensor_data(self, sensor_name: str, data: Dict[str, Any]) -> bool:
        """センサーデータをデータベースに保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for key, value in data.items():
                    if key not in ['timestamp', 'sensor']:
                        cursor.execute("""
                            INSERT INTO sensor_data (sensor_name, data_type, value, unit)
                            VALUES (?, ?, ?, ?)
                        """, (sensor_name, key, value, self._get_unit(key)))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"センサーデータ保存エラー: {str(e)}")
            return False
    
    def _get_unit(self, data_type: str) -> str:
        """データタイプに対応する単位を取得"""
        units = {
            'temperature': '°C',
            'humidity': '%',
            'soil_moisture': '',
            'pressure': 'Pa',
            'water_height': 'cm',
            'water_volume': 'ml'
        }
        return units.get(data_type, '')
    
    def get_sensor_data(self, 
                       sensor_name: str, 
                       days: int = 7) -> List[Dict[str, Any]]:
        """センサーデータをデータベースから取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM sensor_data 
                    WHERE sensor_name = ? 
                    AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                """.format(days), (sensor_name,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"センサーデータ取得エラー: {str(e)}")
            return []
    
    def cleanup_old_data(self, days: int = 90) -> int:
        """古いデータを削除"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM sensor_data 
                    WHERE timestamp < datetime('now', '-{} days')
                """.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"古いデータを削除しました: {deleted_count}件")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"古いデータ削除エラー: {str(e)}")
            return 0
```

## 🧪 テスト方法

### 1. CSVハンドラーテスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# CSVハンドラーテスト
python -c "
from src.data.csv_handler import CSVHandler
handler = CSVHandler()
data = {'temperature': 25.5, 'humidity': 60.0}
success = handler.save_sensor_data('test_sensor', data)
print(f'CSV保存結果: {success}')
"
```

### 2. データマネージャーテスト
```bash
# データマネージャーテスト
python -c "
from src.data.data_manager import DataManager
manager = DataManager()
data = {'temperature': 25.5, 'humidity': 60.0}
success = manager.save_sensor_data('test_sensor', data)
print(f'データ保存結果: {success}')
info = manager.get_storage_info()
print(f'ストレージ情報: {info}')
"
```

### 3. 統合テスト
```bash
# 統合テスト
python -c "
from src.data.data_manager import DataManager
import time

manager = DataManager()

# センサーデータを保存
sensor_data = {'temperature': 25.5, 'humidity': 60.0, 'soil_moisture': 180}
manager.save_sensor_data('temperature_humidity', sensor_data)

# 給水履歴を保存
watering_data = {'duration': 5, 'soil_moisture_before': 150, 'manual': False}
manager.save_watering_history(watering_data)

# データを取得
sensor_history = manager.get_sensor_data('temperature_humidity', days=1)
watering_history = manager.get_watering_history(days=1)

print(f'センサーデータ: {len(sensor_history)}件')
print(f'給水履歴: {len(watering_history)}件')
"
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

