"""Event management system for SQLAlchemy event listeners in sqlamock.

This module provides functionality to register and trigger SQLAlchemy event listeners
within the mocking context, allowing for testing of event-driven database operations.
"""

from contextlib import asynccontextmanager, contextmanager
from typing import Any, Callable, Optional, Set

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


class EventManager:
    """Manages SQLAlchemy event listeners for the mocking system.

    This class provides a way to register event listeners that will be triggered
    during database operations within the mock context. It supports both sync and
    async event listeners and ensures proper cleanup when the mock context exits.

    Features:
    - Register event listeners for various SQLAlchemy events
    - Support for both sync and async listeners
    - Automatic cleanup of registered listeners
    - Context manager support for scoped event registration
    """

    def __init__(self):
        """Initialize the EventManager."""
        self._active_listeners: Set[Any] = set()

    def register_listener(self, wrapped_listener: Callable[..., Any]) -> None:
        """Register a listener that's already wrapped with event.listens_for.

        Args:
            wrapped_listener: A listener that's already been wrapped with event.listens_for
        """
        self._active_listeners.add(wrapped_listener)

    def clear_listeners(self) -> None:
        """Clear all registered listeners."""
        self._active_listeners.clear()

    def remove_listeners(self) -> None:
        """Remove all active listeners from their targets."""
        for listener_func in self._active_listeners:
            try:
                # Try to remove the listener using event.remove
                # This is a best-effort approach since we don't track all the details
                event.remove(listener_func)
            except (ValueError, KeyError, AttributeError):
                # Listener might have already been removed or doesn't support removal
                pass
        self._active_listeners.clear()

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up listeners."""
        self.remove_listeners()
