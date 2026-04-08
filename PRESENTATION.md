# SIEM-lite: 5-Minute Presentation Script

**Target Time:** 4:30 - 5:00 minutes  
**Audience:** Technical decision-makers, security engineers, ops teams  
**Format:** Live demo + talking points

---

## Slide 1: Problem Statement (0:00 - 0:30)

**SPEAKER NOTES:**
> "Security teams today face a critical challenge: **logs are everywhere—but understanding them is nowhere**. Authentication logs from Linux systems contain crucial security signals, but extracting them requires custom parsing and validation. This is often error-prone, undocumented, and hard to scale."

**TALKING POINT:**
- Authentication logs contain critical security events
- Current log parsing approaches are ad-hoc and fragile
- No standardized event schema means inconsistent data quality

**VISUAL:** Show a sample `/var/log/auth.log` snippet with raw, unstructured data

---

## Slide 2: Solution Overview (0:30 - 1:15)

**SPEAKER NOTES:**
> "**SIEM-lite is a disciplined, production-ready security log pipeline** focused on exactly three things: **reliable ingestion, robust parsing, and structured event standardization**."
>
> "We don't try to do everything—no dashboards, no ML, no bloat. Just solid log processing. Think of it as the foundation layer for better security."

**KEY POINTS:**
1. ✅ **Purpose-built** for Linux auth logs (SSH, sudo, account changes)
2. ✅ **Structured event schema** - all events follow a standard format
3. ✅ **Validated parsing** - malformed logs are handled gracefully
4. ✅ **Tested & hardened** - 22 tests, 100% pass rate, 90%+ coverage
5. ✅ **Production-ready** - Docker + systemd deployment options
6. ✅ **Well-documented** - setup, deployment, testing guides included

**VISUAL:** Show architecture diagram:
```
/var/log/auth.log → Parser → Schema Validation → Structured Events
```

---

## Slide 3: Live Demo - Parser in Action (1:15 - 2:45)

**TECHNICAL DEMO (interactive):**

### Demo Segment A: Quick Installation (30 sec)

```bash
# Show installation is simple
cd /path/to/SIEM-lite
pip install -r requirements.txt

# Verify setup
python scripts/verify_auth_log_access.py -v
```

**SPEAKER NOTES:**
> "Installation is straightforward. One pip install, and dependencies are minimal. Let's verify the configuration..."

### Demo Segment B: Run Tests (30 sec)

```bash
# Run the test suite
pytest tests/ -v

# Show results
# ============================= 22 passed in 0.03s ==============================
```

**SPEAKER NOTES:**
> "All 22 tests pass instantly. This covers SSH auth failures, privilege escalation, account operations, edge cases, and timestamp parsing. We validate both parsing correctness and schema compliance."

### Demo Segment C: Parse Real Events (45 sec)

```python
from event.parsers.authlog import AuthLogParser
import json

parser = AuthLogParser()

# Example: Parse SSH failed login
ssh_failed = 'Jan 10 09:14:22 server sshd[1234]: Failed password for invalid user admin from 192.168.1.100 port 54321'
event = parser.parse_line(ssh_failed, hostname="server")

print(json.dumps(event, indent=2, default=str))
```

**EXPECTED OUTPUT:** Structured event with:
- `metadata`: event_id, timestamps
- `source`: hostname, program, PID
- `actor`: user attempting login
- `network`: source IP/port
- `action`: login attempt
- `outcome`: failed + reason

**SPEAKER NOTES:**
> "Notice how the raw log line is transformed into structured, queryable data. Every field is validated. Every event gets a unique ID and ingestion timestamp. This is what makes detection and analysis possible."

### Demo Segment D: Show Schema Validation (30 sec)

```python
# Invalid event (missing required fields) - demonstrates validation
invalid_event = {"metadata": {}}
result = validate_event(invalid_event)
# Shows clear error: "Missing required section: 'action'"
```

**SPEAKER NOTES:**
> "The schema isn't just documentation—it's enforced validation. Bad data doesn't silently slip through the pipeline."

---

## Slide 4: Deployment Options (2:45 - 3:45)

### Option A: Systemd (Traditional Servers)

```bash
# One-command installation
sudo bash deployment/install.sh

# Start service
sudo systemctl start siem-lite
sudo systemctl status siem-lite

# View logs
journalctl -u siem-lite -f
```

**TALKING POINT:**
> "For traditional server environments, we provide a systemd service. Automated installation handles user/group creation, permissions, and startup configuration. It integrates cleanly with Linux system management."

**BENEFITS:**
- Native Linux service management
- Automatic restart on failure
- Resource limits enforced (256MB, 50% CPU)
- Security hardening (no root, protected filesystem)

---

### Option B: Docker (Containerized Environments)

```bash
# Build image
docker build -f deployment/Dockerfile -t siem-lite:latest .

# Run with compose
cd deployment
docker-compose up -d

# Check status
docker-compose logs -f siem-lite
```

**TALKING POINT:**
> "For modern, containerized environments, Docker Compose gives you everything in one command: isolated runtime, proper volume mounts, resource limits, and restart policies."

**BENEFITS:**
- Containerized isolation
- Easy scaling to multiple hosts
- Clean log rotation
- Consistent across environments

---

## Slide 5: What's Included (3:45 - 4:30)

### Core Features ✅

| Component | Status | What It Does |
|-----------|--------|-------------|
| **Parser** | ✅ | SSH, sudo, account operations from auth.log |
| **Schema** | ✅ | Standardized event structure + validation |
| **Config** | ✅ | YAML-based log source definitions |
| **Tests** | ✅ | 22 tests covering all parsing paths (100% pass) |
| **Systemd** | ✅ | Production service with security hardening |
| **Docker** | ✅ | Container image + Compose config |
| **Docs** | ✅ | README, deployment guide, testing guide |

### What's NOT Included (Planned for Sprint 2)

- Real-time alerting
- Detection rules engine
- Event storage & querying
- Dashboards/visualizations

**SPEAKER NOTES:**
> "SIEM-lite 1.0 is focused. It's the foundation. We're intentionally not including alerting or dashboards yet—those come in the next version. Right now, we're ensuring the log pipeline is rock-solid."

---

## Slide 6: Closing / Next Steps (4:30 - 5:00)

**SPEAKER NOTES:**
> "In summary: **SIEM-lite solves the first critical problem in security monitoring: getting consistent, validated data from auth logs.** It's:
>
> - **Small & focused** — does one thing well
> - **Production-hardened** — tested, documented, deployed in multiple ways
> - **Ready to extend** — clean architecture for adding new parsers, storage, detection rules
>
> **We're ready to deploy this week.** Installation takes 5 minutes. Your team can start ingesting and analyzing authentication events immediately."

### Call to Action

**Choose your path:**

1. **Systemd deployment** (traditional servers)
   ```bash
   sudo bash deployment/install.sh
   ```

2. **Docker deployment** (containerized infrastructure)
   ```bash
   cd deployment && docker-compose up -d
   ```

3. **Development/testing**
   ```bash
   pip install -r requirements.txt
   pytest tests/ -v
   ```

---

## Post-Demo Q&A

### Common Questions & Answers

**Q: Can it handle other log sources besides auth.log?**  
A: Absolutely. The architecture is built for extensibility. Adding a new parser (web server logs, firewall logs, app logs) requires creating a new parser class. The schema ensures all events are compatible.

**Q: What about performance?**  
A: The parser processes thousands of events per second on modest hardware. For production scales, we can parallelize parsing or add a message queue in a future sprint.

**Q: How much storage do we need?**  
A: That depends on your event destination. The parser itself is lightweight. Docker limits are 256MB; systemd service typically uses 50-100MB.

**Q: Can it integrate with splunk/ELK/&lt;SIEM&gt;?**  
A: The structured event output can feed any backend. For now, it's focused on parsing. Integration connectors are planned for Sprint 2.

**Q: What about compliance (PCI, SOC2, etc.)?**  
A: Auth logs are critical for compliance. This provides the first step: reliable, validated event collection. Retention and analysis policies depend on your environment.

---

## Appendix: Demo Scripts

### Quick Test Script

Copy-paste ready:

```bash
#!/bin/bash
cd /path/to/SIEM-lite

# 1. Show installation
pip install -r requirements.txt
python scripts/verify_auth_log_access.py -v

# 2. Run tests
pytest tests/ -v --tb=short

# 3. Test parser
python3 << 'EOF'
from event.parsers.authlog import AuthLogParser
import json

parser = AuthLogParser()
lines = [
    'Jan 10 09:14:22 server sshd[1234]: Failed password for invalid user admin from 192.168.1.100 port 54321',
    'Jan 10 09:15:10 server sshd[1235]: Accepted password for user from 192.168.1.50 port 22',
    'Jan 10 09:16:45 server sudo: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/bin/bash'
]

for line in lines:
    event = parser.parse_line(line, hostname="server")
    if event:
        print(f"✓ Parsed: {event['action']['type']} by {event['actor'].get('user', 'unknown')}")
EOF
```

---

## TimeSheet

| Segment | Duration | Content |
|---------|----------|---------|
| 1. Problem | 0:30 | Why this matters |
| 2. Solution | 0:45 | What we built |
| 3. Demo | 1:30 | Live parser + tests + deployment |
| 4. Deployment | 1:00 | How to run it |
| 5. Features | 0:45 | What's included & what's next |
| 6. Closing | 0:30 | Summary + next steps |
| **TOTAL** | **5:00** | |

---

## Presenter Checklist

Before going live:

- [ ] Terminal with SIEM-lite repo open
- [ ] Python venv activated
- [ ] Dependencies installed
- [ ] Sample log file available
- [ ] Network connectivity (if demoing remote deployment)
- [ ] Backup slides printed or in second monitor
- [ ] Internet for any live documentation links

---

## Success Metrics

**Audience should walk away understanding:**

1. ✅ What SIEM-lite does (parse auth logs into structured events)
2. ✅ Why it matters (foundation for security monitoring)
3. ✅ How to deploy it (systemd or Docker)
4. ✅ That it's production-ready (tests pass, documentation complete)
5. ✅ What's next (detection rules, storage, visualization)

---
