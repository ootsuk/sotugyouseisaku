# センサー制御機能 実装手順書

## 📋 概要
温湿度センサー(AHT25)と土壌水分センサー(SEN0193)の制御機能を実装するための詳細手順書

## 🎯 実装目標
- AHT25温湿度センサーのI2C通信制御
- SEN0193土壌水分センサーのADC制御
- センサー値のフィルタリング処理
- エラーハンドリングと故障時対応
- データ取得の定期実行

## 🛠️ 必要な環境

### ハードウェア
- Raspberry Pi 5
- 温湿度センサー AHT25
- 土壌水分センサー SEN0193
- ADC MCP3002
- ジャンパーワイヤー
- ブレッドボード

### ソフトウェア
- Python 3.11.x
- RPi.GPIO
- smbus2 (I2C通信用)
- spidev (SPI通信用)
- numpy (データ処理用)

## 🔧 実装手順

### Step 1: ハードウェア接続

#### 1.1 GPIOピン配置
```python
# GPIOピン定義
GPIO_PINS = {
    # I2C通信 (AHT25温湿度センサー)
    'I2C_SDA': 2,  # GPIO 2 (Pin 3)
    'I2C_SCL': 3,  # GPIO 3 (Pin 5)
    
    # SPI通信 (MCP3002 ADC)
    'SPI_MOSI': 10,  # GPIO 10 (Pin 19)
    'SPI_MISO': 9,   # GPIO 9 (Pin 21)
    'SPI_SCLK': 11,  # GPIO 11 (Pin 23)
    'SPI_CE0': 8,    # GPIO 8 (Pin 24)
    
    # フロートスイッチ
    'FLOAT_SWITCH': 18,  # GPIO 18 (Pin 12)
    
    # リレーモジュール (水ポンプ制御)
    'RELAY_PUMP': 16,    # GPIO 16 (Pin 36)
}
```

#### 1.2 配線図
```
AHT25温湿度センサー:
- VCC → 3.3V (Pin 1)
- GND → GND (Pin 6)
- SDA → GPIO 2 (Pin 3)
- SCL → GPIO 3 (Pin 5)

SEN0193土壌水分センサー:
- VCC → 5V (Pin 2)
- GND → GND (Pin 6)
- SIG → MCP3002 CH0

MCP3002 ADC:
- VDD → 3.3V (Pin 1)
- VREF → 3.3V (Pin 1)
- AGND → GND (Pin 6)
- DGND → GND (Pin 6)
- CLK → GPIO 11 (Pin 23)
- DOUT → GPIO 9 (Pin 21)
- DIN → GPIO 10 (Pin 19)
- CS/SHDN → GPIO 8 (Pin 24)
```

### Step 2: システム設定

#### 2.1 I2C・SPI有効化
```bash
# Raspberry Pi設定
sudo raspi-config

# 選択項目:
# 3 Interface Options
#   P4 I2C → Enable
#   P5 SPI → Enable

# 再起動
sudo reboot
```

#### 2.2 必要なライブラリインストール
```bash
# Pythonライブラリインストール
pip install RPi.GPIO
pip install smbus2
pip install spidev
pip install numpy
```

## 📊 実装完了チェックリスト

- [ ] ハードウェア接続完了
- [ ] I2C・SPI有効化完了
- [ ] 必要なライブラリインストール完了
- [ ] 基本センサークラス実装完了
- [ ] AHT25センサークラス実装完了
- [ ] SEN0193センサークラス実装完了
- [ ] フロートスイッチクラス実装完了
- [ ] センサーマネージャークラス実装完了
- [ ] テストスクリプト実行完了
- [ ] エラーハンドリング確認完了
- [ ] ログ出力確認完了

## 🎯 次のステップ

1. **自動給水機能実装**: センサーデータに基づく給水制御
2. **データ保存機能**: CSV形式でのデータ保存
3. **LINE通知統合**: センサー異常時の通知
4. **Web UI統合**: リアルタイムデータ表示

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

