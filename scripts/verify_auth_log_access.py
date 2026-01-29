#!/usr/bin/env python3

"""
verify_auth_log_access.py

Purpose:
- Verify authentication log access before any parsing or detection logic
- Fail fast if assumptions about the log source are invalid

This script intentionally does NOT parse log contents.
It only verifies that the data source is real, readable, and usable.
"""

import os
import sys
import yaml

CONFIG_PATH = "config/log_sources.yaml"


def fatal(message: str):
    print(f"[FATAL] {message}")
    sys.exit(1)


def info(message: str):
    print(f"[INFO] {message}")


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        fatal(f"Config file not found: {path}")

    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        fatal(f"Failed to load YAML config: {e}")


def verify_log_file(path: str):
    info(f"Verifying log file path: {path}")

    if not os.path.exists(path):
        fatal("Log file does not exist")

    if not os.path.isfile(path):
        fatal("Log path exists but is not a file")

    if not os.access(path, os.R_OK):
        fatal("Log file is not readable by current user")

    size = os.path.getsize(path)
    info(f"Log file size: {size} bytes")

    if size == 0:
        info("Log file is empty (this may be normal for a baseline system)")
    else:
        info("Log file contains data")

    return size


def preview_log(path: str, lines: int = 5):
    info(f"Previewing first {lines} lines of log file")
    try:
        with open(path, "r", errors="replace") as f:
            for i in range(lines):
                line = f.readline()
                if not line:
                    break
                print(f"  {line.rstrip()}")
    except Exception as e:
        fatal(f"Failed to read log file: {e}")


def main():
    info("Starting auth.log access verification")

config = load_config(CONFIG_PATH)

if config is None:
    fatal("YAML config loaded as None (file may be empty or invalid)")

    sources = config.get("log_sources", {})
    auth_source = sources.get("auth_log")

    if not auth_source or not auth_source.get("enabled"):
        fatal("auth_log source is missing or disabled in config")

    log_path = auth_source.get("path")
    if not log_path:
        fatal("auth_log path is not defined in config")

    size = verify_log_file(log_path)

    # Only preview if data exists
    if size > 0:
        preview_log(log_path)

    info("Auth log verification completed successfully")
    info("You may proceed to parsing in the next sprint")


if __name__ == "__main__":
    main()
