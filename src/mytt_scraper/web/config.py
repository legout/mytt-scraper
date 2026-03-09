"""Web application configuration."""

from dataclasses import dataclass


@dataclass
class WebConfig:
    """Configuration for the web application.
    
    Attributes:
        host: Host address to bind to (default: "127.0.0.1")
        port: Port number to listen on (default: 8000)
        debug: Enable debug mode (default: False)
    """
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False