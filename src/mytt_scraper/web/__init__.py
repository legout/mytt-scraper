"""MyTischtennis Web Interface - StarHTML + StarUI presentation layer."""

from .app import create_app
from .config import WebConfig

__all__ = ["create_app", "WebConfig"]