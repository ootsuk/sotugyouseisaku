# デプロイスクリプト 実装ガイド

## 📋 概要
Raspberry Piへの自動デプロイ、サービス管理、設定管理のスクリプト実装手順書

## 🎯 実装目標
- 自動デプロイスクリプト
- systemdサービス設定
- 環境設定管理
- 依存関係インストール
- サービス起動・停止・再起動
- ログローテーション設定

## 📁 ファイル作成手順

### Step 1: スクリプトディレクトリの確認
```bash
# プロジェクトディレクトリに移動
cd /Users/ootsukayuya/wrok_space/sotugyouseisaku/smart-planter

# スクリプトディレクトリの確認
ls -la scripts/
```

### Step 2: 各ファイルの作成順序
1. `scripts/deploy.sh` - デプロイスクリプト
2. `scripts/smart-planter.service` - systemdサービス
3. `scripts/setup.sh` - 初期セットアップ
4. `scripts/update.sh` - アップデートスクリプト

### Step 3: ファイル作成コマンド
```bash
# 各ファイルを作成
touch scripts/deploy.sh
touch scripts/smart-planter.service
touch scripts/setup.sh
touch scripts/update.sh
chmod +x scripts/*.sh
```

## 📄 実装コード

### 📄 scripts/deploy.sh
デプロイスクリプト

```bash
#!/bin/bash

# すくすくミントちゃん デプロイスクリプト
# 使用方法: ./scripts/deploy.sh [環境]

set -e  # エラー時に停止

# 設定
PROJECT_NAME="smart-planter"
PROJECT_DIR="/home/pi/${PROJECT_NAME}"
SERVICE_NAME="smart-planter"
USER="pi"
PYTHON_VERSION="3.11"

# 色付きログ関数
log_info() {
    echo -e "\033[32m[INFO]\033[0m $1"
}

log_warn() {
    echo -e "\033[33m[WARN]\033[0m $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# 環境チェック
check_environment() {
    log_info "環境をチェック中..."
    
    # OSチェック
    if [[ ! -f /etc/os-release ]]; then
        log_error "OS情報を取得できません"
        exit 1
    fi
    
    source /etc/os-release
    if [[ "$ID" != "raspbian" && "$ID" != "debian" ]]; then
        log_warn "Raspberry Pi OS以外の環境です: $ID"
    fi
    
    # Python バージョンチェック
    if ! command -v python${PYTHON_VERSION} &> /dev/null; then
        log_error "Python ${PYTHON_VERSION} が見つかりません"
        exit 1
    fi
    
    log_info "環境チェック完了"
}

# 依存関係のインストール
install_dependencies() {
    log_info "依存関係をインストール中..."
    
    # システムパッケージの更新
    sudo apt update
    sudo apt upgrade -y
    
    # 必要なシステムパッケージのインストール
    sudo apt install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        git \
        i2c-tools \
        spi-tools \
        libatlas-base-dev \
        libopenjp2-7 \
        libtiff5 \
        libjpeg62-turbo \
        libfreetype6 \
        liblcms2-2 \
        libwebp6 \
        libharfbuzz0b \
        libfribidi0 \
        libxcb1 \
        ffmpeg
    
    log_info "依存関係のインストール完了"
}

# プロジェクトディレクトリの準備
prepare_project_directory() {
    log_info "プロジェクトディレクトリを準備中..."
    
    # プロジェクトディレクトリが存在しない場合は作成
    if [[ ! -d "$PROJECT_DIR" ]]; then
        sudo mkdir -p "$PROJECT_DIR"
        sudo chown $USER:$USER "$PROJECT_DIR"
        log_info "プロジェクトディレクトリを作成しました: $PROJECT_DIR"
    fi
    
    # バックアップディレクトリの作成
    sudo mkdir -p /mnt/usb-storage/{images,logs,backup,sensor_data,watering_history}
    sudo chown -R $USER:$USER /mnt/usb-storage/
    
    log_info "プロジェクトディレクトリの準備完了"
}

# 仮想環境のセットアップ
setup_virtual_environment() {
    log_info "仮想環境をセットアップ中..."
    
    cd "$PROJECT_DIR"
    
    # 仮想環境が存在しない場合は作成
    if [[ ! -d "venv" ]]; then
        python${PYTHON_VERSION} -m venv venv
        log_info "仮想環境を作成しました"
    fi
    
    # 仮想環境をアクティベート
    source venv/bin/activate
    
    # pipをアップグレード
    pip install --upgrade pip
    
    # requirements.txtが存在する場合はインストール
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_info "Python依存関係をインストールしました"
    fi
    
    log_info "仮想環境のセットアップ完了"
}

# サービスファイルのインストール
install_service() {
    log_info "systemdサービスをインストール中..."
    
    # サービスファイルをコピー
    sudo cp "$PROJECT_DIR/scripts/smart-planter.service" /etc/systemd/system/
    
    # systemdをリロード
    sudo systemctl daemon-reload
    
    # サービスを有効化
    sudo systemctl enable $SERVICE_NAME
    
    log_info "systemdサービスのインストール完了"
}

# 設定ファイルのセットアップ
setup_configuration() {
    log_info "設定ファイルをセットアップ中..."
    
    cd "$PROJECT_DIR"
    
    # 環境変数ファイルが存在しない場合はコピー
    if [[ ! -f ".env" ]]; then
        if [[ -f "env.example" ]]; then
            cp env.example .env
            log_warn "環境変数ファイルを作成しました。必要に応じて編集してください: .env"
        fi
    fi
    
    # ログディレクトリの作成
    mkdir -p logs
    
    # 設定ファイルの権限設定
    chmod 600 .env 2>/dev/null || true
    
    log_info "設定ファイルのセットアップ完了"
}

# データベースの初期化
initialize_database() {
    log_info "データベースを初期化中..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # データベース初期化スクリプトを実行
    python -c "
from src.data.database_manager import DatabaseManager
db = DatabaseManager()
print('データベースが初期化されました')
" || log_warn "データベースの初期化に失敗しました"
    
    log_info "データベースの初期化完了"
}

# サービスを起動
start_service() {
    log_info "サービスを起動中..."
    
    sudo systemctl start $SERVICE_NAME
    
    # 起動確認
    sleep 3
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        log_info "サービスが正常に起動しました"
    else
        log_error "サービスの起動に失敗しました"
        sudo systemctl status $SERVICE_NAME
        exit 1
    fi
}

# デプロイ後の確認
verify_deployment() {
    log_info "デプロイメントを確認中..."
    
    # サービス状態の確認
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        log_info "✓ サービスが稼働中です"
    else
        log_error "✗ サービスが停止しています"
    fi
    
    # ポートの確認
    if netstat -tlnp | grep -q ":5000"; then
        log_info "✓ アプリケーションがポート5000でリッスン中です"
    else
        log_warn "✗ アプリケーションがポート5000でリッスンしていません"
    fi
    
    # ログファイルの確認
    if [[ -f "$PROJECT_DIR/logs/smart-planter.log" ]]; then
        log_info "✓ ログファイルが作成されています"
    else
        log_warn "✗ ログファイルが見つかりません"
    fi
    
    log_info "デプロイメント確認完了"
}

# メイン実行関数
main() {
    local environment=${1:-"production"}
    
    log_info "すくすくミントちゃん デプロイ開始 (環境: $environment)"
    
    check_environment
    install_dependencies
    prepare_project_directory
    setup_virtual_environment
    setup_configuration
    initialize_database
    install_service
    start_service
    verify_deployment
    
    log_info "デプロイメントが完了しました！"
    log_info "Web UI: http://localhost:5000"
    log_info "サービス管理: sudo systemctl status $SERVICE_NAME"
    log_info "ログ確認: tail -f $PROJECT_DIR/logs/smart-planter.log"
}

# スクリプト実行
main "$@"
```

### 📄 scripts/smart-planter.service
systemdサービスファイル

```ini
[Unit]
Description=Smart Planter - すくすくミントちゃん
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/smart-planter
Environment=PATH=/home/pi/smart-planter/venv/bin
ExecStart=/home/pi/smart-planter/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=smart-planter

# 環境変数
Environment=FLASK_ENV=production
Environment=PYTHONPATH=/home/pi/smart-planter

# セキュリティ設定
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/pi/smart-planter /mnt/usb-storage

# リソース制限
LimitNOFILE=65536
MemoryMax=512M

[Install]
WantedBy=multi-user.target
```

### 📄 scripts/setup.sh
初期セットアップスクリプト

```bash
#!/bin/bash

# すくすくミントちゃん 初期セットアップスクリプト

set -e

# 設定
PROJECT_NAME="smart-planter"
PROJECT_DIR="/home/pi/${PROJECT_NAME}"

# 色付きログ関数
log_info() {
    echo -e "\033[32m[INFO]\033[0m $1"
}

log_warn() {
    echo -e "\033[33m[WARN]\033[0m $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# I2C/SPIの有効化
enable_interfaces() {
    log_info "I2C/SPIインターフェースを有効化中..."
    
    # raspi-configを使用してI2C/SPIを有効化
    sudo raspi-config nonint do_i2c 0
    sudo raspi-config nonint do_spi 0
    
    log_info "I2C/SPIインターフェースの有効化完了"
}

# カメラの有効化
enable_camera() {
    log_info "カメラを有効化中..."
    
    sudo raspi-config nonint do_camera 0
    
    log_info "カメラの有効化完了"
}

# ユーザーをgpioグループに追加
setup_gpio_permissions() {
    log_info "GPIO権限を設定中..."
    
    sudo usermod -a -G gpio $USER
    sudo usermod -a -G i2c $USER
    sudo usermod -a -G spi $USER
    
    log_info "GPIO権限の設定完了"
}

# USBストレージのマウント設定
setup_usb_storage() {
    log_info "USBストレージの設定中..."
    
    # マウントポイントの作成
    sudo mkdir -p /mnt/usb-storage
    
    # マウント設定をfstabに追加
    if ! grep -q "usb-storage" /etc/fstab; then
        echo "/dev/sda1 /mnt/usb-storage vfat defaults,uid=pi,gid=pi,umask=0022 0 0" | sudo tee -a /etc/fstab
        log_info "USBストレージのマウント設定を追加しました"
    fi
    
    log_info "USBストレージの設定完了"
}

# ログローテーションの設定
setup_log_rotation() {
    log_info "ログローテーションを設定中..."
    
    cat << EOF | sudo tee /etc/logrotate.d/smart-planter
/home/pi/smart-planter/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 pi pi
    postrotate
        systemctl reload smart-planter || true
    endscript
}
EOF
    
    log_info "ログローテーションの設定完了"
}

# ファイアウォールの設定
setup_firewall() {
    log_info "ファイアウォールを設定中..."
    
    # ufwがインストールされていない場合はインストール
    if ! command -v ufw &> /dev/null; then
        sudo apt install -y ufw
    fi
    
    # ファイアウォールをリセット
    sudo ufw --force reset
    
    # デフォルトポリシーを設定
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # SSHを許可
    sudo ufw allow ssh
    
    # ローカルネットワークからのアクセスを許可
    sudo ufw allow from 192.168.0.0/16 to any port 5000
    sudo ufw allow from 10.0.0.0/8 to any port 5000
    
    # ファイアウォールを有効化
    sudo ufw --force enable
    
    log_info "ファイアウォールの設定完了"
}

# 自動アップデートの設定
setup_auto_update() {
    log_info "自動アップデートを設定中..."
    
    cat << EOF | sudo tee /etc/cron.d/smart-planter-update
# 毎日午前3時にアップデートチェック
0 3 * * * pi /home/pi/smart-planter/scripts/update.sh >> /home/pi/smart-planter/logs/update.log 2>&1
EOF
    
    log_info "自動アップデートの設定完了"
}

# メイン実行関数
main() {
    log_info "すくすくミントちゃん 初期セットアップ開始"
    
    enable_interfaces
    enable_camera
    setup_gpio_permissions
    setup_usb_storage
    setup_log_rotation
    setup_firewall
    setup_auto_update
    
    log_info "初期セットアップが完了しました！"
    log_warn "システムを再起動することをお勧めします: sudo reboot"
}

# スクリプト実行
main "$@"
```

### 📄 scripts/update.sh
アップデートスクリプト

```bash
#!/bin/bash

# すくすくミントちゃん アップデートスクリプト

set -e

# 設定
PROJECT_NAME="smart-planter"
PROJECT_DIR="/home/pi/${PROJECT_NAME}"
SERVICE_NAME="smart-planter"
BACKUP_DIR="/mnt/usb-storage/backup"

# 色付きログ関数
log_info() {
    echo -e "\033[32m[INFO]\033[0m $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warn() {
    echo -e "\033[33m[WARN]\033[0m $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# バックアップの作成
create_backup() {
    log_info "アップデート前のバックアップを作成中..."
    
    local backup_name="update_backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # プロジェクトディレクトリをバックアップ
    tar -czf "$backup_path/project.tar.gz" -C /home/pi "$PROJECT_NAME"
    
    # 設定ファイルをバックアップ
    cp -r /etc/systemd/system/${SERVICE_NAME}.service "$backup_path/" 2>/dev/null || true
    
    log_info "バックアップを作成しました: $backup_path"
}

# Gitから最新コードを取得
update_code() {
    log_info "最新コードを取得中..."
    
    cd "$PROJECT_DIR"
    
    # 現在のブランチを確認
    current_branch=$(git branch --show-current)
    log_info "現在のブランチ: $current_branch"
    
    # 変更をステージング
    git add .
    
    # コミットされていない変更がある場合はコミット
    if ! git diff --staged --quiet; then
        git commit -m "Auto-commit before update $(date '+%Y-%m-%d %H:%M:%S')"
        log_info "変更をコミットしました"
    fi
    
    # 最新コードを取得
    git fetch origin
    git reset --hard origin/$current_branch
    
    log_info "最新コードの取得完了"
}

# 依存関係を更新
update_dependencies() {
    log_info "依存関係を更新中..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # pipをアップグレード
    pip install --upgrade pip
    
    # requirements.txtから依存関係をインストール
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_info "Python依存関係を更新しました"
    fi
    
    log_info "依存関係の更新完了"
}

# データベースマイグレーション
migrate_database() {
    log_info "データベースマイグレーションを実行中..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # データベースマイグレーションスクリプトを実行
    python -c "
from src.data.database_manager import DatabaseManager
db = DatabaseManager()
print('データベースマイグレーション完了')
" || log_warn "データベースマイグレーションに失敗しました"
    
    log_info "データベースマイグレーション完了"
}

# サービスを再起動
restart_service() {
    log_info "サービスを再起動中..."
    
    sudo systemctl restart $SERVICE_NAME
    
    # 起動確認
    sleep 5
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        log_info "サービスの再起動完了"
    else
        log_error "サービスの再起動に失敗しました"
        sudo systemctl status $SERVICE_NAME
        return 1
    fi
}

# ヘルスチェック
health_check() {
    log_info "ヘルスチェックを実行中..."
    
    # サービス状態の確認
    if ! sudo systemctl is-active --quiet $SERVICE_NAME; then
        log_error "サービスが停止しています"
        return 1
    fi
    
    # ポートの確認
    if ! netstat -tlnp | grep -q ":5000"; then
        log_error "アプリケーションがポート5000でリッスンしていません"
        return 1
    fi
    
    # HTTPレスポンスの確認
    if curl -f -s http://localhost:5000/api/status > /dev/null; then
        log_info "ヘルスチェック完了 - システムは正常に動作しています"
    else
        log_error "HTTPレスポンスの確認に失敗しました"
        return 1
    fi
}

# ロールバック
rollback() {
    log_info "ロールバックを実行中..."
    
    # 最新のバックアップを探す
    latest_backup=$(ls -t "$BACKUP_DIR"/update_backup_* 2>/dev/null | head -1)
    
    if [[ -z "$latest_backup" ]]; then
        log_error "ロールバック用のバックアップが見つかりません"
        return 1
    fi
    
    log_info "バックアップから復元中: $latest_backup"
    
    # サービスを停止
    sudo systemctl stop $SERVICE_NAME
    
    # プロジェクトディレクトリを復元
    cd /home/pi
    tar -xzf "$latest_backup/project.tar.gz"
    
    # サービスを再起動
    sudo systemctl start $SERVICE_NAME
    
    log_info "ロールバック完了"
}

# メイン実行関数
main() {
    local action=${1:-"update"}
    
    case "$action" in
        "update")
            log_info "アップデートを開始します"
            
            create_backup
            update_code
            update_dependencies
            migrate_database
            restart_service
            
            if health_check; then
                log_info "アップデートが正常に完了しました"
            else
                log_error "アップデート後のヘルスチェックに失敗しました"
                log_info "ロールバックを実行します"
                rollback
                exit 1
            fi
            ;;
        "rollback")
            log_info "ロールバックを開始します"
            rollback
            ;;
        "health")
            log_info "ヘルスチェックを実行します"
            health_check
            ;;
        *)
            echo "使用方法: $0 [update|rollback|health]"
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"
```

## 🧪 テスト方法

### 1. デプロイスクリプトテスト
```bash
# デプロイスクリプトをテスト
chmod +x scripts/deploy.sh
./scripts/deploy.sh production
```

### 2. サービス管理テスト
```bash
# サービスの状態確認
sudo systemctl status smart-planter

# サービスの再起動
sudo systemctl restart smart-planter

# ログの確認
sudo journalctl -u smart-planter -f
```

### 3. アップデートスクリプトテスト
```bash
# アップデートテスト
chmod +x scripts/update.sh
./scripts/update.sh update

# ヘルスチェック
./scripts/update.sh health
```

---

**作成日**: 2025年1月
**バージョン**: 1.0
**チーム**: KEBABS

