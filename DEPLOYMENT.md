# Deployment Guide

This guide covers deploying SIEM-lite to production environments.

## Prerequisites

- Linux system (Debian/Ubuntu or CentOS/RHEL compatible)
- Python 3.8 or higher
- `sudo` access or root privileges for installation
- At least 256MB available memory
- Read access to `/var/log/auth.log`

## Quick Start - Systemd Installation

### 1. Automated Installation

```bash
sudo bash deployment/install.sh
```

This script will:
- Create a dedicated service user (`siem-lite`)
- Install Python dependencies
- Configure log file permissions
- Install and enable the systemd service

### 2. Verify Installation

```bash
# Check service status
systemctl status siem-lite

# View logs
journalctl -u siem-lite -f

# Run verification
systemctl start siem-lite
```

### 3. Enable Auto-start

```bash
sudo systemctl enable siem-lite
sudo systemctl start siem-lite
```

## Docker Deployment

### Build Image

```bash
docker build -f deployment/Dockerfile -t siem-lite:latest .
```

### Using Docker Compose

```bash
cd deployment
docker-compose up -d
```

This will:
- Build and start the container
- Mount `/var/log/auth.log` as read-only
- Persist data in a named volume
- Apply resource limits (0.5 CPU, 256MB RAM)

### View Logs

```bash
docker-compose logs -f siem-lite
```

### Stop Service

```bash
docker-compose down
```

## Manual Installation

If the automated script doesn't work for your environment:

### 1. Create Service User

```bash
sudo useradd -r -s /bin/false siem-lite
```

### 2. Clone and Install

```bash
sudo mkdir -p /opt/siem-lite
cd /opt/siem-lite

# Copy files
sudo git clone <repo> .
sudo chown -R siem-lite:siem-lite /opt/siem-lite

# Install dependencies (as root)
sudo pip install -r requirements.txt
```

### 3. Configure Permissions

```bash
# Allow siem-lite user to read auth.log
sudo usermod -a -G adm siem-lite
sudo usermod -a -G systemd-journal siem-lite
```

### 4. Install Systemd Service

```bash
sudo cp deployment/siem-lite.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable siem-lite
```

### 5. Start Service

```bash
sudo systemctl start siem-lite
```

## Configuration

### Main Config File

Edit `config/log_sources.yaml`:

```yaml
log_sources:
  auth_log:
    enabled: true
    platform: linux
    path: /var/log/auth.log
    format:
      type: plaintext
      encoding: utf-8
```

### Service Configuration

Edit `/etc/systemd/system/siem-lite.service` to customize:
- Resource limits (memory, CPU)
- User/group
- Environment variables
- Restart policy

Then reload: `sudo systemctl daemon-reload`

## Testing

### Run Verification Script

```bash
python3 scripts/verify_auth_log_access.py -v
```

### Run Unit Tests

```bash
pytest tests/ -v
pytest tests/ --cov=event --cov-report=html
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status siem-lite -l

# View detailed logs
journalctl -u siem-lite -n 100

# Test manually
python3 -m siem_lite.daemon
```

### Permission Denied on auth.log

```bash
# Verify user is in correct groups
id siem-lite

# Check file permissions
ls -la /var/log/auth.log

# Add user to groups if needed
sudo usermod -a -G adm siem-lite
sudo usermod -a -G systemd-journal siem-lite

# Restart service
sudo systemctl restart siem-lite
```

### Memory or CPU Issues

Edit `/etc/systemd/system/siem-lite.service` and adjust:

```ini
MemoryLimit=512M    # Increase memory limit
CPUQuota=100%       # Increase CPU quota
```

Then reload: `sudo systemctl daemon-reload && sudo systemctl restart siem-lite`

### Log File Rotation

SIEM-lite handles log rotation automatically. However, if encountering issues:

```bash
# Check logrotate configuration
cat /etc/logrotate.d/rsyslog

# Force rotation test
sudo logrotate -f /etc/logrotate.d/rsyslog

# Verify siem-lite continues working
journalctl -u siem-lite -f
```

## Uninstall

### Systemd Remove

```bash
sudo systemctl stop siem-lite
sudo systemctl disable siem-lite
sudo rm /etc/systemd/system/siem-lite.service
sudo systemctl daemon-reload
sudo rm -rf /opt/siem-lite
sudo userdel -r siem-lite
```

### Docker Remove

```bash
cd deployment
docker-compose down -v
docker rmi siem-lite:latest
```

## Security Considerations

### File Permissions
- Service runs as non-root user (`siem-lite`)
- Config files readable only by service user
- Log files read-only access

### Network Security
- Service does not listen on network by default
- All processing is local

### System Hardening
- Uses systemd security features (ProtectSystem, ProtectHome)
- Memory and CPU limits applied
- Restart limit to prevent resource exhaustion

## Performance Tuning

### For High-Volume Logs

In `/etc/systemd/system/siem-lite.service`:

```ini
MemoryLimit=512M
CPUQuota=100%  # Or higher if 2+ cores available
```

And edit `siem_lite/daemon.py`, change `interval`:

```python
daemon.run(interval=1)  # Check logs more frequently
```

### For Low-Resource Systems

In `/etc/systemd/system/siem-lite.service`:

```ini
MemoryLimit=128M
CPUQuota=25%
```

And edit `siem_lite/daemon.py`:

```python
daemon.run(interval=30)  # Check logs less frequently
```

## Monitoring

### Check Service Health

```bash
systemctl status siem-lite
```

### View Recent Events

```bash
journalctl -u siem-lite --since "10 minutes ago"
```

### Monitor Resources

```bash
sudo systemctl status siem-lite.service
ps aux | grep siem-lite
```

## Support

For issues or questions:
1. Check logs: `journalctl -u siem-lite -n 50`
2. Run verification: `python3 scripts/verify_auth_log_access.py -v`
3. Review configuration: `cat config/log_sources.yaml`
