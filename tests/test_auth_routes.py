"""Tests for authentication routes.

Tests cover login page rendering, login/logout handlers, SSE updates,
and protected route access control.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starhtml import TestClient
from starlette.requests import Request

from mytt_scraper.web.app import create_app
from mytt_scraper.web.routes.auth import get_session_id_from_request, require_auth
from mytt_scraper.web.signals.session import auth_error, auth_status, session_username, session_valid
from mytt_scraper.web.state import SessionStore, WebSession


@pytest.fixture
def app():
    """Create test app instance."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client that doesn't follow redirects automatically."""
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def mock_session_store():
    """Create a mock session store for testing."""
    store = SessionStore()
    return store


class TestGetSessionIdFromRequest:
    """Test session ID extraction from requests."""

    def test_extracts_session_id_from_cookies(self):
        """Test that session ID is extracted from request cookies."""
        request = MagicMock(spec=Request)
        request.cookies = {"session_id": "test-session-123"}
        
        result = get_session_id_from_request(request)
        
        assert result == "test-session-123"

    def test_returns_none_when_no_session_cookie(self):
        """Test that None is returned when no session cookie exists."""
        request = MagicMock(spec=Request)
        request.cookies = {}
        
        result = get_session_id_from_request(request)
        
        assert result is None

    def test_returns_none_for_empty_session_id(self):
        """Test that empty session ID is handled."""
        request = MagicMock(spec=Request)
        request.cookies = {"session_id": ""}
        
        result = get_session_id_from_request(request)
        
        assert result == ""


class TestRequireAuthDecorator:
    """Test the require_auth decorator functionality."""

    def test_redirects_when_no_session_cookie(self):
        """Test that unauthenticated requests are redirected."""
        request = MagicMock(spec=Request)
        request.cookies = {}
        
        @require_auth
        def protected_handler(request):
            return {"message": "secret"}
        
        import asyncio
        result = asyncio.run(protected_handler(request))
        
        assert result.status_code == 302
        assert result.headers["location"] == "/login"

    def test_redirects_when_session_not_found(self, mock_session_store):
        """Test redirect when session ID doesn't exist in store."""
        request = MagicMock(spec=Request)
        request.cookies = {"session_id": "nonexistent-session"}
        
        @require_auth
        def protected_handler(request):
            return {"message": "secret"}
        
        import asyncio
        result = asyncio.run(protected_handler(request))
        
        assert result.status_code == 302
        assert result.headers["location"] == "/login"

    def test_redirects_when_no_username_in_session(self, mock_session_store):
        """Test redirect when session exists but no username (not authenticated)."""
        session = mock_session_store.create_session({})  # No username
        
        request = MagicMock(spec=Request)
        request.cookies = {"session_id": session.session_id}
        
        @require_auth
        def protected_handler(request):
            return {"message": "secret"}
        
        import asyncio
        result = asyncio.run(protected_handler(request))
        
        assert result.status_code == 302
        assert result.headers["location"] == "/login"

    def test_allows_access_when_authenticated(self, mock_session_store):
        """Test that authenticated requests proceed to handler."""
        session = mock_session_store.create_session({"username": "testuser"})
        
        request = MagicMock(spec=Request)
        request.cookies = {"session_id": session.session_id}
        
        @require_auth
        def protected_handler(request):
            return {"message": "secret"}
        
        # Patch the global session_store to use our mock
        with patch("mytt_scraper.web.routes.auth.session_store", mock_session_store):
            import asyncio
            result = asyncio.run(protected_handler(request))
        
        assert result == {"message": "secret"}

    def test_allows_async_handlers(self, mock_session_store):
        """Test that async handlers work with the decorator."""
        session = mock_session_store.create_session({"username": "testuser"})
        
        request = MagicMock(spec=Request)
        request.cookies = {"session_id": session.session_id}
        
        @require_auth
        async def async_protected_handler(request):
            return {"message": "async secret"}
        
        with patch("mytt_scraper.web.routes.auth.session_store", mock_session_store):
            import asyncio
            result = asyncio.run(async_protected_handler(request))
        
        assert result == {"message": "async secret"}


class TestLoginPage:
    """Test login page rendering."""

    def test_login_page_renders_form(self, client):
        """Test that login page contains the login form."""
        response = client.get("/login")
        
        assert response.status_code == 200
        html = response.text.lower()
        assert "username" in html
        assert "password" in html
        assert "login" in html

    def test_login_page_has_form_inputs(self, client):
        """Test that login form has required input fields."""
        response = client.get("/login")
        
        assert response.status_code == 200
        html = response.text
        assert 'name="username"' in html
        assert 'name="password"' in html
        assert 'type="password"' in html

    def test_redirects_when_already_authenticated(self, client, mock_session_store):
        """Test that authenticated users are redirected from login page."""
        session = mock_session_store.create_session({"username": "testuser"})
        
        with patch("mytt_scraper.web.routes.auth.session_store", mock_session_store):
            client.cookies = {"session_id": session.session_id}
            response = client.get("/login")
        
        assert response.status_code == 302
        assert response.headers["location"] == "/"


class TestLoginHandler:
    """Test login POST handler with SSE."""

    @patch("mytt_scraper.web.routes.auth.login_with_playwright", new_callable=AsyncMock)
    def test_successful_login_creates_session(self, mock_login, client):
        """Test that successful login creates a session."""
        mock_login.return_value = True
        
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"}
        )
        
        assert response.status_code == 200
        # Check that login was called with correct params
        mock_login.assert_called_once()
        call_args = mock_login.call_args
        assert call_args[0][0] == "testuser"
        assert call_args[0][1] == "testpass"
        # Check that session_cookies dict is passed
        assert call_args[1].get("headless") == True
        assert "session_cookies" in call_args[1]
        # Response should contain SSE data
        assert "data:" in response.text

    @patch("mytt_scraper.web.routes.auth.login_with_playwright", new_callable=AsyncMock)
    def test_failed_login_returns_error(self, mock_login, client):
        """Test that failed login returns error signals."""
        mock_login.return_value = False
        
        response = client.post(
            "/login",
            data={"username": "testuser", " password": "wrongpass"}
        )
        
        assert response.status_code == 200
        # Response should contain SSE data with error
        assert "data:" in response.text
        assert "auth_error" in response.text

    @patch("mytt_scraper.web.routes.auth.login_with_playwright", new_callable=AsyncMock)
    def test_login_exception_handling(self, mock_login, client):
        """Test that login exceptions are handled gracefully."""
        mock_login.side_effect = Exception("Connection error")
        
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"}
        )
        
        assert response.status_code == 200
        # Response should contain error signal
        assert "data:" in response.text
        assert "auth_error" in response.text


class TestLogoutHandler:
    """Test logout POST handler."""

    def test_logout_clears_session(self, client, mock_session_store):
        """Test that logout clears the session."""
        session = mock_session_store.create_session({"username": "testuser"})
        
        with patch("mytt_scraper.web.routes.auth.session_store", mock_session_store):
            client.cookies = {"session_id": session.session_id}
            response = client.post("/logout")
        
        assert response.status_code == 302
        assert response.headers["location"] == "/login"
        # Verify session was cleared
        assert mock_session_store.get_session(session.session_id) is None

    def test_logout_without_session_still_redirects(self, client):
        """Test that logout works even without an active session."""
        response = client.post("/logout")
        
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    def test_logout_deletes_cookie(self, client, mock_session_store):
        """Test that logout deletes the session cookie."""
        session = mock_session_store.create_session({"username": "testuser"})
        
        with patch("mytt_scraper.web.routes.auth.session_store", mock_session_store):
            client.cookies = {"session_id": session.session_id}
            response = client.post("/logout")
        
        # Check for Set-Cookie header that deletes the cookie
        set_cookie = response.headers.get("set-cookie", "")
        assert "session_id" in set_cookie.lower() or "max-age=0" in set_cookie.lower()


class TestProtectedRoutes:
    """Test that protected routes require authentication."""

    def test_home_redirects_when_unauthenticated(self, client):
        """Test that / redirects to login when not authenticated."""
        response = client.get("/")
        
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    def test_search_redirects_when_unauthenticated(self, client):
        """Test that /search redirects to login when not authenticated."""
        response = client.get("/search")
        
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    def test_tables_redirects_when_unauthenticated(self, client):
        """Test that /tables redirects to login when not authenticated."""
        response = client.get("/tables")
        
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    def test_home_accessible_when_authenticated(self, client, mock_session_store):
        """Test that / is accessible when authenticated."""
        session = mock_session_store.create_session({"username": "testuser"})
        
        with patch("mytt_scraper.web.routes.auth.session_store", mock_session_store):
            client.cookies = {"session_id": session.session_id}
            response = client.get("/")
        
        assert response.status_code == 200
        assert "Welcome" in response.text

    def test_search_accessible_when_authenticated(self, client):
        """Test that /search is accessible when authenticated."""
        # Use the real session store since search.py imports it at registration time
        from mytt_scraper.web.routes.auth import session_store
        
        # Clear any existing sessions
        session_store._sessions.clear()
        
        # Create a session in the real store
        session = session_store.create_session({"username": "testuser"})
        
        client.cookies = {"session_id": session.session_id}
        response = client.get("/search")
        
        assert response.status_code == 200
        assert "Player Search" in response.text

    def test_tables_accessible_when_authenticated(self, client):
        """Test that /tables is accessible when authenticated."""
        # Use the real session store since tables.py imports it at registration time
        from mytt_scraper.web.routes.auth import session_store
        
        # Clear any existing sessions
        session_store._sessions.clear()
        
        # Create a session in the real store
        session = session_store.create_session({"username": "testuser"})
        
        client.cookies = {"session_id": session.session_id}
        response = client.get("/tables")
        
        assert response.status_code == 200
        assert "League Tables" in response.text


class TestSessionSignals:
    """Test session signal defaults and behavior."""

    def test_session_valid_default(self):
        """Test session_valid signal default value."""
        assert session_valid.initial == False

    def test_session_username_default(self):
        """Test session_username signal default value."""
        assert session_username.initial == ""

    def test_auth_error_default(self):
        """Test auth_error signal default value."""
        assert auth_error.initial == ""

    def test_auth_status_default(self):
        """Test auth_status signal default value."""
        assert auth_status.initial == "idle"
