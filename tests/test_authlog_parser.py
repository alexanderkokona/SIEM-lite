"""
tests/test_authlog_parser.py

Unit tests for auth.log parser
"""

import pytest
from datetime import datetime
from event.parsers.authlog import AuthLogParser
from event.event_types import AUTHENTICATION, LOGIN, SUDO, SUCCESS, FAILURE


class TestAuthLogParser:
    """Test cases for AuthLogParser"""
    
    def setup_method(self):
        """Set up parser for each test"""
        self.parser = AuthLogParser()
    
    def test_parse_ssh_failed_password(self):
        """Test parsing failed SSH password attempt"""
        line = "Jan 10 09:14:22 localhost sshd[1234]: Failed password for admin from 127.0.0.1 port 51234 ssh2"
        event = self.parser.parse_line(line)
        
        assert event is not None
        assert event["source"]["program"] == "sshd"
        assert event["source"]["pid"] == 1234
        assert event["actor"]["user"] == "admin"
        assert event["network"]["src_ip"] == "127.0.0.1"
        assert event["network"]["src_port"] == 51234
        assert event["action"]["category"] == AUTHENTICATION
        assert event["action"]["type"] == LOGIN
        assert event["outcome"]["result"] == FAILURE
        assert event["outcome"]["reason"] == "invalid_password"
    
    def test_parse_ssh_failed_invalid_user(self):
        """Test parsing failed SSH login for invalid user"""
        line = "Jan 10 10:15:33 localhost sshd[5678]: Failed password for invalid user testuser from 192.168.1.100 port 54321 ssh2"
        event = self.parser.parse_line(line)
        
        assert event is not None
        assert event["actor"]["user"] == "testuser"
        assert event["network"]["src_ip"] == "192.168.1.100"
        assert event["outcome"]["reason"] == "invalid_password"
    
    def test_parse_ssh_accepted_password(self):
        """Test parsing successful SSH login"""
        line = "Jan 10 11:22:44 localhost sshd[9012]: Accepted password for ubuntu from 203.0.113.45 port 55555 ssh2"
        event = self.parser.parse_line(line)
        
        assert event is not None
        assert event["actor"]["user"] == "ubuntu"
        assert event["network"]["src_ip"] == "203.0.113.45"
        assert event["network"]["src_port"] == 55555
        assert event["outcome"]["result"] == SUCCESS
    
    def test_parse_ssh_invalid_user(self):
        """Test parsing invalid user attempt"""
        line = "Jan 10 12:33:55 localhost sshd[3456]: Invalid user hacker from 198.51.100.5 port 12345 ssh2"
        event = self.parser.parse_line(line)
        
        assert event is not None
        assert event["actor"]["user"] == "hacker"
        assert event["outcome"]["reason"] == "invalid_user"
        assert event["outcome"]["result"] == FAILURE
    
    def test_parse_sudo_command(self):
        """Test parsing sudo privilege escalation"""
        line = "Jan 10 14:45:10 localhost sudo[7890]: ubuntu : sudo : TTY=pts/0 ; PWD=/home/ubuntu ; USER=root ; COMMAND=/usr/bin/apt update"
        event = self.parser.parse_line(line)
        
        assert event is not None
        assert event["source"]["program"] == "sudo"
        assert event["actor"]["user"] == "ubuntu"
        assert event["privilege"]["escalated"] is True
        assert event["privilege"]["target_user"] == "root"
        assert event["outcome"]["result"] == SUCCESS
    
    def test_parse_empty_line(self):
        """Test that empty lines return None"""
        assert self.parser.parse_line("") is None
        assert self.parser.parse_line("   ") is None
    
    def test_parse_malformed_line(self):
        """Test that malformed lines return None"""
        assert self.parser.parse_line("This is not a valid log line") is None
        assert self.parser.parse_line("Jan 10 some invalid data") is None
    
    def test_syslog_time_parsing(self):
        """Test syslog timestamp parsing"""
        dt = self.parser._parse_syslog_time("Jan", "10", "09:14:22")
        assert isinstance(dt, datetime)
        assert dt.month == 1
        assert dt.day == 10
        assert dt.hour == 9
        assert dt.minute == 14
        assert dt.second == 22
    
    def test_syslog_time_invalid_month(self):
        """Test that invalid month raises error"""
        with pytest.raises(ValueError):
            self.parser._parse_syslog_time("Foo", "10", "09:14:22")
    
    def test_syslog_time_invalid_day(self):
        """Test that invalid day raises error"""
        with pytest.raises(ValueError):
            self.parser._parse_syslog_time("Jan", "32", "09:14:22")
    
    def test_syslog_time_invalid_time(self):
        """Test that invalid time raises error"""
        with pytest.raises(ValueError):
            self.parser._parse_syslog_time("Jan", "10", "25:00:00")
    
    def test_parse_multiple_lines(self):
        """Test parsing multiple log lines"""
        lines = [
            "Jan 10 09:14:22 localhost sshd[1234]: Failed password for admin from 127.0.0.1 port 51234 ssh2",
            "Jan 10 09:15:33 localhost sshd[5678]: Accepted password for ubuntu from 203.0.113.45 port 55555 ssh2",
            "This is a malformed line",
            "Jan 10 14:45:10 localhost sudo[7890]: ubuntu : sudo : TTY=pts/0 ; PWD=/home/ubuntu ; USER=root ; COMMAND=/usr/bin/apt update"
        ]
        
        events = []
        for line in lines:
            event = self.parser.parse_line(line)
            if event:
                events.append(event)
        
        # Should parse 3 out of 4 lines successfully
        assert len(events) == 3
        assert events[0]["actor"]["user"] == "admin"
        assert events[1]["actor"]["user"] == "ubuntu"
        assert events[2]["actor"]["user"] == "ubuntu"
