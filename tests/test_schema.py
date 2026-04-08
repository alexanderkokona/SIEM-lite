"""
tests/test_schema.py

Unit tests for event schema and validation
"""

import pytest
from datetime import datetime, timezone
from event.schema import base_event, validate_event


class TestEventSchema:
    """Test cases for event schema"""
    
    def test_base_event_structure(self):
        """Test that base_event creates proper structure"""
        event = base_event()
        
        # Check all required sections exist
        required_sections = [
            "metadata", "source", "actor", "target",
            "action", "outcome", "network", "privilege", "raw"
        ]
        for section in required_sections:
            assert section in event
    
    def test_metadata_has_event_id(self):
        """Test that metadata includes event_id"""
        event = base_event()
        assert "event_id" in event["metadata"]
        assert event["metadata"]["event_id"] is not None
        assert len(event["metadata"]["event_id"]) > 0
    
    def test_metadata_has_ingest_time(self):
        """Test that metadata includes ingest_time"""
        event = base_event()
        assert "ingest_time" in event["metadata"]
        assert isinstance(event["metadata"]["ingest_time"], datetime)
    
    def test_validate_event_minimal_valid(self):
        """Test validation of minimal valid event"""
        event = base_event()
        event["metadata"]["event_time"] = datetime.now(timezone.utc)
        event["action"]["category"] = "authentication"
        event["action"]["type"] = "login"
        event["outcome"]["result"] = "success"
        event["raw"]["message"] = "Test message"
        
        # Should not raise
        validate_event(event)
    
    def test_validate_event_missing_section(self):
        """Test validation fails with missing section"""
        event = base_event()
        del event["metadata"]
        
        with pytest.raises(ValueError, match="Missing required section"):
            validate_event(event)
    
    def test_validate_event_missing_event_time(self):
        """Test validation fails without event_time"""
        event = base_event()
        event["action"]["category"] = "authentication"
        event["action"]["type"] = "login"
        event["outcome"]["result"] = "success"
        event["raw"]["message"] = "Test message"
        
        with pytest.raises(ValueError, match="event_time must be set"):
            validate_event(event)
    
    def test_validate_event_missing_action_category(self):
        """Test validation fails without action category"""
        event = base_event()
        event["metadata"]["event_time"] = datetime.now(timezone.utc)
        event["action"]["type"] = "login"
        event["outcome"]["result"] = "success"
        event["raw"]["message"] = "Test message"
        
        with pytest.raises(ValueError, match="action.category must be set"):
            validate_event(event)
    
    def test_validate_event_missing_action_type(self):
        """Test validation fails without action type"""
        event = base_event()
        event["metadata"]["event_time"] = datetime.now(timezone.utc)
        event["action"]["category"] = "authentication"
        event["outcome"]["result"] = "success"
        event["raw"]["message"] = "Test message"
        
        with pytest.raises(ValueError, match="action.type must be set"):
            validate_event(event)
    
    def test_validate_event_invalid_outcome(self):
        """Test validation fails with invalid outcome"""
        event = base_event()
        event["metadata"]["event_time"] = datetime.now(timezone.utc)
        event["action"]["category"] = "authentication"
        event["action"]["type"] = "login"
        event["outcome"]["result"] = "maybe"  # Invalid
        event["raw"]["message"] = "Test message"
        
        with pytest.raises(ValueError, match="outcome.result must be"):
            validate_event(event)
    
    def test_validate_event_missing_raw_message(self):
        """Test validation fails without raw message"""
        event = base_event()
        event["metadata"]["event_time"] = datetime.now(timezone.utc)
        event["action"]["category"] = "authentication"
        event["action"]["type"] = "login"
        event["outcome"]["result"] = "success"
        
        with pytest.raises(ValueError, match="raw.message must be preserved"):
            validate_event(event)
