# バックアップ管理機能 実装ガイド

## 📋 概要
データベース、設定ファイル、画像データの自動バックアップ・復元機能の実装手順書

## 🎯 実装目標
- 自動バックアップスケジューリング
- データベースバックアップ・復元
- 設定ファイルバックアップ
- 画像データバックアップ
- バックアップの圧縮・暗号化
- リモートバックアップ対応

## 📁 ファイル作成手順

### Step 1: ファイル作成
```bash
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter
touch src/backup/backup_manager.py
touch src/backup/backup_scheduler.py
mkdir -p src/backup
```

## 📄 実装コード

### 📄 src/backup/backup_manager.py
バックアップ管理クラス

```python
import logging
import time
import shutil
import zipfile
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import json

class BackupManager:
    """バックアップ管理クラス"""
    
    def __init__(self, backup_dir: str = "/mnt/usb-storage/backup"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('backup_manager')
        
        # バックアップ設定
        self.backup_settings = {
            'database': {
                'enabled': True,
                'source_path': '/mnt/usb-storage/smart_planter.db',
                'retention_days': 30
            },
            'images': {
                'enabled': True,
                'source_path': '/mnt/usb-storage/images',
                'retention_days': 90
            },
            'logs': {
                'enabled': True,
                'source_path': '/mnt/usb-storage/logs',
                'retention_days': 30
            },
            'settings': {
                'enabled': True,
                'source_path': '/home/pi/smart-planter/config',
                'retention_days': 90
            }
        }
    
    def create_full_backup(self, backup_name: str = None) -> Dict[str, Any]:
        """フルバックアップを作成"""
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"full_backup_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            backup_results = {}
            total_size = 0
            
            # 各コンポーネントをバックアップ
            for component, settings in self.backup_settings.items():
                if settings['enabled']:
                    result = self._backup_component(component, settings, backup_path)
                    backup_results[component] = result
                    if result['success']:
                        total_size += result['size_bytes']
            
            # バックアップ情報を記録
            backup_info = {
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'components': backup_results,
                'total_size_bytes': total_size,
                'backup_type': 'full'
            }
            
            info_file = backup_path / 'backup_info.json'
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            self.logger.info(f"フルバックアップを作成しました: {backup_name}")
            
            return {
                'success': True,
                'message': 'フルバックアップを作成しました',
                'backup_name': backup_name,
                'backup_path': str(backup_path),
                'total_size_bytes': total_size,
                'components': backup_results,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"フルバックアップ作成エラー: {str(e)}")
            return {
                'success': False,
                'message': f'フルバックアップ作成エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def _backup_component(self, component: str, settings: Dict[str, Any], backup_path: Path) -> Dict[str, Any]:
        """個別コンポーネントをバックアップ"""
        try:
            source_path = Path(settings['source_path'])
            
            if not source_path.exists():
                return {
                    'success': False,
                    'message': f'ソースパスが存在しません: {source_path}',
                    'size_bytes': 0
                }
            
            component_backup_path = backup_path / component
            
            if source_path.is_file():
                # ファイルの場合
                shutil.copy2(source_path, component_backup_path)
                size = component_backup_path.stat().st_size
            else:
                # ディレクトリの場合
                shutil.copytree(source_path, component_backup_path)
                size = sum(f.stat().st_size for f in component_backup_path.rglob('*') if f.is_file())
            
            return {
                'success': True,
                'message': f'{component}をバックアップしました',
                'source_path': str(source_path),
                'backup_path': str(component_backup_path),
                'size_bytes': size
            }
            
        except Exception as e:
            self.logger.error(f"{component}バックアップエラー: {str(e)}")
            return {
                'success': False,
                'message': f'{component}バックアップエラー: {str(e)}',
                'size_bytes': 0
            }
    
    def restore_from_backup(self, backup_name: str, components: List[str] = None) -> Dict[str, Any]:
        """バックアップから復元"""
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                return {
                    'success': False,
                    'message': f'バックアップが見つかりません: {backup_name}',
                    'timestamp': time.time()
                }
            
            # バックアップ情報を読み込み
            info_file = backup_path / 'backup_info.json'
            if info_file.exists():
                with open(info_file, 'r') as f:
                    backup_info = json.load(f)
            else:
                backup_info = {}
            
            if not components:
                components = list(self.backup_settings.keys())
            
            restore_results = {}
            
            for component in components:
                if component in self.backup_settings:
                    result = self._restore_component(component, backup_path)
                    restore_results[component] = result
            
            self.logger.info(f"バックアップから復元しました: {backup_name}")
            
            return {
                'success': True,
                'message': 'バックアップから復元しました',
                'backup_name': backup_name,
                'restored_components': restore_results,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"バックアップ復元エラー: {str(e)}")
            return {
                'success': False,
                'message': f'バックアップ復元エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def _restore_component(self, component: str, backup_path: Path) -> Dict[str, Any]:
        """個別コンポーネントを復元"""
        try:
            component_backup_path = backup_path / component
            
            if not component_backup_path.exists():
                return {
                    'success': False,
                    'message': f'コンポーネントバックアップが見つかりません: {component}'
                }
            
            settings = self.backup_settings[component]
            target_path = Path(settings['source_path'])
            
            # 既存ファイルをバックアップ
            if target_path.exists():
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_target = target_path.parent / f"{target_path.name}.backup_{backup_suffix}"
                shutil.move(str(target_path), str(backup_target))
            
            # 復元
            if component_backup_path.is_file():
                shutil.copy2(component_backup_path, target_path)
            else:
                shutil.copytree(component_backup_path, target_path)
            
            return {
                'success': True,
                'message': f'{component}を復元しました',
                'target_path': str(target_path)
            }
            
        except Exception as e:
            self.logger.error(f"{component}復元エラー: {str(e)}")
            return {
                'success': False,
                'message': f'{component}復元エラー: {str(e)}'
            }
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """古いバックアップをクリーンアップ"""
        try:
            cleanup_results = {}
            
            for component, settings in self.backup_settings.items():
                retention_days = settings['retention_days']
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                deleted_count = 0
                deleted_size = 0
                
                # バックアップディレクトリをスキャン
                for backup_dir in self.backup_dir.iterdir():
                    if backup_dir.is_dir():
                        # バックアップの作成日時をチェック
                        backup_mtime = datetime.fromtimestamp(backup_dir.stat().st_mtime)
                        
                        if backup_mtime < cutoff_date:
                            # バックアップサイズを計算
                            backup_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
                            
                            # 削除
                            shutil.rmtree(backup_dir)
                            deleted_count += 1
                            deleted_size += backup_size
                            
                            self.logger.info(f"古いバックアップを削除しました: {backup_dir.name}")
                
                cleanup_results[component] = {
                    'deleted_count': deleted_count,
                    'deleted_size_bytes': deleted_size,
                    'retention_days': retention_days
                }
            
            total_deleted = sum(result['deleted_count'] for result in cleanup_results.values())
            total_size = sum(result['deleted_size_bytes'] for result in cleanup_results.values())
            
            self.logger.info(f"古いバックアップのクリーンアップ完了: {total_deleted}件, {total_size} bytes")
            
            return {
                'success': True,
                'message': '古いバックアップをクリーンアップしました',
                'cleanup_results': cleanup_results,
                'total_deleted_count': total_deleted,
                'total_deleted_size_bytes': total_size,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"バックアップクリーンアップエラー: {str(e)}")
            return {
                'success': False,
                'message': f'バックアップクリーンアップエラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """バックアップ一覧を取得"""
        try:
            backups = []
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    # バックアップ情報を読み込み
                    info_file = backup_dir / 'backup_info.json'
                    
                    if info_file.exists():
                        with open(info_file, 'r') as f:
                            backup_info = json.load(f)
                    else:
                        # 情報ファイルがない場合は基本情報のみ
                        backup_info = {
                            'backup_name': backup_dir.name,
                            'created_at': datetime.fromtimestamp(backup_dir.stat().st_mtime).isoformat(),
                            'backup_type': 'unknown'
                        }
                    
                    # バックアップサイズを計算
                    backup_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
                    
                    backup_info['backup_size_bytes'] = backup_size
                    backup_info['backup_path'] = str(backup_dir)
                    
                    backups.append(backup_info)
            
            # 作成日時でソート（新しい順）
            backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return backups
            
        except Exception as e:
            self.logger.error(f"バックアップ一覧取得エラー: {str(e)}")
            return []
    
    def get_backup_status(self) -> Dict[str, Any]:
        """バックアップ状態を取得"""
        try:
            backups = self.list_backups()
            
            # 最新バックアップの情報
            latest_backup = backups[0] if backups else None
            
            # バックアップ統計
            total_backups = len(backups)
            total_size = sum(backup['backup_size_bytes'] for backup in backups)
            
            # 最後のバックアップからの経過時間
            last_backup_age = None
            if latest_backup:
                last_backup_time = datetime.fromisoformat(latest_backup['created_at'])
                last_backup_age = (datetime.now() - last_backup_time).total_seconds() / 3600  # 時間
            
            return {
                'total_backups': total_backups,
                'total_size_bytes': total_size,
                'latest_backup': latest_backup,
                'last_backup_age_hours': last_backup_age,
                'backup_settings': self.backup_settings,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"バックアップ状態取得エラー: {str(e)}")
            return {
                'error': str(e),
                'timestamp': time.time()
            }
```

### 📄 src/backup/backup_scheduler.py
バックアップスケジューラー

```python
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any
from .backup_manager import BackupManager

class BackupScheduler:
    """バックアップスケジューラークラス"""
    
    def __init__(self, backup_manager: BackupManager = None):
        self.backup_manager = backup_manager or BackupManager()
        self.logger = logging.getLogger('backup_scheduler')
        
        # スケジュール設定
        self.schedule_settings = {
            'full_backup_enabled': True,
            'full_backup_interval_hours': 24,  # 24時間ごと
            'full_backup_time': '02:00',  # 午前2時
            'cleanup_enabled': True,
            'cleanup_interval_hours': 24,  # 24時間ごと
            'cleanup_time': '03:00'  # 午前3時
        }
        
        # 実行状態
        self.running = False
        self.last_full_backup = None
        self.last_cleanup = None
    
    def start_scheduler(self):
        """スケジューラーを開始"""
        if self.running:
            self.logger.warning("バックアップスケジューラーは既に稼働中です")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.logger.info("バックアップスケジューラーを開始しました")
    
    def stop_scheduler(self):
        """スケジューラーを停止"""
        if not self.running:
            self.logger.warning("バックアップスケジューラーは稼働していません")
            return
        
        self.running = False
        if hasattr(self, 'scheduler_thread'):
            self.scheduler_thread.join()
        
        self.logger.info("バックアップスケジューラーを停止しました")
    
    def _scheduler_loop(self):
        """スケジューラーのメインループ"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # フルバックアップの実行
                if self.schedule_settings['full_backup_enabled']:
                    self._check_full_backup(current_time)
                
                # クリーンアップの実行
                if self.schedule_settings['cleanup_enabled']:
                    self._check_cleanup(current_time)
                
                # 60秒待機
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"バックアップスケジューラーループエラー: {str(e)}")
                time.sleep(60)
    
    def _check_full_backup(self, current_time: datetime):
        """フルバックアップの実行をチェック"""
        try:
            backup_time = self.schedule_settings['full_backup_time']
            hour, minute = map(int, backup_time.split(':'))
            
            target_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 指定時刻を過ぎていて、前回のバックアップから十分時間が経過している場合
            if (current_time >= target_time and 
                (not self.last_full_backup or 
                 (current_time - self.last_full_backup).total_seconds() >= self.schedule_settings['full_backup_interval_hours'] * 3600)):
                
                self.logger.info("スケジュールされたフルバックアップを開始します")
                
                result = self.backup_manager.create_full_backup()
                
                if result['success']:
                    self.last_full_backup = current_time
                    self.logger.info(f"スケジュールされたフルバックアップが完了しました: {result['backup_name']}")
                else:
                    self.logger.error(f"スケジュールされたフルバックアップが失敗しました: {result['message']}")
                    
        except Exception as e:
            self.logger.error(f"フルバックアップチェックエラー: {str(e)}")
    
    def _check_cleanup(self, current_time: datetime):
        """クリーンアップの実行をチェック"""
        try:
            cleanup_time = self.schedule_settings['cleanup_time']
            hour, minute = map(int, cleanup_time.split(':'))
            
            target_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 指定時刻を過ぎていて、前回のクリーンアップから十分時間が経過している場合
            if (current_time >= target_time and 
                (not self.last_cleanup or 
                 (current_time - self.last_cleanup).total_seconds() >= self.schedule_settings['cleanup_interval_hours'] * 3600)):
                
                self.logger.info("スケジュールされたクリーンアップを開始します")
                
                result = self.backup_manager.cleanup_old_backups()
                
                if result['success']:
                    self.last_cleanup = current_time
                    self.logger.info(f"スケジュールされたクリーンアップが完了しました: {result['total_deleted_count']}件削除")
                else:
                    self.logger.error(f"スケジュールされたクリーンアップが失敗しました: {result['message']}")
                    
        except Exception as e:
            self.logger.error(f"クリーンアップチェックエラー: {str(e)}")
    
    def update_schedule_settings(self, settings: Dict[str, Any]) -> bool:
        """スケジュール設定を更新"""
        try:
            self.schedule_settings.update(settings)
            self.logger.info("バックアップスケジュール設定を更新しました")
            return True
            
        except Exception as e:
            self.logger.error(f"スケジュール設定更新エラー: {str(e)}")
            return False
    
    def get_schedule_settings(self) -> Dict[str, Any]:
        """スケジュール設定を取得"""
        return self.schedule_settings.copy()
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """スケジューラーの状態を取得"""
        return {
            'running': self.running,
            'schedule_settings': self.schedule_settings,
            'last_full_backup': self.last_full_backup.isoformat() if self.last_full_backup else None,
            'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
            'timestamp': time.time()
        }
    
    def force_full_backup(self) -> Dict[str, Any]:
        """強制的にフルバックアップを実行"""
        try:
            self.logger.info("強制フルバックアップを開始します")
            
            result = self.backup_manager.create_full_backup()
            
            if result['success']:
                self.last_full_backup = datetime.now()
                self.logger.info("強制フルバックアップが完了しました")
            
            return result
            
        except Exception as e:
            self.logger.error(f"強制フルバックアップエラー: {str(e)}")
            return {
                'success': False,
                'message': f'強制フルバックアップエラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def force_cleanup(self) -> Dict[str, Any]:
        """強制的にクリーンアップを実行"""
        try:
            self.logger.info("強制クリーンアップを開始します")
            
            result = self.backup_manager.cleanup_old_backups()
            
            if result['success']:
                self.last_cleanup = datetime.now()
                self.logger.info("強制クリーンアップが完了しました")
            
            return result
            
        except Exception as e:
            self.logger.error(f"強制クリーンアップエラー: {str(e)}")
            return {
                'success': False,
                'message': f'強制クリーンアップエラー: {str(e)}',
                'timestamp': time.time()
            }
```

## 🧪 テスト方法

### 1. バックアップ管理テスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# バックアップ管理テスト
python -c "
from src.backup.backup_manager import BackupManager
manager = BackupManager('/tmp/backup_test')
result = manager.create_full_backup()
print(f'バックアップ結果: {result}')
"
```

### 2. バックアップスケジューラーテスト
```bash
# バックアップスケジューラーテスト
python -c "
from src.backup.backup_manager import BackupManager
from src.backup.backup_scheduler import BackupScheduler

manager = BackupManager('/tmp/backup_test')
scheduler = BackupScheduler(manager)
scheduler.start_scheduler()
time.sleep(5)
status = scheduler.get_scheduler_status()
print(f'スケジューラー状態: {status}')
scheduler.stop_scheduler()
"
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

