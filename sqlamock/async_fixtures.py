from typing import TYPE_CHECKING

import pytest

from sqlamock.patches import Patches

from .async_connection_provider import MockAsyncConnectionProvider
from .async_db_mock import AsyncDBMock
from .event_manager import EventManager

if TYPE_CHECKING:
    from .types import BaseType


@pytest.fixture(scope="session")
def db_mock_async_connection() -> "MockAsyncConnectionProvider":
    return MockAsyncConnectionProvider()


@pytest.fixture(scope="session")
def db_mock_async_event_manager() -> "EventManager":
    """Fixture that provides an EventManager for registering async SQLAlchemy event listeners.

    This fixture creates and returns an EventManager instance that can be used to
    register event listeners for testing async event-driven database operations.

    Returns:
        EventManager: An instance of EventManager for use in async tests.
    """
    return EventManager()


@pytest.fixture(scope="session")
def db_mock_async(
    db_mock_async_connection: "MockAsyncConnectionProvider",
    db_mock_base_model: "type[BaseType]",
    db_mock_patches: "Patches",
    db_mock_async_event_manager: "EventManager",
) -> "AsyncDBMock":
    return AsyncDBMock(
        db_mock_base_model,
        db_mock_async_connection,
        db_mock_patches,
        db_mock_async_event_manager,
    )
