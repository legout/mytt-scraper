"""Session and authentication signals for reactive updates.

This module provides Signal instances for tracking authentication state
and session validity in the web interface. These signals work with
Datastar's SSE mechanism for real-time UI updates.
"""

from starhtml import Signal

# Authentication state signals
session_valid = Signal("session_valid", initial=False)
"""Signal indicating if the current session is authenticated."""

session_username = Signal("session_username", initial="")
"""Signal containing the username of the authenticated user."""

auth_error = Signal("auth_error", initial="")
"""Signal containing any authentication error message."""

auth_status = Signal("auth_status", initial="idle")
"""Signal tracking authentication progress state.

Values:
    - "idle": No authentication in progress
    - "authenticating": Login request in progress
    - "done": Authentication successful
    - "error": Authentication failed
"""
