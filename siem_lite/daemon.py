"""
daemon.py

Main daemon process for SIEM-lite authentication log pipeline.
Monitors auth.log for new entries and processes them continuously.
"""

import logging
import time
import signal
import sys
import yaml
from pathlib import Path
from typing import Optional

from event.parsers.authlog import AuthLogParser

logger = logging.getLogger(__name__)


class SIEMLiteDaemon:
    """Main daemon for processing authentication logs"""
    
    def __init__(self, config_path: str = "config/log_sources.yaml"):
        """
        Initialize daemon
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = None
        self.running = False
        self.parser = AuthLogParser()
        self.last_position = 0
        
        # Signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse configuration: {e}")
            raise
    
    def get_log_path(self) -> str:
        """Get auth log path from configuration"""
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        sources = self.config.get("log_sources", {})
        auth_source = sources.get("auth_log", {})
        
        if not auth_source.get("enabled"):
            raise ValueError("auth_log source is not enabled")
        
        path = auth_source.get("path")
        if not path:
            raise ValueError("auth_log path not configured")
        
        return path
    
    def process_log_file(self, filepath: str):
        """
        Process authentication log file
        
        Args:
            filepath: Path to log file
        """
        try:
            with open(filepath, 'r', errors='replace') as f:
                # Seek to last known position
                f.seek(self.last_position)
                
                for line in f:
                    if not self.running:
                        break
                    
                    event = self.parser.parse_line(line)
                    if event:
                        # Process event (placeholder for future logic)
                        self._handle_event(event)
                
                # Update position for next run
                self.last_position = f.tell()
        
        except IOError as e:
            logger.error(f"Failed to read log file: {e}")
    
    def _handle_event(self, event: dict):
        """
        Handle parsed event
        
        Args:
            event: Parsed event dictionary
        """
        logger.debug(f"Processing event: {event['metadata']['event_id']}")
        # Future: send to alerting, storage, etc.
    
    def run(self, interval: int = 5):
        """
        Run daemon
        
        Args:
            interval: Seconds to wait between log checks
        """
        logger.info("Starting SIEM-lite daemon")
        
        try:
            self.load_config()
            log_path = self.get_log_path()
            
            logger.info(f"Monitoring log file: {log_path}")
            
            self.running = True
            
            while self.running:
                try:
                    self.process_log_file(log_path)
                except Exception as e:
                    logger.error(f"Error processing log: {e}", exc_info=True)
                
                if self.running:
                    time.sleep(interval)
        
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return 1
        
        logger.info("Daemon stopped")
        return 0


def main():
    """Entry point for daemon"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    daemon = SIEMLiteDaemon()
    sys.exit(daemon.run())


if __name__ == "__main__":
    main()
