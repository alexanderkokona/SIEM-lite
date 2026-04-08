#!/bin/bash
# Deployment script for SIEM-lite on systemd-based Linux systems

set -e

INSTALL_DIR="/opt/siem-lite"
SERVICE_NAME="siem-lite"
SERVICE_USER="siem-lite"
SERVICE_GROUP="siem-lite"

echo "[*] SIEM-lite Installation Script"
echo "========================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "[!] This script must be run as root"
    exit 1
fi

# Check Python version
echo "[*] Checking Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[+] Found Python 3: ${PYTHON_VERSION}"

# Create service user and group
echo "[*] Setting up service user and group..."
if ! id -u "$SERVICE_USER" &> /dev/null; then
    useradd -r -s /bin/false "$SERVICE_USER"
    echo "[+] Created service user: $SERVICE_USER"
else
    echo "[+] Service user already exists: $SERVICE_USER"
fi

# Create installation directory
echo "[*] Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/data/raw"
mkdir -p "$INSTALL_DIR/data/processed"
mkdir -p "$INSTALL_DIR/logs"

# Copy application files
echo "[*] Copying application files..."
cp -r config/ "$INSTALL_DIR/"
cp -r event/ "$INSTALL_DIR/"
cp -r scripts/ "$INSTALL_DIR/"
cp requirements.txt setup.py README.md "$INSTALL_DIR/"

# Set permissions
echo "[*] Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
chmod 750 "$INSTALL_DIR"
chmod 640 "$INSTALL_DIR/config"/*
chmod 640 "$INSTALL_DIR/logs"

# Allow service user to read auth.log
echo "[*] Configuring log file access..."
usermod -a -G adm "$SERVICE_USER" || true
usermod -a -G systemd-journal "$SERVICE_USER" || true

# Install Python dependencies
echo "[*] Installing Python dependencies..."
cd "$INSTALL_DIR"
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt

# Install application
echo "[*] Installing SIEM-lite package..."
python3 -m pip install -e .

# Copy systemd service file
echo "[*] Installing systemd service..."
cp deployment/siem-lite.service /etc/systemd/system/
systemctl daemon-reload

echo ""
echo "[+] Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Enable the service:  systemctl enable siem-lite"
echo "2. Start the service:   systemctl start siem-lite"
echo "3. Check status:        systemctl status siem-lite"
echo "4. View logs:           journalctl -u siem-lite -f"
echo ""
