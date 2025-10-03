# カメラ制御機能 実装ガイド

## 📋 概要
Raspberry Pi Camera Moduleを使用した写真撮影、タイムラプス作成、画像処理機能の実装手順書

## 🎯 実装目標
- カメラモジュールの初期化と制御
- 写真撮影機能（JPEG形式）
- タイムラプス動画作成
- 画像処理・分析機能
- 自動撮影スケジューリング

## 🛠️ 必要な環境

### ハードウェア
- Raspberry Pi Camera Module v2
- microSDカード（十分な容量）
- カメラケーブル

### ソフトウェア
- Python 3.11.x
- picamera2 (Raspberry Pi OS Bookworm用)
- OpenCV (画像処理用)
- Pillow (画像編集用)
- ffmpeg (動画作成用)

## 📁 ファイル作成手順

### Step 1: カメラディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# カメラディレクトリの確認
ls -la src/camera/
```

### Step 2: 各ファイルの作成順序
1. `src/camera/camera_control.py` - カメラ制御
2. `src/camera/image_processor.py` - 画像処理
3. `src/camera/timelapse_creator.py` - タイムラプス作成

### Step 3: ファイル作成コマンド
```bash
# 各ファイルを作成
touch src/camera/camera_control.py
touch src/camera/image_processor.py
touch src/camera/timelelapse_creator.py
```

### Step 4: 依存関係のインストール
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# 必要なライブラリをインストール
pip install picamera2
pip install opencv-python
pip install Pillow
pip install ffmpeg-python

# requirements.txtを更新
pip freeze > requirements.txt
```

## 📄 実装コード

### 📄 src/camera/camera_control.py
カメラ制御クラス

```python
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os

try:
    from picamera2 import Picamera2
    from libcamera import controls
except ImportError:
    Picamera2 = None
    controls = None

class CameraController:
    """カメラ制御クラス"""
    
    def __init__(self, image_dir: str = "/mnt/usb-storage/images"):
        self.image_dir = Path(image_dir)
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('camera_controller')
        self.camera = None
        self.is_initialized = False
        
        # カメラ設定
        self.camera_config = {
            'main': {
                'format': 'RGB888',
                'size': (1920, 1080)
            },
            'lores': {
                'format': 'YUV420',
                'size': (640, 480)
            }
        }
    
    def initialize(self) -> bool:
        """カメラを初期化"""
        try:
            if Picamera2 is None:
                self.logger.error("picamera2がインストールされていません")
                return False
            
            self.camera = Picamera2()
            
            # カメラ設定を適用
            self.camera.configure(self.camera_config)
            
            # カメラを開始
            self.camera.start()
            
            self.is_initialized = True
            self.logger.info("カメラが正常に初期化されました")
            return True
            
        except Exception as e:
            self.logger.error(f"カメラ初期化エラー: {str(e)}")
            return False
    
    def capture_photo(self, filename: str = None, save: bool = True) -> Dict[str, Any]:
        """写真を撮影"""
        try:
            if not self.is_initialized:
                return {
                    'success': False,
                    'message': 'カメラが初期化されていません',
                    'timestamp': time.time()
                }
            
            # ファイル名を生成
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"plant_{timestamp}.jpg"
            
            # 写真を撮影
            image = self.camera.capture_array()
            
            if save:
                # 画像を保存
                image_path = self.image_dir / filename
                
                # OpenCVを使用してJPEG形式で保存
                import cv2
                cv2.imwrite(str(image_path), image)
                
                # ファイルサイズを取得
                file_size = image_path.stat().st_size
                
                self.logger.info(f"写真を撮影しました: {image_path}")
                
                return {
                    'success': True,
                    'message': '写真を撮影しました',
                    'filename': filename,
                    'path': str(image_path),
                    'size_bytes': file_size,
                    'timestamp': time.time()
                }
            else:
                return {
                    'success': True,
                    'message': '写真を撮影しました（保存なし）',
                    'filename': filename,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            self.logger.error(f"写真撮影エラー: {str(e)}")
            return {
                'success': False,
                'message': f'写真撮影エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def capture_timelapse_frame(self, frame_number: int) -> Dict[str, Any]:
        """タイムラプス用フレームを撮影"""
        try:
            if not self.is_initialized:
                return {
                    'success': False,
                    'message': 'カメラが初期化されていません',
                    'timestamp': time.time()
                }
            
            # フレーム番号付きファイル名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timelapse_{timestamp}_frame_{frame_number:04d}.jpg"
            
            # 写真を撮影
            result = self.capture_photo(filename, save=True)
            
            if result['success']:
                result['frame_number'] = frame_number
                result['is_timelapse'] = True
            
            return result
            
        except Exception as e:
            self.logger.error(f"タイムラプスフレーム撮影エラー: {str(e)}")
            return {
                'success': False,
                'message': f'タイムラプスフレーム撮影エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def get_camera_info(self) -> Dict[str, Any]:
        """カメラ情報を取得"""
        try:
            if not self.is_initialized:
                return {
                    'initialized': False,
                    'message': 'カメラが初期化されていません'
                }
            
            # カメラの設定情報を取得
            camera_properties = self.camera.camera_properties
            
            return {
                'initialized': True,
                'model': camera_properties.get('Model', 'Unknown'),
                'sensor_resolution': camera_properties.get('PixelArraySize', 'Unknown'),
                'lens_name': camera_properties.get('LensName', 'Unknown'),
                'config': self.camera_config,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"カメラ情報取得エラー: {str(e)}")
            return {
                'initialized': False,
                'message': f'カメラ情報取得エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def set_camera_settings(self, settings: Dict[str, Any]) -> bool:
        """カメラ設定を変更"""
        try:
            if not self.is_initialized:
                self.logger.error("カメラが初期化されていません")
                return False
            
            # 設定を適用
            for key, value in settings.items():
                if hasattr(self.camera, key):
                    setattr(self.camera, key, value)
            
            self.logger.info(f"カメラ設定を更新しました: {settings}")
            return True
            
        except Exception as e:
            self.logger.error(f"カメラ設定変更エラー: {str(e)}")
            return False
    
    def cleanup(self):
        """カメラリソースをクリーンアップ"""
        try:
            if self.camera and self.is_initialized:
                self.camera.stop()
                self.camera.close()
                self.is_initialized = False
                self.logger.info("カメラをクリーンアップしました")
        except Exception as e:
            self.logger.error(f"カメラクリーンアップエラー: {str(e)}")
```

### 📄 src/camera/image_processor.py
画像処理クラス

```python
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

try:
    import cv2
    from PIL import Image, ImageEnhance
except ImportError:
    cv2 = None
    Image = None
    ImageEnhance = None

class ImageProcessor:
    """画像処理・分析クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger('image_processor')
        
        if cv2 is None:
            self.logger.error("OpenCVがインストールされていません")
        if Image is None:
            self.logger.error("Pillowがインストールされていません")
    
    def analyze_plant_growth(self, image_path: str) -> Dict[str, Any]:
        """植物の成長を分析"""
        try:
            if cv2 is None:
                return {
                    'success': False,
                    'message': 'OpenCVがインストールされていません',
                    'timestamp': time.time()
                }
            
            # 画像を読み込み
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'success': False,
                    'message': '画像の読み込みに失敗しました',
                    'timestamp': time.time()
                }
            
            # 画像をHSV色空間に変換
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 緑色の範囲を定義
            lower_green = np.array([35, 40, 40])
            upper_green = np.array([85, 255, 255])
            
            # 緑色のマスクを作成
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # 緑色の面積を計算
            green_pixels = cv2.countNonZero(mask)
            total_pixels = image.shape[0] * image.shape[1]
            green_percentage = (green_pixels / total_pixels) * 100
            
            # 輪郭を検出
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 最大の輪郭を取得
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                # バウンディングボックスを取得
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # アスペクト比を計算
                aspect_ratio = w / h if h > 0 else 0
                
                analysis_result = {
                    'success': True,
                    'green_percentage': round(green_percentage, 2),
                    'green_pixels': int(green_pixels),
                    'total_pixels': int(total_pixels),
                    'contour_count': len(contours),
                    'largest_area': round(area, 2),
                    'bounding_box': {
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h)
                    },
                    'aspect_ratio': round(aspect_ratio, 2),
                    'timestamp': time.time()
                }
            else:
                analysis_result = {
                    'success': True,
                    'green_percentage': round(green_percentage, 2),
                    'green_pixels': int(green_pixels),
                    'total_pixels': int(total_pixels),
                    'contour_count': 0,
                    'message': '植物の輪郭が検出されませんでした',
                    'timestamp': time.time()
                }
            
            self.logger.info(f"植物成長分析完了: 緑色率 {green_percentage:.2f}%")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"植物成長分析エラー: {str(e)}")
            return {
                'success': False,
                'message': f'植物成長分析エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def enhance_image(self, image_path: str, output_path: str = None) -> Dict[str, Any]:
        """画像を補強"""
        try:
            if Image is None:
                return {
                    'success': False,
                    'message': 'Pillowがインストールされていません',
                    'timestamp': time.time()
                }
            
            # 画像を開く
            image = Image.open(image_path)
            
            # コントラストを調整
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # 彩度を調整
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)
            
            # 明度を調整
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.05)
            
            # シャープネスを調整
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # 出力パスを設定
            if not output_path:
                path = Path(image_path)
                output_path = str(path.parent / f"{path.stem}_enhanced{path.suffix}")
            
            # 画像を保存
            image.save(output_path, quality=95)
            
            # ファイルサイズを取得
            output_size = Path(output_path).stat().st_size
            
            self.logger.info(f"画像を補強しました: {output_path}")
            
            return {
                'success': True,
                'message': '画像を補強しました',
                'input_path': image_path,
                'output_path': output_path,
                'output_size_bytes': output_size,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"画像補強エラー: {str(e)}")
            return {
                'success': False,
                'message': f'画像補強エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def create_thumbnail(self, image_path: str, size: Tuple[int, int] = (300, 200)) -> Dict[str, Any]:
        """サムネイルを作成"""
        try:
            if Image is None:
                return {
                    'success': False,
                    'message': 'Pillowがインストールされていません',
                    'timestamp': time.time()
                }
            
            # 画像を開く
            image = Image.open(image_path)
            
            # サムネイルを作成
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # 出力パスを設定
            path = Path(image_path)
            thumbnail_path = str(path.parent / f"{path.stem}_thumb{path.suffix}")
            
            # サムネイルを保存
            image.save(thumbnail_path, quality=85)
            
            # ファイルサイズを取得
            thumbnail_size = Path(thumbnail_path).stat().st_size
            
            self.logger.info(f"サムネイルを作成しました: {thumbnail_path}")
            
            return {
                'success': True,
                'message': 'サムネイルを作成しました',
                'original_path': image_path,
                'thumbnail_path': thumbnail_path,
                'thumbnail_size_bytes': thumbnail_size,
                'size': size,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"サムネイル作成エラー: {str(e)}")
            return {
                'success': False,
                'message': f'サムネイル作成エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def detect_plant_diseases(self, image_path: str) -> Dict[str, Any]:
        """植物の病気を検出（基本的な色分析）"""
        try:
            if cv2 is None:
                return {
                    'success': False,
                    'message': 'OpenCVがインストールされていません',
                    'timestamp': time.time()
                }
            
            # 画像を読み込み
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'success': False,
                    'message': '画像の読み込みに失敗しました',
                    'timestamp': time.time()
                }
            
            # 画像をHSV色空間に変換
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 異常な色の範囲を定義
            # 茶色（病気の可能性）
            lower_brown = np.array([10, 50, 20])
            upper_brown = np.array([25, 255, 200])
            
            # 黄色（栄養不足の可能性）
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            
            # マスクを作成
            brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
            yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # 異常な色の面積を計算
            brown_pixels = cv2.countNonZero(brown_mask)
            yellow_pixels = cv2.countNonZero(yellow_mask)
            total_pixels = image.shape[0] * image.shape[1]
            
            brown_percentage = (brown_pixels / total_pixels) * 100
            yellow_percentage = (yellow_pixels / total_pixels) * 100
            
            # 病気の可能性を判定
            disease_risk = "低"
            if brown_percentage > 5 or yellow_percentage > 10:
                disease_risk = "中"
            if brown_percentage > 10 or yellow_percentage > 20:
                disease_risk = "高"
            
            self.logger.info(f"病気検出分析完了: リスク {disease_risk}")
            
            return {
                'success': True,
                'disease_risk': disease_risk,
                'brown_percentage': round(brown_percentage, 2),
                'yellow_percentage': round(yellow_percentage, 2),
                'brown_pixels': int(brown_pixels),
                'yellow_pixels': int(yellow_pixels),
                'total_pixels': int(total_pixels),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"病気検出エラー: {str(e)}")
            return {
                'success': False,
                'message': f'病気検出エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def compare_images(self, image1_path: str, image2_path: str) -> Dict[str, Any]:
        """2つの画像を比較"""
        try:
            if cv2 is None:
                return {
                    'success': False,
                    'message': 'OpenCVがインストールされていません',
                    'timestamp': time.time()
                }
            
            # 画像を読み込み
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                return {
                    'success': False,
                    'message': '画像の読み込みに失敗しました',
                    'timestamp': time.time()
                }
            
            # 画像サイズを統一
            img1_resized = cv2.resize(img1, (640, 480))
            img2_resized = cv2.resize(img2, (640, 480))
            
            # 差分を計算
            diff = cv2.absdiff(img1_resized, img2_resized)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # 閾値を適用
            _, thresh = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)
            
            # 差分の面積を計算
            diff_pixels = cv2.countNonZero(thresh)
            total_pixels = thresh.shape[0] * thresh.shape[1]
            diff_percentage = (diff_pixels / total_pixels) * 100
            
            self.logger.info(f"画像比較完了: 差分率 {diff_percentage:.2f}%")
            
            return {
                'success': True,
                'difference_percentage': round(diff_percentage, 2),
                'difference_pixels': int(diff_pixels),
                'total_pixels': int(total_pixels),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"画像比較エラー: {str(e)}")
            return {
                'success': False,
                'message': f'画像比較エラー: {str(e)}',
                'timestamp': time.time()
            }
```

### 📄 src/camera/timelapse_creator.py
タイムラプス作成クラス

```python
import logging
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import os

try:
    import ffmpeg
except ImportError:
    ffmpeg = None

class TimelapseCreator:
    """タイムラプス作成クラス"""
    
    def __init__(self, 
                 camera_controller,
                 output_dir: str = "/mnt/usb-storage/timelapse"):
        self.camera_controller = camera_controller
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('timelapse_creator')
        
        # タイムラプス設定
        self.timelapse_settings = {
            'interval_minutes': 30,  # 撮影間隔（分）
            'duration_hours': 24,    # 撮影時間（時間）
            'fps': 10,              # 動画のFPS
            'resolution': (1920, 1080),
            'quality': 'medium'     # low, medium, high
        }
        
        # 実行状態
        self.is_running = False
        self.current_session = None
        self.frame_count = 0
        
        if ffmpeg is None:
            self.logger.warning("ffmpeg-pythonがインストールされていません")
    
    def start_timelapse(self, 
                       duration_hours: int = None,
                       interval_minutes: int = None) -> Dict[str, Any]:
        """タイムラプス撮影を開始"""
        try:
            if self.is_running:
                return {
                    'success': False,
                    'message': 'タイムラプスが既に実行中です',
                    'timestamp': time.time()
                }
            
            # 設定を更新
            if duration_hours:
                self.timelapse_settings['duration_hours'] = duration_hours
            if interval_minutes:
                self.timelapse_settings['interval_minutes'] = interval_minutes
            
            # セッション情報を作成
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_session = {
                'session_id': session_id,
                'start_time': time.time(),
                'end_time': time.time() + (self.timelapse_settings['duration_hours'] * 3600),
                'interval_seconds': self.timelapse_settings['interval_minutes'] * 60,
                'frame_count': 0,
                'frames_dir': self.output_dir / f"session_{session_id}"
            }
            
            # フレーム保存ディレクトリを作成
            self.current_session['frames_dir'].mkdir(exist_ok=True)
            
            # タイムラプススレッドを開始
            self.is_running = True
            self.timelapse_thread = threading.Thread(target=self._timelapse_loop)
            self.timelapse_thread.daemon = True
            self.timelapse_thread.start()
            
            self.logger.info(f"タイムラプスを開始しました: {session_id}")
            
            return {
                'success': True,
                'message': 'タイムラプスを開始しました',
                'session_id': session_id,
                'duration_hours': self.timelapse_settings['duration_hours'],
                'interval_minutes': self.timelapse_settings['interval_minutes'],
                'estimated_frames': self._calculate_estimated_frames(),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"タイムラプス開始エラー: {str(e)}")
            return {
                'success': False,
                'message': f'タイムラプス開始エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def stop_timelapse(self) -> Dict[str, Any]:
        """タイムラプス撮影を停止"""
        try:
            if not self.is_running:
                return {
                    'success': False,
                    'message': 'タイムラプスが実行されていません',
                    'timestamp': time.time()
                }
            
            self.is_running = False
            
            if hasattr(self, 'timelapse_thread'):
                self.timelapse_thread.join(timeout=5)
            
            # 動画を作成
            if self.current_session and self.current_session['frame_count'] > 0:
                video_result = self._create_video_from_frames()
                
                self.logger.info(f"タイムラプスを停止しました: {self.current_session['session_id']}")
                
                return {
                    'success': True,
                    'message': 'タイムラプスを停止し、動画を作成しました',
                    'session_id': self.current_session['session_id'],
                    'total_frames': self.current_session['frame_count'],
                    'video_result': video_result,
                    'timestamp': time.time()
                }
            else:
                return {
                    'success': True,
                    'message': 'タイムラプスを停止しました（フレームなし）',
                    'session_id': self.current_session['session_id'] if self.current_session else None,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            self.logger.error(f"タイムラプス停止エラー: {str(e)}")
            return {
                'success': False,
                'message': f'タイムラプス停止エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def _timelapse_loop(self):
        """タイムラプスのメインループ"""
        try:
            while self.is_running and self.current_session:
                current_time = time.time()
                
                # 終了時間をチェック
                if current_time >= self.current_session['end_time']:
                    self.logger.info("タイムラプス時間が終了しました")
                    break
                
                # フレームを撮影
                frame_result = self.camera_controller.capture_timelapse_frame(
                    self.current_session['frame_count']
                )
                
                if frame_result['success']:
                    # フレームを移動
                    frame_path = Path(frame_result['path'])
                    new_frame_path = self.current_session['frames_dir'] / f"frame_{self.current_session['frame_count']:04d}.jpg"
                    
                    frame_path.rename(new_frame_path)
                    
                    self.current_session['frame_count'] += 1
                    self.logger.info(f"タイムラプスフレーム撮影: {self.current_session['frame_count']}")
                else:
                    self.logger.error(f"タイムラプスフレーム撮影エラー: {frame_result['message']}")
                
                # 次の撮影まで待機
                time.sleep(self.current_session['interval_seconds'])
                
        except Exception as e:
            self.logger.error(f"タイムラプスループエラー: {str(e)}")
        finally:
            self.is_running = False
    
    def _create_video_from_frames(self) -> Dict[str, Any]:
        """フレームから動画を作成"""
        try:
            if not self.current_session:
                return {
                    'success': False,
                    'message': 'セッション情報がありません',
                    'timestamp': time.time()
                }
            
            frames_dir = self.current_session['frames_dir']
            frame_count = self.current_session['frame_count']
            
            if frame_count == 0:
                return {
                    'success': False,
                    'message': 'フレームがありません',
                    'timestamp': time.time()
                }
            
            # 出力ファイル名
            output_filename = f"timelapse_{self.current_session['session_id']}.mp4"
            output_path = self.output_dir / output_filename
            
            if ffmpeg:
                # ffmpeg-pythonを使用
                try:
                    (
                        ffmpeg
                        .input(str(frames_dir / "frame_%04d.jpg"), framerate=self.timelapse_settings['fps'])
                        .output(str(output_path), vcodec='libx264', pix_fmt='yuv420p')
                        .overwrite_output()
                        .run(quiet=True)
                    )
                except Exception as e:
                    self.logger.error(f"ffmpeg-python動画作成エラー: {str(e)}")
                    return self._create_video_with_subprocess(frames_dir, output_path, frame_count)
            else:
                # subprocessを使用
                return self._create_video_with_subprocess(frames_dir, output_path, frame_count)
            
            # ファイルサイズを取得
            file_size = output_path.stat().st_size if output_path.exists() else 0
            
            self.logger.info(f"タイムラプス動画を作成しました: {output_path}")
            
            return {
                'success': True,
                'message': 'タイムラプス動画を作成しました',
                'output_path': str(output_path),
                'file_size_bytes': file_size,
                'frame_count': frame_count,
                'fps': self.timelapse_settings['fps'],
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"動画作成エラー: {str(e)}")
            return {
                'success': False,
                'message': f'動画作成エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def _create_video_with_subprocess(self, frames_dir: Path, output_path: Path, frame_count: int) -> Dict[str, Any]:
        """subprocessを使用して動画を作成"""
        try:
            # ffmpegコマンドを構築
            cmd = [
                'ffmpeg',
                '-y',  # 上書き
                '-framerate', str(self.timelapse_settings['fps']),
                '-i', str(frames_dir / "frame_%04d.jpg"),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                str(output_path)
            ]
            
            # ffmpegを実行
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # ファイルサイズを取得
                file_size = output_path.stat().st_size
                
                return {
                    'success': True,
                    'message': 'タイムラプス動画を作成しました（subprocess）',
                    'output_path': str(output_path),
                    'file_size_bytes': file_size,
                    'frame_count': frame_count,
                    'fps': self.timelapse_settings['fps'],
                    'timestamp': time.time()
                }
            else:
                return {
                    'success': False,
                    'message': f'ffmpeg実行エラー: {result.stderr}',
                    'timestamp': time.time()
                }
                
        except Exception as e:
            self.logger.error(f"subprocess動画作成エラー: {str(e)}")
            return {
                'success': False,
                'message': f'subprocess動画作成エラー: {str(e)}',
                'timestamp': time.time()
            }
    
    def _calculate_estimated_frames(self) -> int:
        """推定フレーム数を計算"""
        duration_seconds = self.timelapse_settings['duration_hours'] * 3600
        interval_seconds = self.timelapse_settings['interval_minutes'] * 60
        return int(duration_seconds / interval_seconds)
    
    def get_timelapse_status(self) -> Dict[str, Any]:
        """タイムラプスの状態を取得"""
        if not self.current_session:
            return {
                'running': False,
                'message': 'タイムラプスセッションがありません'
            }
        
        current_time = time.time()
        elapsed_time = current_time - self.current_session['start_time']
        remaining_time = self.current_session['end_time'] - current_time
        
        return {
            'running': self.is_running,
            'session_id': self.current_session['session_id'],
            'frame_count': self.current_session['frame_count'],
            'elapsed_time_seconds': int(elapsed_time),
            'remaining_time_seconds': max(0, int(remaining_time)),
            'interval_seconds': self.current_session['interval_seconds'],
            'estimated_total_frames': self._calculate_estimated_frames(),
            'timestamp': time.time()
        }
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """古いセッションをクリーンアップ"""
        try:
            cleanup_count = 0
            cutoff_date = time.time() - (days * 24 * 3600)
            
            for session_dir in self.output_dir.glob("session_*"):
                if session_dir.is_dir():
                    # ディレクトリの作成日時をチェック
                    dir_mtime = session_dir.stat().st_mtime
                    
                    if dir_mtime < cutoff_date:
                        # ディレクトリとその中身を削除
                        import shutil
                        shutil.rmtree(session_dir)
                        cleanup_count += 1
                        self.logger.info(f"古いセッションを削除しました: {session_dir}")
            
            self.logger.info(f"古いセッションのクリーンアップ完了: {cleanup_count}件")
            return cleanup_count
            
        except Exception as e:
            self.logger.error(f"セッションクリーンアップエラー: {str(e)}")
            return 0
```

## 🧪 テスト方法

### 1. カメラ制御テスト
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# カメラ制御テスト
python -c "
from src.camera.camera_control import CameraController
camera = CameraController()
if camera.initialize():
    result = camera.capture_photo()
    print(f'撮影結果: {result}')
    camera.cleanup()
"
```

### 2. 画像処理テスト
```bash
# 画像処理テスト
python -c "
from src.camera.image_processor import ImageProcessor
processor = ImageProcessor()
# 画像ファイルパスを指定してテスト
# result = processor.analyze_plant_growth('path/to/image.jpg')
# print(f'分析結果: {result}')
"
```

### 3. タイムラプステスト
```bash
# タイムラプステスト（短時間）
python -c "
from src.camera.camera_control import CameraController
from src.camera.timelapse_creator import TimelapseCreator

camera = CameraController()
if camera.initialize():
    creator = TimelapseCreator(camera)
    result = creator.start_timelapse(duration_hours=0.1, interval_minutes=1)
    print(f'タイムラプス開始: {result}')
    time.sleep(10)
    result = creator.stop_timelapse()
    print(f'タイムラプス停止: {result}')
    camera.cleanup()
"
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

