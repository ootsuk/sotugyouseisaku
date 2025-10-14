import time
# import subprocess
from gpiozero import MCP3002
import datetime 
import os

# 保存先ディレクトリ
LOG_DIR = "sensor_logs"
LOG_FILE = os.path.join(LOG_DIR, "soil_moisture_log.csv")

def get_moisture_status(raw_value):
    """生の水分値（0-255）から状態文字列を返す"""
    # 255に近ければDry, 127に近ければVeryWet
    
    if raw_value > 200:
        return "Dry"
    elif raw_value > 150:
        return "Optimal"
    else:
        return "VeryWet"

class SoilMoistureSensor:
    def __init__(self, vref):
        #電圧基準値
        self.vref = vref
        # 保存ディレクトリが存在しない場合は作成
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
            print(f"ディレクトリを作成しました: {LOG_DIR}")
            
        with open(LOG_FILE, 'a') as f:
            # ファイルが空かどうかを確認
            f.seek(0, 2) # ファイルの終端に移動
            if f.tell() == 0: # 現在のポインタ位置が0ならファイルは空
                f.write('Timestamp,Humidity,Status,RawValue\n') # ヘッダーを書き込む
        
    def measure_and_log(self):
        """センサーから値を読み取り、CSVファイルに記録します。"""
        try:
            sen0193 = MCP3002(channel=0)
            # 0-1.0の値を0-255の整数値に変換
            raw_value = int(sen0193.value * 255)
            
            humidity = round(sen0193.value * self.vref * 100, 2)
            
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            status = get_moisture_status(raw_value)
            
            print(f"Timestamp: {timestamp}, Humidity: {humidity}, Status: {status}, RawValue: {raw_value}")

            with open(LOG_FILE, 'a') as f:
                f.write(f"{timestamp},{humidity},{status},{raw_value}\n")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    
    
if __name__ == "__main__":
    recorder = SoilMoistureSensor(vref=3.3)
    recorder.measure_and_log()

#crontabによるスケジューリング例
#0 7 * * * cd /path/to/your/smart-planter/src && /usr/bin/env python3 camera.py
 
#参考URL 
# https://www.itmedia.co.jp/news/articles/2104/12/news005_2.html