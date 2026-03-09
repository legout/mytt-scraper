"""Session state management for the web application.

This module provides server-side session management and state tracking
for web requests. Sessions are stored in-memory and contain only
serializable data.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WebSession:
    """Server-side session data.
    
    Sessions are identified by a session ID and stored in-memory.
    All session data must be JSON-serializable.
    """
    session_id: str
    data: dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the session."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the session."""
        self.data[key] = value
    
    def delete(self, key: str) -> None:
        """Delete a key from the session."""
        self.data.pop(key, None)