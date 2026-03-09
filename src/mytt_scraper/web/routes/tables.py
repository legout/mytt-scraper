"""League table viewer routes."""

from starhtml import Div, H1, RedirectResponse, StarHTML
from starlette.requests import Request


def register(app: StarHTML) -> None:
    """Register table routes with the application.

    Args:
        app: The StarHTML application instance.
    """
    from .auth import get_session_id_from_request, session_store

    @app.route("/tables")
    def tables_page(request: Request):
        """Render the league tables page.

        Args:
            request: The incoming request.

        Returns:
            Tables page content or redirect to login if not authenticated.
        """
        from ..components.layout import PageLayout

        # Check authentication
        session_id = get_session_id_from_request(request)
        if not session_id:
            return RedirectResponse("/login", status_code=302)
        
        session = session_store.get_session(session_id)
        if not session or not session.get("username"):
            return RedirectResponse("/login", status_code=302)

        content = Div(
            H1("League Tables"),
            Div("Table viewer coming soon...", class_="placeholder"),
        )

        return PageLayout("League Tables", content)
