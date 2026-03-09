"""Authentication routes for login/logout."""

import asyncio
import json
import logging
from functools import wraps
from typing import Any, Callable

from starhtml import (
    Button,
    Div,
    Form,
    H2,
    Input,
    Label,
    P,
    RedirectResponse,
    StarHTML,
)
from starlette.requests import Request
from starlette.responses import StreamingResponse

from ...utils.auth import login_with_playwright
from ..signals.session import auth_error, auth_status, session_username, session_valid
from ..state import session_store

logger = logging.getLogger(__name__)


def get_session_id_from_request(request: Request) -> str | None:
    """Extract session ID from request cookies.
    
    Args:
        request: The incoming request.
        
    Returns:
        Session ID if found in cookies, None otherwise.
    """
    return request.cookies.get("session_id")


def require_auth(handler: Callable) -> Callable:
    """Decorator to protect routes that require authentication.
    
    Checks if the request has a valid session with a username set.
    Redirects to /login if not authenticated.
    
    Args:
        handler: The route handler function to wrap.
        
    Returns:
        Wrapped handler that checks authentication first.
    """
    @wraps(handler)
    async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
        session_id = get_session_id_from_request(request)
        
        if session_id:
            session = session_store.get_session(session_id)
            if session and session.get("username"):
                # User is authenticated, proceed with handler
                return await handler(request, *args, **kwargs) if asyncio.iscoroutinefunction(handler) else handler(request, *args, **kwargs)
        
        # Not authenticated, redirect to login
        return RedirectResponse("/login", status_code=302)
    
    return wrapper


def _sse_signal(**kwargs) -> str:
    """Generate an SSE signal event.
    
    Args:
        **kwargs: Signal key-value pairs to merge.
        
    Returns:
        Formatted SSE event string.
    """
    return f'event: datastar-patch-signals\ndata: signals {json.dumps(kwargs)}\n\n'


def _sse_execute_script(script: str) -> str:
    """Generate an SSE execute script event.
    
    Args:
        script: JavaScript code to execute.
        
    Returns:
        Formatted SSE event string.
    """
    return f'event: datastar-execute-script\ndata: script {json.dumps(script)}\n\n'


def register(app: StarHTML) -> None:
    """Register authentication routes with the application.
    
    Args:
        app: The StarHTML application instance.
    """
    
    @app.route("/")
    def home_page(request: Request):
        """Render the home page.
        
        Args:
            request: The incoming request.
            
        Returns:
            Home page content.
        """
        from ..components.layout import PageLayout
        
        # Check if authenticated
        session_id = get_session_id_from_request(request)
        if not session_id:
            return RedirectResponse("/login", status_code=302)
        
        session = session_store.get_session(session_id)
        if not session or not session.get("username"):
            return RedirectResponse("/login", status_code=302)
        
        content = Div(
            H2(f"Welcome, {session.get('username', 'User')}!"),
            P("Use the navigation to access search and tables."),
        )
        
        return PageLayout("Home", content)
    
    @app.route("/login")
    def login_handler(request: Request):
        """Handle login page (GET) and form submission (POST with SSE).
        
        Args:
            request: The incoming request.
            
        Returns:
            GET: Login page content with form.
            POST: SSE stream with authentication progress.
        """
        from ..components.layout import PageLayout
        
        # Handle POST (login form submission via SSE)
        if request.method == "POST":
            async def sse_stream():
                # Parse form data
                form_data = await request.form()
                username = str(form_data.get("username", ""))
                password = str(form_data.get("password", ""))
                
                # Set authenticating status
                yield _sse_signal(auth_status="authenticating", auth_error="")
                
                try:
                    # Prepare cookie storage for Playwright session
                    playwright_cookies: dict[str, Any] = {}
                    
                    # Call async login directly (login_with_playwright is already async)
                    login_success = await login_with_playwright(
                        username, 
                        password, 
                        headless=True, 
                        session_cookies=playwright_cookies
                    )
                    
                    if login_success:
                        # Create session for authenticated user with cookies
                        session = session_store.create_session({
                            "username": username,
                            "cookies": playwright_cookies,
                        })
                        
                        # Signal success with session info
                        yield _sse_signal(
                            session_valid=True,
                            session_username=username,
                            auth_status="done",
                        )
                        
                        # Set session cookie via JavaScript and redirect
                        # Note: JavaScript cookies can't be httponly, but we get CSRF protection
                        # from the server-side session validation
                        yield _sse_execute_script(
                            f'document.cookie = "session_id={session.session_id}; path=/; max-age=3600"; '
                            f'window.location.href = "/"'
                        )
                    else:
                        # Signal failure
                        yield _sse_signal(
                            auth_error="Invalid credentials",
                            auth_status="error",
                        )
                
                except Exception as e:
                    # Log detailed error server-side
                    logger.exception("Login failed for user %s", username)
                    # Return generic user-facing message
                    yield _sse_signal(
                        auth_error="Login failed. Please try again.",
                        auth_status="error",
                    )
            
            return StreamingResponse(sse_stream(), media_type="text/event-stream")
        
        # Handle GET (render login page)
        # Check if already authenticated
        session_id = get_session_id_from_request(request)
        if session_id:
            session = session_store.get_session(session_id)
            if session and session.get("username"):
                return RedirectResponse("/", status_code=302)
        
        login_form = Div(
            H2("Login to MyTischtennis"),
            Form(
                Div(
                    Label("Username/Email:", _for="username"),
                    Input(
                        type="text",
                        id="username",
                        name="username",
                        placeholder="Enter your username",
                        required=True,
                        data_model="username",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Password:", _for="password"),
                    Input(
                        type="password",
                        id="password",
                        name="password",
                        placeholder="Enter your password",
                        required=True,
                        data_model="password",
                    ),
                    cls="form-group",
                ),
                Div(
                    P(id="auth-error", data_text="auth_error", cls="error-message"),
                    cls="error-container",
                ),
                Button(
                    "Login",
                    type="submit",
                    data_on_submit="@post('/login')",
                    disabled=auth_status == "authenticating",
                ),
                method="POST",
                action="/login",
                data_on_submit="@post('/login')",
            ),
            cls="login-card",
        )
        
        return PageLayout("Login", login_form)
    
    @app.route("/logout", methods=["POST"])
    def logout_handler(request: Request) -> RedirectResponse:
        """Handle logout request.
        
        Clears the session and redirects to login page.
        
        Args:
            request: The incoming request.
            
        Returns:
            Redirect to /login with cleared session cookie.
        """
        session_id = get_session_id_from_request(request)
        
        if session_id:
            session_store.clear_session(session_id)
        
        response = RedirectResponse("/login", status_code=302)
        response.delete_cookie("session_id")
        
        return response
