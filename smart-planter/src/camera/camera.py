print("push_test")#pip install opencv-python

import cv2
import datetime
import os
import glob

# --- 設定 ---
# 保存先ディレクトリ
SAVE_DIR = "plant_images"

# 画像解像度 (C270 HDウェブカメラ)
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720

# 画像の保存期間 (日数)
RETENTION_DAYS = 90

# --- 共通関数 ---
def get_file_name():
    """ファイル名を生成（例: 20250910_100000.jpg）"""
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S.jpg")

def save_image(frame, file_path):
    """画像をJPEG形式で保存"""
    cv2.imwrite(file_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    #print(f"画像を保存しました: {file_path}")

def delete_old_images():
    """指定期間より古い画像を自動削除"""
    today = datetime.datetime.now()
    cutoff_date = today - datetime.timedelta(days=RETENTION_DAYS)
    
    # 保存ディレクトリ内の全JPEGファイルを検索
    image_files = glob.glob(os.path.join(SAVE_DIR, "*.jpg"))
    
    for file_path in image_files:
        # ファイルの作成日時を取得
        timestamp = os.path.getctime(file_path)
        file_date = datetime.datetime.fromtimestamp(timestamp)
        
        if file_date < cutoff_date:
            os.remove(file_path)
    

# --- メイン機能 ---
class PlantCaptureManager:
    def __init__(self):
        # 保存ディレクトリが存在しない場合は作成
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
            print(f"ディレクトリを作成しました: {SAVE_DIR}")

    def capture_and_save(self):
        """カメラから画像をキャプチャして保存"""
        cap = cv2.VideoCapture(0)  # 0は通常、内蔵または最初のUSBカメラ

        # カメラが正しく開かれているか確認
        if not cap.isOpened():
            print("エラー: カメラに接続できませんでした。")
            return

        # 解像度設定
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)

        # 念のため、カメラのウォームアップ
        ret, frame = cap.read()
        if not ret:
            print("エラー: フレームを読み込めませんでした。")
            cap.release()
            return
        
        # ファイル名の生成
        file_name = get_file_name()
        file_path = os.path.join(SAVE_DIR, file_name)

        # 画像の保存
        save_image(frame, file_path)

        # カメラを解放
        cap.release()
        
        # 撮影後に古い画像を削除
        delete_old_images()

# --- 実行例 ---
if __name__ == "__main__":
    manager = PlantCaptureManager()
    print("起動")
  
    # ここにスケジューリングのロジックを実装します。
    # 例：Pythonのthreading.TimerやAPSchedulerライブラリを使用
    # 現在は単純に再度実行する形で示します。
    manager.capture_and_save()