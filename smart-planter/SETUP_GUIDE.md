# チームメンバー向けセットアップガイド

## 🚀 クイックスタート

### 1. リポジトリをクローン
```bash
git clone https://github.com/[リポジトリURL]/smart-planter.git
cd smart-planter
```

### 2. 仮想環境を作成
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
```

### 5. アプリケーションを起動
```bash
python main.py
```

## 📋 必要な環境

### システム要件
- Python 3.11以上
- Git
- 仮想環境管理ツール（venv）

### 主要パッケージ
- Flask 2.3.3
- requests 2.32.5
- Pillow 11.3.0
- numpy 2.2.6
- opencv-python 4.12.0.88

## 🔧 トラブルシューティング

### 仮想環境のアクティベートができない場合
```bash
# パスを確認
which python3

# 仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### パッケージのインストールエラー
```bash
# pipをアップグレード
pip install --upgrade pip

# キャッシュをクリア
pip cache purge

# 再インストール
pip install -r requirements.txt
```

### アクセスできない場合
- ポート5000が使用中でないか確認
- ファイアウォール設定を確認
- ブラウザで `http://localhost:5000` にアクセス

## 📞 サポート

問題が発生した場合は、以下の手順で報告してください：

1. エラーメッセージのスクリーンショット
2. 実行したコマンド
3. 環境情報（OS、Pythonバージョン）

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS
