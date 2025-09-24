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

---

## 📄 実装コード

### 📄 data_manager.py
データ管理クラス

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

class DataManager:
    """データ管理クラス"""
    
    def __init__(self, base_path: str = "/mnt/usb-storage"):
        self.base_path = Path(base_path)  # ベースパスをPathオブジェクトに変換
        self.logger = logging.getLogger("data_manager")  # ロガーを取得
        
        # データ保存期間（日数）
        self.data_retention_days = 90     # データ保持期間を90日に設定
        
        # ディレクトリ構造
        self.directories = {              # ディレクトリ辞書を初期化
            'sensor_data': self.base_path / 'sensor_data',      # センサーデータディレクトリ
            'watering_history': self.base_path / 'watering_history',  # 給水履歴ディレクトリ
            'images': self.base_path / 'images',                # 画像ディレクトリ
            'backup': self.base_path / 'backup',                # バックアップディレクトリ
            'logs': self.base_path / 'logs'                     # ログディレクトリ
        }
        
        # ディレクトリ作成
        self._create_directories()        # 必要なディレクトリを作成
        
        # フォールバック設定
        self.fallback_path = Path('./data')  # フォールバックパスを設定
        self.use_fallback = False        # フォールバック使用フラグを初期化
        
    def _create_directories(self):
        """必要なディレクトリを作成"""
        try:
            for dir_name, dir_path in self.directories.items():  # 全ディレクトリをループ
                dir_path.mkdir(parents=True, exist_ok=True)      # ディレクトリを作成（親ディレクトリも含む）
                self.logger.info(f"ディレクトリ作成: {dir_path}")  # 作成ログ出力
        except Exception as e:
            self.logger.error(f"ディレクトリ作成エラー: {str(e)}")  # エラーログ出力
            self._setup_fallback()       # フォールバック設定を実行
    
    def _setup_fallback(self):
        """フォールバック設定"""
        self.use_fallback = True         # フォールバックフラグを設定
        self.base_path = self.fallback_path  # ベースパスをフォールバックに変更
        
        # フォールバックディレクトリ作成
        for dir_name, dir_path in self.directories.items():  # 全ディレクトリをループ
            fallback_dir = self.fallback_path / dir_name     # フォールバックディレクトリパスを作成
            fallback_dir.mkdir(parents=True, exist_ok=True)  # フォールバックディレクトリを作成
            self.directories[dir_name] = fallback_dir        # ディレクトリ辞書を更新
        
        self.logger.warning("フォールバックモードに切り替えました")  # 警告ログ出力
    
    def save_sensor_data(self, sensor_name: str, data: Dict[str, Any]) -> bool:
        """センサーデータをCSV形式で保存"""
        try:
            csv_file = self.directories['sensor_data'] / f"{sensor_name}.csv"  # CSVファイルパスを作成
            
            # データにタイムスタンプ追加
            data['timestamp'] = datetime.now().isoformat()  # 現在時刻をISO形式で追加
            
            # CSVファイルの存在確認
            file_exists = csv_file.exists()  # ファイル存在確認
            
            # CSVに書き込み
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:  # CSVファイルを追記モードで開く
                fieldnames = list(data.keys())  # フィールド名を取得
                writer = csv.DictWriter(f, fieldnames=fieldnames)  # CSVライターを作成
                
                # ヘッダー書き込み（新規ファイルの場合のみ）
                if not file_exists:       # ファイルが存在しない場合
                    writer.writeheader()  # ヘッダーを書き込み
                
                writer.writerow(data)     # データ行を書き込み
            
            self.logger.debug(f"センサーデータ保存完了: {sensor_name}")  # デバッグログ出力
            return True                    # 成功を返す
            
        except Exception as e:
            self.logger.error(f"センサーデータ保存エラー: {str(e)}")  # エラーログ出力
            return False                   # 失敗を返す
    
    def save_watering_history(self, watering_data: Dict[str, Any]) -> bool:
        """給水履歴をJSON形式で保存"""
        try:
            json_file = self.directories['watering_history'] / 'watering_history.json'  # JSONファイルパスを作成
            
            # 既存データ読み込み
            history = []                  # 履歴リストを初期化
            if json_file.exists():        # JSONファイルが存在する場合
                with open(json_file, 'r', encoding='utf-8') as f:  # JSONファイルを読み込みモードで開く
                    history = json.load(f)  # JSONデータを読み込み
            
            # 新しいデータ追加
            watering_data['timestamp'] = datetime.now().isoformat()  # 現在時刻をISO形式で追加
            history.append(watering_data) # 履歴リストに追加
            
            # 最新100件のみ保持
            history = history[-100:]      # 最新100件に制限
            
            # JSONファイルに保存
            with open(json_file, 'w', encoding='utf-8') as f:  # JSONファイルを書き込みモードで開く
                json.dump(history, f, ensure_ascii=False, indent=2)  # JSONデータを書き込み
            
            self.logger.debug("給水履歴保存完了")  # デバッグログ出力
            return True                    # 成功を返す
            
        except Exception as e:
            self.logger.error(f"給水履歴保存エラー: {str(e)}")  # エラーログ出力
            return False                   # 失敗を返す
    
    def save_image(self, image_data: bytes, filename: str = None) -> Optional[str]:
        """画像データをJPEG形式で保存"""
        try:
            if filename is None:          # ファイル名が指定されていない場合
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # タイムスタンプを生成
                filename = f"plant_{timestamp}.jpg"  # ファイル名を生成
            
            image_path = self.directories['images'] / filename  # 画像ファイルパスを作成
            
            # 画像データをPIL Imageオブジェクトに変換
            image = Image.open(io.BytesIO(image_data))  # バイトデータからPIL Imageを作成
            
            # JPEG形式で保存
            image.save(image_path, 'JPEG', quality=85)  # JPEG形式で保存（品質85%）
            
            self.logger.debug(f"画像保存完了: {filename}")  # デバッグログ出力
            return str(image_path)        # 保存パスを返す
            
        except Exception as e:
            self.logger.error(f"画像保存エラー: {str(e)}")  # エラーログ出力
            return None                   # 失敗時はNoneを返す
    
    def get_sensor_data(self, sensor_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """センサーデータを取得"""
        try:
            csv_file = self.directories['sensor_data'] / f"{sensor_name}.csv"  # CSVファイルパスを作成
            
            if not csv_file.exists():     # CSVファイルが存在しない場合
                return []                 # 空リストを返す
            
            # pandasでCSV読み込み
            df = pd.read_csv(csv_file)    # CSVファイルをpandas DataFrameに読み込み
            
            # 日付フィルタリング
            cutoff_date = datetime.now() - timedelta(days=days)  # カットオフ日時を計算
            df['timestamp'] = pd.to_datetime(df['timestamp'])    # タイムスタンプ列を日時型に変換
            filtered_df = df[df['timestamp'] >= cutoff_date]     # カットオフ日時以降のデータをフィルタ
            
            return filtered_df.to_dict('records')  # DataFrameを辞書リストに変換して返す
            
        except Exception as e:
            self.logger.error(f"センサーデータ取得エラー: {str(e)}")  # エラーログ出力
            return []                     # 失敗時は空リストを返す
    
    def get_watering_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """給水履歴を取得"""
        try:
            json_file = self.directories['watering_history'] / 'watering_history.json'  # JSONファイルパスを作成
            
            if not json_file.exists():    # JSONファイルが存在しない場合
                return []                 # 空リストを返す
            
            with open(json_file, 'r', encoding='utf-8') as f:  # JSONファイルを読み込みモードで開く
                history = json.load(f)    # JSONデータを読み込み
            
            # 日付フィルタリング
            cutoff_date = datetime.now() - timedelta(days=days)  # カットオフ日時を計算
            filtered_history = []         # フィルタ済み履歴リストを初期化
            
            for record in history:        # 履歴をループ
                record_date = datetime.fromisoformat(record['timestamp'])  # 記録日時を取得
                if record_date >= cutoff_date:  # カットオフ日時以降の場合
                    filtered_history.append(record)  # フィルタ済みリストに追加
            
            return filtered_history       # フィルタ済み履歴を返す
            
        except Exception as e:
            self.logger.error(f"給水履歴取得エラー: {str(e)}")  # エラーログ出力
            return []                     # 失敗時は空リストを返す
    
    def get_latest_image(self) -> Optional[str]:
        """最新の画像パスを取得"""
        try:
            images_dir = self.directories['images']  # 画像ディレクトリを取得
            
            if not images_dir.exists():   # 画像ディレクトリが存在しない場合
                return None               # Noneを返す
            
            # 最新の画像ファイルを取得
            image_files = list(images_dir.glob("*.jpg"))  # JPGファイルのリストを取得
            if not image_files:           # 画像ファイルがない場合
                return None               # Noneを返す
            
            latest_image = max(image_files, key=os.path.getctime)  # 最新の画像ファイルを取得
            return str(latest_image)      # ファイルパスを文字列で返す
            
        except Exception as e:
            self.logger.error(f"最新画像取得エラー: {str(e)}")  # エラーログ出力
            return None                   # 失敗時はNoneを返す
    
    def cleanup_old_data(self) -> Dict[str, int]:
        """古いデータを削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)  # カットオフ日時を計算
            deleted_counts = {}           # 削除件数辞書を初期化
            
            # センサーデータクリーンアップ
            sensor_dir = self.directories['sensor_data']  # センサーデータディレクトリを取得
            deleted_counts['sensor_files'] = self._cleanup_csv_files(sensor_dir, cutoff_date)  # CSVファイルクリーンアップ
            
            # 画像データクリーンアップ
            images_dir = self.directories['images']       # 画像ディレクトリを取得
            deleted_counts['image_files'] = self._cleanup_image_files(images_dir, cutoff_date)  # 画像ファイルクリーンアップ
            
            # ログファイルクリーンアップ
            logs_dir = self.directories['logs']           # ログディレクトリを取得
            deleted_counts['log_files'] = self._cleanup_log_files(logs_dir, cutoff_date)  # ログファイルクリーンアップ
            
            self.logger.info(f"データクリーンアップ完了: {deleted_counts}")  # 完了ログ出力
            return deleted_counts         # 削除件数を返す
            
        except Exception as e:
            self.logger.error(f"データクリーンアップエラー: {str(e)}")  # エラーログ出力
            return {}                     # 失敗時は空辞書を返す
    
    def _cleanup_csv_files(self, directory: Path, cutoff_date: datetime) -> int:
        """CSVファイルのクリーンアップ"""
        deleted_count = 0                # 削除件数を初期化
        
        try:
            for csv_file in directory.glob("*.csv"):  # CSVファイルをループ
                # ファイルの最終更新日時をチェック
                file_mtime = datetime.fromtimestamp(csv_file.stat().st_mtime)  # ファイル更新日時を取得
                
                if file_mtime < cutoff_date:  # カットオフ日時より古い場合
                    # バックアップ作成
                    self._backup_file(csv_file)  # ファイルをバックアップ
                    
                    # ファイル削除
                    csv_file.unlink()     # ファイルを削除
                    deleted_count += 1    # 削除件数を増加
                    self.logger.debug(f"CSVファイル削除: {csv_file}")  # デバッグログ出力
        
        except Exception as e:
            self.logger.error(f"CSVクリーンアップエラー: {str(e)}")  # エラーログ出力
        
        return deleted_count              # 削除件数を返す
    
    def _cleanup_image_files(self, directory: Path, cutoff_date: datetime) -> int:
        """画像ファイルのクリーンアップ"""
        deleted_count = 0                # 削除件数を初期化
        
        try:
            for image_file in directory.glob("*.jpg"):  # JPGファイルをループ
                # ファイルの最終更新日時をチェック
                file_mtime = datetime.fromtimestamp(image_file.stat().st_mtime)  # ファイル更新日時を取得
                
                if file_mtime < cutoff_date:  # カットオフ日時より古い場合
                    # バックアップ作成
                    self._backup_file(image_file)  # ファイルをバックアップ
                    
                    # ファイル削除
                    image_file.unlink()   # ファイルを削除
                    deleted_count += 1    # 削除件数を増加
                    self.logger.debug(f"画像ファイル削除: {image_file}")  # デバッグログ出力
        
        except Exception as e:
            self.logger.error(f"画像クリーンアップエラー: {str(e)}")  # エラーログ出力
        
        return deleted_count              # 削除件数を返す
    
    def _cleanup_log_files(self, directory: Path, cutoff_date: datetime) -> int:
        """ログファイルのクリーンアップ"""
        deleted_count = 0                # 削除件数を初期化
        
        try:
            for log_file in directory.glob("*.log"):  # LOGファイルをループ
                # ファイルの最終更新日時をチェック
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)  # ファイル更新日時を取得
                
                if file_mtime < cutoff_date:  # カットオフ日時より古い場合
                    # バックアップ作成
                    self._backup_file(log_file)  # ファイルをバックアップ
                    
                    # ファイル削除
                    log_file.unlink()     # ファイルを削除
                    deleted_count += 1    # 削除件数を増加
                    self.logger.debug(f"ログファイル削除: {log_file}")  # デバッグログ出力
        
        except Exception as e:
            self.logger.error(f"ログクリーンアップエラー: {str(e)}")  # エラーログ出力
        
        return deleted_count              # 削除件数を返す
    
    def _backup_file(self, file_path: Path):
        """ファイルをバックアップ"""
        try:
            backup_dir = self.directories['backup']  # バックアップディレクトリを取得
            backup_dir.mkdir(exist_ok=True)         # バックアップディレクトリを作成
            
            # バックアップファイル名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # タイムスタンプを生成
            backup_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"  # バックアップファイル名を作成
            backup_path = backup_dir / backup_filename  # バックアップパスを作成
            
            # ファイルコピー
            shutil.copy2(file_path, backup_path)    # ファイルをコピー（メタデータも含む）
            self.logger.debug(f"バックアップ作成: {backup_path}")  # デバッグログ出力
            
        except Exception as e:
            self.logger.error(f"バックアップ作成エラー: {str(e)}")  # エラーログ出力
    
    def get_storage_info(self) -> Dict[str, Any]:
        """ストレージ情報を取得"""
        try:
            info = {                      # 情報辞書を初期化
                'base_path': str(self.base_path),  # ベースパスを文字列で追加
                'use_fallback': self.use_fallback,  # フォールバック使用フラグを追加
                'directories': {},        # ディレクトリ情報辞書を初期化
                'total_size': 0          # 総サイズを初期化
            }
            
            # 各ディレクトリの情報
            for dir_name, dir_path in self.directories.items():  # 全ディレクトリをループ
                if dir_path.exists():     # ディレクトリが存在する場合
                    dir_info = {          # ディレクトリ情報を構築
                        'path': str(dir_path),  # パスを文字列で追加
                        'exists': True,    # 存在フラグを設定
                        'file_count': len(list(dir_path.glob('*'))),  # ファイル数をカウント
                        'size': self._get_directory_size(dir_path)  # ディレクトリサイズを取得
                    }
                    info['total_size'] += dir_info['size']  # 総サイズに加算
                else:                     # ディレクトリが存在しない場合
                    dir_info = {          # ディレクトリ情報を構築
                        'path': str(dir_path),  # パスを文字列で追加
                        'exists': False,   # 存在フラグを設定
                        'file_count': 0,   # ファイル数を0に設定
                        'size': 0          # サイズを0に設定
                    }
                
                info['directories'][dir_name] = dir_info  # ディレクトリ情報を追加
            
            return info                   # 情報辞書を返す
            
        except Exception as e:
            self.logger.error(f"ストレージ情報取得エラー: {str(e)}")  # エラーログ出力
            return {}                     # 失敗時は空辞書を返す
    
    def _get_directory_size(self, directory: Path) -> int:
        """ディレクトリのサイズを取得"""
        total_size = 0                    # 総サイズを初期化
        try:
            for file_path in directory.rglob('*'):  # ディレクトリ内の全ファイルを再帰的にループ
                if file_path.is_file():   # ファイルの場合
                    total_size += file_path.stat().st_size  # ファイルサイズを加算
        except Exception as e:
            self.logger.error(f"ディレクトリサイズ取得エラー: {str(e)}")  # エラーログ出力
        
        return total_size                 # 総サイズを返す
    
    def create_backup(self) -> bool:
        """全データのバックアップを作成"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # タイムスタンプを生成
            backup_name = f"backup_{timestamp}"  # バックアップ名を作成
            backup_path = self.directories['backup'] / backup_name  # バックアップパスを作成
            
            # バックアップディレクトリ作成
            backup_path.mkdir(exist_ok=True)  # バックアップディレクトリを作成
            
            # 各ディレクトリをバックアップ
            for dir_name, dir_path in self.directories.items():  # 全ディレクトリをループ
                if dir_name != 'backup' and dir_path.exists():  # バックアップディレクトリ以外で存在する場合
                    dest_path = backup_path / dir_name  # バックアップ先パスを作成
                    shutil.copytree(dir_path, dest_path)  # ディレクトリを再帰的にコピー
            
            self.logger.info(f"バックアップ作成完了: {backup_path}")  # 完了ログ出力
            return True                    # 成功を返す
            
        except Exception as e:
            self.logger.error(f"バックアップ作成エラー: {str(e)}")  # エラーログ出力
            return False                   # 失敗を返す
```

### 📄 data_manager_service.py
データ管理サービス

```python
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .data_manager import DataManager
from ..sensors.sensor_manager import SensorManager
from ..watering.watering_controller import WateringController

class DataManagerService:
    """データ管理サービス"""
    
    def __init__(self, sensor_manager: SensorManager, watering_controller: WateringController):
        self.sensor_manager = sensor_manager  # センサーマネージャーを設定
        self.watering_controller = watering_controller  # 給水制御を設定
        self.data_manager = DataManager()     # データマネージャーを初期化
        self.logger = logging.getLogger("data_manager_service")  # ロガーを取得
        
        self.running = False              # 実行フラグを初期化
        self.save_thread = None           # 保存スレッドを初期化
        self.cleanup_thread = None        # クリーンアップスレッドを初期化
        
        # 保存間隔（秒）
        self.save_interval = 300          # 保存間隔を5分に設定
        self.cleanup_interval = 86400     # クリーンアップ間隔を24時間に設定
        
    def start_service(self):
        """データ管理サービス開始"""
        if self.running:                  # 既に実行中の場合
            self.logger.warning("データ管理サービスは既に実行中です")  # 警告ログ出力
            return
        
        self.running = True               # 実行フラグを設定
        
        # データ保存スレッド
        self.save_thread = threading.Thread(  # 保存スレッドを作成
            target=self._save_data_loop,  # 保存ループ関数を指定
            daemon=True                   # デーモンスレッドに設定
        )
        self.save_thread.start()          # 保存スレッド開始
        
        # クリーンアップスレッド
        self.cleanup_thread = threading.Thread(  # クリーンアップスレッドを作成
            target=self._cleanup_loop,    # クリーンアップループ関数を指定
            daemon=True                   # デーモンスレッドに設定
        )
        self.cleanup_thread.start()       # クリーンアップスレッド開始
        
        self.logger.info("データ管理サービス開始")  # 開始ログ出力
    
    def stop_service(self):
        """データ管理サービス停止"""
        self.running = False              # 実行フラグをクリア
        
        if self.save_thread:              # 保存スレッドが存在する場合
            self.save_thread.join(timeout=5)  # 保存スレッド終了を待機
        if self.cleanup_thread:           # クリーンアップスレッドが存在する場合
            self.cleanup_thread.join(timeout=5)  # クリーンアップスレッド終了を待機
        
        self.logger.info("データ管理サービス停止")  # 停止ログ出力
    
    def _save_data_loop(self):
        """データ保存ループ"""
        while self.running:               # 実行中の場合
            try:
                # センサーデータ保存
                sensor_data = self.sensor_manager.get_latest_data()  # 最新センサーデータを取得
                
                for sensor_name, data in sensor_data.items():  # センサーデータをループ
                    if 'error' not in data:  # エラーがない場合
                        self.data_manager.save_sensor_data(sensor_name, data)  # センサーデータを保存
                
                time.sleep(self.save_interval)  # 保存間隔待機
                
            except Exception as e:
                self.logger.error(f"データ保存ループエラー: {str(e)}")  # エラーログ出力
                time.sleep(60)            # エラー時は1分待機
    
    def _cleanup_loop(self):
        """クリーンアップループ"""
        while self.running:               # 実行中の場合
            try:
                # 毎日午前2時にクリーンアップ実行
                now = datetime.now()       # 現在時刻を取得
                if now.hour == 2 and now.minute < 5:  # 午前2時0-4分の場合
                    self.logger.info("データクリーンアップ開始")  # 開始ログ出力
                    deleted_counts = self.data_manager.cleanup_old_data()  # 古いデータをクリーンアップ
                    self.logger.info(f"クリーンアップ完了: {deleted_counts}")  # 完了ログ出力
                
                time.sleep(self.cleanup_interval)  # クリーンアップ間隔待機
                
            except Exception as e:
                self.logger.error(f"クリーンアップループエラー: {str(e)}")  # エラーログ出力
                time.sleep(3600)          # エラー時は1時間待機
    
    def save_watering_event(self, watering_data: Dict[str, Any]) -> bool:
        """給水イベントを保存"""
        try:
            return self.data_manager.save_watering_history(watering_data)  # 給水履歴を保存
        except Exception as e:
            self.logger.error(f"給水イベント保存エラー: {str(e)}")  # エラーログ出力
            return False                   # 失敗を返す
    
    def save_image_data(self, image_data: bytes, filename: str = None) -> Optional[str]:
        """画像データを保存"""
        try:
            return self.data_manager.save_image(image_data, filename)  # 画像を保存
        except Exception as e:
            self.logger.error(f"画像保存エラー: {str(e)}")  # エラーログ出力
            return None                   # 失敗時はNoneを返す
    
    def get_sensor_data_summary(self, days: int = 7) -> Dict[str, Any]:
        """センサーデータのサマリーを取得"""
        try:
            summary = {}                   # サマリー辞書を初期化
            
            # 各センサーのデータ取得
            for sensor_name in ['temperature_humidity', 'soil_moisture', 'water_level']:  # センサー名をループ
                data = self.data_manager.get_sensor_data(sensor_name, days)  # センサーデータを取得
                if data:                   # データが存在する場合
                    summary[sensor_name] = {  # センサーサマリーを構築
                        'count': len(data),  # データ件数
                        'latest': data[-1] if data else None,  # 最新データ
                        'first': data[0] if data else None     # 最初のデータ
                    }
            
            return summary                 # サマリーを返す
            
        except Exception as e:
            self.logger.error(f"センサーデータサマリー取得エラー: {str(e)}")  # エラーログ出力
            return {}                       # 失敗時は空辞書を返す
    
    def get_watering_summary(self, days: int = 30) -> Dict[str, Any]:
        """給水履歴のサマリーを取得"""
        try:
            history = self.data_manager.get_watering_history(days)  # 給水履歴を取得
            
            if not history:               # 履歴がない場合
                return {                  # 空のサマリーを返す
                    'total_waterings': 0,
                    'successful_waterings': 0,
                    'failed_waterings': 0,
                    'total_water_amount': 0,
                    'average_interval_hours': 0
                }
            
            successful = [h for h in history if h.get('success', False)]  # 成功した給水をフィルタ
            failed = [h for h in history if not h.get('success', False)]  # 失敗した給水をフィルタ
            
            total_amount = sum(h.get('water_amount_ml', 0) for h in successful)  # 総給水量を計算
            
            # 平均給水間隔計算
            intervals = []                # 間隔リストを初期化
            for i in range(1, len(history)):  # 履歴をループ（2番目から）
                prev_time = datetime.fromisoformat(history[i-1]['timestamp'])  # 前回の給水時間
                curr_time = datetime.fromisoformat(history[i]['timestamp'])    # 今回の給水時間
                interval = (curr_time - prev_time).total_seconds() / 3600      # 間隔を時間で計算
                intervals.append(interval) # 間隔リストに追加
            
            avg_interval = sum(intervals) / len(intervals) if intervals else 0  # 平均間隔を計算
            
            return {                      # サマリーを返す
                'total_waterings': len(history),  # 総給水回数
                'successful_waterings': len(successful),  # 成功給水回数
                'failed_waterings': len(failed),  # 失敗給水回数
                'total_water_amount': total_amount,  # 総給水量
                'average_interval_hours': round(avg_interval, 1)  # 平均間隔（小数点1桁）
            }
            
        except Exception as e:
            self.logger.error(f"給水サマリー取得エラー: {str(e)}")  # エラーログ出力
            return {}                       # 失敗時は空辞書を返す
    
    def get_storage_status(self) -> Dict[str, Any]:
        """ストレージ状態を取得"""
        try:
            storage_info = self.data_manager.get_storage_info()  # ストレージ情報を取得
            
            # 空き容量チェック
            import shutil
            total, used, free = shutil.disk_usage(self.data_manager.base_path)  # ディスク使用量を取得
            
            storage_info.update({         # ストレージ情報を更新
                'total_space': total,     # 総容量
                'used_space': used,       # 使用容量
                'free_space': free,       # 空き容量
                'usage_percentage': round((used / total) * 100, 1)  # 使用率（小数点1桁）
            })
            
            return storage_info           # ストレージ情報を返す
            
        except Exception as e:
            self.logger.error(f"ストレージ状態取得エラー: {str(e)}")  # エラーログ出力
            return {}                       # 失敗時は空辞書を返す
    
    def create_emergency_backup(self) -> bool:
        """緊急バックアップ作成"""
        try:
            return self.data_manager.create_backup()  # バックアップを作成
        except Exception as e:
            self.logger.error(f"緊急バックアップ作成エラー: {str(e)}")  # エラーログ出力
            return False                   # 失敗を返す
```

---

## 📊 実装完了チェックリスト

- [ ] データ管理クラス実装完了
- [ ] CSV保存機能実装完了
- [ ] JSON保存機能実装完了
- [ ] 画像保存機能実装完了
- [ ] 自動削除機能実装完了
- [ ] USBストレージ対応完了
- [ ] エラーハンドリング実装完了
- [ ] バックアップ機能実装完了
- [ ] テストスクリプト実行完了
- [ ] パフォーマンステスト完了

## 🎯 次のステップ

1. **API実装**: データ取得・検索API
2. **Web UI統合**: データ可視化
3. **統計機能**: データ分析・レポート
4. **統合テスト**: 全システムの動作確認

---

## 🏗️ クラス全体の流れと意味

### **DataManagerクラス**
**意味**: データの永続化と管理を担当する核となるクラス
**役割**:
- センサーデータのCSV形式保存
- 給水履歴のJSON形式保存
- 画像データのJPEG形式保存
- 古いデータの自動削除（90日間保持）
- USBストレージのフォールバック機能

### **DataManagerServiceクラス**
**意味**: データ管理の統合サービス層
**役割**:
- バックグラウンドでの継続的なデータ保存
- 定期クリーンアップの実行
- データサマリーの提供
- ストレージ状態の監視

**全体の流れ**:
1. **初期化**: ディレクトリ構造の作成、フォールバック設定
2. **データ保存**: センサーデータをCSV、給水履歴をJSON、画像をJPEGで保存
3. **定期保存**: 5分間隔でセンサーデータを自動保存
4. **定期クリーンアップ**: 毎日午前2時に90日以上古いデータを削除
5. **バックアップ**: 削除前にデータをバックアップ
6. **状態監視**: ストレージ使用量とディレクトリ状態を監視
7. **エラー処理**: USBストレージ失敗時はSDカードにフォールバック

**データ形式**:
- **CSV**: センサーデータ（タイムスタンプ、温度、湿度、土壌水分、水位）
- **JSON**: 給水履歴（タイムスタンプ、給水量、成功/失敗、連続回数）
- **JPEG**: 植物画像（品質85%、タイムスタンプ付きファイル名）

**安全機能**:
- **フォールバック**: USBストレージ失敗時のSDカード使用
- **バックアップ**: 削除前の自動バックアップ
- **容量監視**: ディスク使用量の継続監視
- **エラー処理**: 各操作での例外処理とログ出力

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

