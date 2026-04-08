"""
authlog.py

Parser for Linux authentication logs (/var/log/auth.log).
Extracts structured events from syslog-formatted authentication messages.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from ..schema import base_event, validate_event
from ..event_types import (
    AUTHENTICATION, LOGIN, SUCCESS, FAILURE, SUDO
)


class AuthLogParser:
    """
    Parses standard Linux auth.log entries.
    
    Handles patterns from common services:
    - sshd (SSH authentication)
    - sudo (privilege escalation)
    - passwd/useradd (account modifications)
    """
    
    PARSER_VERSION = "authlog-v1"
    
    # Pattern for standard syslog timestamp: Jan 10 09:14:22
    SYSLOG_PATTERN = r"^(\w{3}\s+\d{1,2}\s+[\d:]{8})"
    
    # SSH patterns
    SSH_FAILED_PASSWORD = r"Failed password for (?:invalid user )?(\S+) from (\S+) port (\d+)"
    SSH_ACCEPTED_PASSWORD = r"Accepted password for (\S+) from (\S+) port (\d+)"
    SSH_INVALID_USER = r"Invalid user (\S+) from (\S+) port (\d+)"
    
    # sudo patterns
    SUDO_PATTERN = r"^(\S+)\s*:\s*sudo\s*:\s*TTY=(\S*)\s*;\s*PWD=\s*([^;]+)\s*;\s*USER=(\S+)\s*;\s*COMMAND=\s*(.*)"
    
    # useradd/userdel patterns
    USERADD_PATTERN = r"new user: name=(\S+), UID=(\d+), GID=(\d+)"
    USERDEL_PATTERN = r"delete user (\S+)\s"
    
    def parse_line(self, line: str, hostname: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Parse a single auth.log line into a structured event.
        
        Args:
            line: Raw log line
            hostname: Optional hostname override (for testing)
            
        Returns:
            Structured event dict, or None if line cannot be parsed
        """
        line = line.strip()
        if not line:
            return None
        
        event = base_event()
        
        # Extract syslog components
        parts = line.split(None, 3)  # Split on whitespace, max 4 parts
        if len(parts) < 4:
            return None
        
        # parts[0:3] = Month Day Time
        # parts[3] = hostname program[pid]: message
        
        month_str, day_str, time_str = parts[0], parts[1], parts[2]
        
        # Parse timestamp (assuming current year)
        try:
            event_time = self._parse_syslog_time(month_str, day_str, time_str)
            event["metadata"]["event_time"] = event_time
        except ValueError:
            return None
        
        # Extract hostname, program, and message
        rest = parts[3]
        match = re.match(r"(\S+)\s+(\w+)(?:\[(\d+)\])?\s*:\s*(.*)", rest)
        if not match:
            return None
        
        hostname_raw, program, pid, message = match.groups()
        event["source"]["host"] = hostname or hostname_raw
        event["source"]["program"] = program
        if pid:
            event["source"]["pid"] = int(pid)
        event["raw"]["message"] = line
        
        # Route to appropriate parser based on program
        if program == "sshd":
            return self._parse_sshd(event, message)
        elif program == "sudo":
            return self._parse_sudo(event, message)
        elif program in ("useradd", "userdel", "passwd"):
            return self._parse_account_event(event, program, message)
        
        # If no specific parser matched, return minimal event
        return None
    
    def _parse_sshd(self, event: Dict[str, Any], message: str) -> Optional[Dict[str, Any]]:
        """Parse SSH daemon authentication events."""
        
        # Failed password
        match = re.search(self.SSH_FAILED_PASSWORD, message)
        if match:
            user, src_ip, src_port = match.groups()
            event["actor"]["user"] = user
            event["network"]["src_ip"] = src_ip
            event["network"]["src_port"] = int(src_port)
            event["network"]["protocol"] = "ssh"
            event["action"]["category"] = AUTHENTICATION
            event["action"]["type"] = LOGIN
            event["outcome"]["result"] = FAILURE
            event["outcome"]["reason"] = "invalid_password"
            validate_event(event)
            return event
        
        # Accepted password
        match = re.search(self.SSH_ACCEPTED_PASSWORD, message)
        if match:
            user, src_ip, src_port = match.groups()
            event["actor"]["user"] = user
            event["network"]["src_ip"] = src_ip
            event["network"]["src_port"] = int(src_port)
            event["network"]["protocol"] = "ssh"
            event["action"]["category"] = AUTHENTICATION
            event["action"]["type"] = LOGIN
            event["outcome"]["result"] = SUCCESS
            validate_event(event)
            return event
        
        # Invalid user
        match = re.search(self.SSH_INVALID_USER, message)
        if match:
            user, src_ip, src_port = match.groups()
            event["actor"]["user"] = user
            event["network"]["src_ip"] = src_ip
            event["network"]["src_port"] = int(src_port)
            event["network"]["protocol"] = "ssh"
            event["action"]["category"] = AUTHENTICATION
            event["action"]["type"] = LOGIN
            event["outcome"]["result"] = FAILURE
            event["outcome"]["reason"] = "invalid_user"
            validate_event(event)
            return event
        
        return None
    
    def _parse_sudo(self, event: Dict[str, Any], message: str) -> Optional[Dict[str, Any]]:
        """Parse sudo privilege escalation events."""
        
        match = re.search(self.SUDO_PATTERN, message)
        if not match:
            return None
        
        user, tty, pwd, target_user, command = match.groups()
        event["actor"]["user"] = user
        event["target"]["user"] = target_user
        event["action"]["category"] = SUDO
        event["action"]["type"] = "execute"
        event["outcome"]["result"] = SUCCESS  # sudo log entries are only created on success
        event["privilege"]["escalated"] = True
        event["privilege"]["target_user"] = target_user
        validate_event(event)
        return event
    
    def _parse_account_event(self, event: Dict[str, Any], program: str, 
                            message: str) -> Optional[Dict[str, Any]]:
        """Parse user account management events."""
        
        if program == "useradd":
            match = re.search(self.USERADD_PATTERN, message)
            if match:
                username, uid, gid = match.groups()
                event["target"]["user"] = username
                event["action"]["category"] = "account"
                event["action"]["type"] = "user_add"
                event["outcome"]["result"] = SUCCESS
                validate_event(event)
                return event
        
        elif program == "userdel":
            match = re.search(self.USERDEL_PATTERN, message)
            if match:
                username = match.group(1)
                event["target"]["user"] = username
                event["action"]["category"] = "account"
                event["action"]["type"] = "user_delete"
                event["outcome"]["result"] = SUCCESS
                validate_event(event)
                return event
        
        return None
    
    @staticmethod
    def _parse_syslog_time(month: str, day: str, time_str: str) -> datetime:
        """
        Parse syslog timestamp (no year component).
        Assumes current or previous year if month hasn't occurred yet this year.
        """
        months = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        
        if month not in months:
            raise ValueError(f"Invalid month: {month}")
        
        month_num = months[month]
        day_num = int(day)
        time_parts = time_str.split(":")
        if len(time_parts) != 3:
            raise ValueError(f"Invalid time: {time_str}")
        
        hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
        
        # Use current year by default
        now = datetime.now(timezone.utc)
        year = now.year
        
        # If the month/day hasn't occurred yet this year, assume last year
        try:
            dt = datetime(year, month_num, day_num, hour, minute, second, tzinfo=timezone.utc)
        except ValueError:
            raise ValueError(f"Invalid date/time: {month} {day} {time_str}")
        
        if dt > now:
            dt = datetime(year - 1, month_num, day_num, hour, minute, second, tzinfo=timezone.utc)
        
        return dt
    
    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parse entire auth.log file.
        
        Args:
            filepath: Path to auth.log file
            
        Returns:
            List of successfully parsed events (skips unparseable lines)
        """
        events = []
        
        try:
            with open(filepath, "r", errors="replace") as f:
                for line in f:
                    event = self.parse_line(line)
                    if event:
                        event["metadata"]["parser_version"] = self.PARSER_VERSION
                        event["metadata"]["source_type"] = "auth_log"
                        events.append(event)
        except IOError as e:
            raise IOError(f"Failed to read auth log file: {e}")
        
        return events
