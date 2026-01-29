"""
schema.py

Canonical event schema for SIEM-lite.
All parsed events MUST conform to this structure.

This file defines structure and validation rules only.
No parsing, no detection logic.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid


def generate_event_id() -> str:
    return str(uuid.uuid4())


def base_event() -> Dict[str, Any]:
    """
    Returns a skeleton event with required top-level keys.
    Parsers should populate fields, not invent new ones.
    """
    return {
        "metadata": {
            "event_id": generate_event_id(),
            "event_time": None,      # datetime
            "ingest_time": datetime.utcnow(),
            "source_type": None,     # e.g. "auth_log"
            "parser_version": None   # e.g. "authlog-v1"
        },
        "source": {
            "host": None,
            "program": None,
            "pid": None
        },
        "actor": {
            "user": None,
            "uid": None
        },
        "target": {
            "user": None,
            "resource": None
        },
        "action": {
            "category": None,
            "type": None
        },
        "outcome": {
            "result": None,
            "reason": None
        },
        "network": {
            "src_ip": None,
            "src_port": None,
            "protocol": None
        },
        "privilege": {
            "escalated": None,
            "target_user": None
        },
        "raw": {
            "message": None
        }
    }


def validate_event(event: Dict[str, Any]) -> None:
    """
    Minimal structural validation.
    Raises ValueError if required fields are missing.
    """

    required_sections = [
        "metadata", "source", "actor", "target",
        "action", "outcome", "network", "privilege", "raw"
    ]

    for section in required_sections:
        if section not in event:
            raise ValueError(f"Missing required section: {section}")

    if event["metadata"]["event_time"] is None:
        raise ValueError("metadata.event_time must be set")

    if event["action"]["category"] is None:
        raise ValueError("action.category must be set")

    if event["action"]["type"] is None:
        raise ValueError("action.type must be set")

    if event["outcome"]["result"] not in ("success", "failure"):
        raise ValueError("outcome.result must be 'success' or 'failure'")

    if event["raw"]["message"] is None:
        raise ValueError("raw.message must be preserved")
