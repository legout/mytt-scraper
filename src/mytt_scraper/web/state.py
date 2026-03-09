"""Session state management for the web application.

This module provides server-side session management and state tracking
for web requests. Sessions are stored in-memory and contain only
serializable data.
"""

from __future__ import annotations

import json
import secrets
import threading
import time
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
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600)

    def __post_init__(self) -> None:
        """Validate that all data is JSON-serializable at construction time."""
        self.validate_serializable(self.data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the session."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the session."""
        self.validate_serializable({key: value})
        self.data[key] = value

    def delete(self, key: str) -> None:
        """Delete a key from the session."""
        self.data.pop(key, None)

    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return time.time() > self.expires_at

    def validate_serializable(self, data: dict[str, Any] | None = None) -> bool:
        """Validate that all data is JSON-serializable.

        Args:
            data: Optional data dict to validate. If None, validates self.data.

        Returns:
            True if data is JSON-serializable.

        Raises:
            ValueError: If data contains non-serializable values.
        """
        data_to_validate = data if data is not None else self.data
        return self.validate_data_serializable(data_to_validate)

    @staticmethod
    def _is_json_serializable(value: Any) -> bool:
        """Check if a value is JSON-serializable."""
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    def validate_data_serializable(cls, data: dict[str, Any]) -> bool:
        """Validate that all data is JSON-serializable (class method).

        Args:
            data: Data dict to validate.

        Returns:
            True if data is JSON-serializable.

        Raises:
            ValueError: If data contains non-serializable values.
        """
        for key, value in data.items():
            if not cls._is_json_serializable(value):
                raise ValueError(
                    f"Session data key '{key}' contains non-serializable value: {type(value).__name__}"
                )
        return True

    def to_cookie_dict(self) -> dict[str, Any]:
        """Convert session to a dict suitable for cookie storage.

        Returns minimal data needed to identify the session.
        Full session data is stored server-side.
        """
        return {
            "session_id": self.session_id,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_cookie_dict(cls, data: dict[str, Any]) -> WebSession:
        """Reconstruct a minimal WebSession from cookie data.

        Note: This creates a session shell. Full data must be retrieved
        from the SessionStore using the session_id.
        """
        return cls(
            session_id=data["session_id"],
            expires_at=data.get("expires_at", time.time() + 3600),
        )


@dataclass
class CookieSession:
    """Stores cookie state for HTTP session persistence."""

    cookies: dict[str, str] = field(default_factory=dict)
    domain: str | None = None
    path: str = "/"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "cookies": self.cookies,
            "domain": self.domain,
            "path": self.path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CookieSession:
        """Create CookieSession from dictionary."""
        return cls(
            cookies=data.get("cookies", {}),
            domain=data.get("domain"),
            path=data.get("path", "/"),
        )


class SessionStore:
    """In-memory session store with TTL cleanup and max session cap.

    Thread-safe operations for concurrent web server access.
    """

    MAX_SESSIONS = 100
    DEFAULT_TTL_SECONDS = 3600  # 1 hour

    def __init__(self) -> None:
        """Initialize the session store."""
        self._sessions: dict[str, WebSession] = {}
        self._lock = threading.Lock()

    def create_session(
        self, data: dict[str, Any] | None = None, ttl_seconds: int | None = None
    ) -> WebSession:
        """Create a new session with unique ID.

        Args:
            data: Optional initial session data (must be JSON-serializable).
            ttl_seconds: Optional custom TTL (defaults to DEFAULT_TTL_SECONDS).

        Returns:
            New WebSession instance.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL_SECONDS

        # Validate data is serializable before creating session
        if data:
            WebSession.validate_data_serializable(data)

        with self._lock:
            # Clean up and enforce limits atomically under lock
            self._cleanup_expired_unlocked()
            self._enforce_max_sessions_unlocked()

            session_id = self._generate_session_id_unlocked()
            session = WebSession(
                session_id=session_id,
                data=data or {},
                created_at=time.time(),
                expires_at=time.time() + ttl,
            )

            self._sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> WebSession | None:
        """Retrieve a session if it exists and is not expired.

        Args:
            session_id: The session ID to look up.

        Returns:
            WebSession if found and not expired, None otherwise.
        """
        with self._lock:
            session = self._sessions.get(session_id)

        if session is None:
            return None

        if session.is_expired():
            self.clear_session(session_id)
            return None

        return session

    def update_session(self, session_id: str, data: dict[str, Any]) -> bool:
        """Merge data into an existing session.

        Args:
            session_id: The session ID to update.
            data: Data to merge (must be JSON-serializable).

        Returns:
            True if session was updated, False if not found.
        """
        # Validate data is serializable
        WebSession.validate_data_serializable(data)

        with self._lock:
            session = self._sessions.get(session_id)
            if session is None or session.is_expired():
                return False

            session.data.update(data)
            return True

    def clear_session(self, session_id: str) -> bool:
        """Remove a session from the store.

        Args:
            session_id: The session ID to remove.

        Returns:
            True if session was removed, False if not found.
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def _generate_session_id_unlocked(self) -> str:
        """Generate a cryptographically secure session ID.

        Ensures uniqueness by checking against existing sessions.
        Must be called with lock held.
        """
        while True:
            session_id = secrets.token_urlsafe(32)
            if session_id not in self._sessions:
                return session_id

    def _cleanup_expired_unlocked(self) -> int:
        """Remove all expired sessions.

        Must be called with lock held.

        Returns:
            Number of sessions removed.
        """
        expired_ids: list[str] = [
            sid for sid, session in self._sessions.items() if session.is_expired()
        ]

        for session_id in expired_ids:
            del self._sessions[session_id]

        return len(expired_ids)

    def _enforce_max_sessions_unlocked(self) -> int:
        """Remove oldest sessions when max cap is reached.

        Must be called with lock held.

        Returns:
            Number of sessions removed.
        """
        removed = 0

        while len(self._sessions) >= self.MAX_SESSIONS:
            # Find oldest session
            oldest_id = min(
                self._sessions.keys(),
                key=lambda sid: self._sessions[sid].created_at,
            )
            del self._sessions[oldest_id]
            removed += 1

        return removed

    def _generate_session_id(self) -> str:
        """Generate a cryptographically secure session ID (public wrapper)."""
        with self._lock:
            return self._generate_session_id_unlocked()

    def _cleanup_expired(self) -> int:
        """Remove all expired sessions (public wrapper)."""
        with self._lock:
            return self._cleanup_expired_unlocked()

    def _enforce_max_sessions(self) -> int:
        """Remove oldest sessions when max cap is reached (public wrapper)."""
        with self._lock:
            return self._enforce_max_sessions_unlocked()

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about current sessions.

        Returns:
            Dict with session count, oldest/newest timestamps.
        """
        with self._lock:
            if not self._sessions:
                return {
                    "count": 0,
                    "oldest_created": None,
                    "newest_created": None,
                    "oldest_expires": None,
                    "newest_expires": None,
                }

            sessions_list = list(self._sessions.values())
            created_times = [s.created_at for s in sessions_list]
            expires_times = [s.expires_at for s in sessions_list]

            return {
                "count": len(self._sessions),
                "oldest_created": min(created_times),
                "newest_created": max(created_times),
                "oldest_expires": min(expires_times),
                "newest_expires": max(expires_times),
            }

    def save_cookies(self, session_id: str, cookies: dict[str, str]) -> bool:
        """Store cookies in a session.

        Args:
            session_id: The session ID.
            cookies: Cookie key-value pairs.

        Returns:
            True if cookies were saved, False if session not found.
        """
        cookie_session = CookieSession(cookies=cookies)
        return self.update_session(session_id, {"_cookies": cookie_session.to_dict()})

    def restore_cookies(self, session_id: str) -> dict[str, str]:
        """Retrieve cookies from a session.

        Args:
            session_id: The session ID.

        Returns:
            Cookie dict if found, empty dict otherwise.
        """
        session = self.get_session(session_id)
        if session is None:
            return {}

        cookie_data = session.get("_cookies")
        if cookie_data is None:
            return {}

        try:
            cookie_session = CookieSession.from_dict(cookie_data)
            return cookie_session.cookies
        except (KeyError, TypeError):
            return {}


# Global session store instance
session_store = SessionStore()
