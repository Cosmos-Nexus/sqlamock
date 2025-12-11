from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from sqlamock.async_connection_provider import MockAsyncConnectionProvider
from sqlamock.async_db_mock import AsyncDBMock
from sqlamock.connection_provider import MockConnectionProvider
from sqlamock.db_mock import DBMock
from sqlamock.patches import Patches
from tests.example_tests.example_async_app import Base as AsyncBase
from tests.example_tests.example_schemas import Base

if TYPE_CHECKING:
    pass


@pytest.fixture(scope="session")
def db_mock_connection() -> "MockConnectionProvider":
    return MockConnectionProvider()


@pytest.fixture(scope="session")
def db_mock_patches() -> "Patches":
    return Patches()


@pytest.fixture(scope="session")
def db_mock_base_model() -> "type[Base]":
    return Base


@pytest.fixture(scope="session")
def db_mock(
    db_mock_connection: "MockConnectionProvider",
    db_mock_base_model: "type[Base]",
    db_mock_patches: "Patches",
) -> "DBMock":
    return DBMock(db_mock_base_model, db_mock_connection, db_mock_patches)


@pytest.fixture(scope="session", autouse=True)
def mock_example_session(db_mock_connection: "MockConnectionProvider"):
    def get_engine(*args, **kwargs):
        return db_mock_connection.get_engine()

    with patch("tests.example_tests.example_schemas.create_engine", get_engine):
        yield


@pytest.fixture(scope="session")
def db_mock_async_connection() -> "MockAsyncConnectionProvider":
    return MockAsyncConnectionProvider()


@pytest.fixture(scope="session")
def db_mock_async_base_model() -> "type[AsyncBase]":
    return AsyncBase


@pytest.fixture(scope="session")
def db_mock_async(
    db_mock_async_connection: "MockAsyncConnectionProvider",
    db_mock_async_base_model: "type[AsyncBase]",
    db_mock_patches: "Patches",
) -> "AsyncDBMock":
    return AsyncDBMock(
        db_mock_async_base_model, db_mock_async_connection, db_mock_patches
    )


@pytest.fixture(scope="session", autouse=True)
def mock_example_async_session(db_mock_async_connection: "MockAsyncConnectionProvider"):
    def get_session(*args, **kwargs):
        return db_mock_async_connection.get_async_session()

    with patch("tests.example_tests.example_async_app.get_session", get_session):
        yield
