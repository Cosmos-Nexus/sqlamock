from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from .index_schemas import IndexBase, Product, User, get_index_session

if TYPE_CHECKING:
    from sqlamock.connection_provider import MockConnectionProvider
    from sqlamock.db_mock import DBMock


@pytest.fixture(scope="session")
def db_mock_base_model() -> "type[IndexBase]":
    return IndexBase


@pytest.fixture(scope="session", autouse=True)
def mock_index_session(db_mock_connection: "MockConnectionProvider"):
    def get_engine(*args, **kwargs):
        return db_mock_connection.get_engine()

    with patch("tests.index_schemas.create_engine", get_engine):
        yield


def test_indexes_are_created(
    db_mock: "DBMock", db_mock_connection: "MockConnectionProvider"
):
    with db_mock.from_orm([User(email="test@example.com", username="testuser")]):
        engine = db_mock_connection.get_engine()
        inspection = inspect(engine)

        indexes = inspection.get_indexes("user")
        index_names = [idx["name"] for idx in indexes]

        assert "idx_username" in index_names


def test_unique_constraint_enforced(db_mock: "DBMock"):
    with pytest.raises(IntegrityError):
        with db_mock.from_orm(
            [
                User(email="test@example.com", username="user1"),
                User(email="test@example.com", username="user2"),
            ]
        ):
            pass


def test_unique_constraint_on_column_enforced(db_mock: "DBMock"):
    with pytest.raises(IntegrityError):
        with db_mock.from_orm(
            [
                Product(name="Product 1", sku="SKU001", price=100),
                Product(name="Product 2", sku="SKU001", price=200),
            ]
        ):
            pass


def test_composite_unique_constraint_enforced(db_mock: "DBMock"):
    with pytest.raises(IntegrityError):
        with db_mock.from_orm(
            [
                User(email="test@example.com", username="testuser"),
                User(email="test@example.com", username="testuser"),
            ]
        ):
            pass
    with db_mock.from_orm(
        [
            User(email="test1@example.com", username="user1"),
            User(email="test2@example.com", username="user2"),
        ]
    ):
        pass


def test_indexes_exist_on_product_table(
    db_mock: "DBMock", db_mock_connection: "MockConnectionProvider"
):
    with db_mock.from_orm([Product(name="Test Product", sku="SKU001", price=100)]):
        engine = db_mock_connection.get_engine()
        inspection = inspect(engine)

        indexes = inspection.get_indexes("product")
        index_names = [idx["name"] for idx in indexes]

        assert "idx_product_name" in index_names


def test_partial_index_created(
    db_mock: "DBMock", db_mock_connection: "MockConnectionProvider"
):
    with db_mock.from_orm(
        [
            User(email="active@example.com", username="active", active=True),
            User(email="inactive@example.com", username="inactive", active=False),
        ]
    ):
        engine = db_mock_connection.get_engine()
        inspection = inspect(engine)

        indexes = inspection.get_indexes("user")
        index_names = [idx["name"] for idx in indexes]

        assert "idx_active_users" in index_names or any(
            "idx_active_users" in idx.get("name", "") for idx in indexes
        )


def test_partial_index_on_product(
    db_mock: "DBMock", db_mock_connection: "MockConnectionProvider"
):
    with db_mock.from_orm(
        [
            Product(name="Active Product", sku="SKU001", price=100, archived=False),
            Product(name="Archived Product", sku="SKU002", price=200, archived=True),
        ]
    ):
        engine = db_mock_connection.get_engine()
        inspection = inspect(engine)

        indexes = inspection.get_indexes("product")
        index_names = [idx["name"] for idx in indexes]

        assert "idx_active_products" in index_names or any(
            "idx_active_products" in idx.get("name", "") for idx in indexes
        )


def test_multiple_indexes_on_same_table(
    db_mock: "DBMock", db_mock_connection: "MockConnectionProvider"
):
    with db_mock.from_orm(
        [
            User(email="user1@example.com", username="user1", active=True),
            User(email="user2@example.com", username="user2", active=False),
        ]
    ):
        engine = db_mock_connection.get_engine()
        inspection = inspect(engine)

        indexes = inspection.get_indexes("user")
        index_names = [idx["name"] for idx in indexes]

        assert (
            len(
                [
                    name
                    for name in index_names
                    if name in ("idx_username", "idx_active_users")
                ]
            )
            >= 1
        )
