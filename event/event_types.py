"""
event_types.py

Enumerations for event categories and action types.
Used by parsers and detectors to stay consistent.
"""

# Action categories
AUTHENTICATION = "authentication"
AUTHORIZATION = "authorization"
ACCOUNT = "account"

# Authentication actions
LOGIN = "login"

# Authorization actions
SUDO = "sudo"

# Account actions
USER_ADD = "user_add"

# Outcomes
SUCCESS = "success"
FAILURE = "failure"
