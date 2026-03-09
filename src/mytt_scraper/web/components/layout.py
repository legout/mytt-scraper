"""Page layout components."""

from starhtml import Div, H1, Header, Main, Nav


def PageLayout(title: str, content) -> Div:
    """Create a page layout with navigation and content.
    
    Args:
        title: Page title to display in the header.
        content: Page content element(s).
        
    Returns:
        A Div containing the full page layout.
    """
    return Div(
        Header(
            Nav("MyTischtennis Web")
        ),
        Main(
            H1(title),
            content
        )
    )