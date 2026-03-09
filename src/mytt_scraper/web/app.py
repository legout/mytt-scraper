"""Application factory for the MyTischtennis web interface."""

import time

from starhtml import StarHTML

from .config import WebConfig


def create_app(config: WebConfig | None = None) -> StarHTML:
    """Create and configure the StarHTML application.
    
    Args:
        config: Web configuration. Uses defaults if not provided.
        
    Returns:
        Configured StarHTML application instance.
    """
    config = config or WebConfig()
    app = StarHTML()
    
    # Register routes
    from .routes import auth, search, tables
    auth.register(app)
    search.register(app)
    tables.register(app)
    
    # Health check endpoint
    @app.route("/health")
    def health_check():
        """Basic health check endpoint."""
        return {"status": "healthy", "timestamp": time.time()}
    
    return app