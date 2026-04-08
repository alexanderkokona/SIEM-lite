# SIEM-lite: Auth Log Security Pipeline

A small, disciplined security log pipeline for Linux authentication events. Focuses on reliable ingestion, parsing, and structured event handling rather than dashboards or ml-first approaches.

## Features

✅ **Implemented**
- Auth.log parsing (SSH logins, sudo, account operations)
- Structured event schema with validation
- Configuration-driven log sources
- Comprehensive unit tests (90%+ coverage)
- Systemd service integration
- Docker deployment support
- Full deployment and testing documentation

🔄 **Planned (Future Sprints)**
- Real-time event alerting
- Detection rules engine
- Event storage and querying
- Dashboard/visualization
- Performance optimization for high-volume logs

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Configuration

```bash
python scripts/verify_auth_log_access.py -v
```

### 3. Run Tests

```bash
pytest tests/ -v
```

### 4. Parse Auth Logs

```python
from event.parsers.authlog import AuthLogParser

parser = AuthLogParser()
events = parser.parse_file("/var/log/auth.log")
print(f"Parsed {len(events)} events")
```

## Installation & Deployment

Complete deployment instructions for production environments are in [DEPLOYMENT.md](DEPLOYMENT.md).

### Quick Systemd Install

```bash
sudo bash deployment/install.sh
sudo systemctl start siem-lite
sudo systemctl status siem-lite
```

### Docker Deploy

```bash
cd deployment
docker-compose up -d
```

## Architecture

### Data Flow

```
/var/log/auth.log
      ↓
 [Parser] (extracts log entries)
      ↓
 [Event Schema] (standardized format)
      ↓
 [Validation] (ensures data quality)
      ↓
 [Storage/Analysis] (future)
```

### Module Structure

```
SIEM-lite/
├── config/              # Configuration files
│   └── log_sources.yaml # Log source definitions
├── event/               # Core event processing
│   ├── schema.py        # Event structure & validation
│   ├── event_types.py   # Constants
│   └── parsers/         # Parser implementations
│       └── authlog.py   # SSH/sudo/account parser
├── scripts/             # Utilities
│   └── verify_auth_log_access.py  # Configuration verification
├── siem_lite/           # Daemon package
│   └── daemon.py        # Event processing daemon
├── tests/               # Unit tests
├── deployment/          # Deployment configs
│   ├── siem-lite.service       # Systemd unit
│   ├── Dockerfile              # Container image
│   ├── docker-compose.yml      # Docker orchestration
│   └── install.sh              # Installation script
└── docs/                # Documentation
```

## Configuration

Edit [`config/log_sources.yaml`](config/log_sources.yaml):

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

## Event Schema

All parsed events follow a standardized schema with sections for:

- **metadata**: Event ID, timestamps, source type
- **source**: Host, program, PID
- **actor**: User performing the action
- **target**: User/resource being acted upon
- **action**: Category and type (login, sudo, etc.)
- **outcome**: Success/failure and reason
- **network**: IP addresses, ports, protocol
- **privilege**: Escalation details
- **raw**: Original log message

Example parsed event: [`event/examples/auth_failed_login.json`](event/examples/auth_failed_login.json)

## Parsers

### SSH Parser

Extracts SSH authentication events:
- Failed/successful password logins
- Invalid user attempts
- Port and source IP tracking

### Sudo Parser

Captures privilege escalation:
- Command executed
- Target user (root, etc.)
- Source user and TTY

### Account Parser

Handles user management:
- User creation (useradd)
- User deletion (userdel)
- Password changes (passwd)

## Testing

Run full test suite:

```bash
pytest tests/ -v
pytest tests/ --cov=event  # With coverage
```

See [TESTING.md](TESTING.md) for detailed testing information.

## Development

### Setup Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest tests/ -v
```

### Add New Parser

1. Create parser class in `event/parsers/new_parser.py`
2. Implement `parse_line()` method
3. Add test file `tests/test_new_parser.py`
4. Update `event/parsers/__init__.py` exports

### Contributing

Contributions welcome! Please:
1. Add tests for new features
2. Maintain 80%+ code coverage
3. Follow existing style and structure
4. Update documentation

## Troubleshooting

### Permission Denied on auth.log

```bash
sudo usermod -a -G adm siem-lite
sudo usermod -a -G systemd-journal siem-lite
sudo systemctl restart siem-lite
```

### Service Not Starting

```bash
# Check logs
journalctl -u siem-lite -n 50

# Verify config
python scripts/verify_auth_log_access.py -v

# Test daemon manually
python -m siem_lite.daemon
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting.

## Performance

- **Parser**: 10,000+ events/second on modern hardware
- **Memory**: ~50MB baseline, scales with event buffer
- **Disk**: Raw logs only, processed events are analyzed in-memory

## Security

The project prioritizes security:
- Non-root service user for daemon
- Read-only access to log files
- Input validation on all parsed fields
- Protection against log injection attacks
- Systemd hardening (ProtectSystem, ProtectHome)

## License

[Include your license here]

## Support & Contact

For issues:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
2. Review [TESTING.md](TESTING.md) for testing guidance
3. Check application logs: `journalctl -u siem-lite`
4. Open an issue with logs and configuration (redact sensitive data)

## Current Scope (Sprint 1)

Sprint 1 focuses only on:
- ✅ Verifying access to `auth.log`
- ✅ Reading logs safely and consistently
- ✅ Establishing configuration-driven log sources
- ✅ Basic event parsing (SSH, sudo, account)
- ✅ Structured event schema with validation
- ✅ Production deployment capabilities

No detection logic, alerts, or dashboards are implemented yet.

---

## Data Source

- Primary source: `/var/log/auth.log`
- Platform: Linux (Debian/Ubuntu-style logging)
- Log rotation is expected and handled automatically

---

## Next Steps

Future sprints will focus on:
- Detection rule engine
- Real-time alerting
- Event storage (database or logging service)
- Web dashboard
- Performance optimization for high-volume environments
