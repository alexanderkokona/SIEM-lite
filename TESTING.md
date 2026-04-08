# Testing Guide

Comprehensive testing ensures code quality and reliability before deployment.

## Running Tests

### All Tests

```bash
pytest tests/
```

### With Coverage Report

```bash
pytest tests/ --cov=event --cov-report=html
pytest tests/ --cov=event --cov-report=term-missing
```

### Specific Test File

```bash
pytest tests/test_authlog_parser.py -v
pytest tests/test_schema.py -v
```

### Specific Test Function

```bash
pytest tests/test_authlog_parser.py::TestAuthLogParser::test_parse_ssh_failed_password -v
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration
├── test_authlog_parser.py   # Parser tests
└── test_schema.py           # Schema validation tests
```

## Test Categories

### Parser Tests (`test_authlog_parser.py`)

Tests for the auth.log parser:

- **SSH Authentication**: Failed passwords, invalid users, successful logins
- **Sudo Events**: Privilege escalation parsing
- **Account Events**: User creation/deletion
- **Edge Cases**: Empty lines, malformed entries
- **Timestamp Parsing**: Syslog format handling

Example:

```bash
pytest tests/test_authlog_parser.py -v -k "ssh"
```

### Schema Tests (`test_schema.py`)

Tests for event schema and validation:

- **Structure**: Base event creation
- **Validation**: Required fields, enum values
- **Error Handling**: Invalid data detection

Example:

```bash
pytest tests/test_schema.py::TestEventSchema -v
```

## Test Coverage

Current coverage targets:

- Event schema: 95%+
- Logger parser: 90%+
- Overall: 85%+

View detailed coverage:

```bash
pytest tests/ --cov=event --cov-report=html
open htmlcov/index.html  # View in browser
```

## Adding Tests

Create test files in `tests/` directory:

```python
import pytest
from event.parsers.authlog import AuthLogParser

def test_my_feature():
    parser = AuthLogParser()
    event = parser.parse_line("test log line")
    assert event is not None
    assert event["actor"]["user"] == "testuser"
```

Run: `pytest tests/ -v`

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=event
      - run: pytest tests/ --cov=event --cov-fail-under=80
```

## Manual Testing

### Verify Script

```bash
# Test configuration loading
python3 scripts/verify_auth_log_access.py

# Verbose output
python3 scripts/verify_auth_log_access.py -v

# Custom config
python3 scripts/verify_auth_log_access.py -c custom_config.yaml
```

### Parser Interactive Test

```python
from event.parsers.authlog import AuthLogParser

parser = AuthLogParser()

# Test single line
line = "Jan 10 09:14:22 localhost sshd[1234]: Failed password for admin from 127.0.0.1 port 51234 ssh2"
event = parser.parse_line(line)
print(event)

# Test file
events = parser.parse_file("/var/log/auth.log")
print(f"Parsed {len(events)} events")
```

## Performance Testing

### Parser Performance

```bash
time python3 -c "
from event.parsers.authlog import AuthLogParser
parser = AuthLogParser()
events = parser.parse_file('/var/log/auth.log')
print(f'Parsed {len(events)} events')
"
```

### Expected Performance
- Small logs (< 1MB): < 100ms
- Medium logs (1-10MB): < 1s
- Large logs (10-100MB): 1-10s

## Integration Testing

Test with real auth.log entries:

```bash
# Copy sample to test data
cp /var/log/auth.log data/raw/auth.log.test

# Parse and verify
python3 -c "
from event.parsers.authlog import AuthLogParser
parser = AuthLogParser()
events = parser.parse_file('data/raw/auth.log.test')
for event in events[:5]:
    print(f'{event[\"metadata\"][\"event_time\"]}: ' \
          f'{event[\"action\"][\"category\"]} - {event[\"actor\"][\"user\"]}')
"
```

## Debugging Tests

### Verbose Output

```bash
pytest tests/ -v -s  # -s shows print statements
```

### Drop into Debugger

```bash
pytest tests/ --pdb  # Drops into pdb on failure
```

### Show Local Variables

```bash
pytest tests/ -l  # Shows local variables on failure
```

## Continuous Testing

Watch mode (requires pytest-watch):

```bash
pip install pytest-watch
ptw tests/
```

Auto-run tests on file changes.

## Test Data

Sample log entries in [examples/](event/examples/):

- `auth_failed_login.json`: Failed SSH login event structure

Use for reference when writing tests.
