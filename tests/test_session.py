"""Unit tests for session state management.

Tests cover WebSession serialization, SessionStore CRUD operations,
TTL cleanup, max session cap enforcement, and cookie persistence.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest

from mytt_scraper.web.state import (
    CookieSession,
    SessionStore,
    WebSession,
    session_store,
)


class TestWebSession:
    """Test WebSession dataclass functionality."""

    def test_basic_creation(self) -> None:
        """Test basic WebSession creation."""
        session = WebSession(session_id="test-123")
        assert session.session_id == "test-123"
        assert session.data == {}
        assert session.created_at <= time.time()
        assert session.expires_at > session.created_at

    def test_get_set_delete(self) -> None:
        """Test get, set, and delete operations."""
        session = WebSession(session_id="test-123")

        # Test set and get
        session.set("key1", "value1")
        assert session.get("key1") == "value1"

        # Test default value
        assert session.get("nonexistent", "default") == "default"
        assert session.get("nonexistent") is None

        # Test delete
        session.delete("key1")
        assert session.get("key1") is None

        # Test delete nonexistent key doesn't raise
        session.delete("nonexistent")

    def test_is_expired(self) -> None:
        """Test session expiration check."""
        # Expired session
        expired_session = WebSession(
            session_id="expired",
            expires_at=time.time() - 1,
        )
        assert expired_session.is_expired() is True

        # Valid session
        valid_session = WebSession(
            session_id="valid",
            expires_at=time.time() + 3600,
        )
        assert valid_session.is_expired() is False

    def test_validate_serializable_rejects_functions(self) -> None:
        """Test that functions are rejected as non-serializable."""
        session = WebSession(session_id="test-123")

        with pytest.raises(ValueError) as exc_info:
            session.set("func", lambda x: x)

        assert "non-serializable" in str(exc_info.value)
        assert "func" in str(exc_info.value)

    def test_validate_serializable_rejects_objects(self) -> None:
        """Test that arbitrary objects are rejected."""
        session = WebSession(session_id="test-123")

        class CustomClass:
            pass

        with pytest.raises(ValueError) as exc_info:
            session.set("obj", CustomClass())

        assert "non-serializable" in str(exc_info.value)

    def test_validate_serializable_accepts_primitives(self) -> None:
        """Test that primitive types are accepted."""
        session = WebSession(session_id="test-123")

        # Should not raise
        session.set("string", "value")
        session.set("integer", 42)
        session.set("float", 3.14)
        session.set("boolean", True)
        session.set("none", None)
        session.set("list", [1, 2, 3])
        session.set("dict", {"nested": "value"})

        assert session.validate_serializable() is True

    def test_validate_serializable_accepts_nested(self) -> None:
        """Test nested structures are validated."""
        session = WebSession(session_id="test-123")

        nested_data = {
            "level1": {
                "level2": {
                    "level3": ["a", "b", "c"],
                },
            },
        }
        session.set("nested", nested_data)
        assert session.validate_serializable() is True

    def test_to_cookie_dict(self) -> None:
        """Test conversion to cookie-safe dict."""
        session = WebSession(
            session_id="test-123",
            data={"sensitive": "data", "user_id": 42},
            expires_at=1234567890.0,
        )

        cookie_dict = session.to_cookie_dict()

        assert "session_id" in cookie_dict
        assert "expires_at" in cookie_dict
        assert cookie_dict["session_id"] == "test-123"
        assert cookie_dict["expires_at"] == 1234567890.0
        assert "sensitive" not in cookie_dict  # Data should not be in cookie

    def test_from_cookie_dict(self) -> None:
        """Test reconstruction from cookie data."""
        cookie_data = {
            "session_id": "test-123",
            "expires_at": 1234567890.0,
        }

        session = WebSession.from_cookie_dict(cookie_data)

        assert session.session_id == "test-123"
        assert session.expires_at == 1234567890.0
        assert session.data == {}  # Empty data - must be retrieved from store


class TestCookieSession:
    """Test CookieSession dataclass."""

    def test_creation(self) -> None:
        """Test CookieSession creation."""
        cs = CookieSession(cookies={"session": "abc"}, domain="example.com")
        assert cs.cookies == {"session": "abc"}
        assert cs.domain == "example.com"
        assert cs.path == "/"

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        cs = CookieSession(cookies={"a": "1"}, domain="example.com", path="/api")
        data = cs.to_dict()

        assert data == {
            "cookies": {"a": "1"},
            "domain": "example.com",
            "path": "/api",
        }

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {
            "cookies": {"b": "2"},
            "domain": "test.com",
            "path": "/v1",
        }
        cs = CookieSession.from_dict(data)

        assert cs.cookies == {"b": "2"}
        assert cs.domain == "test.com"
        assert cs.path == "/v1"

    def test_from_dict_defaults(self) -> None:
        """Test from_dict with missing fields uses defaults."""
        cs = CookieSession.from_dict({})

        assert cs.cookies == {}
        assert cs.domain is None
        assert cs.path == "/"


class TestSessionStore:
    """Test SessionStore functionality."""

    @pytest.fixture(autouse=True)
    def reset_store(self) -> None:
        """Reset the global session store before each test."""
        # Clear all sessions
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)
        yield
        # Clean up after test
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)

    def test_create_session_basic(self) -> None:
        """Test basic session creation."""
        session = session_store.create_session()

        assert session.session_id
        assert len(session.session_id) > 0
        assert session.data == {}
        assert not session.is_expired()

    def test_create_session_with_data(self) -> None:
        """Test creating session with initial data."""
        data = {"user_id": 42, "username": "test"}
        session = session_store.create_session(data=data)

        assert session.data == data

    def test_create_session_with_custom_ttl(self) -> None:
        """Test creating session with custom TTL."""
        short_ttl = 5  # 5 seconds
        session = session_store.create_session(ttl_seconds=short_ttl)

        expected_expires = time.time() + short_ttl
        assert abs(session.expires_at - expected_expires) < 1

    def test_create_session_rejects_non_serializable(self) -> None:
        """Test that non-serializable data is rejected on creation."""
        with pytest.raises(ValueError):
            session_store.create_session(data={"func": lambda x: x})

    def test_get_session_exists(self) -> None:
        """Test retrieving an existing session."""
        created = session_store.create_session(data={"test": "data"})
        retrieved = session_store.get_session(created.session_id)

        assert retrieved is not None
        assert retrieved.session_id == created.session_id
        assert retrieved.data == created.data

    def test_get_session_not_found(self) -> None:
        """Test retrieving non-existent session."""
        result = session_store.get_session("non-existent-id")
        assert result is None

    def test_get_session_expired(self) -> None:
        """Test that expired sessions return None and are cleaned up."""
        # Create session with very short TTL
        session = session_store.create_session(ttl_seconds=0)
        time.sleep(0.1)  # Wait for expiration

        result = session_store.get_session(session.session_id)
        assert result is None

    def test_update_session_success(self) -> None:
        """Test updating an existing session."""
        session = session_store.create_session(data={"initial": "value"})

        success = session_store.update_session(
            session.session_id, {"new_key": "new_value"}
        )

        assert success is True
        updated = session_store.get_session(session.session_id)
        assert updated is not None
        assert updated.get("initial") == "value"
        assert updated.get("new_key") == "new_value"

    def test_update_session_not_found(self) -> None:
        """Test updating non-existent session."""
        success = session_store.update_session("non-existent", {"key": "value"})
        assert success is False

    def test_update_session_rejects_non_serializable(self) -> None:
        """Test that non-serializable updates are rejected."""
        session = session_store.create_session()

        with pytest.raises(ValueError):
            session_store.update_session(
                session.session_id, {"func": lambda x: x}
            )

    def test_clear_session_success(self) -> None:
        """Test clearing an existing session."""
        session = session_store.create_session()

        success = session_store.clear_session(session.session_id)
        assert success is True

        result = session_store.get_session(session.session_id)
        assert result is None

    def test_clear_session_not_found(self) -> None:
        """Test clearing non-existent session."""
        success = session_store.clear_session("non-existent")
        assert success is False

    def test_session_id_uniqueness(self) -> None:
        """Test that generated session IDs are unique."""
        sessions = [session_store.create_session() for _ in range(100)]
        ids = [s.session_id for s in sessions]

        assert len(ids) == len(set(ids))  # All unique

    def test_session_id_secure(self) -> None:
        """Test that session IDs are cryptographically secure."""
        session = session_store.create_session()

        # Should be URL-safe base64, reasonable length
        assert len(session.session_id) >= 32
        # Should not contain URL-unsafe characters
        assert " " not in session.session_id
        assert "+" not in session.session_id
        assert "/" not in session.session_id


class TestSessionStoreCleanup:
    """Test TTL cleanup and max session enforcement."""

    @pytest.fixture(autouse=True)
    def reset_store(self) -> None:
        """Reset the global session store before each test."""
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)
        yield
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)

    def test_cleanup_expired_removes_old_sessions(self) -> None:
        """Test that expired sessions are cleaned up."""
        # Create sessions with very short TTL
        short_session = session_store.create_session(ttl_seconds=0)
        long_session = session_store.create_session(ttl_seconds=3600)

        time.sleep(0.1)  # Wait for short session to expire

        # Trigger cleanup via creating another session
        session_store.create_session()

        assert session_store.get_session(short_session.session_id) is None
        assert session_store.get_session(long_session.session_id) is not None

    def test_max_session_cap_enforced(self) -> None:
        """Test that max session cap is enforced."""
        # Temporarily lower max for testing
        original_max = SessionStore.MAX_SESSIONS
        SessionStore.MAX_SESSIONS = 5

        try:
            # Create sessions up to the cap
            sessions = [session_store.create_session() for _ in range(5)]
            initial_count = len(session_store._sessions)
            assert initial_count == 5

            # Create one more - should trigger cleanup
            new_session = session_store.create_session()

            # Should still be at cap (oldest removed)
            assert len(session_store._sessions) == 5
            # Oldest session should be gone
            assert session_store.get_session(sessions[0].session_id) is None
            # New session should exist
            assert session_store.get_session(new_session.session_id) is not None
        finally:
            SessionStore.MAX_SESSIONS = original_max

    def test_max_session_removes_oldest_first(self) -> None:
        """Test that oldest sessions are removed first when at cap."""
        original_max = SessionStore.MAX_SESSIONS
        SessionStore.MAX_SESSIONS = 3

        try:
            # Create sessions with delay to ensure different timestamps
            session1 = session_store.create_session()
            time.sleep(0.01)
            session2 = session_store.create_session()
            time.sleep(0.01)
            session3 = session_store.create_session()

            # Create 4th session - should remove session1 (oldest)
            session4 = session_store.create_session()

            assert session_store.get_session(session1.session_id) is None
            assert session_store.get_session(session2.session_id) is not None
            assert session_store.get_session(session3.session_id) is not None
            assert session_store.get_session(session4.session_id) is not None
        finally:
            SessionStore.MAX_SESSIONS = original_max


class TestSessionStoreStats:
    """Test SessionStore statistics."""

    @pytest.fixture(autouse=True)
    def reset_store(self) -> None:
        """Reset the global session store before each test."""
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)
        yield
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)

    def test_stats_empty_store(self) -> None:
        """Test stats on empty store."""
        stats = session_store.get_stats()

        assert stats["count"] == 0
        assert stats["oldest_created"] is None
        assert stats["newest_created"] is None

    def test_stats_with_sessions(self) -> None:
        """Test stats with active sessions."""
        now = time.time()

        session1 = session_store.create_session()
        time.sleep(0.01)
        session2 = session_store.create_session()

        stats = session_store.get_stats()

        assert stats["count"] == 2
        assert stats["oldest_created"] <= stats["newest_created"]
        assert stats["oldest_expires"] <= stats["newest_expires"]


class TestCookiePersistence:
    """Test cookie save/restore functionality."""

    @pytest.fixture(autouse=True)
    def reset_store(self) -> None:
        """Reset the global session store before each test."""
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)
        yield
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)

    def test_save_cookies_success(self) -> None:
        """Test saving cookies to session."""
        session = session_store.create_session()
        cookies = {"session_id": "abc123", "auth_token": "xyz789"}

        success = session_store.save_cookies(session.session_id, cookies)

        assert success is True
        retrieved = session_store.get_session(session.session_id)
        assert retrieved is not None
        assert "_cookies" in retrieved.data

    def test_save_cookies_not_found(self) -> None:
        """Test saving cookies to non-existent session."""
        success = session_store.save_cookies("non-existent", {"key": "value"})
        assert success is False

    def test_restore_cookies_success(self) -> None:
        """Test restoring cookies from session."""
        session = session_store.create_session()
        original_cookies = {"session_id": "abc123", "auth_token": "xyz789"}

        session_store.save_cookies(session.session_id, original_cookies)
        restored = session_store.restore_cookies(session.session_id)

        assert restored == original_cookies

    def test_restore_cookies_not_found(self) -> None:
        """Test restoring cookies from non-existent session."""
        result = session_store.restore_cookies("non-existent")
        assert result == {}

    def test_restore_cookies_no_cookies(self) -> None:
        """Test restoring cookies from session with no cookies."""
        session = session_store.create_session()
        result = session_store.restore_cookies(session.session_id)
        assert result == {}

    def test_cookie_round_trip(self) -> None:
        """Test full cookie save/restore round-trip."""
        session = session_store.create_session()
        cookies = {
            "session_id": "test_session_123",
            "auth_token": "bearer_token_xyz",
            "preferences": "dark_mode",
        }

        # Save
        session_store.save_cookies(session.session_id, cookies)

        # Restore
        restored = session_store.restore_cookies(session.session_id)

        assert restored == cookies


class TestConcurrency:
    """Test thread-safe operations."""

    @pytest.fixture(autouse=True)
    def reset_store(self) -> None:
        """Reset the global session store before each test."""
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)
        yield
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)

    def test_concurrent_create_sessions(self) -> None:
        """Test creating sessions concurrently."""
        num_threads = 10
        sessions: list[WebSession] = []
        lock = threading.Lock()

        def create_session() -> None:
            session = session_store.create_session()
            with lock:
                sessions.append(session)

        threads = [threading.Thread(target=create_session) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(sessions) == num_threads
        # All IDs should be unique
        ids = [s.session_id for s in sessions]
        assert len(ids) == len(set(ids))

    def test_concurrent_read_write(self) -> None:
        """Test concurrent reads and updates."""
        session = session_store.create_session(data={"counter": 0})
        num_operations = 50

        def increment() -> None:
            for i in range(num_operations):
                current = session_store.get_session(session.session_id)
                if current:
                    session_store.update_session(
                        session.session_id, {"counter": i}
                    )

        # Run concurrent updates from multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(increment) for _ in range(5)]
            for f in futures:
                f.result()

        # Session should still be intact (no crashes)
        final = session_store.get_session(session.session_id)
        assert final is not None
        # Counter should have some value (exact value depends on timing)
        assert isinstance(final.get("counter"), int)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture(autouse=True)
    def reset_store(self) -> None:
        """Reset the global session store before each test."""
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)
        yield
        for sid in list(session_store._sessions.keys()):
            session_store.clear_session(sid)

    def test_update_expired_session(self) -> None:
        """Test updating an expired session fails."""
        session = session_store.create_session(ttl_seconds=0)
        time.sleep(0.1)

        success = session_store.update_session(
            session.session_id, {"key": "value"}
        )
        assert success is False

    def test_empty_data_operations(self) -> None:
        """Test operations with empty data."""
        session = session_store.create_session()

        # Empty update should succeed
        success = session_store.update_session(session.session_id, {})
        assert success is True

        # Empty cookies should work
        session_store.save_cookies(session.session_id, {})
        restored = session_store.restore_cookies(session.session_id)
        assert restored == {}

    def test_unicode_data(self) -> None:
        """Test handling of unicode data."""
        unicode_data = {
            "chinese": "你好世界",
            "emoji": "🎉🎊",
            "arabic": "مرحبا",
            "special": "ñáéíóú",
        }

        session = session_store.create_session(data=unicode_data)
        retrieved = session_store.get_session(session.session_id)

        assert retrieved is not None
        assert retrieved.data == unicode_data

    def test_large_data(self) -> None:
        """Test handling of larger data structures."""
        large_data = {
            "items": [{"id": i, "data": "x" * 100} for i in range(100)],
            "nested": {"deeply": {"nested": {"value": list(range(50))}}},
        }

        session = session_store.create_session(data=large_data)
        retrieved = session_store.get_session(session.session_id)

        assert retrieved is not None
        assert len(retrieved.get("items")) == 100
